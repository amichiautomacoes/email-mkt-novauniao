#!/bin/sh
set -eu

CRON_SCHEDULE="${EMAIL_CRON_SCHEDULE:-*/5 * * * *}"
CRON_ENV_FILE="/tmp/email-mkt-cron.env"
CRON_FILE="/etc/cron.d/email-mkt"

write_export() {
  key="$1"
  value="$(printenv "$key" 2>/dev/null || true)"
  escaped="$(printf "%s" "$value" | sed "s/'/'\\\\''/g")"
  printf "export %s='%s'\n" "$key" "$escaped" >> "$CRON_ENV_FILE"
}

: > "$CRON_ENV_FILE"

for key in \
  SUPABASE_DATABASE_URL \
  SUPABASE_SCHEMA \
  RESEND_API_KEY \
  EMAIL_FROM \
  EMAIL_REPLY_TO \
  EMAIL_BATCH_SIZE \
  RESEND_REQUESTS_PER_SECOND \
  DRY_RUN_DEFAULT \
  EMAIL_SCHEDULE_DRY_RUN \
  EMAIL_CRON_SCHEDULE \
  EMAIL_SCHEDULE_SPREADSHEET_NAME \
  EMAIL_SCHEDULE_SPREADSHEET_ID \
  GOOGLE_SERVICE_ACCOUNT_FILE \
  GOOGLE_SERVICE_ACCOUNT_JSON \
  GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 \
  TZ
do
  write_export "$key"
done

printf "export PYTHONPATH='/app/src'\n" >> "$CRON_ENV_FILE"

{
  echo "SHELL=/bin/sh"
  echo "PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"
  printf "%s root . %s && /app/scripts/docker/run-scheduled-once.sh >> /proc/1/fd/1 2>> /proc/1/fd/2\n" "$CRON_SCHEDULE" "$CRON_ENV_FILE"
} > "$CRON_FILE"

chmod 0644 "$CRON_FILE"

echo "email-mkt worker cron started with schedule: $CRON_SCHEDULE"
exec cron -f
