from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from email_mkt.metrics.click_classification import (
    AUTOMATED,
    INDETERMINATE,
    ClickSignal,
    classify_clicks,
    parse_timestamp,
)

BASE = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)


def signal(index, host="wa.me", seconds=0, **kwargs):
    return ClickSignal(
        event_id=str(index),
        message_id="email-1",
        link=f"https://{host}/link",
        timestamp=BASE + timedelta(seconds=seconds),
        ip="192.0.2.1",
        user_agent="Mozilla/5.0",
        **kwargs,
    )


def test_scanner_burst_is_detected_regardless_of_arrival_order():
    burst = [signal(1), signal(2, "instagram.com", 1), signal(3, "maps.google.com", 2)]
    result = classify_clicks(list(reversed(burst)))
    assert all(a.classification == AUTOMATED for a in result.values())
    assert result["1"].reasons == ("three_hosts_within_two_seconds",)


def test_later_click_is_not_flagged_because_same_message_had_a_scanner():
    clicks = [signal(1), signal(2, "instagram.com"), signal(3, "maps.google.com")]
    clicks += [signal(4, seconds=60)]
    result = classify_clicks(clicks)
    assert result["1"].classification == AUTOMATED
    assert result["4"].classification == INDETERMINATE


def test_overlapping_burst_windows_include_all_participating_events():
    clicks = [
        signal(1),
        signal(2, "instagram.com", 1),
        signal(3, "maps.google.com", 2),
        signal(4, seconds=3),
    ]
    assert all(a.classification == AUTOMATED for a in classify_clicks(clicks).values())


@pytest.mark.parametrize(
    "field,value",
    [
        ("message_id", "other-message"),
        ("ip", "192.0.2.2"),
        ("user_agent", "another-browser"),
        ("ip", ""),
        ("user_agent", ""),
        ("timestamp", None),
        ("timestamp", BASE.replace(tzinfo=None)),
    ],
)
def test_different_or_missing_identity_does_not_form_a_burst(field, value):
    clicks = [
        signal(1),
        signal(2, "instagram.com"),
        replace(signal(3, "maps.google.com"), **{field: value}),
    ]
    assert all(
        a.classification == INDETERMINATE for a in classify_clicks(clicks).values()
    )


def test_three_paths_on_same_host_are_not_three_hosts():
    clicks = [replace(signal(i), link=f"https://wa.me/{i}") for i in range(3)]
    assert all(
        a.classification == INDETERMINATE for a in classify_clicks(clicks).values()
    )


def test_three_hosts_over_more_than_two_seconds_stay_indeterminate():
    clicks = [
        signal(1),
        signal(2, "instagram.com", 1),
        signal(3, "maps.google.com", 2.001),
    ]
    assert all(
        a.classification == INDETERMINATE for a in classify_clicks(clicks).values()
    )


def test_known_automated_agent_is_suspected_without_a_burst():
    result = classify_clicks([replace(signal(1), user_agent="Proofpoint URL scanner")])
    assert result["1"].classification == AUTOMATED
    assert result["1"].reasons == ("automated_user_agent",)


@pytest.mark.parametrize("value", [None, "bad", "2026-11-03T12:00:00", {}, 42])
def test_unusable_timestamp_is_not_guessed(value):
    assert parse_timestamp(value) is None


def test_timestamp_offsets_compare_the_same_instant():
    assert parse_timestamp("2026-11-03T09:00:00-03:00") == parse_timestamp(
        "2026-11-03T12:00:00Z"
    )
