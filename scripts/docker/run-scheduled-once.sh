#!/bin/sh
set -eu

cd /app

echo "[$(date -Iseconds)] Running scheduled email campaign"
python scripts/run_scheduled_campaign.py "$@"
