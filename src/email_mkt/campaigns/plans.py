import re

from email_mkt.campaigns.models import CampaignPlan

CAMPAIGN_PLANS = {
    "lote1": CampaignPlan(
        campaign_key="lote1",
        lote_key="lote1",
        template_key="3formas-melhorar-experiencia",
    ),
    "lote2": CampaignPlan(
        campaign_key="lote2",
        lote_key="lote2",
        template_key="etiquetas-ideais",
    ),
    "lote3": CampaignPlan(
        campaign_key="lote3",
        lote_key="lote3",
        template_key="segredo-sistema",
    ),
    "lote4": CampaignPlan(
        campaign_key="lote4",
        lote_key="lote4",
        template_key="detalhe-loja",
    ),
    "lote5": CampaignPlan(
        campaign_key="lote5",
        lote_key="lote5",
        template_key="3formas-melhorar-experiencia",
    ),
}


def normalize_campaign_key(campaign_key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", campaign_key.lower())


def resolve_campaign_plan(campaign_key: str) -> CampaignPlan | None:
    return CAMPAIGN_PLANS.get(normalize_campaign_key(campaign_key))
