from pathlib import Path

import typer

from email_mkt.templates.cleaner import personalize_with_contact_name


def main(
    source_dir: Path = Path("templates/agosto-2026/raw"),
    destination_dir: Path = Path("templates/agosto-2026/clean"),
) -> None:
    for source_path in source_dir.glob("*.html"):
        personalize_with_contact_name(source_path, destination_dir / source_path.name)
        typer.echo(f"cleaned {source_path.name}")


if __name__ == "__main__":
    typer.run(main)
