import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateMetadata:
    key: str
    subject: str
    html: str
    links_validated: bool = False
    images_validated: bool = False


class TemplateCatalog:
    def __init__(
        self, path: Path = Path("templates/agosto-2026/catalog.json")
    ) -> None:
        self.path = path
        self._items = self._load()

    def get(self, template_key: str) -> TemplateMetadata | None:
        item = self._items.get(template_key)
        if item is None:
            return None
        return TemplateMetadata(key=template_key, **item)

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
