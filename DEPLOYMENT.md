# Roots Party – Deployment Guide

This document describes how to deploy the Roots Party platform to Google Cloud Run and related infrastructure.

---

## Architecture Overview

| Component      | Technology                          | Purpose                        |
|----------------|-------------------------------------|--------------------------------|
| **Compute**    | Google Cloud Run                    | Runs the Django application    |
| **Database**   | PostgreSQL (Neon / Cloud SQL)       | Production data store          |
| **Cache**      | Redis (e.g. Upstash, Memorystore)   | Sessions, caching, Celery      |
| **Storage**    | Google Cloud Storage (GCS)          | Media files (images, PDFs)     |
| **Container**  | Docker                              | Application packaging          |
| **Web server** | Gunicorn (inside container)         | WSGI application server        |

---

## Prerequisites

- **Google Cloud SDK** (`gcloud`) installed and authenticated
- **Docker** (optional; Cloud Build can build images)
- **Environment variables** configured (see [SECURITY.md](SECURITY.md))

---

## Automated Deployment (PowerShell)

From the project root:

```powershell
.\deploy.ps1
```

This script:

1. Sets the active Google Cloud project
2. Builds the container image via `gcloud builds submit`
3. Deploys the new image to Cloud Run
4. Allows unauthenticated access (adjust for your security needs)

---

## Manual Deployment

### 1. Build the container

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/roots-party .
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy roots-party \
    --image gcr.io/YOUR_PROJECT_ID/roots-party \
    --platform managed \
    --region YOUR_REGION \
    --allow-unauthenticated
```

### 3. Set environment variables

Configure production variables in Cloud Run (Console or CLI), including:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `GS_BUCKET_NAME` (for media)
- `REDIS_URL` (for cache, Celery, **and rate limiting**)
- `CSRF_TRUSTED_ORIGINS`
- `SITE_BASE_URL`

**Rate limiting**: `django-ratelimit` requires a cache backend that supports atomic operations (e.g. Redis). Without Redis, rate limiting is automatically disabled. In production, always set `REDIS_URL` so rate limiting works across instances. See [SECURITY.md](SECURITY.md) for the full checklist.

---

## Post-deploy

1. Run migrations if needed: `python manage.py migrate`
2. Collect static files (done in Dockerfile): `python manage.py collectstatic --noinput`
3. Ensure Celery workers are running if using async tasks (PDF generation, member seeding, etc.)

---

## Troubleshooting

### Media files not loading

When `GS_BUCKET_NAME` is set, media is served from GCS. Ensure:

- Bucket is public or configured for appropriate access
- `MEDIA_URL` points to the bucket (handled by settings)
- Do not rely on `/media/` URLs from the app in production

### Database connection issues

- Confirm `DATABASE_URL` is correct (including `?sslmode=require` for Neon)
- Check Cloud Run’s outbound connectivity to the database

### Static files 404

- Static files are collected at build time (WhiteNoise)
- Verify `collectstatic` runs during the Docker build
- Ensure `STATIC_ROOT` and `STATIC_URL` are correct

---

**Roots Party of Kenya** – _Tingiza Mti!_
