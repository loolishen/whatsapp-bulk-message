"""
Django settings for whatsapp_bulk project.
Cloud Run–friendly, with sane defaults for local dev.
"""

from pathlib import Path
import os

try:
    import dj_database_url  # optional, only used if DATABASE_URL is set
except Exception:
    dj_database_url = None


# --------------------------------------------------------------------------------------
# Core paths
# --------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------------
# Flags & environment
# --------------------------------------------------------------------------------------
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Secret key from env in prod; fall back for dev only
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-secret")

# When running on Cloud Run, Google sets K_SERVICE
RUNNING_IN_CLOUD_RUN = bool(os.getenv("K_SERVICE"))

# --------------------------------------------------------------------------------------
# Hosts & CSRF
# --------------------------------------------------------------------------------------
# Comma-separated list in env, or sensible defaults
# Simple and safe:
ALLOWED_HOSTS = ["creativeunicorn.com", "www.creativeunicorn.com", "localhost", "127.0.0.1"]

# You’re serving under a subpath:
FORCE_SCRIPT_NAME = "/whatsapp-crm"
USE_X_FORWARDED_HOST = True

CSRF_TRUSTED_ORIGINS = [
    "https://creativeunicorn.com",
    "https://www.creativeunicorn.com",
]

# If you have a custom domain, add it via env (comma-separated)
_EXTRA_CSRF = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if _EXTRA_CSRF.strip():
    CSRF_TRUSTED_ORIGINS.extend([v.strip() for v in _EXTRA_CSRF.split(",") if v.strip()])

# Cloud Run is HTTPS-terminated at the proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# --------------------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Whitenoise helper must come before staticfiles to disable dev static handler
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "messaging",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise must be right after SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "whatsapp_bulk.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "whatsapp_bulk.wsgi.application"

# --------------------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------------------
# Prefer DATABASE_URL if provided (Cloud SQL, Postgres, etc.)
if os.getenv("DATABASE_URL") and dj_database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=False,
        )
    }
else:
    # SQLite for dev & demo. In Cloud Run, use /tmp since the root FS is read-only.
    sqlite_name = "/tmp/db.sqlite3" if (RUNNING_IN_CLOUD_RUN and not DEBUG) else str(BASE_DIR / "db.sqlite3")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_name,
        }
    }

# --------------------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------------------
# I18N
# --------------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------------------
# Static & Media
# --------------------------------------------------------------------------------------
STATIC_URL = "/whatsapp-crm/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Optionally serve extra local static during dev
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# WhiteNoise compressed manifest storage in prod
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/whatsapp-crm/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------------------
# Auth redirects
# --------------------------------------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# --------------------------------------------------------------------------------------
# WhatsApp / Cloudinary – read from env (no secrets in code)
# --------------------------------------------------------------------------------------
WHATSAPP_API = {
    'ACCESS_TOKEN': '68a0a10422130',
    'BASE_URL': 'https://app.wabot.my/api',
    'DEFAULT_INSTANCE_ID': '68A0A11A89A8D',  # Static Instance ID - Do not change
    'DEFAULT_TEST_NUMBER': '+60162107682',
}

# Cloudinary Configuration for Image Hosting
CLOUDINARY = {
    'CLOUD_NAME': 'dzbje38xw',
    'API_KEY': '645993869662484',
    'API_SECRET': '43OPTPwCt8cWEim-L9GHtwmj7_w',
    'SECURE': True,
    'FOLDER': 'whatsapp_bulk',  # Default folder for uploads
}