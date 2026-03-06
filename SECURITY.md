# Security and environment configuration

This document describes how to keep the Roots Party app secure in development and production. **No secrets or credentials should be committed to the repository.**

---

## Environment variables

- Use a `.env` file for local development only; **never commit `.env`** (it is in `.gitignore`).
- Copy `.env.example` to `.env` and fill in real values locally.
- In **production** (e.g. Google Cloud Run), set all variables via the platform’s **environment** or **Secret Manager**—do not rely on a `.env` file on the server.

---

## Critical settings

### DEBUG

- **Production:** Must be `False`. With `DEBUG=True`, Django can expose stack traces and configuration.
- **Development:** Set `DEBUG=True` in `.env` only when needed.
- The app defaults `DEBUG` from the `DEBUG` env var (defaults to `False` if unset).

### SECRET_KEY

- **Production:** **Must** be set via environment (e.g. Secret Manager). If `DEBUG` is not `True` and `SECRET_KEY` is missing, the app will not start.
- Use a long, random value (e.g. `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`).
- Never commit the production `SECRET_KEY` to the repo.

### ALLOWED_HOSTS

- **Production:** Must be set to your real domain(s), e.g. `rootsparty.co.ke,www.rootsparty.co.ke,your-cloud-run-url.run.app`.
- **Development:** If unset, the app allows `127.0.0.1`, `localhost`, `.localhost` when `DEBUG=True`.

### CSRF_TRUSTED_ORIGINS

- In production, set to the exact origins that serve the app (e.g. `https://rootsparty.co.ke`, `https://your-service.run.app`).
- Comma-separated list; required for HTTPS form submissions and redirects.

### DATABASE_URL

- Production database URL (e.g. PostgreSQL) should be provided via environment or Secret Manager.
- Do not commit connection strings.

### GS_BUCKET_NAME (Google Cloud Storage)

- Used in production for media/file storage.
- Set via environment or Secret Manager; keep the bucket name and any associated credentials out of the repo.
- **When `GS_BUCKET_NAME` is set:** Media files are stored in and served from GCS. `MEDIA_URL` is set to the bucket URL (e.g. `https://storage.googleapis.com/<bucket>/`). The app does **not** serve `/media/` paths in this mode—all media links must use `{{ object.photo.url }}` or the full `MEDIA_URL`. Do not use hardcoded `/media/` paths in templates when using GCS.

### REDIS_URL (optional but recommended for production)

- Used for cache, sessions, and **rate limiting** in production.
- Set via environment (e.g. Cloud Memorystore, Upstash). Leave unset for local dev (in-memory cache is used).
- **Rate limiting requires Redis.** Without Redis, `RATELIMIT_ENABLE` is disabled (DummyCache does not support atomic operations). Set `REDIS_URL` in production so rate limits on join, donate, aspirant registration, contact, and newsletter are enforced.

### Silenced system checks (django-ratelimit)

- `E003`: Silenced when using DummyCache (no Redis)—rate limiting is disabled in that case.
- `W001`: Silenced for flexible cache configuration; rate limiting works when Redis is configured.
- Ensure `REDIS_URL` is set in production for rate limiting to function.

---

## Production checklist

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` set from env/Secret Manager
- [ ] `ALLOWED_HOSTS` set to your domain(s)
- [ ] `CSRF_TRUSTED_ORIGINS` set to your HTTPS origin(s)
- [ ] `DATABASE_URL` (and DB credentials) from env/Secret Manager
- [ ] `GS_BUCKET_NAME` set if using Cloud Storage
- [ ] `.env` not deployed; all secrets from platform env or Secret Manager

---

## Optional: reCAPTCHA and email

- **RECAPTCHA_TESTING:** Set to `True` only in test environments so tests can bypass reCAPTCHA.
- Email credentials (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc.) should be set via env/Secret Manager in production; use console backend in dev if desired.
