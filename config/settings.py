import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Fix for JFIF images on Windows
import mimetypes
mimetypes.add_type("image/jpeg", ".jfif", True)

# Google Cloud Logging (Production Only)
def setup_cloud_logging():
    if os.environ.get('GOOGLE_CLOUD_PROJECT') and not os.environ.get('DEBUG', 'False') == 'True':
        try:
            import google.cloud.logging
            client = google.cloud.logging.Client()
            client.setup_logging()
            print("✅ Google Cloud Logging configured")
        except Exception as e:
            print(f"⚠️ Google Cloud Logging setup failed: {e}")

setup_cloud_logging()




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# In production, SECRET_KEY must be set via environment variable
_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    if os.environ.get('DEBUG', 'False') == 'True':
        # Only allow insecure key in explicit debug mode
        _secret_key = 'django-insecure-dev-only-key-do-not-use-in-production'
    else:
        raise ValueError("SECRET_KEY environment variable must be set in production!")
SECRET_KEY = _secret_key

# SECURITY WARNING: don't run with debug turned on in production!
# Defaults to False for safety - must explicitly set DEBUG=True for development
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS must be configured properly
_allowed_hosts = os.environ.get('ALLOWED_HOSTS')
if not _allowed_hosts:
    if DEBUG:
        ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.localhost']
    else:
        raise ValueError("ALLOWED_HOSTS environment variable must be set in production!")
else:
    ALLOWED_HOSTS = _allowed_hosts.split(',')

# CSRF Trusted Origins
_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS')
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = _csrf_origins.split(',')
else:
    # Default fallback for development
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8080',
        'http://localhost:8080',
    ]

# Site Base URL (Used for absolute links and embeds)
SITE_BASE_URL = os.environ.get('SITE_BASE_URL', 'http://127.0.0.1:8080' if DEBUG else 'https://rootsparty.co.ke')


# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Add whitenoise
    'django.contrib.staticfiles',
    
    # Third-party
    'django_htmx',
    'django_ratelimit',
    'easy_thumbnails',
    'image_cropping',
    'django_ckeditor_5',

    # Local
    'core',
    'users',
    'finance',
    'aspirants',
    'commerce',
    'rest_framework',
    'django_filters',
    'drf_spectacular',  # API documentation
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
}

# DRF Spectacular Settings (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Roots Party API',
    'DESCRIPTION': 'API documentation for the Roots Party of Kenya platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# Image Cropping Settings
from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

# ... (omitted middleware) ...

SILENCED_SYSTEM_CHECKS = [
    'django_ratelimit.E003',
    'django_ratelimit.W001',
]

# Ratelimit Settings
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_ENABLE = True

# Cache Configuration
if os.environ.get('REDIS_URL'):
    # Production: Use Redis for high-performance caching
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'IGNORE_EXCEPTIONS': True,  # Don't crash if Redis is down
            },
            'KEY_PREFIX': 'roots_party',
            'VERSION': 2,
            'TIMEOUT': 300,  # Default 5 minutes
        }
    }
    
    # Use Redis for session storage (faster than DB)
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    
elif DEBUG:
    # Development: Use in-memory cache (or Redis if available via docker-compose)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'VERSION': 2,
        }
    }
else:
    # Fallback: Dummy cache (no caching) if Redis unavailable
    # This is safer than database cache which requires table creation
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Proxy & Security Settings (Critical for Cloud Run + Nginx)

# Proxy & Security Settings (Critical for Cloud Run + Nginx)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

if not DEBUG:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True
    # HSTS Settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Secure Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Content Security Policy (CSP) Configuration
if not DEBUG:
    # Strict CSP for production
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com")
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.tailwindcss.com")
    CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
    CSP_IMG_SRC = ("'self'", "data:", "https://storage.googleapis.com")
    CSP_CONNECT_SRC = ("'self'",)
    CSP_FRAME_ANCESTORS = ("'self'",)
    CSP_BASE_URI = ("'self'",)
    CSP_FORM_ACTION = ("'self'",)
else:
    # Relaxed CSP for development
    CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.tailwindcss.com")
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.tailwindcss.com")
    CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
    CSP_IMG_SRC = ("'self'", "data:", "https://storage.googleapis.com")



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Enable Gzip Compression
    'csp.middleware.CSPMiddleware',  # Content Security Policy
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'core.middleware.CacheStatsMiddleware',  # Cache performance monitoring
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
                'core.context_processors.site_settings',  # Make site settings available globally
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import dj_database_url

# ... existing code ...

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Use DATABASE_URL env var if set (e.g. Cloud Run), otherwise fall back to discrete vars or sqlite
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
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

USE_I18N = False

USE_TZ = True





# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# STORAGES Configuration (Django 4.2+)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Use standard static storage in development/tests to avoid manifest errors
if DEBUG:
    STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"

# WhiteNoise Configuration for Performance
WHITENOISE_COMPRESS_OFFLINE = True  # Pre-compress static files
WHITENOISE_COMPRESS_OFFLINE_MANIFEST = "staticfiles.json"
WHITENOISE_USE_FINDERS = DEBUG  # Only use finders in development
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files (immutable)
WHITENOISE_ALLOW_ALL_ORIGINS = False  # Security: only allow same-origin
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br', 'swf', 'flv', 'woff', 'woff2')
WHITENOISE_ADD_HEADERS_FUNCTION = None  # Use default headers


# Persistent Storage (Google Cloud Storage) for production
GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
if GS_BUCKET_NAME:
    STORAGES["default"]["BACKEND"] = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_ACL = None  # Use bucket policy
    GS_QUERYSTRING_AUTH = False # Disable signed URLs (public bucket)
    # Ensure media is served through the bucket
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'

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

