web: gunicorn config.wsgi:application --bind :$PORT --workers 2 --threads 4 --timeout 120 --log-file -
worker: celery -A config worker -l info --concurrency=2
