from dataclasses import dataclass, field


@dataclass(frozen=True)
class CampaignPlan:
    campaign_key: str
    lote_key: str
    template_key: str


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    reply_to: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CampaignRunResult:
    attempted: int
    sent: int
    failed: int
    dry_run: bool
    errors: list[str] = field(default_factory=list)
