import io
import json
from urllib.parse import parse_qs, urlsplit

import pytest
from bs4 import BeautifulSoup

from email_mkt.config import Settings
from email_mkt.metrics.click_report import build_click_report, normalized_url
from email_mkt.metrics.whatsapp_attribution import (
    REFERENCE_PATTERN,
    WhatsAppReceiptRepository,
    add_reference_to_html,
    new_reference,
    parse_receipt,
)
from email_mkt.templates.renderer import TemplateRenderer
from scripts import run_resend_webhook_server as server

REF = "NU-" + "A" * 24
CTA = "https://wa.me/553141049383?text=Olá%21%20Quero%20etiquetas."


def receipt_payload(**overrides):
    return {
        "message_id": "wamid.test-1",
        "received_at": "2026-11-09T16:00:00-03:00",
        "text": "Olá! Quero etiquetas.\n\nReferência: " + REF,
        "provider": "test",
        **overrides,
    }


def test_reference_preserves_direct_link_and_both_outlook_and_html_targets():
    html = f'<!--[if mso]><v:roundrect href="{CTA}"/><![endif]--><a href="{CTA}">WhatsApp</a>'
    html += '<a href="https://instagram.com/test">Instagram</a>'
    result, changed = add_reference_to_html(html, REF)
    assert changed
    assert "v:roundrect" in result and "<!--[if mso]>" in result
    assert result.count(REF) == 2
    anchor = BeautifulSoup(result, "html.parser").find("a")
    url = urlsplit(anchor["href"])
    assert url.hostname == "wa.me"
    assert parse_qs(url.query)["text"] == [
        "Olá! Quero etiquetas.\n\nReferência: " + REF
    ]
    assert '<a href="https://instagram.com/test">Instagram</a>' in result
    assert normalized_url(anchor["href"]) == normalized_url(CTA)


def test_reference_replacement_is_idempotent_and_only_uses_valid_whatsapp_host():
    html = f'<a href="{CTA}">WhatsApp</a><a href="https://wa.me.attacker.test/?text=x">X</a>'
    first, _ = add_reference_to_html(html, REF)
    second, _ = add_reference_to_html(first, REF)
    assert first == second
    assert "https://wa.me.attacker.test/?text=x" in second


def test_renderer_generates_unique_reference_per_send_without_leaking_email():
    renderer = TemplateRenderer(Settings(_env_file=None))
    messages = [
        renderer.render_message(
            "preparacao_black_friday", {"email": "lead@example.invalid"}
        )
        for _ in range(2)
    ]
    refs = [m.metadata["whatsapp_reference"] for m in messages]
    assert refs[0] != refs[1]
    for message, reference in zip(messages, refs):
        assert REFERENCE_PATTERN.fullmatch(reference)
        assert message.html.count(reference) == 4  # two buttons, HTML + VML
        assert "lead@example.invalid" not in reference


@pytest.mark.parametrize(
    "overrides",
    [
        {"text": "no reference"},
        {"text": REF + " NU-" + "B" * 24},
        {"received_at": "2026-11-09T16:00:00"},
        {"message_id": ""},
        {"provider": "invalid:provider"},
        {"text": None},
    ],
)
def test_invalid_or_ambiguous_receipts_are_rejected(overrides):
    with pytest.raises(ValueError):
        parse_receipt(receipt_payload(**overrides))


def test_receipt_accepts_one_reference_repeated_and_normalizes_case():
    receipt = parse_receipt(receipt_payload(text=REF.lower() + " " + REF))
    assert receipt.reference == REF
    assert receipt.received_at.utcoffset().total_seconds() == -10800


def test_new_reference_is_opaque():
    assert REFERENCE_PATTERN.fullmatch(new_reference())


def test_report_correlates_received_messages_once_and_separates_them_from_clicks():
    sends = [
        {"resend_email_id": "e1", "template_key": "campaign", "whatsapp_reference": REF}
    ]
    receipt = {"id": "r1", "data": {"reference": REF}}
    report = build_click_report(
        sends,
        [],
        {"campaign": {normalized_url(CTA)}},
        [receipt, receipt, {"id": "r2", "data": {"reference": "unknown"}}],
    )
    assert report["whatsapp_attribution_available"]
    assert report["total"]["sends_with_whatsapp_reference"] == 1
    assert report["total"]["sends_with_whatsapp_reply"] == 1
    assert report["total"]["whatsapp_reply_events"] == 1
    assert report["total"]["cta_click_events"] == 0
    assert report["total"]["human_confirmed_cta_events"] is None


def test_duplicate_history_reference_is_rejected():
    sends = [
        {"resend_email_id": key, "template_key": "campaign", "whatsapp_reference": REF}
        for key in ["e1", "e2"]
    ]
    with pytest.raises(ValueError, match="Referencia WhatsApp duplicada"):
        build_click_report(sends, [], {"campaign": {normalized_url(CTA)}})


def test_receipt_storage_uses_existing_dedup_key_and_does_not_store_message_text(
    monkeypatch,
):
    recorded = []

    class Cursor:
        rowcount = 1

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, query, params):
            recorded.append(params)

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def cursor(self):
            return Cursor()

    monkeypatch.setattr(
        "email_mkt.metrics.whatsapp_attribution.psycopg.connect", lambda _: Connection()
    )
    repository = WhatsAppReceiptRepository(
        Settings(_env_file=None, supabase_database_url="fake")
    )
    assert repository.save(parse_receipt(receipt_payload()))
    params = recorded[0]
    assert params[0] == "whatsapp:test:wamid.test-1"
    assert params[3].obj == {"reference": REF, "provider": "test"}
    assert "Olá" not in str(params)


@pytest.mark.parametrize(
    "token,authorization,status",
    [
        ("", "Bearer token", 503),
        ("token", "", 401),
        ("token", "Bearer wrong", 401),
        ("token", "Bearer token", 200),
    ],
)
def test_whatsapp_endpoint_authenticates_before_storage(
    monkeypatch, token, authorization, status
):
    body = json.dumps(receipt_payload()).encode()
    handler = object.__new__(server.ResendWebhookHandler)
    handler.path = "/webhooks/whatsapp"
    handler.headers = {"authorization": authorization, "content-length": str(len(body))}
    handler.rfile = io.BytesIO(body)
    responses = []
    stored = []
    handler._json_response = lambda code, data: responses.append((code, data))
    monkeypatch.setattr(
        server,
        "get_settings",
        lambda: Settings(_env_file=None, whatsapp_inbound_token=token),
    )
    monkeypatch.setattr(
        server.WhatsAppReceiptRepository,
        "save",
        lambda self, receipt: stored.append(receipt) or True,
    )
    handler.do_POST()
    assert responses[0][0] == status
    assert bool(stored) == (status == 200)
