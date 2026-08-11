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


def test_all_clean_templates_are_ready_to_render() -> None:
    expected_subjects = {
        "3formas-melhorar-experiencia": "3 formas de melhorar a experiência do cliente na sua loja através da etiqueta",
        "detalhe-loja": "Um detalhe que sua loja não pode esquecer",
        "etiquetas-ideais": "As etiquetas ideais para a sua loja",
        "segredo-sistema": "O segredo para o seu sistema PDV rodar sem travar no caixa",
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
        assert "rdstation" not in message.html.lower()
        assert "unsubscribe_url" not in message.html
        assert "tracking_pixel_url" not in message.html
