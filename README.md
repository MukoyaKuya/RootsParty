# ROOTS PARTY PLATFORM (Digital Brutalism)

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: htmx + TailwindCSS (CDN for dev)
- **Database**: PostgreSQL (configured in settings, falls back to SQLite if env vars missing)
- **Payments**: Daraja API (Mock)

## Setup

1. **Environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Design System

- **Colors**: Black (#1a1a1a), White (#FFFFFF), Red (#E60000).
- **Font**: Oswald (Google Fonts).
- **Style**: Digital Brutalism.

## Navigation

- Sticky bottom bar (Home, Manifesto, Donate, Join).
