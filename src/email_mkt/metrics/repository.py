import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from email_mkt.config import Settings

METRICS_TABLE = "email_mkt_metricas"


class ResendMetricsRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def save_metrics_snapshot(
        self,
        payload: dict,
        *,
        timezone: str,
        granularity: str,
    ) -> bool:
        if not self.settings.supabase_database_url:
            return False

        query = sql.SQL("""
            insert into {}.{} (
              start_date,
              end_date,
              timezone,
              granularity,
              metrics,
              dimensions,
              totals,
              data,
              raw_payload
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """).format(
            sql.Identifier(self.settings.supabase_schema),
            sql.Identifier(METRICS_TABLE),
        )
        params = (
            payload.get("start_date"),
            payload.get("end_date"),
            timezone,
            granularity,
            payload.get("metrics", []),
            payload.get("dimensions", []),
            Jsonb(payload.get("totals", {})),
            Jsonb(payload.get("data", [])),
            Jsonb(payload),
        )

        with psycopg.connect(
            self.settings.supabase_database_url
        ) as conn, conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
        return True
