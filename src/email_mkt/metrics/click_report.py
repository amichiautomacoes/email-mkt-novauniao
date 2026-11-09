"""Read-only campaign cohort reporting with conservative click heuristics."""

import json
from collections import Counter
from datetime import date, datetime, time, timedelta
from urllib.parse import parse_qsl, urlsplit
from zoneinfo import ZoneInfo

import psycopg
from bs4 import BeautifulSoup
from psycopg import sql
from psycopg.rows import dict_row

from email_mkt.config import Settings
from email_mkt.metrics.click_classification import (
    AUTOMATED,
    CLASSIFIER_VERSION,
    ClickSignal,
    classify_clicks,
    parse_timestamp,
)
from email_mkt.metrics.whatsapp_attribution import is_whatsapp_url, strip_reference


def normalized_url(value: str) -> tuple:
    parsed = urlsplit(value)
    params = parse_qsl(parsed.query, keep_blank_values=True)
    if is_whatsapp_url(value):
        params = [
            (key, strip_reference(text) if key == "text" else text)
            for key, text in params
        ]
    return (
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        tuple(sorted(params)),
    )


def load_cta_urls(settings: Settings, template_keys: set[str]) -> dict[str, set[tuple]]:
    catalog = json.loads(settings.templates_catalog_path.read_text(encoding="utf-8"))
    result = {}
    for key in sorted(template_keys):
        metadata = catalog.get(key)
        if not metadata:
            raise ValueError(f"Template {key!r} ausente do catalogo selecionado.")
        filename = metadata["html"]
        source = settings.templates_clean_dir / filename
        if not source.is_file():
            source = settings.templates_raw_dir / filename
        soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
        urls = {
            normalized_url(link["href"]) for link in soup.select("a.main-cta[href]")
        }
        if not urls:
            raise ValueError(
                f"Template {key!r} sem CTA identificado por class=main-cta."
            )
        result[key] = urls
    return result


def build_click_report(
    sends: list[dict],
    events: list[dict],
    cta_urls: dict[str, set[tuple]],
    receipts: list[dict] | None = None,
) -> dict:
    by_message = {
        row["resend_email_id"]: row for row in sends if row["resend_email_id"]
    }
    if len(by_message) != len(sends):
        raise ValueError(
            "Historico com IDs Resend ausentes ou duplicados; confira a base."
        )
    references = {
        row["whatsapp_reference"]: row["resend_email_id"]
        for row in sends
        if row.get("whatsapp_reference")
    }
    if len(references) != sum(bool(row.get("whatsapp_reference")) for row in sends):
        raise ValueError("Referencia WhatsApp duplicada no historico.")
    replies = {}
    for receipt in receipts or []:
        data = receipt.get("data")
        reference = data.get("reference") if isinstance(data, dict) else None
        if reference in references:
            replies[str(receipt["id"])] = references[reference]
    groups = {row["template_key"]: [] for row in sends}
    for row in sends:
        if row["template_key"] not in cta_urls:
            raise ValueError(f"CTA nao resolvido: {row['template_key']}")
        groups[row["template_key"]].append(row["resend_email_id"])
    clicks = []
    opens = set()
    seen = set()
    for event in events:
        mid = event["resend_email_id"]
        if mid not in by_message or str(event["id"]) in seen:
            continue
        seen.add(str(event["id"]))
        if event["event_type"] == "email.opened":
            opens.add(mid)
        if event["event_type"] != "email.clicked":
            continue
        data = event.get("data")
        payload = data.get("click") if isinstance(data, dict) else None
        payload = payload if isinstance(payload, dict) else {}
        clicks.append(
            ClickSignal(
                event_id=str(event["id"]),
                message_id=mid,
                link=str(payload.get("link") or ""),
                timestamp=parse_timestamp(payload.get("timestamp"))
                or parse_timestamp(event.get("event_created_at")),
                ip=str(payload.get("ipAddress") or ""),
                user_agent=str(payload.get("userAgent") or ""),
            )
        )
    assessments = classify_clicks(clicks)
    cta_clicks = []
    unresolved = 0
    for click in clicks:
        try:
            url = normalized_url(click.link)
        except ValueError:
            unresolved += 1
            continue
        if url in cta_urls[by_message[click.message_id]["template_key"]]:
            cta_clicks.append(click)
        elif not url[1]:
            unresolved += 1

    def summarize(messages: set[str]) -> dict:
        selected = [click for click in cta_clicks if click.message_id in messages]
        automated = [
            click
            for click in selected
            if assessments[click.event_id].classification == AUTOMATED
        ]
        return {
            "accepted_sends": len(messages),
            "opened_messages": len(messages & opens),
            "cta_messages": len({click.message_id for click in selected}),
            "cta_click_events": len(selected),
            "suspected_automated_cta_events": len(automated),
            "indeterminate_cta_events": len(selected) - len(automated),
            "human_confirmed_cta_events": None,
            "sends_with_whatsapp_reference": sum(
                bool(by_message[mid].get("whatsapp_reference")) for mid in messages
            ),
            "whatsapp_reply_events": sum(mid in messages for mid in replies.values()),
            "sends_with_whatsapp_reply": len(messages & set(replies.values())),
            "automation_reasons": dict(
                Counter(
                    reason
                    for click in automated
                    for reason in assessments[click.event_id].reasons
                )
            ),
        }

    return {
        "classifier_version": CLASSIFIER_VERSION,
        "human_confirmation_available": False,
        "whatsapp_attribution_available": bool(references),
        "cta_definition": "URL exata dos links a.main-cta no catalogo selecionado",
        "limitations": [
            "Indeterminado nao significa humano; suspeita de automacao e uma heuristica.",
            "Classificacao por evento: um email pode ter cliques suspeitos e indeterminados.",
            "IDs deduplicam envios e eventos, nao pessoas nem visitas ao WhatsApp.",
            "HTML local atual define os CTAs; para campanhas antigas use o catalogo correspondente.",
            "Somente webhooks armazenados: ausencia de evento nao prova ausencia de clique.",
            "Mensagem WhatsApp recebida com referencia mede resposta atribuida, nao confirma cada clique humano.",
            "Referencias podem ser encaminhadas ou removidas pelo usuario; nao comprovam identidade do remetente.",
        ],
        "total": summarize(set(by_message)),
        "campaigns": {key: summarize(set(ids)) for key, ids in sorted(groups.items())},
        "click_events_without_usable_url": unresolved,
    }


