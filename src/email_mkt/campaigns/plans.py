import re

MANUAL_CAMPAIGNS = {"manual", "all", "todos", "todas"}


def normalize_campaign_key(campaign_key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", campaign_key.lower())


def normalize_lote_key(lote_key: str) -> str:
    return normalize_campaign_key(lote_key)


def is_lote_key(value: str) -> bool:
    normalized = normalize_lote_key(value)
    return normalized.startswith("lote") and normalized[4:].isdigit()


def is_manual_campaign(value: str) -> bool:
    return value.lower() in MANUAL_CAMPAIGNS
