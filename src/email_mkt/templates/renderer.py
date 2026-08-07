from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings
from email_mkt.templates.catalog import TemplateCatalog


class TemplateRenderer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.template_dir = self._select_template_dir()
        self.catalog = TemplateCatalog()
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
            subject=contact.get("subject") or (metadata.subject if metadata else template_key.replace("-", " ").title()),
            html=html,
            reply_to=self.settings.email_reply_to or None,
            metadata={"contact_id": contact.get("id"), "template": template_key},
        )

    def _select_template_dir(self) -> Path:
        if self.settings.templates_clean_dir.exists() and any(self.settings.templates_clean_dir.glob("*.html")):
            return self.settings.templates_clean_dir
        return self.settings.templates_raw_dir
