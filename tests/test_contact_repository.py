from typing import Self

from email_mkt.config import Settings
from email_mkt.contacts import repository
from email_mkt.contacts.repository import ContactRepository


def test_contact_repository_returns_empty_without_database_url() -> None:
    contacts = ContactRepository(Settings(supabase_database_url="")).fetch_recipients(
        "manual"
    )

    assert contacts == []


def test_contact_repository_fetches_contacts_from_supabase(monkeypatch) -> None:
    fake_cursor = FakeCursor()
    fake_conn = FakeConnection(fake_cursor)
    monkeypatch.setattr(repository.psycopg, "connect", lambda _: fake_conn)

    contacts = ContactRepository(
        Settings(supabase_database_url="postgres://example")
    ).fetch_recipients(
        "lote 1",
        limit=2,
        sent_campaign_key="3formas-melhorar-experiencia",
    )

    assert contacts == [
        {"id": "1", "nome": "Hugo", "email": "hugo@example.com"},
        {"id": "2", "nome": "Ana", "email": "ana@example.com"},
    ]
    assert fake_cursor.final_params == [
        "3formasmelhorarexperiencia",
        "lote1",
        1,
        "3formasmelhorarexperiencia",
        "lote1",
        2,
    ]


class FakeConnection:
    def __init__(self, cursor: "FakeCursor") -> None:
        self.cursor_instance = cursor

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        return None

    def cursor(self, row_factory=None) -> "FakeCursor":
        return self.cursor_instance


class FakeCursor:
    def __init__(self) -> None:
        self.calls = 0
        self.rows = []
        self.one = None
        self.final_params = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        return None

    def execute(self, query, params=None) -> None:
        self.calls += 1
        if self.calls == 1:
            self.rows = [
                {"column_name": "id"},
                {"column_name": "email"},
                {"column_name": "nome"},
                {"column_name": "lote"},
                {"column_name": "created_at"},
            ]
            return
        if self.calls == 2:
            self.one = {"exists": True}
            return
        if self.calls in {2, 3, 4}:
            self.one = {"exists": True}
            return
        self.final_params = list(params or [])
        self.rows = [
            {"id": "1", "nome": "Hugo", "email": "hugo@example.com"},
            {"id": "2", "nome": "Ana", "email": "ana@example.com"},
        ]

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.one
