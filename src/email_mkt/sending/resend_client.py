import httpx

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings


class ResendClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = httpx.Client(
            base_url="https://api.resend.com",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "User-Agent": "email-mkt-gcp/0.1",
            },
            timeout=30,
        )

    def send_batch(self, messages: list[EmailMessage]) -> httpx.Response:
        payload = [self._serialize_message(message) for message in messages]
        response = self.client.post("/emails/batch", json=payload)
        response.raise_for_status()
        return response

    def send(self, message: EmailMessage) -> httpx.Response:
        response = self.client.post("/emails", json=self._serialize_message(message))
        response.raise_for_status()
        return response

    def _serialize_message(self, message: EmailMessage) -> dict:
        data = {
            "from": self.settings.email_from,
            "to": [message.to],
            "subject": message.subject,
            "html": message.html,
        }
        if message.attachments:
            data["attachments"] = message.attachments
        if message.reply_to:
            data["reply_to"] = message.reply_to
        return data
