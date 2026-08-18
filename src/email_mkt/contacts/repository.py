import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from email_mkt.campaigns.plans import (
    is_lote_key,
    is_manual_campaign,
    normalize_campaign_key,
    normalize_lote_key,
)
from email_mkt.config import Settings
from email_mkt.contacts.filters import ContactFilters

CONTACTS_TABLE = "email_mkt_leads"
SUPPRESSIONS_TABLE = "email_suppressions"
CONTROL_TABLE = "email_mkt_envio"
HISTORY_TABLE = "email_mkt_envio_historico"


class ContactRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch_recipients(
        self,
        campaign_key: str,
        limit: int | None = None,
        sent_campaign_key: str | None = None,
        etapa: int = 1,
    ) -> list[dict]:
        filters = ContactFilters(
            campaign_key=campaign_key,
            limit=limit,
            sent_campaign_key=sent_campaign_key,
            etapa=etapa,
        )
        if not self.settings.supabase_database_url:
            return []

        with psycopg.connect(self.settings.supabase_database_url) as conn, conn.cursor(
            row_factory=dict_row
        ) as cur:
            columns = _get_columns(cur, self.settings.supabase_schema, CONTACTS_TABLE)
            if "email" not in columns:
                raise RuntimeError(
                    f"Coluna email nao encontrada em {self.settings.supabase_schema}.{CONTACTS_TABLE}."
                )

            suppressions_schema = _find_table_schema(
                cur, self.settings.supabase_schema, SUPPRESSIONS_TABLE
            )
            control_schema = _find_table_schema(
                cur, self.settings.supabase_schema, CONTROL_TABLE
            )
            history_schema = _find_table_schema(
                cur, self.settings.supabase_schema, HISTORY_TABLE
            )
            return _fetch_contacts(
                cur,
                self.settings.supabase_schema,
                columns,
                suppressions_schema,
                control_schema,
                history_schema,
                filters,
            )

    def get_lote_etapa_status(self, lote_key: str, etapa: int) -> dict[str, int]:
        if not self.settings.supabase_database_url:
            return {"total": 0, "previous": 0, "current": 0}

        with psycopg.connect(self.settings.supabase_database_url) as conn, conn.cursor(
            row_factory=dict_row
        ) as cur:
            columns = _get_columns(cur, self.settings.supabase_schema, CONTACTS_TABLE)
            if "email" not in columns or "lote" not in columns:
                raise RuntimeError(
                    f"Colunas email/lote nao encontradas em {self.settings.supabase_schema}.{CONTACTS_TABLE}."
                )
            suppressions_schema = _find_table_schema(
                cur, self.settings.supabase_schema, SUPPRESSIONS_TABLE
            )
            history_schema = _find_table_schema(
                cur, self.settings.supabase_schema, HISTORY_TABLE
            )
            if history_schema is None:
                return {"total": 0, "previous": 0, "current": 0}
            return _get_lote_etapa_status(
                cur,
                self.settings.supabase_schema,
                suppressions_schema,
                history_schema,
                lote_key,
                etapa,
            )


def _get_columns(cur: psycopg.Cursor, schema: str, table: str) -> set[str]:
    cur.execute(
        """
        select column_name
        from information_schema.columns
        where table_schema = %s
          and table_name = %s
        """,
        (schema, table),
    )
    return {row["column_name"] for row in cur.fetchall()}


def _find_table_schema(
    cur: psycopg.Cursor, preferred_schema: str, table: str
) -> str | None:
    for schema in (preferred_schema, "public"):
        if _table_exists(cur, schema, table):
            return schema
    return None


def _table_exists(cur: psycopg.Cursor, schema: str, table: str) -> bool:
    cur.execute(
        """
        select exists (
          select 1
          from information_schema.tables
          where table_schema = %s
            and table_name = %s
        )
        """,
        (schema, table),
    )
    return bool(cur.fetchone()["exists"])


