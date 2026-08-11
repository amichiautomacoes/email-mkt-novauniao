from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    supabase_database_url: str = Field(default="", alias="SUPABASE_DATABASE_URL")
    supabase_schema: str = Field(default="mkt_novauniao", alias="SUPABASE_SCHEMA")

    resend_api_key: str = Field(default="", alias="RESEND_API_KEY")
    email_from: str = Field(default="", alias="EMAIL_FROM")
    email_reply_to: str = Field(default="", alias="EMAIL_REPLY_TO")

    email_batch_size: int = Field(default=100, alias="EMAIL_BATCH_SIZE")
    resend_requests_per_second: float = Field(
        default=4.0, alias="RESEND_REQUESTS_PER_SECOND"
    )
    dry_run_default: bool = Field(default=True, alias="DRY_RUN_DEFAULT")

    google_service_account_file: Path = Field(
        default=Path("mkt-novauniao-d64a259b4a40.json"),
        alias="GOOGLE_SERVICE_ACCOUNT_FILE",
    )
    google_service_account_json: str = Field(
        default="", alias="GOOGLE_SERVICE_ACCOUNT_JSON"
    )
    google_service_account_json_base64: str = Field(
        default="", alias="GOOGLE_SERVICE_ACCOUNT_JSON_BASE64"
    )
    email_schedule_spreadsheet_id: str = Field(
        default="", alias="EMAIL_SCHEDULE_SPREADSHEET_ID"
    )
    email_schedule_spreadsheet_name: str = Field(
        default="Cronograma Email MKT", alias="EMAIL_SCHEDULE_SPREADSHEET_NAME"
    )

    templates_catalog_path: Path = Path("templates/agosto-2026/catalog.json")
    templates_raw_dir: Path = Path("templates/agosto-2026/raw")
    templates_clean_dir: Path = Path("templates/agosto-2026/clean")

    @field_validator(
        "supabase_database_url",
        "supabase_schema",
        "resend_api_key",
        "email_from",
        "email_reply_to",
        mode="before",
    )
    @classmethod
    def clean_secret_value(cls, value: object, info) -> object:
        if not isinstance(value, str):
            return value
        first_line = next(
            (line.strip() for line in value.splitlines() if line.strip()), ""
        )
        if first_line.startswith(f"{info.field_name.upper()}="):
            first_line = first_line.split("=", 1)[1].strip()
        return first_line.strip("'\"")


@lru_cache
def get_settings() -> Settings:
    return Settings()
