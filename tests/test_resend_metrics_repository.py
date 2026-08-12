from typing import Self

from email_mkt.config import Settings
from email_mkt.metrics.repository import ResendMetricsRepository


def test_save_metrics_snapshot_skips_without_database_url() -> None:
    repository = ResendMetricsRepository(Settings(supabase_database_url=""))

    saved = repository.save_metrics_snapshot(
        {"totals": {"sent": 10}},
        timezone="America/Sao_Paulo",
        granularity="daily",
    )

    assert saved is False


def test_save_metrics_snapshot_writes_payload(monkeypatch) -> None:
    fake_cursor = FakeCursor()
    fake_conn = FakeConnection(fake_cursor)
    monkeypatch.setattr(
        "email_mkt.metrics.repository.psycopg.connect", lambda _: fake_conn
    )

    repository = ResendMetricsRepository(
        Settings(supabase_database_url="postgres://example")
    )
    saved = repository.save_metrics_snapshot(
        {
            "start_date": "2026-08-12T00:00:00.000Z",
            "end_date": "2026-08-13T00:00:00.000Z",
            "metrics": ["sent"],
            "dimensions": ["period"],
            "totals": {"sent": 10},
            "data": [{"period": "2026-08-12", "sent": 10}],
        },
        timezone="America/Sao_Paulo",
        granularity="daily",
    )

    assert saved is True
    assert fake_cursor.params[0] == "2026-08-12T00:00:00.000Z"
    assert fake_cursor.params[2] == "America/Sao_Paulo"
    assert fake_cursor.params[3] == "daily"
    assert fake_cursor.params[4] == ["sent"]
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
        self.params = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        return None

    def execute(self, query, params) -> None:
        self.params = params
