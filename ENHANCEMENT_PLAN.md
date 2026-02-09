# Roots Party – Codebase Enhancement Plan

**Constraints:** No database schema changes. No breaking changes to URLs, behaviour, or public APIs.

---

## 1. Current State (Post-Analysis)

| Area | Finding |
|------|--------|
| **core/views.py** | ~569 lines, 25+ FBVs; gate pass PDF ~120 lines inline |
| **aspirants/views.py** | ~448 lines; single aspirant PDF ~165 lines, list report ~165 lines inline |
| **users/views.py** | ~380 lines; member card PDF inline |
| **Services** | Only `finance/services.py` (Mpesa); no PDF or dashboard services |
| **Templates** | `manifesto_detail.html` ~154 KB; `home.html` ~50 KB |
| **Tests** | Good model/API/contact/dashboard tests; no dedicated PDF or registration-flow tests |
| **Root scripts** | Many one-off `.py` scripts (e.g. `check_counties.py`, `dump_cloud_db.py`) that could become management commands |

---

## 2. Phased Roadmap

### Phase 1 – Maintainability (current focus)

| # | Task | Description | Risk |
|---|------|-------------|------|
| 1.1 | **Core PDF service** | Extract gate pass PDF generation from `core/views.py` into `core/services/pdf.py`. View: resolve event, create GatePass + bump counter, call service, return `FileResponse`. | None |
| 1.2 | **Aspirants PDF services** | Add `aspirants/services.py`: `build_aspirant_profile_pdf(aspirant)` and `build_aspirants_report_pdf()`. Views only: get object, call service, return `FileResponse`. | None |
| 1.3 | **Dashboard stats helper** | Move dashboard aggregation into `core/cache_utils.py` (e.g. `get_dashboard_stats()`) or `core/services/dashboard.py`. View calls helper and passes context to template. | None |
| 1.4 | **Optional: users PDF** | Extract member card PDF from `users/views.py` into `users/services.py` (same pattern). | None |

### Phase 2 – Structure & templates

| # | Task | Description | Risk |
|---|------|-------------|------|
| 2.1 | **Core views split** | Option A: Keep single `core/views.py` but group related functions with comments. Option B: Split into `core/views/` package (e.g. `pages.py`, `dashboard.py`, `pdf.py`) and re-export. No URL or behaviour change. | Low |
| 2.2 | **Template partials** | Break large templates (`manifesto_detail`, `home`) into `{% include %}` partials for repeated sections. No logic change. | None |
| 2.3 | **Root scripts → commands** | Move suitable root-level scripts into `core.management.commands` (or relevant app) as management commands. Prefer scripts that are clearly “run once” or “maintenance”. | Low (some scripts may need special env/args) |

### Phase 3 – Quality & hardening (later)

| # | Task | Description | Risk |
|---|------|-------------|------|
| 3.1 | **Integration tests** | Add tests for aspirant registration flow (multi-step) and for PDF generation (service or view returning correct content-type/filename). | None |
| 3.2 | **Security / env** | Ensure `DEBUG` and production secrets (e.g. `GS_BUCKET_NAME`) are doc’d and use env/Secret Manager; no code change to behaviour. | None |
| 3.3 | **UUIDs / async** | Deferred: UUIDs need migrations and URL changes; Celery/Cloud Tasks are additive and can be done later. | N/A |

---

## 3. Implementation Order (Phase 1)

1. **1.1 Core gate pass PDF service** – Implement `core/services/pdf.py` and thin `download_gate_pass` view.
2. **1.2 Aspirants PDF services** – Implement `aspirants/services.py` and thin aspirant profile + list report views.
3. **1.3 Dashboard stats** – Implement `get_dashboard_stats()` and thin dashboard view.
4. **1.4 (Optional)** – Users member card PDF service.

---

## 4. Done / In Progress

- [x] Aspirants app refactor (models, views, templates, URLs, admin, migrations).
- [x] 1.1 Core PDF service (gate pass) – `core/services/pdf.py` + thin `download_gate_pass` view.
- [x] 1.2 Aspirants PDF services – `aspirants/services.py` (`build_aspirant_profile_pdf`, `build_aspirants_report_pdf`) + thin views.
- [x] 1.3 Dashboard stats helper – `get_dashboard_stats()` in `core/cache_utils.py` + thin dashboard view.
- [x] 1.4 Users PDF (member card) – `users/services.py` (`build_member_card_pdf`) + thin `download_card` view.
- [x] 2.2 Template partials – `partials/core/manifesto_nav_back.html`, `manifesto_detail_styles.html`, `home_hero.html`; manifesto_detail and home use includes.
- [x] 2.1 Core views split – `core/views/` package: `pages.py`, `dashboard_views.py`, `contact_views.py`; `__init__.py` re-exports; `core.views` and URLs unchanged.
- [x] 2.3 Root scripts → commands – New commands: `clear_kpi_override`, `update_capital_manifesto`, `update_manifesto_evidence`. Removed root scripts: `check_counties.py` (duplicate of existing command), `mark_verified.py` (duplicate of `verify_official_vendor`), `clear_kpi_override.py`, `update_capital.py`, `update_manifesto_content.py`, `load_members_batched.py` (logic already in `users` command `seed_members`).
- [x] 3.1 Integration tests – Aspirant registration flow (page load, submit success, save draft, status lookup); aspirant PDF (staff-only, content-type/filename); core gate pass PDF test in `core.tests.GatePassPDFTest`.
- [x] 3.2 Security / env – `SECURITY.md` added (DEBUG, SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASE_URL, GS_BUCKET_NAME, REDIS_URL, production checklist); `.env.example` updated with production note and SECURITY.md reference.
- [ ] 3.3 UUIDs / async – Deferred.
