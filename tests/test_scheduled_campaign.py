import base64
import json
from datetime import date, time

import pytest

from email_mkt.config import Settings
from email_mkt.scheduling.google_drive_csv import (
    ScheduledCampaign,
    _load_service_account_info,
    parse_schedule_csv,
)
from scripts.run_scheduled_campaign import (
    get_scheduled_campaigns,
    parse_bool_env,
    parse_int_env,
)


def test_parse_schedule_csv_maps_google_sheet_columns() -> None:
    schedule = parse_schedule_csv(
        (
            "Leads segmentados,Data do Envio,Horário,Campanha,Números envios\n"
            "Lote 2,13 ago.,09:30,campanha 3formas-melhorar-experiencia,80"
        ),
        reference_date=date(2026, 8, 11),
    )

    assert schedule == [
        ScheduledCampaign(
            lote_key="lote2",
            send_date=date(2026, 8, 13),
            send_time=time(9, 30),
            campaign_key="3formas-melhorar-experiencia",
            template_key="3formas-melhorar-experiencia",
            limit=80,
        )
    ]


def test_parse_schedule_csv_ignores_incomplete_rows() -> None:
    schedule = parse_schedule_csv(
        (
            "Leads segmentados,Data do Envio,HorÃ¡rio,Campanha,NÃºmeros envios\n"
            "Lote 1,12 ago.,09:30,,80\n"
            "Lote 2,13 ago.,09:30,campanha 3formas-melhorar-experiencia,80"
        ),
        reference_date=date(2026, 8, 11),
    )

    assert len(schedule) == 1
    assert schedule[0].lote_key == "lote2"


def test_parse_schedule_csv_accepts_documented_numero_de_envios_header() -> None:
    schedule = parse_schedule_csv(
        (
            "lote,data envio,hora envio,campanha,numero de envios,etapa\n"
            "Lote 10,18 ago.,09:30,campanha 3formas-melhorar-experiencia,590,1"
        ),
        reference_date=date(2026, 8, 18),
    )

    assert schedule == [
        ScheduledCampaign(
            lote_key="lote10",
            send_date=date(2026, 8, 18),
            send_time=time(9, 30),
            campaign_key="3formas-melhorar-experiencia",
            template_key="3formas-melhorar-experiencia",
            limit=590,
        )
    ]


def test_parse_schedule_csv_ignores_lote_inventory_without_schedule() -> None:
    schedule = parse_schedule_csv(
        (
            "Leads segmentados,Data do Envio,Horario,Campanha,Numeros envios,Etapa\n"
            "Lote 1,,,,,\n"
            "Lote 10,,,,,"
        ),
        reference_date=date(2026, 8, 18),
    )

    assert schedule == []


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


def test_parse_int_env_uses_default_for_empty_values() -> None:
    assert parse_int_env(None, default=80) == 80
    assert parse_int_env("", default=80) == 80
    assert parse_int_env("  ", default=80) == 80


def test_parse_int_env_parses_configured_value() -> None:
    assert parse_int_env("50", default=80) == 50


def test_load_service_account_info_accepts_base64_json() -> None:
    payload = {
        "type": "service_account",
        "project_id": "example",
        "client_email": "service@example.iam.gserviceaccount.com",
    }
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")

    assert (
        _load_service_account_info(Settings(google_service_account_json_base64=encoded))
        == payload
    )
