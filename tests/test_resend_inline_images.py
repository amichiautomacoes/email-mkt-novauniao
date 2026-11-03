import base64
import json
import re

import httpx

from email_mkt.campaigns.models import EmailMessage
from email_mkt.config import Settings
from email_mkt.sending.resend_client import ResendClient


def test_inline_images_use_opaque_names_and_matching_cids_without_changing_content():
    requests = []

    def handle_request(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "test-id"})

    logo = {
        "filename": "logo-invertida-sem-fundo.png",
        "content": base64.b64encode(b"logo-content").decode("ascii"),
        "content_type": "image/png",
        "content_id": "logo-invertida-sem-fundo.png",
        "content_disposition": "inline",
    }
    product = {
        "filename": "etiquetas-adesivas-referencia.jpg",
        "content": base64.b64encode(b"product-content").decode("ascii"),
        "content_type": "image/jpeg",
        "content_id": "etiquetas-adesivas-referencia.jpg",
        "content_disposition": "inline",
    }
    duplicate_logo = {**logo, "filename": "rodape.png", "content_id": "rodape.png"}
    download = {
        "filename": "foto.png",
        "content": "cGhvdG8=",
        "content_type": "image/png",
    }
    document = {
        "filename": "catalogo.pdf",
        "content": "cGRm",
        "content_type": "application/pdf",
    }
    html = (
        '<p>Olá, Hugo!</p><img src="cid:logo-invertida-sem-fundo.png">'
        '<img src="cid:etiquetas-adesivas-referencia.jpg">'
        '<img src="cid:rodape.png"><a href="https://example.com">Contato</a>'
    )
    attachments = [logo, product, duplicate_logo, download, document]
    original_attachments = [dict(attachment) for attachment in attachments]
    message = EmailMessage(
        to="teste@example.com", subject="Teste", html=html, attachments=attachments
    )
    client = ResendClient(Settings(_env_file=None))
    client.client.close()
    with httpx.Client(
        base_url="https://api.resend.com", transport=httpx.MockTransport(handle_request)
    ) as transport:
        client.client = transport
        assert client.send(message).json()["id"] == "test-id"

    payload = requests[0]
    images = payload["attachments"][:2]
    cids = re.findall(r'cid:([^" >]+)', payload["html"])
    assert len(payload["attachments"]) == 4
    assert cids == [
        images[0]["content_id"],
        images[1]["content_id"],
        images[0]["content_id"],
    ]
    for original, serialized, extension in zip([logo, product], images, ["png", "jpg"]):
        assert re.fullmatch(rf"[0-9a-f]{{32}}\.{extension}", serialized["filename"])
        assert serialized["content_id"] == serialized["filename"]
        assert serialized["content"] == original["content"]
        assert serialized["content_type"] == original["content_type"]
        assert serialized["content_disposition"] == "inline"
    assert payload["attachments"][2:] == [download, document]
    assert re.sub(r'cid:[^" >]+', "cid:IMAGE", payload["html"]) == re.sub(
        r'cid:[^" >]+', "cid:IMAGE", html
    )
    assert message.html == html
    assert message.attachments == original_attachments


def test_existing_september_image_names_and_cids_are_preserved():
    filename = "ca3cf95e1d231c08a4fc5ad4888908cf.png"
    message = EmailMessage(
        to="teste@example.com",
        subject="Setembro",
        html=f'<img src="cid:{filename}">',
        attachments=[
            {
                "filename": filename,
                "content_id": filename,
                "content_type": "image/png",
                "content_disposition": "inline",
                "content": "aW1hZ2U=",
            }
        ],
    )
    client = ResendClient(Settings(_env_file=None))
    try:
        payload = client._serialize_message(message)
    finally:
        client.client.close()
    assert payload["html"] == message.html
    assert payload["attachments"] == message.attachments
