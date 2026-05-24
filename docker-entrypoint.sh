#!/bin/sh
set -e

# Run migrations only when RUN_MIGRATIONS=true (run in Cloud Build / deploy job, not on every cold start)
if [ "$RUN_MIGRATIONS" = "true" ] || [ "$RUN_MIGRATIONS" = "True" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Warm DB connection (reduces first-request latency)
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection
connection.ensure_connection()
print('DB connection warmed')
" 2>/dev/null || true

# Execute the main command (gunicorn)
exec "$@"
