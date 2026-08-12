import httpx

from email_mkt.config import Settings

DEFAULT_METRICS = [
    "bounced",
    "clicked",
    "complained",
    "opened",
]


class ResendMetricsClient:
    def __init__(self, settings: Settings) -> None:
        self.client = httpx.Client(
            base_url="https://api.resend.com",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "User-Agent": "email-mkt-gcp/0.1",
            },
            timeout=30,
        )

    def retrieve_metrics(
        self,
        *,
        start_date: str,
        end_date: str | None = None,
        timezone: str = "America/Sao_Paulo",
        granularity: str = "daily",
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
    ) -> dict:
        params = {
            "start_date": start_date,
            "timezone": timezone,
            "granularity": granularity,
            "metrics": ",".join(metrics or DEFAULT_METRICS),
            "dimensions": ",".join(dimensions or ["period"]),
        }
        if end_date:
            params["end_date"] = end_date

        response = self.client.get("/emails/metrics", params=params)
        response.raise_for_status()
        return response.json()
