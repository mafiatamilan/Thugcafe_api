#!/bin/bash

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z dpg-cn2fqtv1hbls73b42p90-a.oregon-postgres.render.com 5432; do

  sleep 1
done
echo "PostgreSQL is up."

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
