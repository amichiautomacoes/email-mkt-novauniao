from email_mkt.config import Settings
from email_mkt.pipeline import PipelineRequest, run_campaign_pipeline


def test_pipeline_dry_run_with_no_contacts() -> None:
    result = run_campaign_pipeline(
        PipelineRequest(
            campaign_key="manual", template_key="etiquetas-ideais", dry_run=True
        ),
        Settings(supabase_database_url=""),
    )

    assert result.dry_run is True
    assert result.attempted == 0


def test_pipeline_resolves_template_from_lote_campaign() -> None:
    result = run_campaign_pipeline(
        PipelineRequest(campaign_key="Lote2", dry_run=True),
        Settings(supabase_database_url=""),
    )

    assert result.dry_run is True
    assert result.attempted == 0
