import base64
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings
from email_mkt.templates.catalog import TemplateCatalog


class TemplateRenderer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.template_dir = self._select_template_dir()
        self.catalog = TemplateCatalog(self.settings.templates_catalog_path)
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_message(self, template_key: str, contact: dict) -> EmailMessage:
        metadata = self.catalog.get(template_key)
        template_name = metadata.html if metadata else f"{template_key}.html"
        template = self.env.get_template(template_name)
        html = template.render(contact=contact)
        return EmailMessage(
            to=contact["email"],
            subject=contact.get("subject")
            or (
                metadata.subject if metadata else template_key.replace("-", " ").title()
            ),
            html=html,
            reply_to=self.settings.email_reply_to or None,
            attachments=self._inline_attachments(html, template_name, template_key),
            metadata={"contact_id": contact.get("id"), "template": template_key},
        )

    def _select_template_dir(self) -> Path:
        if self.settings.templates_clean_dir.exists() and any(
            self.settings.templates_clean_dir.glob("*.html")
        ):
            return self.settings.templates_clean_dir
        return self.settings.templates_raw_dir

    def _inline_attachments(
        self, html: str, template_name: str, template_key: str
    ) -> list[dict]:
        attachments = []
        for filename in sorted(set(re.findall(r"cid:([^\"' >]+)", html))):
            image_path = self._find_inline_image(filename, template_name, template_key)
            if image_path is None:
                continue
            attachments.append(
                {
                    "filename": filename,
                    "content": base64.b64encode(image_path.read_bytes()).decode("ascii"),
                    "content_type": "image/png",
                    "content_id": filename,
                    "content_disposition": "inline",
                }
            )
        return attachments

    def _find_inline_image(
        self, filename: str, template_name: str, template_key: str
    ) -> Path | None:
        candidate_dirs = [
            self.settings.templates_raw_dir / Path(template_name).stem / "images",
            self.settings.templates_raw_dir / template_key / "images",
            self.settings.templates_raw_dir / "images",
        ]
        for candidate_dir in candidate_dirs:
            image_path = candidate_dir / filename
            if not image_path.exists():
                continue
            return image_path
        return None
