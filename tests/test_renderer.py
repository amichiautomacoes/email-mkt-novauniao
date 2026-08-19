from bs4 import BeautifulSoup

from email_mkt.config import Settings
from email_mkt.templates.renderer import TemplateRenderer


def test_renderer_uses_catalog_subject_and_contact_name() -> None:
    message = TemplateRenderer(Settings()).render_message(
        "3formas-melhorar-experiencia",
        {"id": "1", "email": "teste@example.com", "nome": "Hugo"},
    )

    assert (
        message.subject
        == "3 formas de melhorar a experiência do cliente na sua loja através da etiqueta"
    )
    assert "Olá, Hugo" in message.html
    assert "row-contact-name" not in message.html
    assert "data:image" not in message.html
    assert 'src="images/' not in message.html
    assert message.html.count("cid:") == 4
    assert len(message.attachments) == 4
    assert all("content_id" in attachment for attachment in message.attachments)
    assert all("contentId" not in attachment for attachment in message.attachments)
    assert all(
        attachment["content_disposition"] == "inline"
        for attachment in message.attachments
    )


def test_all_clean_templates_are_ready_to_render() -> None:
    expected_subjects = {
        "4dicasinfalíveis": "Sua loja já faz isso no estoque? 4 dicas para organizar melhor seu estoque",
        "desorganizacaoestoqueestaondemenosimagina": "O problema do seu estoque pode estar onde você menos imagina",
        "economizarcomecapequenosdetalhes": "Sua loja pode estar gastando sem perceber e o problema está onde você nem imagina",
        "3formas-melhorar-experiencia": "3 formas de melhorar a experiência do cliente na sua loja através da etiqueta",
    }
    renderer = TemplateRenderer(Settings())

    for template_key, subject in expected_subjects.items():
        message = renderer.render_message(
            template_key,
            {"id": "1", "email": "teste@example.com", "nome": "Hugo"},
        )

        assert message.subject == subject
        assert "Olá, Hugo" in message.html
        assert "{{ contact.nome }}" not in message.html
        assert "[PRIMEIRO NOME]" not in message.html
        assert "[Primeiro Nome]" not in message.html
        assert "rdstation" not in message.html.lower()
        assert "unsubscribe_url" not in message.html
        assert "tracking_pixel_url" not in message.html
        soup = BeautifulSoup(message.html, "lxml")
        for link in soup.find_all("a", href=True):
            assert link.get_text("", strip=True) or link.find("img")
