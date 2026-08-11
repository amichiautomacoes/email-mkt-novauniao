from pathlib import Path

import typer

from email_mkt.config import get_settings
from email_mkt.templates.renderer import TemplateRenderer


def main(template: str, email: str = "teste@example.com") -> None:
    renderer = TemplateRenderer(get_settings())
    message = renderer.render_message(template, {"id": "preview", "email": email})
    output = Path("tmp") / f"preview-{template}.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(message.html, encoding="utf-8")
    typer.echo(str(output))


if __name__ == "__main__":
    typer.run(main)
