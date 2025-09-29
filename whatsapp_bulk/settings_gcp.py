"""
Django settings for whatsapp_bulk project on Google Cloud Platform.
"""

import os
from .settings import *

# GCP-specific settings
DEBUG = False
ALLOWED_HOSTS = [
    'creativeunicorn.com',
    'www.creativeunicorn.com',
    '*.appspot.com',
    '*.googleusercontent.com',
    'localhost',  # For local testing
    '127.0.0.1',
]

# Database configuration for Cloud SQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'whatsapp_bulk'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '/cloudsql/your-project:region:instance-name'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration (using Cloud Storage)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', 'your-whatsapp-bulk-bucket')
GS_DEFAULT_ACL = 'publicRead'
GS_FILE_OVERWRITE = False

# Secret key from environment
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-dev-secret')

# WhatsApp API configuration
WHATSAPP_API = {
    'api_key': os.getenv('WHATSAPP_API_KEY'),
    'base_url': os.getenv('WHATSAPP_BASE_URL', 'https://api.wabot.com/v1'),
}

# Cloudinary configuration
CLOUDINARY = {
    'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.getenv('CLOUDINARY_API_KEY'),
    'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
}

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://creativeunicorn.com',
    'https://www.creativeunicorn.com',
    'https://*.appspot.com',
]

# Session settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
    },
}

# Email configuration (using Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Cache configuration (using Cloud Memorystore Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery configuration for background tasks
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Remove subdirectory settings (not needed for GCP)
FORCE_SCRIPT_NAME = None
USE_X_FORWARDED_HOST = False

# Update static and media URLs (no subdirectory needed)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Update login redirects (no subdirectory needed)
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"
