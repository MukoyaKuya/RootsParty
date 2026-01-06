import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-bs0uensq%3k++r0epml1$6csr=q56nq8=@jpl-dv^hngh5^=5+')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Add whitenoise
    'django.contrib.staticfiles',
    
    # Third-party
    'django_htmx',

    # Local
    'core',
    'users',
    'finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Use PostgreSQL if configured, else default to SQLite for dev
DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3')
DB_NAME = os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3')
DB_USER = os.environ.get('DB_USER', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', '')
DB_PORT = os.environ.get('DB_PORT', '')

if DB_ENGINE == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Persistent connections (e.g., 60s) to reuse DB connections between requests
# This is crucial for high-concurrency environments to reduce overhead.
DATABASES['default']['CONN_MAX_AGE'] = 60


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allow embedding in frames (required for PDF viewer)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Roots Party <info@rootsparty.co.ke>')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'info@rootsparty.co.ke')

# Jazzmin Configuration
# Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "ROOTS PARTY",
    "site_header": "ROOTS PARTY",
    "site_brand": "ROOTS ADMIN",
    "welcome_sign": "Welcome to the Roots Party Command Center",
    "copyright": "Roots Party of Kenya",
    "search_model": ["core.Leader", "users.Member"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"name": "Analytics Dashboard", "url": "/analytics/", "new_window": False},
    ],
    "show_ui_builder": False,
    
    # Custom CSS
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Leader": "fas fa-user-tie",
        "core.Event": "fas fa-calendar-alt",
        "core.Product": "fas fa-tshirt",
        "core.ManifestoItem": "fas fa-scroll",
        "core.GalleryPost": "fas fa-images",
        "core.ContactMessage": "fas fa-envelope",
        "core.BlogPost": "fas fa-newspaper",
        "core.County": "fas fa-map-marker-alt",
        "users.Member": "fas fa-users",
        "finance.Donation": "fas fa-hand-holding-usd",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-danger",
    "accent": "accent-danger",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-danger",
    "sidebar_nav_small_text": False,
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-danger",
        "secondary": "btn-outline-danger",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
