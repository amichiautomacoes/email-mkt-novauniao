from typing import Self

from email_mkt.campaigns.models import EmailMessage
from email_mkt.campaigns.repository import CampaignRepository
from email_mkt.config import Settings


def test_record_sent_recipients_skips_without_database_url() -> None:
    repository = CampaignRepository(Settings(supabase_database_url=""))

    repository.record_sent_recipients(
        "lote1",
        [EmailMessage(to="hugo@example.com", subject="Teste", html="<p>Teste</p>")],
    )


def test_record_sent_recipients_upserts_control_table(monkeypatch) -> None:
    fake_cursor = FakeCursor()
    fake_conn = FakeConnection(fake_cursor)
    monkeypatch.setattr(
        "email_mkt.campaigns.repository.psycopg.connect", lambda _: fake_conn
    )

    repository = CampaignRepository(
        Settings(supabase_database_url="postgres://example")
    )
    repository.record_sent_recipients(
        "lote1",
        [
            EmailMessage(to="hugo@example.com", subject="Teste", html="<p>Teste</p>"),
            EmailMessage(to="ana@example.com", subject="Teste", html="<p>Teste</p>"),
        ],
        lote_key="lote1",
        etapa=2,
        resend_email_ids=["resend-1", "resend-2"],
    )

    assert fake_cursor.executemany_params[0] == [
        ("hugo@example.com", "lote1"),
        ("ana@example.com", "lote1"),
    ]
    assert fake_cursor.executemany_params[1][0][:6] == (
        "hugo@example.com",
        "lote1",
        2,
        "lote1",
        "lote1",
        "resend-1",
    )
    assert fake_conn.committed is True


class FakeConnection:
    def __init__(self, cursor: "FakeCursor") -> None:
        self.cursor_instance = cursor
        self.committed = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        return None

    def cursor(self) -> "FakeCursor":
        return self.cursor_instance

    def commit(self) -> None:
        self.committed = True


class FakeCursor:
    def __init__(self) -> None:
        self.executemany_params = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        return None

    def executemany(self, query, params) -> None:
        self.executemany_params.append(list(params))
