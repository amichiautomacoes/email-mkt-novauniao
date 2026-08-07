from datetime import date

from scripts.run_scheduled_campaign import get_scheduled_campaign


def test_get_scheduled_campaign_for_august_2026_lotes() -> None:
    assert get_scheduled_campaign(date(2026, 8, 10)) == "lote1"
    assert get_scheduled_campaign(date(2026, 8, 11)) == "lote2"
    assert get_scheduled_campaign(date(2026, 8, 12)) == "lote3"
    assert get_scheduled_campaign(date(2026, 8, 13)) == "lote4"
    assert get_scheduled_campaign(date(2026, 8, 14)) == "lote5"


def test_get_scheduled_campaign_ignores_other_dates() -> None:
    assert get_scheduled_campaign(date(2026, 8, 15)) is None
    assert get_scheduled_campaign(date(2027, 8, 10)) is None
