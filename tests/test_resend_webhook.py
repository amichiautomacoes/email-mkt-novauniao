import base64
import hashlib
import hmac
import json

import pytest

from email_mkt.config import Settings
from email_mkt.webhooks import resend
from email_mkt.webhooks.resend import (
    ResendWebhookEvent,
    ResendWebhookRepository,
    WebhookVerificationError,
    verify_resend_webhook,
)


def test_verify_resend_webhook_accepts_valid_signature() -> None:
    secret = "whsec_" + base64.b64encode(b"test-secret").decode("ascii")
    payload = json.dumps({"type": "email.opened", "created_at": "2026-08-12T12:00:00Z"}).encode(
        "utf-8"
    )
    headers = _headers(secret=secret, payload=payload, timestamp="1786536000")

    event = verify_resend_webhook(
        payload=payload,
        headers=headers,
        secret=secret,
        now=1786536000,
    )

    assert event.svix_id == "msg_test"
    assert event.event_type == "email.opened"


def test_verify_resend_webhook_rejects_invalid_signature() -> None:
    payload = b'{"type":"email.opened"}'

    with pytest.raises(WebhookVerificationError):
        verify_resend_webhook(
            payload=payload,
            headers={
                "svix-id": "msg_test",
                "svix-timestamp": "1786536000",
                "svix-signature": "v1,invalid",
            },
            secret="whsec_" + base64.b64encode(b"test-secret").decode("ascii"),
            now=1786536000,
        )


def test_webhook_repository_saves_campaign_template_and_lote_tags(monkeypatch) -> None:
    fake_cursor = FakeCursor()
    fake_conn = FakeConnection(fake_cursor)
    monkeypatch.setattr(resend.psycopg, "connect", lambda _: fake_conn)

    event = ResendWebhookEvent(
        svix_id="evt_1",
        event_type="email.opened",
        event_created_at="2026-08-19T12:00:00Z",
        payload={
            "data": {
                "email_id": "email_1",
                "message_id": "message_1",
                "to": ["lead@example.com"],
                "subject": "Teste",
                "tags": [
                    {"name": "campaign", "value": "4dicasinfalíveis"},
                    {"name": "template", "value": "4dicasinfalíveis"},
                    {"name": "lote", "value": "lote10"},
                ],
            }
        },
    )

    inserted = ResendWebhookRepository(
        Settings(supabase_database_url="postgres://example")
    ).save_event(event)

    assert inserted is True
    assert fake_cursor.params[7:10] == (
        "4dicasinfalíveis",
        "4dicasinfalíveis",
        "lote10",
    )
    assert fake_conn.committed is True


def _headers(*, secret: str, payload: bytes, timestamp: str) -> dict:
    svix_id = "msg_test"
    secret_bytes = base64.b64decode(secret.split("_", 1)[1])
    signed_payload = b".".join([svix_id.encode(), timestamp.encode(), payload])
    signature = base64.b64encode(
        hmac.new(secret_bytes, signed_payload, hashlib.sha256).digest()
    ).decode("ascii")
    return {
        "svix-id": svix_id,
        "svix-timestamp": timestamp,
        "svix-signature": f"v1,{signature}",
    }


class FakeConnection:
    def __init__(self, cursor: "FakeCursor") -> None:
        self.cursor_instance = cursor
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        return None

    def cursor(self) -> "FakeCursor":
        return self.cursor_instance

    def commit(self) -> None:
        self.committed = True


class FakeCursor:
    def __init__(self) -> None:
        self.params = None
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        return None

    def execute(self, query, params) -> None:
        self.params = params
