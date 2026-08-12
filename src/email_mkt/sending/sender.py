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
        lote_key: str | None = None,
        etapa: int = 1,
    ) -> CampaignRunResult:
        attempted = len(messages)
        if dry_run or not messages:
            return CampaignRunResult(
                attempted=attempted, sent=0, failed=0, dry_run=True
            )

        client = ResendClient(self.settings)
        if campaign_key and hasattr(client, "default_tags"):
            client.default_tags["campaign"] = campaign_key
        campaign_repository = CampaignRepository(self.settings)
        sent = 0
        errors: list[str] = []

        for message in [message for message in messages if message.attachments]:
            self.rate_limiter.wait()
            try:
                response = client.send(message)
                resend_id = response.json().get("id")
                if resend_id:
                    sent += 1
                    if campaign_key:
                        campaign_repository.record_sent_recipients(
                            campaign_key,
                            [message],
                            lote_key=lote_key,
                            etapa=etapa,
                            resend_email_ids=[resend_id],
                        )
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))

        batchable_messages = [message for message in messages if not message.attachments]
        for batch in _chunks(batchable_messages, self.settings.email_batch_size):
            self.rate_limiter.wait()
            try:
                response = client.send_batch(batch)
                data = response.json().get("data", [])
                sent_count = len(data)
                sent += sent_count
                if campaign_key:
                    campaign_repository.record_sent_recipients(
                        campaign_key,
                        batch[:sent_count],
                        lote_key=lote_key,
                        etapa=etapa,
                        resend_email_ids=[
                            item.get("id") if isinstance(item, dict) else None
                            for item in data[:sent_count]
                        ],
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
