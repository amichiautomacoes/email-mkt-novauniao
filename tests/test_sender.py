from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings
from email_mkt.sending import sender
from email_mkt.sending.sender import EmailSender


def test_sender_records_accepted_recipients(monkeypatch) -> None:
    recorded = []
    monkeypatch.setattr(sender, "ResendClient", FakeResendClient)
    monkeypatch.setattr(
        sender, "CampaignRepository", lambda settings: FakeCampaignRepository(recorded)
    )

    messages = [
        EmailMessage(to="hugo@example.com", subject="Teste", html="<p>Teste</p>"),
        EmailMessage(to="ana@example.com", subject="Teste", html="<p>Teste</p>"),
    ]
    result = EmailSender(
        Settings(email_batch_size=50, resend_requests_per_second=100)
    ).send_batch(
        messages,
        dry_run=False,
        campaign_key="lote1",
    )

    assert result.sent == 2
    assert recorded == [("lote1", messages)]


def test_sender_dry_run_does_not_record_recipients(monkeypatch) -> None:
    recorded = []
    monkeypatch.setattr(
        sender, "CampaignRepository", lambda settings: FakeCampaignRepository(recorded)
    )

    result = EmailSender(Settings()).send_batch(
        [EmailMessage(to="hugo@example.com", subject="Teste", html="<p>Teste</p>")],
        dry_run=True,
        campaign_key="lote1",
    )

    assert result.dry_run is True
    assert recorded == []


def test_sender_uses_single_send_for_inline_attachments(monkeypatch) -> None:
    recorded = []
    FakeResendClient.sent_single = []
    FakeResendClient.sent_batches = []
    monkeypatch.setattr(sender, "ResendClient", FakeResendClient)
    monkeypatch.setattr(
        sender, "CampaignRepository", lambda settings: FakeCampaignRepository(recorded)
    )

    message = EmailMessage(
        to="hugo@example.com",
        subject="Teste",
        html='<img src="cid:logo.png">',
        attachments=[
            {
                "filename": "logo.png",
                "content": "abc",
                "contentId": "logo.png",
            }
        ],
    )
    result = EmailSender(
        Settings(email_batch_size=50, resend_requests_per_second=100)
    ).send_batch([message], dry_run=False, campaign_key="lote1")

    assert result.sent == 1
    assert FakeResendClient.sent_single == [message]
    assert FakeResendClient.sent_batches == []
    assert recorded == [("lote1", [message])]


def test_resend_client_serializes_safe_metadata_tags() -> None:
    client = sender.ResendClient(Settings())
    client.default_tags["campaign"] = "lote 1"
    payload = client._serialize_message(
        EmailMessage(
            to="hugo@example.com",
            subject="Teste",
            html="<p>Teste</p>",
            metadata={"template": "etiquetas-ideais"},
        )
    )

    assert payload["tags"] == [
        {"name": "campaign", "value": "lote-1"},
        {"name": "template", "value": "etiquetas-ideais"},
    ]


class FakeResendClient:
    sent_single = []
    sent_batches = []

    def __init__(self, settings) -> None:
        self.settings = settings

    def send(self, message):
        self.sent_single.append(message)
        return FakeSingleResponse(message)

    def send_batch(self, messages):
        self.sent_batches.append(messages)
        return FakeResponse(messages)


class FakeSingleResponse:
    def __init__(self, message) -> None:
        self.message = message

    def json(self):
        return {"id": "single-id"}


class FakeResponse:
    def __init__(self, messages) -> None:
        self.messages = messages

    def json(self):
        return {
            "data": [{"id": str(index)} for index, _message in enumerate(self.messages)]
        }


class FakeCampaignRepository:
    def __init__(self, recorded) -> None:
        self.recorded = recorded

    def record_sent_recipients(self, campaign_key, messages) -> None:
        self.recorded.append((campaign_key, messages))
