import pytest

from email_mkt.config import Settings
from email_mkt import pipeline
from email_mkt.campaigns.models import CampaignRunResult, EmailMessage
from email_mkt.pipeline import PipelineRequest, run_campaign_pipeline


def test_pipeline_dry_run_with_no_contacts() -> None:
    result = run_campaign_pipeline(
        PipelineRequest(
            campaign_key="manual",
            template_key="3formas-melhorar-experiencia",
            dry_run=True,
        ),
        Settings(supabase_database_url=""),
    )

    assert result.dry_run is True
    assert result.attempted == 0


def test_pipeline_rejects_lote_without_campaign_template() -> None:
    with pytest.raises(ValueError, match="Informe --template"):
        run_campaign_pipeline(
            PipelineRequest(campaign_key="Lote 10", dry_run=True),
            Settings(supabase_database_url=""),
        )


def test_pipeline_uses_campaign_key_as_template_with_explicit_lote() -> None:
    result = run_campaign_pipeline(
        PipelineRequest(
            campaign_key="3formas-melhorar-experiencia",
            lote_key="Lote 10",
            dry_run=True,
        ),
        Settings(supabase_database_url=""),
    )

    assert result.dry_run is True
    assert result.attempted == 0


def test_pipeline_uses_template_as_control_campaign_key(monkeypatch) -> None:
    calls = {}

    class FakeContactRepository:
        def __init__(self, settings) -> None:
            self.settings = settings

        def fetch_recipients(
            self, campaign_key, limit=None, sent_campaign_key=None, etapa=1
        ):
            calls["fetch"] = (campaign_key, limit, sent_campaign_key, etapa)
            return [{"id": "1", "nome": "Hugo", "email": "hugo@example.com"}]

    class FakeTemplateRenderer:
        def __init__(self, settings) -> None:
            self.settings = settings

        def render_message(self, template_key, contact):
            calls["template_key"] = template_key
            return EmailMessage(to=contact["email"], subject="Teste", html="<p>Ok</p>")

    class FakeEmailSender:
        def __init__(self, settings) -> None:
            self.settings = settings

        def send_batch(
            self,
            messages,
            dry_run=True,
            campaign_key=None,
            lote_key=None,
            etapa=1,
        ):
            calls["send"] = (messages, dry_run, campaign_key, lote_key, etapa)
            return CampaignRunResult(
                attempted=len(messages), sent=0, failed=0, dry_run=dry_run
            )

    monkeypatch.setattr(pipeline, "ContactRepository", FakeContactRepository)
    monkeypatch.setattr(pipeline, "TemplateRenderer", FakeTemplateRenderer)
    monkeypatch.setattr(pipeline, "EmailSender", FakeEmailSender)

    result = run_campaign_pipeline(
        PipelineRequest(
            campaign_key="3formas-melhorar-experiencia",
            lote_key="lote1",
            dry_run=True,
        ),
        Settings(supabase_database_url=""),
    )

    assert result.attempted == 1
    assert calls["fetch"] == (
        "lote1",
        None,
        "3formas-melhorar-experiencia",
        1,
    )
    assert calls["template_key"] == "3formas-melhorar-experiencia"
    assert calls["send"][2] == "3formas-melhorar-experiencia"
    assert calls["send"][3:] == ("lote1", 1)


def test_pipeline_blocks_next_stage_until_previous_stage_is_complete(
    monkeypatch,
) -> None:
    class FakeContactRepository:
        def __init__(self, settings) -> None:
            self.settings = settings

        def get_lote_etapa_status(self, lote_key, etapa):
            return {"total": 10, "previous": 8, "current": 0}

        def fetch_recipients(self, *args, **kwargs):
            raise AssertionError("Nao deve buscar contatos com etapa incompleta.")

    monkeypatch.setattr(pipeline, "ContactRepository", FakeContactRepository)

    result = run_campaign_pipeline(
        PipelineRequest(
            campaign_key="3formas-melhorar-experiencia",
            lote_key="lote1",
            etapa=2,
            dry_run=True,
        ),
        Settings(supabase_database_url=""),
    )

    assert result.attempted == 0
    assert result.errors == [
        "Etapa 2 bloqueada para lote1: 8/10 leads ativos receberam a etapa 1."
    ]
