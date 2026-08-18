import re

from email_mkt.campaigns.models import CampaignPlan

INITIAL_TEMPLATE_KEY = "3formas-melhorar-experiencia"

CAMPAIGN_PLANS = {
    f"lote{number}": CampaignPlan(
        campaign_key=f"lote{number}",
        lote_key=f"lote{number}",
        template_key=INITIAL_TEMPLATE_KEY,
    )
    for number in range(1, 11)
}


def normalize_campaign_key(campaign_key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", campaign_key.lower())


def resolve_campaign_plan(campaign_key: str) -> CampaignPlan | None:
    return CAMPAIGN_PLANS.get(normalize_campaign_key(campaign_key))
