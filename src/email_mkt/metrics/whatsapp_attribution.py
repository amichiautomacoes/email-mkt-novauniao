"""References carried by direct WhatsApp links and actually received messages."""

import re
import secrets
from dataclasses import dataclass
from datetime import datetime
from html import escape, unescape
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from email_mkt.config import Settings
from email_mkt.metrics.click_classification import parse_timestamp

REFERENCE_PATTERN = re.compile(r"\bNU-[A-F0-9]{24}\b", re.IGNORECASE)
REFERENCE_SUFFIX = re.compile(r"\n\nReferência: NU-[A-F0-9]{24}$", re.IGNORECASE)
HREF = re.compile(r"(\bhref\s*=\s*)([\"'])(.*?)\2", re.IGNORECASE | re.DOTALL)


def new_reference() -> str:
    return "NU-" + secrets.token_hex(12).upper()


def strip_reference(text: str) -> str:
    return REFERENCE_SUFFIX.sub("", text)


def is_whatsapp_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return parsed.scheme == "https" and parsed.hostname in {
            "wa.me",
            "api.whatsapp.com",
            "web.whatsapp.com",
        }
    except ValueError:
        return False


def add_reference_to_html(html: str, reference: str) -> tuple[str, bool]:
    """Replace only href values, preserving email markup and Outlook VML."""
    if not REFERENCE_PATTERN.fullmatch(reference):
        raise ValueError("Referencia WhatsApp invalida.")
    changed = False

    def replace(match: re.Match) -> str:
        nonlocal changed
        url = unescape(match[3])
        if not is_whatsapp_url(url):
            return match[0]
        parsed = urlsplit(url)
        params = parse_qsl(parsed.query, keep_blank_values=True)
        texts = [value for key, value in params if key == "text"]
        if len(texts) != 1 or not texts[0].strip():
            return match[0]
        text = strip_reference(texts[0]) + "\n\nReferência: " + reference
        params = [(key, text if key == "text" else value) for key, value in params]
        updated = urlunsplit(parsed._replace(query=urlencode(params)))
        changed = True
        return match[1] + match[2] + escape(updated, quote=True) + match[2]

    return HREF.sub(replace, html), changed


@dataclass(frozen=True)
class WhatsAppReceipt:
    message_id: str
    received_at: datetime
    reference: str
    provider: str


def parse_receipt(payload: dict) -> WhatsAppReceipt:
    if not isinstance(payload, dict):
        raise TypeError("O corpo deve ser um objeto JSON.")
    message_id = payload.get("message_id")
    provider = payload.get("provider", "integration")
    timestamp = parse_timestamp(payload.get("received_at"))
    text = payload.get("text")
    if not isinstance(message_id, str) or not re.fullmatch(
        r"[\w.:-]{1,256}", message_id
    ):
        raise ValueError("Informe message_id estavel, de ate 256 caracteres.")
    if not isinstance(provider, str) or not re.fullmatch(
        r"[a-zA-Z0-9_-]{1,64}", provider
    ):
        raise ValueError("provider invalido.")
    if timestamp is None:
        raise ValueError("received_at deve ser ISO 8601 com fuso horario.")
    if not isinstance(text, str) or len(text) > 16000:
        raise ValueError("text deve conter a mensagem recebida, ate 16000 caracteres.")
    references = {value.upper() for value in REFERENCE_PATTERN.findall(text)}
    if len(references) != 1:
        raise ValueError("A mensagem deve conter exatamente uma referencia NU valida.")
    return WhatsAppReceipt(message_id, timestamp, references.pop(), provider)


class WhatsAppReceiptRepository:
    def __init__(self, settings: Settings):
        self.settings = settings

    def save(self, receipt: WhatsAppReceipt) -> bool:
        if not self.settings.supabase_database_url:
            raise ValueError("SUPABASE_DATABASE_URL nao configurada.")
        # Use the existing event table; no complete message text or phone is stored.
        query = sql.SQL("""
            insert into {}.email_mkt_metricas (
                source, svix_id, event_type, event_created_at, webhook_received_at,
                message_id, data
            ) values ('whatsapp_inbound', %s, 'whatsapp.message_received', %s, now(), %s, %s)
            on conflict (svix_id) where svix_id is not null do nothing
        """).format(sql.Identifier(self.settings.supabase_schema))
        with (
            psycopg.connect(self.settings.supabase_database_url) as conn,
            conn.cursor() as cur,
        ):
            cur.execute(
                query,
                (
                    f"whatsapp:{receipt.provider}:{receipt.message_id}",
                    receipt.received_at,
                    receipt.message_id,
                    Jsonb(
                        {"reference": receipt.reference, "provider": receipt.provider}
                    ),
                ),
            )
            return cur.rowcount > 0