def _fetch_contacts(
    cur: psycopg.Cursor,
    schema: str,
    columns: set[str],
    suppressions_schema: str | None,
    control_schema: str | None,
    history_schema: str | None,
    filters: ContactFilters,
) -> list[dict]:
    select_columns = [
        _select_column(columns, "id", "id"),
        _select_column(
            columns,
            "nome",
            "nome",
            fallback_names=("name", "first_name", "primeiro_nome"),
        ),
        sql.SQL("source.{}::text as email").format(sql.Identifier("email")),
    ]
    where_clauses = [
        sql.SQL("source.{} is not null").format(sql.Identifier("email")),
        sql.SQL("btrim(source.{}::text) <> ''").format(sql.Identifier("email")),
    ]
    params: list[object] = []

    if suppressions_schema is not None:
        where_clauses.append(
            sql.SQL("""
                not exists (
                  select 1
                  from {}.{} as suppression
                  where lower(suppression.email) = lower(source.{}::text)
                )
                """).format(
                sql.Identifier(suppressions_schema),
                sql.Identifier(SUPPRESSIONS_TABLE),
                sql.Identifier("email"),
            )
        )

    lote_key = _resolve_lote_key(filters.campaign_key)
    sent_campaign_key = _resolve_sent_campaign_key(filters)
    if history_schema is not None and sent_campaign_key is not None:
        where_clauses.append(
            sql.SQL("""
                not exists (
                  select 1
                  from {}.{} as history
                  where history.email_norm = lower(btrim(source.{}::text))
                    and history.status = 'accepted'
                    and lower(regexp_replace(history.template_key, '[^a-zA-Z0-9]', '', 'g')) = %s
                )
                """).format(
                sql.Identifier(history_schema),
                sql.Identifier(HISTORY_TABLE),
                sql.Identifier("email"),
            )
        )
        params.append(sent_campaign_key)

    if history_schema is not None and lote_key is not None:
        where_clauses.append(
            sql.SQL("""
                not exists (
                  select 1
                  from {}.{} as history
                  where history.email_norm = lower(btrim(source.{}::text))
                    and history.lote_key = %s
                    and history.etapa = %s
                    and history.status = 'accepted'
                )
                """).format(
                sql.Identifier(history_schema),
                sql.Identifier(HISTORY_TABLE),
                sql.Identifier("email"),
            )
        )
        params.extend([lote_key, filters.etapa])
        if filters.etapa > 1:
            where_clauses.append(
                sql.SQL("""
                    exists (
                      select 1
                      from {}.{} as history
                      where history.email_norm = lower(btrim(source.{}::text))
                        and history.lote_key = %s
                        and history.etapa = %s
                        and history.status = 'accepted'
                    )
                    """).format(
                    sql.Identifier(history_schema),
                    sql.Identifier(HISTORY_TABLE),
                    sql.Identifier("email"),
                )
            )
            params.extend([lote_key, filters.etapa - 1])

    if control_schema is not None and sent_campaign_key is not None:
        where_clauses.append(
            sql.SQL("""
                not exists (
                  select 1
                  from {}.{} as control
                  where lower(btrim(control.email)) = lower(btrim(source.{}::text))
                    and lower(regexp_replace(control.campanha, '[^a-zA-Z0-9]', '', 'g')) = %s
                )
                """).format(
                sql.Identifier(control_schema),
                sql.Identifier(CONTROL_TABLE),
                sql.Identifier("email"),
            )
        )
        params.append(sent_campaign_key)

    if lote_key is not None:
        if "lote" not in columns:
            raise RuntimeError(
                f"Coluna lote nao encontrada em {schema}.{CONTACTS_TABLE}."
            )
        where_clauses.append(
            sql.SQL(
                "lower(regexp_replace(source.{}::text, '[^a-zA-Z0-9]', '', 'g')) = %s"
            ).format(sql.Identifier("lote"))
        )
        params.append(lote_key)

    order_by = _order_by(columns)
    sort_columns = _sort_columns(columns)
    query = sql.SQL("""
        with candidates as (
          select
            {select_columns},
            {sort_columns},
            row_number() over (
              partition by lower(btrim(source.{}::text))
              order by {order_by}
            ) as email_rank
          from {table} as source
          where {where_clauses}
        )
        select id, nome, email
        from candidates
        where email_rank = 1
        order by {final_order_by}
        """).format(
        sql.Identifier("email"),
        select_columns=sql.SQL(", ").join(select_columns),
        sort_columns=sql.SQL(", ").join(sort_columns),
        final_order_by=_final_order_by(columns),
        order_by=order_by,
        table=sql.SQL("{}.{}").format(
            sql.Identifier(schema), sql.Identifier(CONTACTS_TABLE)
        ),
        where_clauses=sql.SQL(" and ").join(where_clauses),
    )

    if filters.limit is not None:
        query += sql.SQL(" limit %s")
        params.append(filters.limit)

    cur.execute(query, params)
    return [dict(row) for row in cur.fetchall()]


