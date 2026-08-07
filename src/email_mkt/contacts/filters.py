from dataclasses import dataclass


@dataclass(frozen=True)
class ContactFilters:
    campaign_key: str
    limit: int | None = None
    only_opted_in: bool = True

