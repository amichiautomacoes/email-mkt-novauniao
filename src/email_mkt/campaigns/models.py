from dataclasses import dataclass, field


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    reply_to: str | None = None
    attachments: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CampaignRunResult:
    attempted: int
    sent: int
    failed: int
    dry_run: bool
    errors: list[str] = field(default_factory=list)
