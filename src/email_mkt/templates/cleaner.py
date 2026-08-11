import re
from pathlib import Path

from bs4 import BeautifulSoup

GREEN_BOX_COLOR = "#40A155"
WHITE_BACKGROUND = "#FFFFFF"


def clean_saved_preview_html(source_path: Path, destination_path: Path) -> None:
    html = source_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    source_lines = soup.select("td.line-content")
    if source_lines:
        html = "\n".join(line.get_text("", strip=False) for line in source_lines)
        soup = BeautifulSoup(html, "lxml")
    else:
        for selector in [".line-gutter-backdrop", ".line-wrap-control", ".line-number"]:
            for node in soup.select(selector):
                node.decompose()

    _remove_rdstation_web_preview(soup)
    _remove_rdstation_unsubscribe(soup)
    _remove_template_tokens(soup)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(_to_html_document(soup), encoding="utf-8")


def apply_green_content_box(template_path: Path) -> None:
    html = template_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    if soup.body is not None:
        _set_style_property(soup.body, "background-color", WHITE_BACKGROUND)

    for container in soup.select("table.nl-container"):
        _set_style_property(container, "background-color", WHITE_BACKGROUND)
        container["bgcolor"] = WHITE_BACKGROUND

    for content in soup.select("table.row-content"):
        _set_style_property(content, "background-color", GREEN_BOX_COLOR)
        content["bgcolor"] = GREEN_BOX_COLOR

    template_path.write_text(_to_html_document(soup), encoding="utf-8")


def personalize_with_contact_name(source_path: Path, destination_path: Path) -> None:
    clean_saved_preview_html(source_path, destination_path)
    html = destination_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    if _replace_name_merge_tags(soup):
        destination_path.write_text(_to_html_document(soup), encoding="utf-8")
        return

    container_cell = soup.select_one("body > table > tbody > tr > td")
    if container_cell is None:
        raise RuntimeError(
            f"Nao foi possivel localizar o container principal em {destination_path}"
        )

    greeting = BeautifulSoup(
        """
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-contact-name" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0" width="100%">
          <tbody>
            <tr>
              <td>
                <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;color:#000;width:500px;margin:0 auto" width="500">
                  <tbody>
                    <tr>
                      <td class="column column-1" style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;vertical-align:top" width="100%">
                        <table border="0" cellpadding="10" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word" width="100%">
                          <tr>
                            <td class="pad">
                              <div style="font-family:Montserrat,'Trebuchet MS','Lucida Grande','Lucida Sans Unicode','Lucida Sans',Tahoma,sans-serif;font-size:16px;color:#ffffff;line-height:1.4">
                                <p style="margin:0;text-align:left">Ol&aacute;, {{ contact.nome }}.</p>
                              </div>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>
        """,
        "lxml",
    ).table

    container_cell.insert(0, greeting)
    destination_path.write_text(_to_html_document(soup), encoding="utf-8")


def _replace_name_merge_tags(soup: BeautifulSoup) -> bool:
    replaced = False
    merge_tags = ["*|PRIMEIRO_NOME|*", "*|NOME|*"]
    for text_node in soup.find_all(string=True):
        cleaned = str(text_node)
        for merge_tag in merge_tags:
            cleaned = cleaned.replace(merge_tag, "{{ contact.nome }}")
        cleaned = re.sub(
            r"(Ol.,\s*\{\{\s*contact\.nome\s*\}\})\s+([!.])", r"\1\2", cleaned
        )
        if cleaned != text_node:
            text_node.replace_with(cleaned)
            replaced = True
    return replaced


def _set_style_property(node, property_name: str, value: str) -> None:
    declarations = []
    found = False
    for raw_declaration in node.get("style", "").split(";"):
        declaration = raw_declaration.strip()
        if not declaration or ":" not in declaration:
            continue
        name, current_value = declaration.split(":", 1)
        if name.strip().lower() == property_name.lower():
            declarations.append(f"{property_name}:{value}")
            found = True
        else:
            declarations.append(f"{name.strip()}:{current_value.strip()}")
    if not found:
        declarations.append(f"{property_name}:{value}")
    node["style"] = ";".join(declarations)


def _remove_rdstation_unsubscribe(soup: BeautifulSoup) -> None:
    for link in soup.find_all("a", href=True):
        if "app.rdstation.email/descadastrar/*UUID*" in link["href"]:
            link.unwrap()


def _remove_rdstation_web_preview(soup: BeautifulSoup) -> None:
    for link in soup.find_all("a", href=True):
        if "app.rdstation.email/mail/" not in link["href"]:
            continue
        row_table = link.find_parent(
            lambda tag: tag.name == "table" and "row" in tag.get("class", [])
        )
        if row_table is not None:
            row_table.decompose()
        else:
            link.unwrap()


def _remove_template_tokens(soup: BeautifulSoup) -> None:
    for text_node in soup.find_all(string=True):
        cleaned = (
            text_node.replace("{{ unsubscribe_url }}", "")
            .replace("{{ tracking_pixel_url }}", "")
            .replace("app.rdstation.email/descadastrar/*UUID*", "")
        )
        if cleaned != text_node:
            text_node.replace_with(cleaned)


def _to_html_document(soup: BeautifulSoup) -> str:
    html = str(soup)
    if "<!DOCTYPE HTML>" not in html[:100].upper():
        html = "<!DOCTYPE html>\n" + html
    return html
