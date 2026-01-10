# ROOTS PARTY PLATFORM

The digital headquarters for the Roots Party of Kenya. A brutalist, high-impact web platform built with Django.

![Roots Party](static/images/logo.png)

## 🏗 Technology Stack

- **Backend**: Django 5.0+ (Python)
- **Frontend**: TailwindCSS + HTMX (Digital Brutalist Aesthetic)
- **Database**:
  - **Local**: SQLite (Default)
  - **Production**: PostgreSQL (Neon/Cloud SQL)
- **Storage**: Google Cloud Storage (Production) / Local (Development)
- **Hosting**: Google Cloud Run

---

## 🚀 Local Development Setup

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

Ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

### 2. Clone the Repository

```bash
git clone https://github.com/MukoyaKuya/RootsParty.git
cd RootsParty
```

### 3. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment Configuration

Create a `.env` file in the root directory (same level as `manage.py`). You can copy the template below:

```bash
# .env

# Security
DEBUG=True
SECRET_KEY=dev-secret-key-change-this-in-prod

# Database (Leave empty to use SQLite locally)
DATABASE_URL=
DB_ENGINE=django.db.backends.sqlite3

# Email (Defaults to Console Backend for Dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Hosting
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Database Setup

Apply the migrations to set up your local SQLite database.

```bash
python manage.py migrate
```

### 7. Create an Administrator

Create a superuser to access the Django admin panel.

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 8. Run the Server

```bash
python manage.py runserver
```

Open your browser and navigate to:

- **Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🎨 Frontend Development (TailwindCSS)

The project uses TailwindCSS. For development, the standard CDN build is often sufficient, but if you need to recompile styles:

1.  **Install Node dependencies** (if `package.json` exists):
    ```bash
    npm install
    ```
2.  **Run Tailwind Watcher**:
    ```bash
    npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
    ```

---

## 📂 Project Structure

- `core/`: Main app handling events, manifesto, and general page logic.
- `users/`: Member registration, profiles, and authentication.
- `finance/`: Donations/M-Pesa integrations.
- `templates/`: HTML templates (Django + Tailwind classes).
- `static/`: CSS, Images, and JavaScript assets.

---

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

**Roots Party of Kenya** - _Tingiza Mti!_
