from bs4 import BeautifulSoup

from email_mkt.config import Settings
from email_mkt.templates.renderer import TemplateRenderer


def _agosto_settings() -> Settings:
    return Settings(
        templates_catalog_path="templates/agosto-2026/catalog.json",
        templates_raw_dir="templates/agosto-2026/raw",
        templates_clean_dir="templates/agosto-2026/clean",
    )


def test_renderer_uses_catalog_subject_and_contact_name() -> None:
    message = TemplateRenderer(_agosto_settings()).render_message(
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
        "4dicasinfaliveis": "Sua loja já faz isso no estoque? 4 dicas para organizar melhor seu estoque",
        "desorganizacaoestoqueestaondemenosimagina": "O problema do seu estoque pode estar onde você menos imagina",
        "economizarcomecapequenosdetalhes": "Sua loja pode estar gastando sem perceber e o problema está onde você nem imagina",
        "3formas-melhorar-experiencia": "3 formas de melhorar a experiência do cliente na sua loja através da etiqueta",
    }
    renderer = TemplateRenderer(_agosto_settings())

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


def test_setembro_templates_use_catalog_subjects() -> None:
    expected_subjects = {
        "3dicasdiminuirdesperdicio": "Você pode estar gastando mais etiquetas do que deveria",
        "4Pontosevitarfalhanaleitura": "Seu código de barras está difícil de ler?",
        "O problema do seu estoque pode começar aqui": "O problema do seu estoque pode começar aqui",
        "o-problema-do-seu-estoque-pode-comecar-aqui": "O problema do seu estoque pode começar aqui",
        "Qualimpressora": "Qual impressora usar para suas etiquetas?",
        "Qualimpressorautilizar": "Qual impressora usar para suas etiquetas?",
    }
    renderer = TemplateRenderer(Settings())

    for template_key, subject in expected_subjects.items():
        message = renderer.render_message(
            template_key,
            {"id": "1", "email": "teste@example.com", "nome": "Hugo"},
        )

        assert message.subject == subject
        assert "Ol" in message.html
        assert "{{ contact.nome }}" not in message.html
        assert "ses:no-track" not in message.html
