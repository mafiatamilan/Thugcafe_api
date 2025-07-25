#!/bin/bash

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000
