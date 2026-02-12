# Codebase Issues Report

**Date:** February 9, 2026  
**Scope:** Static analysis, config, tests, views, cache, and structure (re-analyzed).

---

## 1. Django system check

- **Current status:** `python manage.py check` passes with **no issues** (2 silenced: `django_ratelimit.E003`, `django_ratelimit.W001`).
- CKEditor: Project uses **django-ckeditor-5**; no CKEditor 4 dependency. No CKEditor-related system check warnings.

---

## 2. Donation amount validation (resolved)

- **finance/views.py**: Now includes `Decimal` coercion and validation with error handling for non-numeric or non-positive values.

---

## 3. Production media URL (documentation / low)

- When **GS_BUCKET_NAME** is set, `config/settings.py` sets `MEDIA_URL` to the GCS bucket URL and **config/urls.py** does **not** add the `/media/` `re_path` in production when GCS is used (lines 111–116: media route only when `not os.environ.get('GS_BUCKET_NAME')`).
- **Recommendation:** Document in SECURITY.md or README that in GCS-backed production, all media links must use `MEDIA_URL` (e.g. `{{ object.photo.url }}`) and that relative `/media/` paths are not served from the app.

---

## 4. Cache keys and invalidation (resolved)

- **core/views/pages.py**: Home uses `home:stats:v1`, counties uses `counties:page_stats:v1`.
- **core/cache_utils.py**: `invalidate_aspirant_cache()` and `invalidate_county_cache()` use patterns `counties:*`, `counties:page_stats:*`, `home:stats:*`, so invalidation now matches page cache keys. **No inconsistency.**

---

## 5. Donation metric (resolved)

- **core/cache_utils.py** `get_dashboard_stats()` uses `Donation.objects.filter(status='COMPLETED')` for `total_donations_amount`. **Fixed**; analytics and admin KPIs are aligned.

---

## 6. Jazzmin / Unfold (resolved)

- **config/urls.py**: No Jazzmin monkeypatch; media route conditional on `GS_BUCKET_NAME` only.
- **config/settings.py**: Unfold block is correctly commented as "Unfold Admin Configuration".
- **requirements.txt**: No `django-jazzmin`; project uses Unfold only.

---

## 7. Bare `except` (resolved)

- **users/views.py** (seed_members_view): KPI reset uses `except Exception:` (line 153).
- **users/management/commands/seed_members.py**: Temp file cleanup uses `except Exception:` (lines 47–48). No bare `except:` found in codebase.

---

## 8. Legacy admin template (resolved)

- **templates/admin/core/aspirantregistration/** was removed (per git status). Only **templates/admin/aspirants/aspirantregistration/change_list.html** remains. No duplicate legacy path.

---

## 9. Indentation style (resolved)

- **aspirants/models.py** (lines 57–59): Normalized to standard 4-space indentation.

---

## 10. Seed / test DB (low)

- Running tests with a PostgreSQL `DATABASE_URL` (e.g. Neon) can hit "database already exists" or an interactive prompt. For CI/scripted runs, use `--keepdb` or force SQLite for tests. Document in README or CI config.

---

## 11. Silenced system checks (low)

- **SILENCED_SYSTEM_CHECKS** includes `django_ratelimit.E003` and `django_ratelimit.W001`. Ensure the reasons for silencing (e.g. intentional ratelimit configuration) are documented so future changes don’t reintroduce problems.

---

## 12. Summary table

| Issue | Severity | Area | Status / Action |
|-------|----------|------|-----------------|
| Donation amount validation | — | finance/views | Resolved |
| Production media / GCS | Low | Config / docs | Document that media must use MEDIA_URL in GCS prod |
| Indentation (aspirants/models) | — | Code quality | Resolved |
| Test DB / CI (PostgreSQL) | Low | Testing / CI | Use --keepdb or SQLite; document |
| Silenced ratelimit checks | Low | Config | Document why E003/W001 are silenced |
| Donation metric (COMPLETED) | — | core/cache_utils | Resolved |
| Cache key alignment | — | core cache | Resolved |
| Jazzmin / Unfold | — | Config | Resolved |
| Bare except | — | users | Resolved |
| Legacy admin template | — | Templates | Resolved |
| Redundant Cache Logic | — | core/cache_utils | Resolved |

---

## 13. What was verified as OK

- **core.views** – All page, dashboard, and contact views re-exported from `core.views`; URLs and UNFOLD `DASHBOARD_CALLBACK` work.
- **core.cache_utils** – Uses `AspirantRegistration` and County’s `aspirantregistration_set`; `get_dashboard_stats()` uses `status='COMPLETED'` for donations.
- **core.tests_models** – Imports `Aspirant` from `aspirants.models`; consistent with current model location.
- **aspirants.views** – `mp_candidate_detail` passes `candidate` (may be None); template handles with `{% if candidate %}` and uses `constituency.county` (Constituency has FK to County).
- **commerce** – Vendor/Product in commerce app with `related_name='products'`; core admin does not register Vendor/Product (commerce does).
- **Counties / home cache** – Keys `counties:page_stats:v1` and `home:stats:v1` are invalidated by `counties:*` and `home:stats:*` in cache_utils.

---

*Generated from static analysis and `manage.py check`. Re-run tests with your chosen DB (e.g. `--keepdb` or SQLite) to confirm.*
