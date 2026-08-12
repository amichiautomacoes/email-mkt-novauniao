import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from email_mkt.config import get_settings
from email_mkt.metrics.resend_client import DEFAULT_METRICS, ResendMetricsClient
from email_mkt.metrics.repository import ResendMetricsRepository

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _today() -> str:
    return datetime.now(SAO_PAULO).date().isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default=_today())
    parser.add_argument("--end-date")
    parser.add_argument("--timezone", default="America/Sao_Paulo")
    parser.add_argument("--granularity", default="daily")
    parser.add_argument("--metrics", default=",".join(DEFAULT_METRICS))
    parser.add_argument("--dimensions", default="period")
    parser.add_argument(
        "--strict-metrics",
        action="store_true",
        help="Falha se o endpoint beta /emails/metrics nao estiver disponivel.",
    )
    args = parser.parse_args()

    settings = get_settings()
    client = ResendMetricsClient(settings)
    repository = ResendMetricsRepository(settings)

    try:
        metrics_payload = client.retrieve_metrics(
            start_date=args.start_date,
            end_date=args.end_date,
            timezone=args.timezone,
            granularity=args.granularity,
            metrics=_csv(args.metrics),
            dimensions=_csv(args.dimensions),
        )
        saved = repository.save_metrics_snapshot(
            metrics_payload,
            timezone=args.timezone,
            granularity=args.granularity,
        )
        print(
            "Snapshot de metricas salvo."
            if saved
            else "Snapshot de metricas lido, mas Supabase nao configurado."
        )
    except httpx.HTTPStatusError as exc:
        if args.strict_metrics:
            raise
        print(
            "Nao foi possivel ler /emails/metrics; "
            f"status={exc.response.status_code}. "
            "Nenhuma tabela auxiliar de emails sera criada."
        )


if __name__ == "__main__":
    main()
