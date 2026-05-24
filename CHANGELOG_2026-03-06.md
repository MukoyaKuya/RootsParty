# Changelog – 6 March 2026

Summary of changes made during this session.

---

## 1. Tribes List Page (`/tribes/`)

### UI Overhaul
- **Header:** Added "Letters from Wajackoyah" label, bold title with black badge and roots-red shadow
- **Background:** Gradient plus subtle grid pattern
- **Cards:** Brutalist layout with `border-4 border-roots-black` and offset shadows
- **Hover:** Red shadow and slight lift on hover
- **Interaction:** Entire card is clickable (wrapped in `<a>`)
- **Icons:** Bordered icon boxes with roots-red accents; hover turns background red
- **Buttons:** Black background with red shadow; roots-red on hover with arrow animation
- **"Coming Soon" card:** Dashed border and styling aligned with the rest of the page
- **Technical:** Removed dynamic `color_class` Tailwind classes (unreliable with JIT)

### Files Changed
- `templates/core/tribes.html`

---

## 2. Tribe Detail Page (`/tribes/<slug>/`)

### Layout & Styling
- **Background:** Gradient and grid pattern instead of flat gray
- **Back button (desktop):** Brutalist style – `border-4`, red shadow, label "All Tribes"
- **Letter paper:** `border-4 border-roots-black` and `shadow-[10px_10px_0px_0px_#1a1a1a]`
- **Letterhead:** `border-b-4`, Roots Party text in roots-red
- **Subject line:** "Open Letter" badge with black background; small typography adjustments
- **Signature:** Text in black (not blue), roots-red pen stroke, approved stamp with `border-4`
- **Sidebar context card:** Brutalist borders and shadows; fixed broken `color_class` background
- **Sidebar action card:** `border-4`, red shadow, hover effect
- **Mobile back button:** Brutalist style consistent with desktop

### Image
- **Alignment:** `absolute inset-0` fill so image fully covers the container
- **Cropping:** `object-top` to keep heads visible
- **Height:** `h-52` instead of `h-44` for more vertical space
- **Fallback:** `bg-gray-100` while loading

### Fonts
- Moved Google Fonts into `extra_css` block
- Dropped Merriweather; kept Playfair Display, Courier Prime, Dancing Script for letter layout

### Files Changed
- `templates/core/tribe_detail.html`

---

## 3. Manifesto (`/manifesto/`)

### Content: 11 → 10 Points
Replaced the previous manifesto with 10 professional policy points:

| # | New Point | Replaces / Notes |
|---|-----------|------------------|
| 1 | Cannabis Industry | Reframed from "Legalize Marijuana"; regulated medicinal/industrial |
| 2 | New Niche Markets | Snake farming + hyena meat (previously separate) |
| 3 | Tourism | Elephant riding, wildlife, cultural tourism (new) |
| 4 | Security | New |
| 5 | Health | New |
| 6 | Infrastructure | New |
| 7 | Education | New |
| 8 | Accountability | Replaces "Hang The Corrupt"; anti-corruption, rule of law |
| 9 | New Administrative Capital | Move to Isiolo (refined) |
| 10 | Youth & Employment | New |

### Removed
- Hang The Corrupt (death penalty)
- Suspend Constitution
- 4-Day Work Week
- Federal System
- Deportations
- Shut Down SGR

### Tone
- Content rewritten in more professional, policy-focused language
- Evidence references kept where relevant (Canada, Singapore, Nigeria, etc.)

### Template Updates
- Header: "Our 10-Point Agenda" (was "These Are Our 11 Point Agendas")
- Comment: "The 10 Points Grid"

### Files Changed
- `core/management/commands/populate_manifesto.py` – full rewrite
- `templates/core/manifesto.html`

---

## 4. Home Page Quick Links

- **Cannabis link:** "Weed" → "Cannabis"; description: "A regulated industry for medicinal and industrial hemp"
- **Niche Markets link:** `/manifesto/snake-farming/` → `/manifesto/niche-markets/`; "Snakes" → "Niche Markets"; description: "Snake farming, hyena meat, and other high-value niche industries"

### Files Changed
- `templates/core/home.html`

---

## 5. Locale

- `msgid "Our 11 Point Manifesto"` → `msgid "Our 10 Point Manifesto"`

### Files Changed
- `locale/sw/LC_MESSAGES/django.po`

---

## 6. Git

- **Commit:** `5d86b07`
- **Message:** "Manifesto: 10-point professional agenda, Tribes/Manifesto UI improvements"
- **Pushed to:** `origin/main` (https://github.com/MukoyaKuya/RootsParty.git)

---

## 7. Post-Deploy

- `populate_manifesto` run locally to refresh manifesto data in `db.sqlite3`
- Production deployments that use a separate database should run `python manage.py populate_manifesto` in that environment
