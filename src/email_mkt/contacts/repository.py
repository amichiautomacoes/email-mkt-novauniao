import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from email_mkt.campaigns.plans import normalize_campaign_key, resolve_campaign_plan
from email_mkt.config import Settings
from email_mkt.contacts.filters import ContactFilters

CONTACTS_TABLE = "email_mkt_leads"
SUPPRESSIONS_TABLE = "email_suppressions"
CONTROL_TABLE = "email_mkt_envio"
MANUAL_CAMPAIGNS = {"manual", "all", "todos", "todas"}


class ContactRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch_recipients(
        self,
        campaign_key: str,
        limit: int | None = None,
        sent_campaign_key: str | None = None,
    ) -> list[dict]:
        filters = ContactFilters(
            campaign_key=campaign_key,
            limit=limit,
            sent_campaign_key=sent_campaign_key,
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
            return _fetch_contacts(
                cur,
                self.settings.supabase_schema,
                columns,
                suppressions_schema,
                control_schema,
                filters,
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
    if control_schema is not None and sent_campaign_key is not None:
        where_clauses.append(
            sql.SQL("""
                not exists (
                  select 1
                  from {}.{} as control
                  where lower(control.email) = lower(source.{}::text)
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
    query = sql.SQL("""
        select {select_columns}
        from {table} as source
        where {where_clauses}
        order by {order_by}
        """).format(
        select_columns=sql.SQL(", ").join(select_columns),
        table=sql.SQL("{}.{}").format(
            sql.Identifier(schema), sql.Identifier(CONTACTS_TABLE)
        ),
        where_clauses=sql.SQL(" and ").join(where_clauses),
        order_by=order_by,
    )

    if filters.limit is not None:
        query += sql.SQL(" limit %s")
        params.append(filters.limit)

    cur.execute(query, params)
    return [dict(row) for row in cur.fetchall()]


def _resolve_lote_key(campaign_key: str) -> str | None:
    if campaign_key.lower() in MANUAL_CAMPAIGNS:
        return None
    plan = resolve_campaign_plan(campaign_key)
    if plan is not None:
        return plan.lote_key
    normalized = normalize_campaign_key(campaign_key)
    if normalized.startswith("lote"):
        return normalized
    return None


def _resolve_sent_campaign_key(filters: ContactFilters) -> str | None:
    campaign_key = filters.sent_campaign_key or filters.campaign_key
    if campaign_key.lower() in MANUAL_CAMPAIGNS:
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
