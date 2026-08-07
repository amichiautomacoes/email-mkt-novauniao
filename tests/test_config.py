from email_mkt.config import Settings


def test_settings_cleans_secret_values_copied_from_env_lines() -> None:
    settings = Settings(
        supabase_database_url="SUPABASE_DATABASE_URL=postgresql://example/db?sslmode=require\nSUPABASE_SCHEMA=x",
        resend_api_key=" RESEND_API_KEY=re_example ",
    )

    assert settings.supabase_database_url == "postgresql://example/db?sslmode=require"
    assert settings.resend_api_key == "re_example"
