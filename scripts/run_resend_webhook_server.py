import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from email_mkt.config import get_settings
from email_mkt.webhooks.resend import (
    ALLOWED_RESEND_WEBHOOK_EVENTS,
    ResendWebhookRepository,
    WebhookVerificationError,
    verify_resend_webhook,
)

WEBHOOK_PATH = "/webhooks/resend"


class ResendWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json_response(HTTPStatus.OK, {"ok": True})
            return
        self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != WEBHOOK_PATH:
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        content_length = int(self.headers.get("content-length", "0"))
        payload = self.rfile.read(content_length)
        settings = get_settings()

        try:
            event = verify_resend_webhook(
                payload=payload,
                headers={
                    "svix-id": self.headers.get("svix-id"),
                    "svix-timestamp": self.headers.get("svix-timestamp"),
                    "svix-signature": self.headers.get("svix-signature"),
                },
                secret=settings.resend_webhook_secret,
            )
            if event.event_type not in ALLOWED_RESEND_WEBHOOK_EVENTS:
                self._json_response(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "status": "ignored",
                        "event_type": event.event_type,
                    },
                )
                return
            inserted = ResendWebhookRepository(settings).save_event(event)
        except WebhookVerificationError as exc:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"error": "invalid_webhook", "detail": str(exc)},
            )
            return
        except json.JSONDecodeError:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return

        self._json_response(
            HTTPStatus.OK,
            {
                "ok": True,
                "status": "stored" if inserted else "duplicate_or_not_configured",
                "event_type": event.event_type,
            },
        )

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _json_response(self, status: HTTPStatus, body: dict) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status.value)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT") or os.getenv("PORT") or "8000")
    server = ThreadingHTTPServer((host, port), ResendWebhookHandler)
    print(f"Resend webhook server listening on http://{host}:{port}{WEBHOOK_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    main()
