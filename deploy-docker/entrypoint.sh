#!/bin/sh
set -e

echo "==> migrate"
python manage.py migrate --noinput

echo "==> collectstatic"
python manage.py collectstatic --noinput

WORKERS="${GUNICORN_WORKERS:-3}"
echo "==> gunicorn (workers=$WORKERS)"
exec gunicorn green_decor.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --forwarded-allow-ips '*' \
    --access-logfile - \
    --error-logfile -
