import base64
import hashlib
import hmac
import json

import pytest

from email_mkt.webhooks.resend import (
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
