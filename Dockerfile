# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files
# Need dummy secret key for collectstatic
RUN SECRET_KEY=dummy-key-for-build ALLOWED_HOSTS=127.0.0.1 python manage.py collectstatic --noinput

# Run gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 config.wsgi:application
