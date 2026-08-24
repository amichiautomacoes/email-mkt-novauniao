from pathlib import Path

import typer

from email_mkt.templates.cleaner import personalize_with_contact_name


def _iter_template_sources(source_dir: Path) -> list[tuple[Path, str]]:
    sources: list[tuple[Path, str]] = [
        (source_path, source_path.name) for source_path in source_dir.glob("*.html")
    ]
    for template_dir in sorted(path for path in source_dir.iterdir() if path.is_dir()):
        source_path = template_dir / "email.html"
        if source_path.exists():
            sources.append((source_path, f"{template_dir.name}.html"))
    return sources


def main(
    source_dir: Path = Path("templates/agosto-2026/raw"),
    destination_dir: Path = Path("templates/agosto-2026/clean"),
) -> None:
    for source_path, destination_name in _iter_template_sources(source_dir):
        personalize_with_contact_name(source_path, destination_dir / destination_name)
        typer.echo(f"cleaned {source_path} -> {destination_name}")


if __name__ == "__main__":
    typer.run(main)
