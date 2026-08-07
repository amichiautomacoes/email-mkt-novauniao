import argparse
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

from email_mkt.config import get_settings
from email_mkt.logging_config import configure_logging
from email_mkt.pipeline import PipelineRequest, run_campaign_pipeline


SAO_PAULO = ZoneInfo("America/Sao_Paulo")
SCHEDULED_CAMPAIGNS = {
    date(2026, 8, 10): "lote1",
    date(2026, 8, 11): "lote2",
    date(2026, 8, 12): "lote3",
    date(2026, 8, 13): "lote4",
    date(2026, 8, 14): "lote5",
}


def get_scheduled_campaign(run_date: date) -> str | None:
    return SCHEDULED_CAMPAIGNS.get(run_date)


def parse_run_date(value: str | None) -> date:
    if value:
        return date.fromisoformat(value)
    return datetime.now(SAO_PAULO).date()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-date", help="Data em formato YYYY-MM-DD. Padrao: hoje em Sao Paulo.")
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.getenv("EMAIL_SCHEDULE_LIMIT", "80")),
        help="Quantidade maxima de contatos para esta execucao.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simula sem enviar pela Resend.")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Envia pela Resend.")
    parser.set_defaults(dry_run=True)
    args = parser.parse_args()

    run_date = parse_run_date(args.run_date)
    campaign_key = get_scheduled_campaign(run_date)
    if campaign_key is None:
        print(f"Nenhuma campanha programada para {run_date.isoformat()}.")
        return

    configure_logging()
    result = run_campaign_pipeline(
        PipelineRequest(campaign_key=campaign_key, limit=args.limit, dry_run=args.dry_run),
        get_settings(),
    )
    print(result)
    if result.errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
