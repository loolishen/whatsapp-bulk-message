"""
Production settings for WhatsApp Bulk Messaging
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# FLATTENED STRUCTURE - settings are now in root, so BASE_DIR is just parent
BASE_DIR = Path(__file__).resolve().parent

# Security settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-this-in-production')
ALLOWED_HOSTS = [
    '*.appspot.com',
    'whatsapp-bulk-messaging-480620.as.r.appspot.com',
    'localhost',
    '127.0.0.1',
    'testserver',  # For Django tests
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'messaging.apps.MessagingConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database - Use PostgreSQL for production
# Auto-detect environment: Cloud Shell (TCP) vs App Engine (Unix socket)
if os.getenv('GAE_ENV', '').startswith('standard'):
    # Running on App Engine - use Unix socket
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'whatsapp_bulk',
            'USER': 'whatsapp_user',
            'PASSWORD': 'P@##w0rd',
            'HOST': '/cloudsql/whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db',
            'PORT': '5432',
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Running in Cloud Shell or locally - use TCP via Cloud SQL Proxy
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'whatsapp_bulk',
            'USER': 'whatsapp_user',
            'PASSWORD': 'P@##w0rd',
            'HOST': '127.0.0.1',  # Cloud SQL Proxy on localhost
            'PORT': '5432',
        }
    }

# TEMPORARY: If Cloud SQL connection fails, uncomment below and comment out above
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
# Password validation
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
LANGUAGE_CODE = 'en-us'
# App is Malaysia-focused; contest start/end inputs come from browser `datetime-local`
# (no timezone info). Use MYT so "active now" checks behave as users expect.
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs - Updated to match the actual URL structure
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# WhatsApp API Configuration
WHATSAPP_API = {
    'ACCESS_TOKEN': '68a0a10422130',
    'BASE_URL': 'https://app.wabot.my/api',
    'DEFAULT_INSTANCE_ID': '68A0A11A89A8D',
    'DEFAULT_TEST_NUMBER': '+60162107682',
}

# Cloudinary Configuration
CLOUDINARY = {
    'CLOUD_NAME': 'dzbje38xw',
    'API_KEY': '645993869662484',
    'API_SECRET': '43OPTPwCt8cWEim-L9GHtwmj7_w',
    'SECURE': True,
    'FOLDER': 'whatsapp_bulk',
}

# WABot.my Configuration
WABOT_WEBHOOK_TOKEN = os.environ.get('WABOT_WEBHOOK_TOKEN', '6bb47e635cd7649c10a503e7032ecff4')
WABOT_PHONE_NUMBER = os.environ.get('WABOT_PHONE_NUMBER', '60162107682')
WABOT_API_URL = os.environ.get('WABOT_API_URL', 'https://app.wabot.my/api')
WABOT_API_TOKEN = os.environ.get('WABOT_API_TOKEN', '')  # Get this from WABot dashboard

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CSRF settings for App Engine
CSRF_TRUSTED_ORIGINS = [
    'https://whatsapp-bulk-messaging-480620.as.r.appspot.com',
    'https://whatsapp-bulk-messaging-480620.appspot.com',
    'https://*.appspot.com',
]

# Additional CSRF settings for production
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access for AJAX
CSRF_COOKIE_SAMESITE = 'Lax'  # More permissive for App Engine

# Logging configuration for App Engine
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'messaging': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'messaging.whatsapp_webhook': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Logging configuration for App Engine
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'messaging': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'messaging.whatsapp_webhook': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