def _get_lote_etapa_status(
    cur: psycopg.Cursor,
    schema: str,
    suppressions_schema: str | None,
    history_schema: str,
    lote_key: str,
    etapa: int,
) -> dict[str, int]:
    where_clauses = [
        sql.SQL("source.{} is not null").format(sql.Identifier("email")),
        sql.SQL("btrim(source.{}::text) <> ''").format(sql.Identifier("email")),
        sql.SQL(
            "lower(regexp_replace(source.{}::text, '[^a-zA-Z0-9]', '', 'g')) = %s"
        ).format(sql.Identifier("lote")),
    ]
    params: list[object] = [lote_key]

    if suppressions_schema is not None:
        where_clauses.append(
            sql.SQL("""
                not exists (
                  select 1
                  from {}.{} as suppression
                  where lower(btrim(suppression.email)) = lower(btrim(source.{}::text))
                )
                """).format(
                sql.Identifier(suppressions_schema),
                sql.Identifier(SUPPRESSIONS_TABLE),
                sql.Identifier("email"),
            )
        )

    query = sql.SQL("""
        with leads as (
          select distinct lower(btrim(source.{email_column}::text)) as email_norm
          from {leads_table} as source
          where {where_clauses}
        )
        select
          count(*)::int as total,
          count(*) filter (
            where exists (
              select 1
              from {history_table} as history
              where history.email_norm = leads.email_norm
                and history.lote_key = %s
                and history.etapa = %s
                and history.status = 'accepted'
            )
          )::int as previous,
          count(*) filter (
            where exists (
              select 1
              from {history_table} as history
              where history.email_norm = leads.email_norm
                and history.lote_key = %s
                and history.etapa = %s
                and history.status = 'accepted'
            )
          )::int as current
        from leads
        """).format(
        email_column=sql.Identifier("email"),
        leads_table=sql.SQL("{}.{}").format(
            sql.Identifier(schema), sql.Identifier(CONTACTS_TABLE)
        ),
        history_table=sql.SQL("{}.{}").format(
            sql.Identifier(history_schema), sql.Identifier(HISTORY_TABLE)
        ),
        where_clauses=sql.SQL(" and ").join(where_clauses),
    )
    params.extend([lote_key, etapa - 1, lote_key, etapa])
    cur.execute(query, params)
    return dict(cur.fetchone())


def _resolve_lote_key(campaign_key: str) -> str | None:
    if is_manual_campaign(campaign_key):
        return None
    return normalize_lote_key(campaign_key) if is_lote_key(campaign_key) else None


def _resolve_sent_campaign_key(filters: ContactFilters) -> str | None:
    campaign_key = filters.sent_campaign_key or filters.campaign_key
    if is_manual_campaign(campaign_key):
        return None
    return normalize_campaign_key(campaign_key)


def _select_column(
    columns: set[str],
    alias: str,
    preferred_name: str,
    fallback_names: tuple[str, ...] = (),
) -> sql.Composable:
    for name in (preferred_name, *fallback_names):
        if name in columns:
            return sql.SQL("source.{}::text as {}").format(
                sql.Identifier(name), sql.Identifier(alias)
            )
    return sql.SQL("null::text as {}").format(sql.Identifier(alias))


def _order_by(columns: set[str]) -> sql.Composable:
    preferred = ("created_at", "id", "email", "telefone", "nome")
    selected = [column for column in preferred if column in columns]
    if not selected:
        selected = ["email"]
    return sql.SQL(", ").join(
        sql.SQL("source.{} nulls last").format(sql.Identifier(column_name))
        for column_name in selected
    )


def _sort_columns(columns: set[str]) -> list[sql.Composable]:
    preferred = ("created_at", "id", "email", "telefone", "nome")
    selected = [column for column in preferred if column in columns]
    if "email" not in selected:
        selected.append("email")
    return [
        sql.SQL("source.{} as {}").format(
            sql.Identifier(column_name),
            sql.Identifier(f"_sort_{column_name}"),
        )
        for column_name in selected
    ]


def _final_order_by(columns: set[str]) -> sql.Composable:
    preferred = ("created_at", "id", "email", "telefone", "nome")
    selected = [column for column in preferred if column in columns]
    if "email" not in selected:
        selected.append("email")
    return sql.SQL(", ").join(
        sql.SQL("{} nulls last").format(sql.Identifier(f"_sort_{column_name}"))
        for column_name in selected
    )
