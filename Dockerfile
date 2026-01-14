# Use an official Python runtime as a parent image
FROM python:3.12-slim
# Force Rebuild: 2026-01-08-v3-skeleton

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
    nginx \
    curl \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Copy Nginx config
COPY nginx.conf /etc/nginx/nginx.conf.template

# Copy startup script
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Collect static files
RUN python manage.py collectstatic --noinput

# Run start script (Nginx + Gunicorn)
CMD ["./start.sh"]