def fetch_click_report(settings: Settings, start: date, end: date) -> dict:
    if start > end:
        raise ValueError("A data inicial deve ser anterior ou igual a final.")
    if not settings.supabase_database_url:
        raise ValueError("SUPABASE_DATABASE_URL nao configurada.")
    zone = ZoneInfo("America/Sao_Paulo")
    bounds = (
        datetime.combine(start, time.min, tzinfo=zone),
        datetime.combine(end + timedelta(days=1), time.min, tzinfo=zone),
    )
    schema = sql.Identifier(settings.supabase_schema)
    with (
        psycopg.connect(
            settings.supabase_database_url,
            connect_timeout=15,
            options="-c default_transaction_read_only=on -c statement_timeout=45000",
            row_factory=dict_row,
        ) as conn,
        conn.cursor() as cur,
    ):
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        cur.execute("select now() as cutoff")
        cutoff = cur.fetchone()["cutoff"]
        cur.execute(
            sql.SQL("""
            select resend_email_id, template_key,
                   resend_response->>'whatsapp_reference' as whatsapp_reference
            from {}.email_mkt_envio_historico
            where status = 'accepted' and data_envio >= %s and data_envio < %s
        """).format(schema),
            bounds,
        )
        sends = cur.fetchall()
        cur.execute(
            sql.SQL("""
            select m.id, m.resend_email_id, m.event_type, m.event_created_at,
                   jsonb_build_object('click', m.data->'click') as data
            from {}.email_mkt_metricas m
            where m.event_type in ('email.clicked', 'email.opened')
              and m.event_created_at <= %s
              and exists (
                select 1 from {}.email_mkt_envio_historico h
                where h.status = 'accepted' and h.data_envio >= %s and h.data_envio < %s
                  and h.resend_email_id = m.resend_email_id
              )
        """).format(schema, schema),
            (cutoff, *bounds),
        )
        events = cur.fetchall()
        cur.execute(
            sql.SQL("""
            select m.id, m.data from {}.email_mkt_metricas m
            where m.source = 'whatsapp_inbound'
              and m.event_type = 'whatsapp.message_received'
              and m.event_created_at <= %s
              and exists (
                select 1 from {}.email_mkt_envio_historico h
                where h.status = 'accepted' and h.data_envio >= %s and h.data_envio < %s
                  and h.resend_response->>'whatsapp_reference' = m.data->>'reference'
              )
        """).format(schema, schema),
            (cutoff, *bounds),
        )
        receipts = cur.fetchall()
    ctas = (
        load_cta_urls(settings, {row["template_key"] for row in sends}) if sends else {}
    )
    report = build_click_report(sends, events, ctas, receipts)
    report.update(
        {
            "send_start_date_inclusive": start.isoformat(),
            "send_end_date_inclusive": end.isoformat(),
            "events_through": cutoff.astimezone(zone).isoformat(),
            "timezone": "America/Sao_Paulo",
            "source": f"{settings.supabase_schema}.email_mkt_envio_historico + email_mkt_metricas",
        }
    )
    return report
