import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, time
from io import StringIO

import requests

from email_mkt.config import Settings

DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
DRIVE_EXPORT_MIME_TYPE = "text/csv"
SPREADSHEET_MIME_TYPE = "application/vnd.google-apps.spreadsheet"


@dataclass(frozen=True)
class ScheduledCampaign:
    lote_key: str
    send_date: date
    send_time: time
    campaign_key: str
    template_key: str
    limit: int | None = None


def load_scheduled_campaigns(
    settings: Settings, reference_date: date
) -> list[ScheduledCampaign]:
    spreadsheet_id = settings.email_schedule_spreadsheet_id or _find_spreadsheet_id(
        settings
    )
    csv_text = _export_spreadsheet_csv(settings, spreadsheet_id)
    return parse_schedule_csv(csv_text, reference_date=reference_date)


def parse_schedule_csv(csv_text: str, reference_date: date) -> list[ScheduledCampaign]:
    reader = csv.reader(StringIO(csv_text))
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        return []

    header_map = _build_header_map(rows[0])
    scheduled: list[ScheduledCampaign] = []
    for row in rows[1:]:
        values = _row_values(row, header_map)
        if not any(values.values()):
            continue

        campaign_key = _normalize_campaign_key(values["campanha"])
        scheduled.append(
            ScheduledCampaign(
                lote_key=_normalize_lote_key(values["lote"]),
                send_date=_parse_date(values["data_envio"], reference_date),
                send_time=_parse_time(values["hora_envio"]),
                campaign_key=campaign_key,
                template_key=campaign_key,
                limit=_parse_limit(values["numero_envios"]),
            )
        )
    return scheduled


def _find_spreadsheet_id(settings: Settings) -> str:
    headers = _auth_headers(
        settings, ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    )
    response = requests.get(
        DRIVE_FILES_URL,
        headers=headers,
        params={
            "q": (f"mimeType = '{SPREADSHEET_MIME_TYPE}' " "and trashed = false"),
            "fields": "files(id,name,modifiedTime)",
            "pageSize": 100,
            "orderBy": "modifiedTime desc",
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
        },
        timeout=30,
    )
    response.raise_for_status()
    target_name = _normalize_sheet_name(settings.email_schedule_spreadsheet_name)
    matches = [
        file
        for file in response.json().get("files", [])
        if _normalize_sheet_name(file["name"]) == target_name
    ]
    if not matches:
        raise RuntimeError(
            f"Planilha {settings.email_schedule_spreadsheet_name!r} nao encontrada no Drive."
        )
    return matches[0]["id"]


def _export_spreadsheet_csv(settings: Settings, spreadsheet_id: str) -> str:
    headers = _auth_headers(
        settings, ["https://www.googleapis.com/auth/drive.readonly"]
    )
    response = requests.get(
        f"{DRIVE_FILES_URL}/{spreadsheet_id}/export",
        headers=headers,
        params={"mimeType": DRIVE_EXPORT_MIME_TYPE},
        timeout=30,
    )
    response.raise_for_status()
    return response.content.decode("utf-8-sig")


def _auth_headers(settings: Settings, scopes: list[str]) -> dict[str, str]:
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account

    if settings.google_service_account_json.strip():
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(settings.google_service_account_json),
            scopes=scopes,
        )
    elif settings.google_service_account_file.exists():
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=scopes,
        )
    else:
        raise RuntimeError(
            "Credencial Google nao encontrada. Configure GOOGLE_SERVICE_ACCOUNT_FILE "
            "ou GOOGLE_SERVICE_ACCOUNT_JSON."
        )

    credentials.refresh(Request())
    return {"Authorization": f"Bearer {credentials.token}"}


