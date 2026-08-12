import httpx
import re

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings


class ResendClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.default_tags: dict[str, str] = {}
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
        tags = _serialize_tags({**self.default_tags, **message.metadata})
        if tags:
            data["tags"] = tags
        return data


def _serialize_tags(metadata: dict) -> list[dict]:
    tags = []
    for name, value in metadata.items():
        clean_name = _clean_tag_part(str(name))
        clean_value = _clean_tag_part(str(value))
        if clean_name and clean_value:
            tags.append({"name": clean_name[:256], "value": clean_value[:256]})
    return tags


def _clean_tag_part(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", value).strip("-")
