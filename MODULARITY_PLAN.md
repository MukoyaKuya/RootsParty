# Modularity Implementation Plan: Extracting Focused Apps

Moving away from the monolithic `core` app to a modular structure will improve maintainability, testing, and scalability. This plan outlines the phased extraction of features into dedicated Django applications.

---

## Phase 1: The `aspirants` App
**Objective**: Extract all aspirant-related functionality. This is the most complex component and will provide the biggest "win" in terms of code organization.

### 1. New App Structure
- **Models**: `Aspirant`, `AspirantRegistration`, `LeadershipRole`.
- **Views**: All registration flows, status checks, and PDF generation logic.
- **Templates**: Move all `templates/core/aspirant_*.html` to `templates/aspirants/`.

### 2. Implementation Steps
1.  Initialize app: `python manage.py startapp aspirants`.
2.  Move model definitions and handle imports (e.g., `Aspirant` depends on `County`).
3.  Migrate views from `core/views.py` to `aspirants/views.py`.
4.  Update `urls.py` with the new app namespace.
5.  **Critical**: Handle database migrations. Since these tables already exist in `core`, we will use "State-only" migrations or rename the tables to avoid data loss.

---

## Phase 2: The `commerce` App (Shop & Vendors)
**Objective**: Separate the marketplace features from the party's core CMS.

### 1. New App Structure
- **Models**: `Vendor`, `Product`.
- **Views**: `shop`, `vendor_detail`, `product_detail`.
- **Templates**: Move `shop.html`, `vendor_detail.html`, etc.

---

## Phase 3: The `events` App
**Objective**: Isolate event management and the gate pass ticketing system.

### 1. New App Structure
- **Models**: `Event`, `GatePass`.
- **Views**: `events`, `download_gate_pass`.

---

## Phase 4: The `manifesto` App
**Objective**: Move policy and manifesto content to its own module.

### 1. New App Structure
- **Models**: `ManifestoItem`, `ManifestoEvidence`.
- **Views**: `manifesto_list`, `manifesto_detail`.

---

## Phase 5: Cleanup `core`
The `core` app will remain responsible only for:
- Home page and "About" content.
- Global CMS elements (Blog, Gallery, Leader profiles).
- Site-wide settings and contact forms.
- Location data (Counties/Constituencies) which act as foundational data for other apps.

---

## Technical Strategy for Migrations
To avoid breaking the production database or losing data:
1.  We will use `SeparateDatabaseAndState` in Django migrations.
2.  Alternatively, we can keep the database table names as `core_aspirant` etc., for a while using `class Meta: db_table = 'core_aspirant'` within the new apps to ensure zero-downtime and zero-data-loss during the transition.

---
**Prepared by**: Antigravity (Advanced Agentic Coding AI)
**Step**: Initiative 1 - Modularity Improvement
