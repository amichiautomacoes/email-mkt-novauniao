import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Mapping

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from email_mkt.config import Settings

WEBHOOK_TABLE = "email_mkt_metricas"
ALLOWED_RESEND_WEBHOOK_EVENTS = {
    "email.bounced",
    "email.clicked",
    "email.complained",
    "email.opened",
}


class WebhookVerificationError(ValueError):
    pass


@dataclass(frozen=True)
class ResendWebhookEvent:
    svix_id: str
    event_type: str
    event_created_at: str | None
    payload: dict

    @property
    def data(self) -> dict:
        data = self.payload.get("data")
        return data if isinstance(data, dict) else {}


def verify_resend_webhook(
    *,
    payload: bytes,
    headers: Mapping[str, str | None],
    secret: str,
    tolerance_seconds: int = 300,
    now: int | None = None,
) -> ResendWebhookEvent:
    svix_id = headers.get("svix-id")
    timestamp = headers.get("svix-timestamp")
    signature = headers.get("svix-signature")
    if not svix_id or not timestamp or not signature:
        raise WebhookVerificationError("Missing Svix headers.")
    if not secret:
        raise WebhookVerificationError("Missing RESEND_WEBHOOK_SECRET.")

    timestamp_int = _parse_timestamp(timestamp)
    current_time = int(time.time()) if now is None else now
    if abs(current_time - timestamp_int) > tolerance_seconds:
        raise WebhookVerificationError("Webhook timestamp outside tolerance.")

    expected = _expected_signature(
        secret=secret,
        svix_id=svix_id,
        timestamp=timestamp,
        payload=payload,
    )
    if not _signature_matches(signature, expected):
        raise WebhookVerificationError("Invalid webhook signature.")

    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("type")
    if not isinstance(event_type, str) or not event_type:
        raise WebhookVerificationError("Missing event type.")
    return ResendWebhookEvent(
        svix_id=svix_id,
        event_type=event_type,
        event_created_at=event.get("created_at"),
        payload=event,
    )


class ResendWebhookRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def save_event(self, event: ResendWebhookEvent) -> bool:
        if not self.settings.supabase_database_url:
            return False

        data = event.data
        tags = _tags_by_name(data.get("tags"))
        query = sql.SQL("""
            insert into {}.{} (
              source,
              svix_id,
              event_type,
              event_created_at,
              webhook_received_at,
              resend_email_id,
              message_id,
              recipient_email,
              subject,
              campaign_key,
              template_key,
              lote_key,
              data,
              raw_payload
            )
            values (
              'resend_webhook',
              %s,
              %s,
              %s,
              now(),
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s
            )
            on conflict (svix_id) where svix_id is not null do nothing
            """).format(
            sql.Identifier(self.settings.supabase_schema),
            sql.Identifier(WEBHOOK_TABLE),
        )
        params = (
            event.svix_id,
            event.event_type,
            event.event_created_at,
            data.get("email_id"),
            data.get("message_id"),
            _first_recipient(data.get("to")),
            data.get("subject"),
            tags.get("campaign"),
            tags.get("template"),
            tags.get("lote"),
            Jsonb(data),
            Jsonb(event.payload),
        )

        with psycopg.connect(
            self.settings.supabase_database_url
        ) as conn, conn.cursor() as cur:
            cur.execute(query, params)
            inserted = cur.rowcount > 0
            conn.commit()
        return inserted


def _parse_timestamp(timestamp: str) -> int:
    try:
        return int(timestamp)
    except ValueError as exc:
        raise WebhookVerificationError("Invalid Svix timestamp.") from exc


def _expected_signature(
    *, secret: str, svix_id: str, timestamp: str, payload: bytes
) -> str:
    secret_bytes = _decode_secret(secret)
    signed_payload = b".".join(
        [svix_id.encode("utf-8"), timestamp.encode("utf-8"), payload]
    )
    digest = hmac.new(secret_bytes, signed_payload, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")


def _decode_secret(secret: str) -> bytes:
    encoded_secret = secret.split("_", 1)[1] if secret.startswith("whsec_") else secret
    try:
        return base64.b64decode(encoded_secret)
    except Exception as exc:
        raise WebhookVerificationError("Invalid webhook secret.") from exc


def _signature_matches(signature_header: str, expected: str) -> bool:
    signatures = signature_header.split()
    for signature in signatures:
        version, _, value = signature.partition(",")
        if version == "v1" and hmac.compare_digest(value, expected):
            return True
    return False


def _first_recipient(value: object) -> str | None:
    if isinstance(value, list) and value:
        first = value[0]
        return first if isinstance(first, str) else None
    if isinstance(value, str):
        return value
    return None


def _tags_by_name(value: object) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            str(name): str(tag_value)
            for name, tag_value in value.items()
            if name and tag_value is not None
        }
    if not isinstance(value, list):
        return {}

    tags = {}
    for item in value:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        tag_value = item.get("value")
        if name and tag_value is not None:
            tags[str(name)] = str(tag_value)
    return tags
