import typer
from rich.console import Console

from email_mkt.config import get_settings
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
    campaign: str = typer.Option("manual", help="Identificador da campanha"),
    limit: int | None = typer.Option(
        None, help="Limite de contatos para esta execucao"
    ),
    dry_run: bool | None = typer.Option(None, help="Simula sem enviar pela Resend"),
) -> None:
    configure_logging()
    settings = get_settings()
    request = PipelineRequest(
        campaign_key=campaign,
        template_key=template,
        limit=limit,
        dry_run=settings.dry_run_default if dry_run is None else dry_run,
    )
    result = run_campaign_pipeline(request, settings)
    console.print(result)


if __name__ == "__main__":
    app()