def _build_header_map(header: list[str]) -> dict[str, int]:
    aliases = {
        "lote": {"lote", "leadssegmentados"},
        "data_envio": {"dataenvio", "datadoenvio"},
        "hora_envio": {"horaenvio", "horario", "hora"},
        "campanha": {"campanha"},
        "numero_envios": {"numeroenvios", "numerosenvios", "limite"},
    }
    normalized_header = {
        _normalize_header(cell): index for index, cell in enumerate(header)
    }
    header_map: dict[str, int] = {}
    missing: list[str] = []
    for field_name, field_aliases in aliases.items():
        index = next(
            (
                normalized_header[alias]
                for alias in field_aliases
                if alias in normalized_header
            ),
            None,
        )
        if index is None:
            missing.append(field_name)
        else:
            header_map[field_name] = index

    if missing:
        raise ValueError(
            f"Colunas obrigatorias ausentes no cronograma: {', '.join(missing)}"
        )
    return header_map


def _row_values(row: list[str], header_map: dict[str, int]) -> dict[str, str]:
    return {
        field_name: row[index].strip() if index < len(row) else ""
        for field_name, index in header_map.items()
    }


def _normalize_header(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", value)
    ascii_value = without_accents.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_value.lower())


def _normalize_sheet_name(value: str) -> str:
    return " ".join(value.strip().split()).lower()


def _normalize_lote_key(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", _strip_accents(value).lower())
    if normalized.isdigit():
        return f"lote{normalized}"
    if normalized.startswith("lote"):
        return normalized
    raise ValueError(f"Lote invalido no cronograma: {value!r}")


def _normalize_campaign_key(value: str) -> str:
    campaign = value.strip()
    campaign = re.sub(r"^campanha\s+", "", campaign, flags=re.IGNORECASE)
    campaign = _strip_accents(campaign).lower()
    campaign = re.sub(r"[^a-z0-9]+", "-", campaign).strip("-")
    if not campaign:
        raise ValueError("Campanha vazia no cronograma.")
    return campaign


def _parse_date(value: str, reference_date: date) -> date:
    cleaned = value.strip().lower().replace(".", "")
    month_names = {
        "jan": 1,
        "janeiro": 1,
        "fev": 2,
        "fevereiro": 2,
        "mar": 3,
        "marco": 3,
        "março": 3,
        "abr": 4,
        "abril": 4,
        "mai": 5,
        "maio": 5,
        "jun": 6,
        "junho": 6,
        "jul": 7,
        "julho": 7,
        "ago": 8,
        "agosto": 8,
        "set": 9,
        "setembro": 9,
        "out": 10,
        "outubro": 10,
        "nov": 11,
        "novembro": 11,
        "dez": 12,
        "dezembro": 12,
    }

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned):
        return date.fromisoformat(cleaned)

    slash_match = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", cleaned)
    if slash_match:
        day = int(slash_match.group(1))
        month = int(slash_match.group(2))
        year = _parse_year(slash_match.group(3), reference_date.year)
        return date(year, month, day)

    month_match = re.fullmatch(r"(\d{1,2})\s+([a-zç]+)(?:\s+(\d{2,4}))?", cleaned)
    if month_match:
        day = int(month_match.group(1))
        month_name = month_match.group(2)
        year = _parse_year(month_match.group(3), reference_date.year)
        if month_name not in month_names:
            raise ValueError(f"Mes invalido no cronograma: {value!r}")
        return date(year, month_names[month_name], day)

    raise ValueError(f"Data invalida no cronograma: {value!r}")


def _parse_year(value: str | None, default: int) -> int:
    if not value:
        return default
    year = int(value)
    return 2000 + year if year < 100 else year


def _parse_time(value: str) -> time:
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", value.strip())
    if not match:
        raise ValueError(f"Horario invalido no cronograma: {value!r}")
    return time(int(match.group(1)), int(match.group(2)))


def _parse_limit(value: str) -> int | None:
    normalized = re.sub(r"[^0-9]", "", value)
    return int(normalized) if normalized else None


def _strip_accents(value: str) -> str:
    return (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
