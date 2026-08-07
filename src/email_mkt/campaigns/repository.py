import psycopg
from psycopg import sql

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings


CONTROL_TABLE = "email_controle_envio"


class CampaignRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def record_sent_recipients(self, campaign_key: str, messages: list[EmailMessage]) -> None:
        if not self.settings.supabase_database_url or not messages:
            return

        query = sql.SQL(
            """
            insert into {}.{} (email, data_envio, campanha, numero_envios)
            values (%s, now(), %s, 1)
            on conflict (email) do update
            set
              data_envio = excluded.data_envio,
              campanha = excluded.campanha,
              numero_envios = {}.numero_envios + 1
            """
        ).format(
            sql.Identifier(self.settings.supabase_schema),
            sql.Identifier(CONTROL_TABLE),
            sql.Identifier(CONTROL_TABLE),
        )
        params = [(message.to, campaign_key) for message in messages]

        with psycopg.connect(self.settings.supabase_database_url) as conn:
            with conn.cursor() as cur:
                cur.executemany(query, params)
            conn.commit()

    def mark_sent(self, campaign_key: str, contact_id: str, resend_email_id: str) -> None:
        _ = (campaign_key, contact_id, resend_email_id)
        # TODO: persistir status de envio no Supabase.

    def mark_failed(self, campaign_key: str, contact_id: str, error: str) -> None:
        _ = (campaign_key, contact_id, error)
        # TODO: persistir erro e contador de tentativas no Supabase.
