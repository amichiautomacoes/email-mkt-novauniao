import json
from datetime import date

import pytest
from typer.testing import CliRunner

from email_mkt.cli import app
from email_mkt.config import Settings
from email_mkt.metrics.click_report import (
    build_click_report,
    fetch_click_report,
    load_cta_urls,
    normalized_url,
)

CTA = "https://wa.me/123?text=hello%20world"
CTAS = {"campaign": {normalized_url(CTA)}}
SENDS = [{"resend_email_id": "email-1", "template_key": "campaign"}]


def event(index, link, timestamp="2026-11-03T12:00:00Z"):
    return {
        "id": str(index),
        "resend_email_id": "email-1",
        "event_type": "email.clicked",
        "event_created_at": timestamp,
        "data": {
            "click": {
                "link": link,
                "timestamp": timestamp,
                "ipAddress": "192.0.2.1",
                "userAgent": "Mozilla/5.0",
            }
        },
    }


def test_report_separates_cta_events_and_never_calls_unknown_click_human():
    events = [
        event(1, CTA),
        event(2, "https://instagram.com/a"),
        event(3, "https://maps.google.com/a"),
        event(4, CTA, "2026-11-03T12:05:00Z"),
    ]
    report = build_click_report(SENDS, events + [events[0]], CTAS)
    total = report["total"]
    assert total["cta_click_events"] == 2  # duplicate webhook excluded
    assert total["cta_messages"] == 1
    assert total["suspected_automated_cta_events"] == 1
    assert total["indeterminate_cta_events"] == 1
    assert total["human_confirmed_cta_events"] is None
    assert report["human_confirmation_available"] is False
    assert "192.0.2.1" not in json.dumps(report)
    assert "Mozilla/5.0" not in json.dumps(report)


def test_other_campaigns_do_not_leak_into_report():
    outside = event(1, CTA)
    outside["resend_email_id"] = "outside-cohort"
    assert build_click_report(SENDS, [outside], CTAS)["total"]["cta_click_events"] == 0


def test_missing_payload_is_reported_as_unresolved_not_as_zero_human():
    broken = event(1, CTA)
    broken["data"] = None
    report = build_click_report(SENDS, [broken], CTAS)
    assert report["click_events_without_usable_url"] == 1
    assert report["total"]["human_confirmed_cta_events"] is None


def test_empty_cohort_has_zero_events_but_human_measurement_still_unavailable():
    report = build_click_report([], [], {})
    assert report["total"]["cta_click_events"] == 0
    assert report["total"]["human_confirmed_cta_events"] is None


def test_missing_or_duplicate_resend_ids_are_rejected():
    for sends in [SENDS * 2, [{"resend_email_id": None, "template_key": "campaign"}]]:
        with pytest.raises(ValueError, match="IDs Resend"):
            build_click_report(sends, [], CTAS)


def test_missing_cta_mapping_is_rejected():
    with pytest.raises(ValueError, match="CTA nao resolvido"):
        build_click_report(SENDS, [], {})


def test_url_equivalence_handles_query_order_and_encoded_spaces():
    assert normalized_url(CTA + "&x=1") == normalized_url(
        "https://wa.me/123?x=1&text=hello+world"
    )


def test_load_cta_uses_main_button_not_footer(tmp_path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"campaign": {"html": "campaign.html"}}))
    (tmp_path / "campaign.html").write_text(
        f'<a class="main-cta" href="{CTA}">WhatsApp</a>'
        '<a href="https://instagram.com/a">Instagram</a>',
        encoding="utf-8",
    )
    settings = Settings(templates_catalog_path=catalog, templates_clean_dir=tmp_path)
    assert load_cta_urls(settings, {"campaign"}) == CTAS
    with pytest.raises(ValueError, match="ausente"):
        load_cta_urls(settings, {"unknown"})


def test_invalid_dates_rejected_without_connecting():
    with pytest.raises(ValueError, match="inicial"):
        fetch_click_report(Settings(), date(2026, 11, 6), date(2026, 11, 3))


@pytest.mark.parametrize(
    "arguments",
    [
        ["--start-date", "invalid", "--end-date", "2026-11-06"],
        ["--start-date", "2026-11-06", "--end-date", "2026-11-03"],
    ],
)
def test_cli_rejects_invalid_dates(arguments):
    assert CliRunner().invoke(app, ["clicks", *arguments]).exit_code == 2