# Location APIs
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Unfold Admin Configuration
from django.urls import reverse_lazy
from django.templatetags.static import static

UNFOLD = {
    "SITE_TITLE": "ROOTS PARTY",
    "SITE_HEADER": "ROOTS PARTY",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "core.views.dashboard_callback",
    
    # Site Logo
    "SITE_LOGO": lambda request: static("images/roots_party_logo.png"),
    
    # Theme: Roots Red/Black/White
    "COLORS": {
        "primary": {
            "50": "254 242 242",
            "100": "254 226 226",
            "200": "254 202 202",
            "300": "252 165 165",
            "400": "248 113 113",
            "500": "239 68 68",    # Base Red
            "600": "220 38 38",
            "700": "185 28 28",
            "800": "153 27 27",
            "900": "127 29 29",
            "950": "69 10 10",
        },
    },
    
    "THEME": "dark",
    
    # Custom CSS
    "STYLES": [
        lambda request: static("css/admin_custom.css"),
    ],
    
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "View Site",
                        "icon": "public",
                        "link": "/",
                        "new_tab": True,
                    },
                    {
                        "title": "Analytics",
                        "icon": "analytics",
                        "link": "/analytics/",
                    },
                ],
            },
            {
                "title": "Content Management",
                "separator": True,
                "items": [
                    {
                        "title": "Blog Posts",
                        "icon": "article",
                        "link": reverse_lazy("admin:core_blogpost_changelist"),
                    },
                    {
                        "title": "Page Content",
                        "icon": "description",
                        "link": reverse_lazy("admin:core_pagecontent_changelist"),
                    },
                    {
                        "title": "Gallery",
                        "icon": "collections",
                        "link": reverse_lazy("admin:core_gallerypost_changelist"),
                    },
                    {
                        "title": "Manifesto",
                        "icon": "menu_book",
                        "link": reverse_lazy("admin:core_manifestoitem_changelist"),
                    },
                    {
                        "title": "Home Videos",
                        "icon": "videocam",
                        "link": reverse_lazy("admin:core_homevideo_changelist"),
                    },
                     {
                        "title": "Carousel Images",
                        "icon": "view_carousel",
                        "link": reverse_lazy("admin:core_carouselimage_changelist"),
                    },
                    {
                        "title": "Floating Images",
                        "icon": "image",
                        "link": reverse_lazy("admin:core_floatingimage_changelist"),
                    },
                ],
            },
            {
                "title": "People & Party",
                "separator": True,
                "items": [
                    {
                        "title": "Leaders",
                        "icon": "groups",
                        "link": reverse_lazy("admin:core_leader_changelist"),
                    },
                     {
                        "title": "Leadership Roles",
                        "icon": "badge",
                        "link": reverse_lazy("admin:aspirants_leadershiprole_changelist"),
                    },
                    {
                        "title": "Aspirants",
                        "icon": "person_search",
                        "link": reverse_lazy("admin:aspirants_aspirant_changelist"),
                    },
                    {
                        "title": "Aspirant Applications",
                        "icon": "how_to_reg",
                        "link": reverse_lazy("admin:aspirants_aspirantregistration_changelist"),
                    },
                    {
                        "title": "Members",
                        "icon": "person",
                        "link": reverse_lazy("admin:users_member_changelist"),
                    },
                    {
                        "title": "Coordinators (Applicants)",
                        "icon": "assignment_ind",
                        "link": reverse_lazy("admin:users_coordinatorapplicant_changelist"),
                    },
                    {
                        "title": "Constituencies",
                        "icon": "map",
                        "link": reverse_lazy("admin:core_constituency_changelist"),
                    },
                    {
                        "title": "Counties",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:core_county_changelist"),
                    },
                ],
            },
             {
                "title": "Operations & Commerce",
                "separator": True,
                "items": [
                    {
                        "title": "Events",
                        "icon": "event",
                        "link": reverse_lazy("admin:core_event_changelist"),
                    },
                    {
                        "title": "Gate Passes",
                        "icon": "qr_code",
                        "link": reverse_lazy("admin:core_gatepass_changelist"),
                    },
                    {
                        "title": "Vendors",
                        "icon": "store",
                        "link": reverse_lazy("admin:commerce_vendor_changelist"),
                    },
                    {
                        "title": "Products",
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:commerce_product_changelist"),
                    },
                    {
                         "title": "Donations",
                         "icon": "paid",
                         "link": reverse_lazy("admin:finance_donation_changelist"),
                    },
                ],
            },
            {
                "title": "System & Settings",
                "separator": True,
                "items": [
                    {
                        "title": "Site Settings & Logo",
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_sitesettings_change", args=[1]),
                    },
                    {
                        "title": "Users & Groups",
                        "icon": "settings_accessibility",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                     {
                        "title": "Contact Messages",
                        "icon": "mail",
                        "link": reverse_lazy("admin:core_contactmessage_changelist"),
                    },
                    {
                        "title": "Newsletter Subscribers",
                        "icon": "forward_to_inbox",
                        "link": reverse_lazy("admin:core_newslettersubscriber_changelist"),
                    },
                    {
                        "title": "Resources (Docs)",
                        "icon": "folder",
                        "link": reverse_lazy("admin:core_resource_changelist"),
                    },
                ],
            },
        ],
    },
}

# CKEditor 5 Configuration
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                   'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignCenter', 'imageStyle:alignRight', 'imageStyle:full', 'imageStyle:side',
                        '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignCenter',
                'alignRight',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': 'hsl(0, 0%, 0%)',
                'backgroundColors': 'hsl(0, 0%, 0%)',
            },
            'tableCellProperties': {
                'borderColors': 'hsl(0, 0%, 0%)',
                'backgroundColors': 'hsl(0, 0%, 0%)',
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
