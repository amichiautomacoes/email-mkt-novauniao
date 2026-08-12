import os
from dataclasses import dataclass

import psycopg
from dotenv import load_dotenv
from psycopg import sql

TABLE_NAME = "email_mkt_leads"


@dataclass(frozen=True)
class Column:
    name: str
    data_type: str


def main() -> None:
    load_dotenv()
    database_url = os.environ["SUPABASE_DATABASE_URL"]
    schema = os.getenv("SUPABASE_SCHEMA", "mkt_novauniao")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            columns = get_columns(cur, schema)
            if not columns:
                raise RuntimeError(f"Tabela {schema}.{TABLE_NAME} nao encontrada.")

            total = get_total(cur, schema)
            lote_column = next(
                (column for column in columns if column.name == "lote"), None
            )
            if lote_column is None:
                cur.execute(
                    sql.SQL("alter table {}.{} add column lote text").format(
                        sql.Identifier(schema),
                        sql.Identifier(TABLE_NAME),
                    )
                )
                columns = [*columns, Column("lote", "text")]
                lote_column = columns[-1]

            order_columns = choose_order_columns(columns)
            assign_lotes(cur, schema, lote_column, order_columns)
            summary = get_summary(cur, schema)

        conn.commit()

    print(f"total_leads={total}")
    for lote, count in summary:
        print(f"{lote}={count}")


def get_columns(cur: psycopg.Cursor, schema: str) -> list[Column]:
    cur.execute(
        """
        select column_name, data_type
        from information_schema.columns
        where table_schema = %s
          and table_name = %s
        order by ordinal_position
        """,
        (schema, TABLE_NAME),
    )
    return [Column(name=row[0], data_type=row[1]) for row in cur.fetchall()]


def get_total(cur: psycopg.Cursor, schema: str) -> int:
    cur.execute(
        sql.SQL("select count(*) from {}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(TABLE_NAME),
        )
    )
    return cur.fetchone()[0]


def choose_order_columns(columns: list[Column]) -> list[str]:
    names = {column.name for column in columns}
    preferred = ["created_at", "id", "email", "telefone", "nome"]
    selected = [name for name in preferred if name in names]
    return selected or [columns[0].name]


def assign_lotes(
    cur: psycopg.Cursor,
    schema: str,
    lote_column: Column,
    order_columns: list[str],
) -> None:
    order_by = sql.SQL(", ").join(
        sql.SQL("{} nulls last").format(sql.Identifier(column_name))
        for column_name in order_columns
    )
    table = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(TABLE_NAME))

    if lote_column.data_type in {"integer", "bigint", "smallint", "numeric"}:
        lote_value = sql.SQL("ranked.lote_num")
    else:
        lote_value = sql.SQL("'lote ' || ranked.lote_num::text")

    cur.execute(sql.SQL("""
            with ranked as (
              select
                ctid,
                ntile(5) over (order by {order_by}) as lote_num
              from {table}
            )
            update {table} as target
            set lote = {lote_value}
            from ranked
            where target.ctid = ranked.ctid
            """).format(order_by=order_by, table=table, lote_value=lote_value))


def get_summary(cur: psycopg.Cursor, schema: str) -> list[tuple[str, int]]:
    cur.execute(sql.SQL("""
            select lote::text, count(*)
            from {}.{}
            group by lote
            order by lote::text
            """).format(sql.Identifier(schema), sql.Identifier(TABLE_NAME)))
    return cur.fetchall()


if __name__ == "__main__":
    main()
