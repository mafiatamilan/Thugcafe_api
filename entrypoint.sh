#!/bin/bash

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z dpg-cn2fqtv1hbls73b42p90-a.oregon-postgres.render.com 5432; do
  sleep 1
done
echo "PostgreSQL is up."

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create default superuser (if not exists)
echo "Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="samplepos").exists():
    User.objects.create_superuser("samplepos", email="", password="pos@123")
EOF

# Start Gunicorn server
echo "Starting server..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
