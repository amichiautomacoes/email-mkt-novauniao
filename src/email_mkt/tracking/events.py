from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmailEvent:
    provider: str
    provider_message_id: str
    event_type: str
    occurred_at: datetime
    payload: dict

