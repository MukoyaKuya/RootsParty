# Roots Party Codebase Analysis (Post-Enhancement)
 
**Date:** February 2026  
**Scope:** Full codebase review after Phases 1–3 of the enhancement plan.

---

## 1. Executive Summary

The Roots Party platform is a Django 6 application for political party management, content delivery, member/aspirant registration, donations, and events. Recent work has **refactored PDF generation into services**, **split core views into a package**, **introduced template partials**, **moved several root scripts into management commands**, **added integration tests** (aspirant flow + PDFs), and **documented security and environment configuration**. The codebase is in a maintainable state with clear separation of concerns and a documented path for production deployment.

---

## 2. Technical Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.x, Python 3.x |
| Database | PostgreSQL (production) / SQLite (dev) |
| Frontend | Tailwind CSS, HTMX |
| PDF | ReportLab, qrcode |
| Cache | Redis (production) / in-memory (dev) |
| Infra | Google Cloud Run, GCS, Nginx, Docker |
| API | Django REST Framework, drf-spectacular (OpenAPI) |
| Admin | django-unfold |

---

## 3. Architecture (Current State)

### 3.1 App Structure

| App | Purpose | Key modules |
|-----|---------|-------------|
| **core** | CMS, events, shop, gallery, manifesto, blog, counties, dashboard, contact, gate pass PDF | `views/` (pages, dashboard_views, contact_views), `services/pdf.py`, `cache_utils.py`, `api/` |
| **aspirants** | Aspirant registration, MP flow, role detail, profile/list PDFs | `views.py`, `services.py`, `forms.py`, `models.py` |
| **users** | Member join, coordinator join, member card PDF, check-id, seed view | `views.py`, `services.py`, `management/commands/seed_members.py` |
| **finance** | Donations, M-Pesa (services) | `views.py`, `services.py` |
| **config** | Settings, root URLs, ASGI/WSGI | `settings.py`, `urls.py` |

### 3.2 Service Layer

- **core/services/pdf.py** – `build_gate_pass_pdf(event, code)`; views call this and return `FileResponse`.
- **aspirants/services.py** – `build_aspirant_profile_pdf(aspirant)`, `build_aspirants_report_pdf()`; used by staff-only PDF views.
- **users/services.py** – `build_member_card_pdf(member)`; used by `download_card` view.
- **finance/services.py** – M-Pesa / payment logic (unchanged).
- **core/cache_utils.py** – `get_dashboard_stats()`, `get_cached_aspirants()`, `get_cached_verified_aspirants()`, and other cache helpers; dashboard view uses `get_dashboard_stats()`.

### 3.3 Views Structure

- **core** – Split into `core/views/`: `pages.py` (~185 lines, 24 FBVs: home, about, manifesto, gallery, shop, blog, events, gate pass, counties, legal), `dashboard_views.py` (~42), `contact_views.py` (~85). All re-exported from `core.views`; `config/urls.py` imports `core_views` and URLs are unchanged.
- **aspirants** – Single `views.py` (~168 lines): registration (with draft), status, list/detail, MP flow, role_detail, staff-only PDF downloads.
- **users** – Single `views.py` (~211 lines): join, join_coordinator, success, download_card, check_id_number, seed_members_view.
- **finance** – Single `views.py` (~29 lines): donate.

### 3.4 Templates

- **Partials in use:** `templates/partials/core/home_hero.html`, `manifesto_nav_back.html`, `manifesto_detail_styles.html`; `home.html` and `manifesto_detail.html` use `{% include %}` for these.
- **Aspirants:** Templates live under `aspirants/templates/aspirants/` (registration, list, detail, draft_saved, success, status, MP flow, role_detail).

### 3.5 Management Commands

| App | Commands |
|-----|----------|
| **core** | `check_counties`, `cleanup_counties`, `clear_kpi_override`, `populate_carousel`, `populate_constituencies`, `populate_manifesto`, `standardize_counties`, `update_capital_manifesto`, `update_manifesto_evidence`, `verify_official_vendor` |
| **users** | `seed_members` (batched JSON fixture load) |
| **finance** | (commands dir present; no commands listed in scan) |

### 3.6 Tests

- **core:** `tests.py` (pages, contact, dashboard, subscribe, blog), `tests_models.py`, `tests_api.py`, `tests_validators.py`, plus **GatePassPDFTest** (gate pass PDF response).
- **aspirants:** **AspirantRegistrationFlowTest** (page load, submit success, save draft, status lookup), **AspirantPDFTest** (staff-only, content-type/filename for profile and list PDFs).
- **users:** Member registration (join page, success, validation, duplicate ID), **PDFGenerationTest** (download_card).
- **finance:** Donation model and donate view tests.

### 3.7 Security & Config

