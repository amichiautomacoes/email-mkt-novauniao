import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings

CONTROL_TABLE = "email_mkt_envio"
HISTORY_TABLE = "email_mkt_envio_historico"


class CampaignRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def record_sent_recipients(
        self,
        campaign_key: str,
        messages: list[EmailMessage],
        *,
        lote_key: str | None = None,
        etapa: int = 1,
        resend_email_ids: list[str | None] | None = None,
    ) -> None:
        if not self.settings.supabase_database_url or not messages:
            return

        control_query = sql.SQL("""
            insert into {}.{} (email, data_envio, campanha, numero_envios)
            values (%s, now(), %s, 1)
            on conflict (email) do update
            set
              data_envio = excluded.data_envio,
              campanha = excluded.campanha,
                numero_envios = {}.numero_envios + 1
            """).format(
            sql.Identifier(self.settings.supabase_schema),
            sql.Identifier(CONTROL_TABLE),
            sql.Identifier(CONTROL_TABLE),
        )
        control_params = [(message.to, campaign_key) for message in messages]

        history_query = sql.SQL("""
            insert into {}.{} (
              email,
              lote_key,
              etapa,
              campanha,
              template_key,
              status,
              resend_email_id,
              resend_response
            )
            values (%s, %s, %s, %s, %s, 'accepted', %s, %s)
            on conflict do nothing
            """).format(
            sql.Identifier(self.settings.supabase_schema),
            sql.Identifier(HISTORY_TABLE),
        )
        history_params = [
            (
                message.to,
                lote_key,
                etapa,
                campaign_key,
                str(message.metadata.get("template") or campaign_key),
                _resend_id_at(resend_email_ids, index),
                Jsonb({"resend_email_id": _resend_id_at(resend_email_ids, index)}),
            )
            for index, message in enumerate(messages)
        ]

        with psycopg.connect(
            self.settings.supabase_database_url
        ) as conn, conn.cursor() as cur:
            cur.executemany(control_query, control_params)
            cur.executemany(history_query, history_params)
            conn.commit()


def _resend_id_at(values: list[str | None] | None, index: int) -> str | None:
    if values is None or index >= len(values):
        return None
    return values[index]
