# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files (optional if using whitenoise)
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Start app
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
