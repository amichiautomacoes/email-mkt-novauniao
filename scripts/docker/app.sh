#!/bin/sh
set -eu

echo "email-mkt app container ready."
echo "Open the EasyPanel console to run manual commands, for example:"
echo "python -m email_mkt.cli send --campaign lote1 --limit 10 --dry-run"

tail -f /dev/null
