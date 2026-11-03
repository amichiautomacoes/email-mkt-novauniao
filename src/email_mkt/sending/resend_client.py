import base64
import hashlib
import mimetypes
import re
from pathlib import Path

import httpx

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
            data["html"], data["attachments"] = _prepare_inline_images(
                message.html, message.attachments
            )
        if message.reply_to:
            data["reply_to"] = message.reply_to
        tags = _serialize_tags({**self.default_tags, **message.metadata})
        if tags:
            data["tags"] = tags
        return data


def _prepare_inline_images(
    html: str, attachments: list[dict]
) -> tuple[str, list[dict]]:
    cid_pattern = r"cid:([^\"' >]+)"
    referenced_cids = set(re.findall(cid_pattern, html))
    aliases: dict[str, str] = {}
    serialized = []
    embedded_images: set[str] = set()

    for attachment in attachments:
        item = dict(attachment)
        content_id = item.get("content_id")
        content_type = item.get("content_type", "")
        content = item.get("content")
        if (
            content_id in referenced_cids
            and content_type.startswith("image/")
            and isinstance(content, str)
        ):
            if item.get("filename") == content_id and re.fullmatch(
                r"[0-9a-f]{32}\.[a-z0-9]+", content_id
            ):
                alias = content_id
            else:
                extension = Path(str(item.get("filename") or "")).suffix.lower()
                extension = extension or mimetypes.guess_extension(content_type) or ""
                digest = hashlib.sha256(
                    base64.b64decode(content, validate=True)
                ).hexdigest()
                alias = f"{digest[:32]}{extension}"
            aliases[content_id] = alias
            item["filename"] = alias
            item["content_id"] = alias
            if alias in embedded_images:
                continue
            embedded_images.add(alias)
        serialized.append(item)

    html = re.sub(
        cid_pattern, lambda match: f"cid:{aliases.get(match[1], match[1])}", html
    )
    return html, serialized


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
