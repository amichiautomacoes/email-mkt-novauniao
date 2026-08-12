import sys
from pathlib import Path

import typer
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from email_mkt.config import get_settings
from email_mkt.sending.sender import EmailSender
from email_mkt.templates.renderer import TemplateRenderer

TEMPLATES = [
    "3formas-melhorar-experiencia",
    "detalhe-loja",
    "etiquetas-ideais",
    "segredo-sistema",
]


def main(recipient: str, nome: str = "Hugo") -> None:
    load_dotenv(override=True)
    settings = get_settings()
    if not settings.resend_api_key:
        raise RuntimeError("RESEND_API_KEY nao configurada no .env")
    if not settings.email_from:
        raise RuntimeError("EMAIL_FROM nao configurado no .env")

    renderer = TemplateRenderer(settings)
    messages = [
        renderer.render_message(
            template_key,
            {"id": "test", "email": recipient, "nome": nome},
        )
        for template_key in TEMPLATES
    ]
    result = EmailSender(settings).send_batch(messages, dry_run=False)
    typer.echo(result)
    if result.errors:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
