#!/bin/sh
set -eu

echo "email-mkt webhook service starting."
echo "Resend endpoint: https://emailmkt.targetdados.com/webhooks/resend"

exec python /app/scripts/run_resend_webhook_server.py
