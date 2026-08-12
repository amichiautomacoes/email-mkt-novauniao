from email_mkt.config import Settings
from email_mkt.metrics import resend_client
from email_mkt.metrics.resend_client import ResendMetricsClient


def test_retrieve_metrics_builds_query_params(monkeypatch) -> None:
    fake_http = FakeHttpClient(
        {
            "object": "metrics",
            "metrics": ["sent"],
            "dimensions": ["period"],
            "totals": {"sent": 10},
        }
    )
    monkeypatch.setattr(resend_client.httpx, "Client", lambda **kwargs: fake_http)

    payload = ResendMetricsClient(Settings(resend_api_key="re_test")).retrieve_metrics(
        start_date="2026-08-12",
        end_date="2026-08-13",
        metrics=["sent"],
        dimensions=["period"],
    )

    assert payload["totals"] == {"sent": 10}
    assert fake_http.last_path == "/emails/metrics"
    assert fake_http.last_params["start_date"] == "2026-08-12"
    assert fake_http.last_params["end_date"] == "2026-08-13"
    assert fake_http.last_params["metrics"] == "sent"
    assert fake_http.last_params["dimensions"] == "period"


class FakeHttpClient:
    def __init__(self, payload) -> None:
        self.payload = payload
        self.calls = []
        self.last_path = None
        self.last_params = None

    def get(self, path, params):
        self.calls.append((path, dict(params)))
        self.last_path = path
        self.last_params = params
        return FakeResponse(self.payload)


class FakeResponse:
    def __init__(self, payload) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload
