import typer
from rich.console import Console

from email_mkt.config import get_settings
from email_mkt.contacts.repository import ContactRepository
from email_mkt.logging_config import configure_logging
from email_mkt.pipeline import PipelineRequest, run_campaign_pipeline

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.callback()
def main() -> None:
    """Email marketing pipeline."""


@app.command()
def send(
    template: str | None = typer.Option(None, help="Nome do template sem .html"),
    campaign: str = typer.Option("manual", help="Identificador da campanha/template"),
    lote: str | None = typer.Option(None, help="Lote de contatos. Ex: lote1"),
    limit: int | None = typer.Option(
        None, help="Limite de contatos para esta execucao"
    ),
    etapa: int = typer.Option(1, help="Etapa da jornada deste lote"),
    dry_run: bool | None = typer.Option(None, help="Simula sem enviar pela Resend"),
) -> None:
    configure_logging()
    settings = get_settings()
    request = PipelineRequest(
        campaign_key=campaign,
        lote_key=lote,
        template_key=template,
        limit=limit,
        etapa=etapa,
        dry_run=settings.dry_run_default if dry_run is None else dry_run,
    )
    result = run_campaign_pipeline(request, settings)
    console.print(result)


@app.command()
def status(
    lote: str = typer.Argument(..., help="Lote a consultar. Ex: lote1"),
    etapa: int = typer.Option(2, help="Etapa que voce quer liberar"),
) -> None:
    """Mostra se um lote pode avancar para a etapa informada."""
    settings = get_settings()
    status_data = ContactRepository(settings).get_lote_etapa_status(lote, etapa)
    faltam = max(status_data["total"] - status_data["previous"], 0)
    liberado = status_data["total"] > 0 and faltam == 0
    console.print(
        {
            "lote": lote,
            "etapa_alvo": etapa,
            "leads_ativos": status_data["total"],
            f"receberam_etapa_{etapa - 1}": status_data["previous"],
            f"ja_receberam_etapa_{etapa}": status_data["current"],
            "faltam_para_liberar": faltam,
            "liberado": liberado,
        }
    )


if __name__ == "__main__":
    app()
