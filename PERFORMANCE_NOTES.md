# Performance Optimizations

This document describes the performance optimizations implemented for faster loading and cold start.

## Cold Start Optimizations

### 1. Conditional Migrations
Migrations no longer run on every container start by default.

- **To skip migrations on startup** (recommended for production): Set `RUN_MIGRATIONS=False` or omit it.
- **To run migrations on startup** (legacy/development): Set `RUN_MIGRATIONS=True`.

**Best practice for production:** The `deploy_production.ps1` script now:
1. Runs migrations locally (with `DATABASE_URL` from env) before building
2. Deploys with `RUN_MIGRATIONS=False` so containers skip migrations on cold start

Ensure `DATABASE_URL` and `SECRET_KEY` are set in your environment when running the deploy script.

### 2. Lazy Celery Loading
Celery is only imported when running as a worker (`celery worker`, `celery beat`, etc.). Web workers (Gunicorn) skip Celery imports, reducing startup time by ~0.5–1.5s.

### 3. Deferred Google Cloud Logging
Cloud Logging setup runs in a background thread instead of blocking startup.

### 4. DB Connection Warm-up
The entrypoint warms the database connection before Gunicorn starts, reducing first-request latency.

### 5. Min Instances
Use `--min-instances 1` in Cloud Run to keep at least one instance warm and avoid cold starts.

## Request Optimizations

### Home View
- `only()` used on queries to limit columns (BlogPost, HomeVideo, CarouselImage, FloatingImage)
- `@cache_page(60 * 15)` caches the full response for 15 minutes
- Stats are cached separately for 5 minutes

### Context Processors
- `site_settings` and `splash` are cached (1 hour) after first load

## Deployment Checklist

1. **Redis**: Ensure `REDIS_URL` is set for server-side caching (required for `cache_page` and context caches).
2. **Migrations**: Run migrations in Cloud Build or set `RUN_MIGRATIONS=True` if you prefer on-start migrations.
3. **Min instances**: Set `--min-instances 1` in `deploy_production.ps1` (already configured).
4. **CPU boost**: `run.googleapis.com/startup-cpu-boost: true` in service.yaml (already configured).
