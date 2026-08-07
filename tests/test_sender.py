from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings
from email_mkt.sending import sender
from email_mkt.sending.sender import EmailSender


def test_sender_records_accepted_recipients(monkeypatch) -> None:
    recorded = []
    monkeypatch.setattr(sender, "ResendClient", FakeResendClient)
    monkeypatch.setattr(sender, "CampaignRepository", lambda settings: FakeCampaignRepository(recorded))

    messages = [
        EmailMessage(to="hugo@example.com", subject="Teste", html="<p>Teste</p>"),
        EmailMessage(to="ana@example.com", subject="Teste", html="<p>Teste</p>"),
    ]
    result = EmailSender(Settings(email_batch_size=50, resend_requests_per_second=100)).send_batch(
        messages,
        dry_run=False,
        campaign_key="lote1",
    )

    assert result.sent == 2
    assert recorded == [("lote1", messages)]


def test_sender_dry_run_does_not_record_recipients(monkeypatch) -> None:
    recorded = []
    monkeypatch.setattr(sender, "CampaignRepository", lambda settings: FakeCampaignRepository(recorded))

    result = EmailSender(Settings()).send_batch(
        [EmailMessage(to="hugo@example.com", subject="Teste", html="<p>Teste</p>")],
        dry_run=True,
        campaign_key="lote1",
    )

    assert result.dry_run is True
    assert recorded == []


class FakeResendClient:
    def __init__(self, settings) -> None:
        self.settings = settings

    def send_batch(self, messages):
        return FakeResponse(messages)


class FakeResponse:
    def __init__(self, messages) -> None:
        self.messages = messages

    def json(self):
        return {"data": [{"id": str(index)} for index, _message in enumerate(self.messages)]}


class FakeCampaignRepository:
    def __init__(self, recorded) -> None:
        self.recorded = recorded

    def record_sent_recipients(self, campaign_key, messages) -> None:
        self.recorded.append((campaign_key, messages))
