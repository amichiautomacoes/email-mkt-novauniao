from dataclasses import dataclass
import psycopg

from email_mkt.campaigns.models import CampaignRunResult
from email_mkt.campaigns.plans import (
    is_lote_key,
    is_manual_campaign,
    normalize_lote_key,
)
from email_mkt.config import Settings
from email_mkt.contacts.repository import ContactRepository
from email_mkt.sending.sender import EmailSender
from email_mkt.templates.renderer import TemplateRenderer


@dataclass(frozen=True)
class PipelineRequest:
    campaign_key: str
    lote_key: str | None = None
    template_key: str | None = None
    limit: int | None = None
    etapa: int = 1
    dry_run: bool = True


def run_campaign_pipeline(
    request: PipelineRequest, settings: Settings
) -> CampaignRunResult:
    template_key = _resolve_template_key(request)
    control_campaign_key = template_key
    lote_key = _resolve_lote_key(request)

    with _CampaignLock(settings, control_campaign_key, request.dry_run) as locked:
        if not locked:
            return CampaignRunResult(
                attempted=0,
                sent=0,
                failed=0,
                dry_run=request.dry_run,
                errors=[f"Campanha {control_campaign_key!r} ja esta em execucao."],
            )

        contact_repository = ContactRepository(settings)
        if request.etapa > 1 and lote_key:
            status = contact_repository.get_lote_etapa_status(lote_key, request.etapa)
            if status["total"] == 0 or status["previous"] < status["total"]:
                return CampaignRunResult(
                    attempted=0,
                    sent=0,
                    failed=0,
                    dry_run=request.dry_run,
                    errors=[
                        (
                            f"Etapa {request.etapa} bloqueada para {lote_key}: "
                            f"{status['previous']}/{status['total']} leads ativos "
                            f"receberam a etapa {request.etapa - 1}."
                        )
                    ],
                )

        contacts = contact_repository.fetch_recipients(
            campaign_key=lote_key or request.campaign_key,
            limit=request.limit,
            sent_campaign_key=control_campaign_key,
            etapa=request.etapa,
        )
        renderer = TemplateRenderer(settings)
        sender = EmailSender(settings)

        messages = [
            renderer.render_message(template_key=template_key, contact=contact)
            for contact in contacts
        ]
        return sender.send_batch(
            messages,
            dry_run=request.dry_run,
            campaign_key=control_campaign_key,
            lote_key=lote_key,
            etapa=request.etapa,
        )


def _resolve_template_key(request: PipelineRequest) -> str:
    if request.template_key:
        return request.template_key
    if not is_manual_campaign(request.campaign_key) and not is_lote_key(
        request.campaign_key
    ):
        return request.campaign_key
    raise ValueError(
        "Informe --template ou use --campaign com a chave da campanha e --lote com o lote."
    )


def _resolve_lote_key(request: PipelineRequest) -> str | None:
    if request.lote_key:
        return normalize_lote_key(request.lote_key)
    if is_lote_key(request.campaign_key):
        return normalize_lote_key(request.campaign_key)
    return None


class _CampaignLock:
    def __init__(self, settings: Settings, lock_key: str, dry_run: bool) -> None:
        self.settings = settings
        self.lock_key = lock_key
        self.dry_run = dry_run
        self.conn: psycopg.Connection | None = None
        self.locked = True

    def __enter__(self) -> bool:
        if self.dry_run or not self.settings.supabase_database_url:
            return True

        self.conn = psycopg.connect(self.settings.supabase_database_url)
        with self.conn.cursor() as cur:
            cur.execute(
                "select pg_try_advisory_lock(hashtextextended(%s, 0))",
                (self.lock_key,),
            )
            self.locked = bool(cur.fetchone()[0])
        return self.locked

    def __exit__(self, *args) -> None:
        if self.conn is None:
            return
        if self.locked:
            with self.conn.cursor() as cur:
                cur.execute(
                    "select pg_advisory_unlock(hashtextextended(%s, 0))",
                    (self.lock_key,),
                )
        self.conn.close()
