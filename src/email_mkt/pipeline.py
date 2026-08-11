from dataclasses import dataclass

from email_mkt.campaigns.models import CampaignRunResult
from email_mkt.campaigns.plans import resolve_campaign_plan
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
    dry_run: bool = True


def run_campaign_pipeline(
    request: PipelineRequest, settings: Settings
) -> CampaignRunResult:
    template_key = _resolve_template_key(request)
    contacts = ContactRepository(settings).fetch_recipients(
        campaign_key=request.lote_key or request.campaign_key,
        limit=request.limit,
        sent_campaign_key=request.campaign_key,
    )
    renderer = TemplateRenderer(settings)
    sender = EmailSender(settings)

    messages = [
        renderer.render_message(template_key=template_key, contact=contact)
        for contact in contacts
    ]
    return sender.send_batch(
        messages, dry_run=request.dry_run, campaign_key=request.campaign_key
    )


def _resolve_template_key(request: PipelineRequest) -> str:
    if request.template_key:
        return request.template_key
    plan = resolve_campaign_plan(request.lote_key or request.campaign_key)
    if plan is not None:
        return plan.template_key
    raise ValueError("Informe --template para campanhas sem lote mapeado.")
