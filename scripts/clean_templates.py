from pathlib import Path

import typer

from email_mkt.templates.cleaner import clean_saved_preview_html


def main(
    source_dir: Path = Path("templates/raw"),
    destination_dir: Path = Path("templates/clean"),
) -> None:
    for source_path in source_dir.glob("*.html"):
        clean_saved_preview_html(source_path, destination_dir / source_path.name)
        typer.echo(f"cleaned {source_path.name}")


if __name__ == "__main__":
    typer.run(main)
