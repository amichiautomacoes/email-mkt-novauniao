import argparse
import os
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from email_mkt.config import get_settings
from email_mkt.logging_config import configure_logging
from email_mkt.pipeline import PipelineRequest, run_campaign_pipeline
from email_mkt.scheduling.google_drive_csv import (
    ScheduledCampaign,
    load_scheduled_campaigns,
)

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def parse_bool_env(value: str | None, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False

    raise ValueError(f"Valor booleano invalido: {value!r}")


def get_scheduled_campaigns(
    schedule: list[ScheduledCampaign],
    run_date: date,
    run_time: time | None = None,
) -> list[ScheduledCampaign]:
    due_campaigns = [
        scheduled for scheduled in schedule if scheduled.send_date == run_date
    ]
    if run_time is None:
        return due_campaigns
    return [
        scheduled
        for scheduled in due_campaigns
        if scheduled.send_time.hour == run_time.hour
        and scheduled.send_time.minute == run_time.minute
    ]


def parse_run_date(value: str | None) -> date:
    if value:
        return date.fromisoformat(value)
    return datetime.now(SAO_PAULO).date()


def parse_run_time(value: str | None) -> time:
    if value:
        return time.fromisoformat(value)
    now = datetime.now(SAO_PAULO)
    return time(now.hour, now.minute)


def main() -> None:
    dry_run_default = parse_bool_env(os.getenv("EMAIL_SCHEDULE_DRY_RUN"), True)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-date", help="Data em formato YYYY-MM-DD. Padrao: hoje em Sao Paulo."
    )
    parser.add_argument(
        "--run-time",
        help=(
            "Horario em formato HH:MM. Padrao: hora atual em Sao Paulo. "
            "Se usar --run-date sem --run-time, confere apenas a data."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simula sem enviar pela Resend."
    )
    parser.add_argument(
        "--no-dry-run", action="store_false", dest="dry_run", help="Envia pela Resend."
    )
    parser.set_defaults(dry_run=dry_run_default)
    args = parser.parse_args()

    run_date = parse_run_date(args.run_date)
    run_time = parse_run_time(args.run_time)
    match_time = args.run_date is None or args.run_time is not None
    settings = get_settings()
    schedule = load_scheduled_campaigns(settings, reference_date=run_date)
    scheduled_campaigns = get_scheduled_campaigns(
        schedule,
        run_date=run_date,
        run_time=run_time if match_time else None,
    )

    if not scheduled_campaigns:
        suffix = f" as {run_time.strftime('%H:%M')}" if match_time else ""
        print(f"Nenhuma campanha programada para {run_date.isoformat()}{suffix}.")
        return

    configure_logging()
    has_errors = False
    for scheduled_campaign in scheduled_campaigns:
        result = run_campaign_pipeline(
            PipelineRequest(
                campaign_key=scheduled_campaign.campaign_key,
                lote_key=scheduled_campaign.lote_key,
                template_key=scheduled_campaign.template_key,
                limit=None,
                etapa=scheduled_campaign.etapa,
                dry_run=args.dry_run,
            ),
            settings,
        )
        print(
            f"{scheduled_campaign.lote_key} -> {scheduled_campaign.campaign_key} "
            f"etapa {scheduled_campaign.etapa} "
            f"({scheduled_campaign.send_date.isoformat()} "
            f"{scheduled_campaign.send_time.strftime('%H:%M')}): {result}"
        )
        has_errors = has_errors or bool(result.errors)
    if has_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
