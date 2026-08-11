from datetime import date, time

import pytest

from email_mkt.scheduling.google_drive_csv import (
    ScheduledCampaign,
    parse_schedule_csv,
)
from scripts.run_scheduled_campaign import get_scheduled_campaigns, parse_bool_env


def test_parse_schedule_csv_maps_google_sheet_columns() -> None:
    schedule = parse_schedule_csv(
        (
            "Leads segmentados,Data do Envio,Horário,Campanha,Números envios\n"
            "Lote 2,13 ago.,09:30,campanha etiquetas-ideais,80"
        ),
        reference_date=date(2026, 8, 11),
    )

    assert schedule == [
        ScheduledCampaign(
            lote_key="lote2",
            send_date=date(2026, 8, 13),
            send_time=time(9, 30),
            campaign_key="etiquetas-ideais",
            template_key="etiquetas-ideais",
            limit=80,
        )
    ]


def test_get_scheduled_campaigns_filters_by_date_and_time() -> None:
    schedule = [
        ScheduledCampaign(
            lote_key="lote1",
            send_date=date(2026, 8, 12),
            send_time=time(9, 30),
            campaign_key="3formas-melhorar-experiencia",
            template_key="3formas-melhorar-experiencia",
            limit=80,
        )
    ]

    assert get_scheduled_campaigns(schedule, date(2026, 8, 12), time(9, 30)) == schedule
    assert get_scheduled_campaigns(schedule, date(2026, 8, 12), time(9, 35)) == []


def test_get_scheduled_campaign_ignores_other_dates() -> None:
    schedule = [
        ScheduledCampaign(
            lote_key="lote1",
            send_date=date(2026, 8, 12),
            send_time=time(9, 30),
            campaign_key="3formas-melhorar-experiencia",
            template_key="3formas-melhorar-experiencia",
            limit=80,
        )
    ]

    assert get_scheduled_campaigns(schedule, date(2026, 8, 15)) == []
    assert get_scheduled_campaigns(schedule, date(2027, 8, 10)) == []


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
def test_parse_bool_env_true_values(value: str) -> None:
    assert parse_bool_env(value, default=False) is True


@pytest.mark.parametrize("value", ["0", "false", "FALSE", "no", "off"])
def test_parse_bool_env_false_values(value: str) -> None:
    assert parse_bool_env(value, default=True) is False


def test_parse_bool_env_uses_default_for_empty_values() -> None:
    assert parse_bool_env(None, default=True) is True
    assert parse_bool_env("", default=False) is False


def test_parse_bool_env_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        parse_bool_env("maybe", default=True)
