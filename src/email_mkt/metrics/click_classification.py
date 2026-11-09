"""Event-level heuristics: unflagged clicks are not proven human clicks."""

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit

CLASSIFIER_VERSION = "click-heuristics-v1"
AUTOMATED = "suspected_automated"
INDETERMINATE = "indeterminate"
BOT_AGENT = re.compile(
    r"\b(bot|crawler|spider|headlesschrome)\b|googlebot|bingbot|"
    r"proofpoint|mimecast|barracuda|python-requests|curl/|wget/",
    re.IGNORECASE,
)


def parse_timestamp(value: object) -> datetime | None:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if not isinstance(value, datetime) or value.utcoffset() is None:
        return None
    return value


@dataclass(frozen=True)
class ClickSignal:
    event_id: str
    message_id: str
    link: str
    timestamp: datetime | None
    ip: str = ""
    user_agent: str = ""


@dataclass(frozen=True)
class ClickAssessment:
    event_id: str
    classification: str
    reasons: tuple[str, ...]


def classify_clicks(clicks: list[ClickSignal]) -> dict[str, ClickAssessment]:
    """Suspect >=3 hosts in <=2s, within the same message/IP/user agent.

    Missing IP, user agent or timezone-aware time cannot prove a burst.
    Flags describe individual events, never an entire recipient's history.
    """
    reasons: dict[str, set[str]] = defaultdict(set)
    streams: dict[tuple[str, str, str], list[ClickSignal]] = defaultdict(list)
    for click in clicks:
        if BOT_AGENT.search(click.user_agent):
            reasons[click.event_id].add("automated_user_agent")
        if click.ip and click.user_agent and parse_timestamp(click.timestamp):
            streams[(click.message_id, click.ip, click.user_agent)].append(click)
    for stream in streams.values():
        ordered = sorted(stream, key=lambda click: click.timestamp)
        right = 0
        hosts: dict[str, int] = defaultdict(int)
        differences = [0] * (len(ordered) + 1)
        domains = [_host(click.link) for click in ordered]
        for left, first in enumerate(ordered):
            while right < len(ordered):
                if (ordered[right].timestamp - first.timestamp).total_seconds() > 2:
                    break
                if domains[right]:
                    hosts[domains[right]] += 1
                right += 1
            if len(hosts) >= 3:
                differences[left] += 1
                differences[right] -= 1
            if domains[left]:
                hosts[domains[left]] -= 1
                if not hosts[domains[left]]:
                    del hosts[domains[left]]
        active = 0
        for index, click in enumerate(ordered):
            active += differences[index]
            if active:
                reasons[click.event_id].add("three_hosts_within_two_seconds")
    return {
        click.event_id: ClickAssessment(
            event_id=click.event_id,
            classification=AUTOMATED if reasons[click.event_id] else INDETERMINATE,
            reasons=tuple(sorted(reasons[click.event_id]))
            or ("insufficient_evidence",),
        )
        for click in clicks
    }


def _host(link: str) -> str:
    try:
        parsed = urlsplit(link)
        if parsed.scheme in {"https", "http"}:
            return (parsed.hostname or "").lower()
    except ValueError:
        pass
    return ""