- **SECURITY.md** – Documents DEBUG, SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASE_URL, GS_BUCKET_NAME, REDIS_URL; production checklist; no committed secrets.
- **.env.example** – Template with comments and reference to SECURITY.md; behaviour unchanged.

---

## 4. Key File Sizes (Approximate)

| File | Lines |
|------|-------|
| core/views/pages.py | ~185 |
| core/views/contact_views.py | ~85 |
| core/views/dashboard_views.py | ~42 |
| core/models.py | ~393 |
| core/cache_utils.py | ~279 |
| core/services/pdf.py | ~101 |
| aspirants/views.py | ~168 |
| aspirants/services.py | ~315 |
| users/views.py | ~211 |
| users/services.py | ~139 |
| finance/views.py | ~29 |
| finance/services.py | (M-Pesa logic) |

---

## 5. Root-Level Scripts (Not Yet Commands)

These remain as standalone `.py` scripts in the project root (candidates for future conversion or retention as ops tools):

| Script | Likely purpose |
|--------|----------------|
| apply_carousel_migration.py, create_carousel_migration.py, run_carousel_migration.py, populate_carousel_data.py | Carousel data/migrations |
| check_logo_alpha.py, check_logo_status.py, resize_logo.py, remove_jua_gig_logo.py | Logo checks/resize/cleanup |
| check_remote_db.py, dump_cloud_db.py | DB connectivity/backup |
| download_media.py, upload_media_to_gcs.py, find_bucket.py | Media/GCS ops |
| migrate_helper.py, migrate_vendors.py, run_migrate.py, run_seed_sql.py, generate_seed_sql.py | Migrations/seeding |
| setup_cloud_vendors.py | Cloud vendor setup |
| fix_pwa_icons.py, update_translations.py, compile_msg.py | PWA/i18n |
| debug_content.py, find_floating_image.py, test_format_html.py | Debug/one-off |

---

## 6. URLs Overview

- **Core:** `/`, `/about/`, `/manifesto/`, `/manifesto/<slug>/`, `/manifesto-list/`, `/gallery/`, `/leader/<slug>/`, `/events/`, `/events/<id>/gate-pass/`, `/shop/`, `/shop/<vendor>/`, `/shop/<vendor>/<product>/`, `/resources/`, `/analytics/` (dashboard), `/contact/`, `/subscribe/`, `/news/`, `/news/<slug>/`, `/counties/`, `/counties/map/`, `/counties/<slug>/`, legal pages, cannabis country detail.
- **Users:** `/join/`, `/join-coordinator/`, `/join/success/`, `/member/<id>/card/`, `/check-id/`, `/seed-members-cloud/`.
- **Finance:** `/donate/`.
- **Aspirants:** `/aspirants/register/`, `/aspirants/register/<draft_token>/`, `/aspirants/status/`, `/aspirants/check-id/`, `/aspirants/list/`, `/aspirants/<id>/`, `/aspirants/roles/<slug>/`, `/aspirants/mps/`, county/candidate detail, `/aspirants/download/profile/<id>/`, `/aspirants/download/report/`.
- **API:** `/api/v1/`, `/api/schema/`, `/api/docs/`, `/api/redoc/`.

---

## 7. Strengths (Post-Enhancement)

1. **Service layer** – PDF and dashboard stats live in dedicated modules; views stay thin.
2. **Core views** – Split into pages/dashboard/contact with stable `core.views` import surface.
3. **Template partials** – Hero, manifesto nav, and manifesto styles are reusable includes.
4. **Management commands** – Common data/maintenance tasks (counties, manifesto, KPI, carousel, seed_members) are run via `manage.py`.
5. **Integration tests** – Aspirant registration flow and PDF endpoints (gate pass, aspirant profile/list) have coverage.
6. **Security and env** – SECURITY.md and .env.example give a clear production and secrets story.

---

## 8. Remaining Opportunities

1. **Root scripts** – Optional: move more one-off/maintenance scripts into management commands (carousel, logo, DB backup, media/GCS) where it improves clarity and discoverability.
2. **UUIDs / async** – Deferred in plan: UUIDs for public IDs (e.g. aspirants, members) and async tasks (e.g. Celery/Cloud Tasks) for heavy or background work.
3. **Template size** – `manifesto_detail.html` is still large (~2.2k+ lines with includes); further partials could improve readability.
4. **dashboard_callback** – Admin dashboard KPI logic is duplicated (dashboard_views vs cache_utils); could be unified on `get_dashboard_stats()` or a shared helper if desired.

---

## 9. Conclusion

The codebase is **well-structured for maintenance and deployment**: services own PDF and dashboard logic, core views are split and re-exported, template partials are in use, and security/env are documented. The enhancement plan (Phases 1–3.2) is complete; remaining work is optional (more commands, template splits) or deferred (UUIDs, async).
