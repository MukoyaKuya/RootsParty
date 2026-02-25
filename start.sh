#!/bin/bash
set -e

echo "Starting Roots Party Application..."
echo "Environment: Cloud Run"

# 1. Configure Nginx
echo "Configuring Nginx..."
envsubst '$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# 2. Run Migrations if enabled
if [ "$RUN_MIGRATIONS" = "True" ] || [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput || echo "WARNING: Migrations failed, continuing..."
fi

# 3. Start Gunicorn (Background)
echo "Starting Gunicorn on socket..."
rm -f /tmp/gunicorn.sock
# Using 3 workers for better concurrency on startup
gunicorn config.wsgi:application --bind unix:/tmp/gunicorn.sock --workers 3 --threads 4 --timeout 120 --log-level debug --log-file - &
APP_PID=$!

# 4. Wait for Socket
echo "Waiting for Gunicorn socket..."
for i in {1..100}; do
    if [ -S /tmp/gunicorn.sock ]; then
        echo "Socket found!"
        break
    fi
    sleep 0.1
done

if [ ! -S /tmp/gunicorn.sock ]; then
    echo "ERROR: Gunicorn socket failed to appear."
    kill $APP_PID
    exit 1
fi

# 5. Start Nginx
echo "Starting Nginx..."
nginx -g 'daemon off;' &
NGINX_PID=$!

echo "Systems Go. PIDS: App=$APP_PID, Nginx=$NGINX_PID"

# 6. Monitor Processes
wait -n
exit $?
