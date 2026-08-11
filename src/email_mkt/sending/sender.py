from itertools import islice

from email_mkt.campaigns.models import CampaignRunResult, EmailMessage
from email_mkt.campaigns.repository import CampaignRepository
from email_mkt.config import Settings
from email_mkt.sending.rate_limiter import RateLimiter
from email_mkt.sending.resend_client import ResendClient


class EmailSender:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.rate_limiter = RateLimiter(settings.resend_requests_per_second)

    def send_batch(
        self,
        messages: list[EmailMessage],
        dry_run: bool = True,
        campaign_key: str | None = None,
    ) -> CampaignRunResult:
        attempted = len(messages)
        if dry_run or not messages:
            return CampaignRunResult(
                attempted=attempted, sent=0, failed=0, dry_run=True
            )

        client = ResendClient(self.settings)
        campaign_repository = CampaignRepository(self.settings)
        sent = 0
        errors: list[str] = []

        for batch in _chunks(messages, self.settings.email_batch_size):
            self.rate_limiter.wait()
            try:
                response = client.send_batch(batch)
                data = response.json().get("data", [])
                sent_count = len(data)
                sent += sent_count
                if campaign_key:
                    campaign_repository.record_sent_recipients(
                        campaign_key, batch[:sent_count]
                    )
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))

        return CampaignRunResult(
            attempted=attempted,
            sent=sent,
            failed=attempted - sent,
            dry_run=False,
            errors=errors,
        )


def _chunks(items: list[EmailMessage], size: int):
    iterator = iter(items)
    while chunk := list(islice(iterator, max(size, 1))):
        yield chunk
