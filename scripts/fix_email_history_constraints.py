import argparse
from datetime import date

import psycopg
from psycopg import sql

from email_mkt.config import get_settings

HISTORY_TABLE = "email_mkt_envio_historico"
CONTROL_TABLE = "email_mkt_envio"
OLD_LOTE_INDEX = "email_mkt_envio_hist_lote_uidx"
NEW_LOTE_TEMPLATE_INDEX = "email_mkt_envio_hist_lote_etapa_template_uidx"


def fix_history_constraints(schema: str, conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("drop index if exists {}").format(
                sql.Identifier(schema, OLD_LOTE_INDEX)
            )
        )
        cur.execute(
            sql.SQL("""
                create unique index if not exists {}
                on {}.{} (email_norm, lote_key, etapa, template_key)
                where status = 'accepted'
                  and lote_key is not null
                  and template_key is not null
                """).format(
                sql.Identifier(NEW_LOTE_TEMPLATE_INDEX),
                sql.Identifier(schema),
                sql.Identifier(HISTORY_TABLE),
            )
        )


def backfill_history(
    schema: str,
    conn: psycopg.Connection,
    *,
    start_date: date,
    end_date: date,
    timezone: str,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("""
                insert into {}.{} (
                  email,
                  lote_key,
                  etapa,
                  campanha,
                  template_key,
                  status,
                  resend_response,
                  data_envio,
                  created_at
                )
                select
                  control.email,
                  control.lote_key,
                  coalesce(control.etapa, 1),
                  control.campanha,
                  control.template_key,
                  'accepted',
                  jsonb_build_object(
                    'source', 'backfill_from_email_mkt_envio',
                    'reason', 'history insert previously conflicted on email_norm+lote_key',
                    'resend_email_id_missing', true
                  ),
                  control.data_envio,
                  now()
                from {}.{} as control
                where control.data_envio >= (%s::date at time zone %s)
                  and control.data_envio < (%s::date at time zone %s)
                  and control.email is not null
                  and btrim(control.email) <> ''
                  and control.lote_key is not null
                  and control.template_key is not null
                  and not exists (
                    select 1
                    from {}.{} as history
                    where history.email_norm = lower(btrim(control.email))
                      and history.lote_key = control.lote_key
                      and history.etapa = coalesce(control.etapa, 1)
                      and history.template_key = control.template_key
                      and history.status = 'accepted'
                  )
                on conflict do nothing
                """).format(
                sql.Identifier(schema),
                sql.Identifier(HISTORY_TABLE),
                sql.Identifier(schema),
                sql.Identifier(CONTROL_TABLE),
                sql.Identifier(schema),
                sql.Identifier(HISTORY_TABLE),
            ),
            (
                start_date.isoformat(),
                timezone,
                end_date.isoformat(),
                timezone,
            ),
        )
        return cur.rowcount


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Corrige a unicidade do historico de email marketing."
    )
    parser.add_argument("--start-date", default="2026-08-25")
    parser.add_argument("--end-date", default="2026-08-29")
    parser.add_argument("--timezone", default="America/Sao_Paulo")
    parser.add_argument(
        "--no-backfill",
        action="store_true",
        help="Apenas ajusta os indices, sem recuperar historico do periodo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    if not settings.supabase_database_url:
        raise RuntimeError("SUPABASE_DATABASE_URL nao configurado.")

    with psycopg.connect(settings.supabase_database_url) as conn:
        fix_history_constraints(settings.supabase_schema, conn)
        backfilled = 0
        if not args.no_backfill:
            backfilled = backfill_history(
                settings.supabase_schema,
                conn,
                start_date=date.fromisoformat(args.start_date),
                end_date=date.fromisoformat(args.end_date),
                timezone=args.timezone,
            )
        conn.commit()

    print("Restricao do historico corrigida.")
    if not args.no_backfill:
        print(f"Linhas de historico recuperadas: {backfilled}")


if __name__ == "__main__":
    main()
