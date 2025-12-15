# Google App Engine Standard - Django Deployment Guide

## 🎯 Overview
Complete guide for deploying Django applications to Google App Engine Standard with Cloud SQL PostgreSQL.

---

## 📋 Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Cloud SQL PostgreSQL** instance created
3. **gcloud CLI** installed and authenticated
4. **Python 3.11** installed locally

---

## 🏗️ Project Structure Requirements

For App Engine Standard, your project must have this structure:

```
project-root/
├── app.yaml                    # App Engine configuration
├── main.py                     # Entry point (imports WSGI app)
├── wsgi.py                     # WSGI application
├── settings_production.py      # Production Django settings
├── manage.py                   # Django management script
├── urls.py                     # URL configuration
├── requirements.txt            # Python dependencies
├── .gcloudignore              # Files to exclude from deployment
├── migrate_db.py              # Database migration script
├── messaging/                  # Your Django app
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
└── templates/                  # HTML templates
```

### ⚠️ CRITICAL: App Engine Standard expects a **FLAT structure**
- No nested `project_name/project_name/` directories
- All Django files should be at the root level
- `manage.py`, `wsgi.py`, `urls.py` should be siblings, not nested

---

## 📝 Essential Configuration Files

### 1. `app.yaml`

```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT main:application

instance_class: F1

env_variables:
  DJANGO_SETTINGS_MODULE: "settings_production"
  SECRET_KEY: "your-secret-key-here"
  CLOUD_SQL_CONNECTION_NAME: "project-id:region:instance-name"

handlers:
- url: /static
  static_dir: static/
  
- url: /.*
  script: auto
  secure: always
  redirect_http_response_code: 301

automatic_scaling:
  min_idle_instances: 0
  max_idle_instances: 1
  min_pending_latency: 30ms
  max_pending_latency: automatic
```

### 2. `main.py`

```python
#!/usr/bin/env python
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Import and expose Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 3. `wsgi.py`

```python
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Import and expose Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 4. `settings_production.py`

```python
from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent  # Note: .parent not .parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-fallback-secret-key')
DEBUG = False
ALLOWED_HOSTS = ['*']

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'messaging',  # Your custom app
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

# URLs
ROOT_URLCONF = 'urls'  # Note: 'urls' not 'project_name.urls'

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

WSGI_APPLICATION = 'main.application'

# Database - Cloud SQL PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': '/cloudsql/project-id:region:instance-name',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = 'static'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
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
}
```

### 5. `.gcloudignore` (MINIMAL VERSION)

```
# Git
.gcloudignore
.git/
.gitignore

# Environment
.env
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*.egg-info/

# Django
*.sqlite3
*.log
static/
staticfiles/
media/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log
```

### 6. `requirements.txt`

```
Django==5.0.6
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

### 7. `migrate_db.py`

```python
#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser

print("=" * 70)
print("DATABASE MIGRATION FOR GCP")
print("=" * 70)

try:
    print("\n1. Running database migrations...")
    call_command('migrate', '--noinput', verbosity=2)
    print("✅ All migrations applied successfully!")
    
    print("\n2. Setting up production user...")
    User = get_user_model()
    
    tenant, created = Tenant.objects.get_or_create(
        name='Demo Tenant',
        defaults={'plan': 'pro'}
    )
    print(f"✅ Tenant: {tenant.name} (ID: {tenant.tenant_id})")
    
    user, user_created = User.objects.get_or_create(
        username='tenant',
        defaults={'email': 'tenant@example.com', 'is_staff': True, 'is_superuser': True}
    )
    user.set_password('Tenant123!')
    user.is_active = True
    user.save()
    print(f"✅ User: {user.username}")
    
    tenant_user, _ = TenantUser.objects.get_or_create(
        user=user,
        defaults={'tenant': tenant, 'role': 'owner'}
    )
    print(f"✅ User linked to tenant")
    
    print("\n" + "=" * 70)
    print("✅ DATABASE SETUP COMPLETED!")
    print("=" * 70)
    print("\n🔐 Login: https://your-project-id.as.r.appspot.com/login/")
    print("   Username: tenant | Password: Tenant123!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

---

## 🚀 Deployment Process

### Step 1: Deploy Application

```bash
# From your local project directory (Windows)
cmd /c "gcloud app deploy --project=your-project-id"
```

### Step 2: Run Database Migrations (in Google Cloud Shell)

```bash
# 1. Upload your source code to Cloud Storage
cd ~/
rm -rf app-full 2>/dev/null
mkdir app-full && cd app-full

# 2. From your LOCAL machine, upload the code
gsutil -m rsync -r -x ".git/*|__pycache__/*|*.pyc|venv/*" . gs://your-bucket/source/

# 3. In Cloud Shell, download the code
gsutil -m rsync -r gs://your-bucket/source/ ~/app-full/

# 4. Upload migrate_db.py
gsutil cp migrate_db.py gs://your-bucket/
gsutil cp gs://your-bucket/migrate_db.py ~/app-full/

# 5. Start Cloud SQL Proxy
cloud-sql-proxy project-id:region:instance-name --port=5432 &
sleep 5

# 6. Install dependencies
pip3 install --user django psycopg2-binary

# 7. Run migrations
cd ~/app-full
python3 migrate_db.py

# 8. Stop proxy
pkill cloud-sql-proxy
```

---

## 🔧 Troubleshooting Guide

### Error: `ModuleNotFoundError: No module named 'whatsapp_bulk'`

**Cause:** Project structure is nested (not flat)

**Solution:**
1. Flatten your project structure
2. Move all files from `project_name/project_name/` to root
3. Update `settings_production.py`:
   - Change `BASE_DIR = Path(__file__).resolve().parent.parent` to `parent`
   - Change `ROOT_URLCONF = 'whatsapp_bulk.urls'` to `'urls'`
4. Update `manage.py` and `wsgi.py` settings module references

---

### Error: `502 Bad Gateway`

**Cause:** App Engine can't find the entry point or imports are failing

**Check:**
1. `main.py` exists at root level
2. `app.yaml` has correct `entrypoint: gunicorn -b :$PORT main:application`
3. Check deployment logs: `gcloud app logs read --limit=50`

---

### Error: `500 Internal Server Error` (after successful deployment)

**Cause:** Database tables don't exist or migrations not run

**Solution:**
1. Run migrations in Cloud Shell (see Step 2 above)
2. Check logs: `gcloud app logs read --limit=50 | grep -i error`

---

### Error: `relation "table_name" does not exist`

**Cause:** Django migrations not applied to Cloud SQL database

**Solution:**
1. Connect to Cloud SQL via Cloud SQL Proxy
2. Run `python3 migrate_db.py`

---

### Error: `DuplicateTable` during migrations

**Cause:** Tables exist but Django doesn't have migration history

**Solution - NUCLEAR OPTION:**

```bash
# In Cloud Shell with proxy running
python3 << 'EOF'
import psycopg2

conn = psycopg2.connect(
    host='127.0.0.1',
    port=5432,
    database='your_db',
    user='your_user',
    password='your_password'
)
cur = conn.cursor()

# Drop all custom app tables
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'messaging_%';")
tables = [row[0] for row in cur.fetchall()]

for table in tables:
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    print(f"Dropped: {table}")

conn.commit()

# Clear migration history
cur.execute("DELETE FROM django_migrations WHERE app = 'messaging';")
conn.commit()

cur.close()
conn.close()
print("✅ Ready for fresh migrations")
EOF

# Now run migrations
python3 migrate_db.py
```

---

### Error: `connection to server at "X.X.X.X", port 5432 failed: Connection timed out`

**Cause:** Direct IP connection timeout (5-minute allowlist expired)

**Solution:** Always use Cloud SQL Proxy instead of direct connections

```bash
# Start proxy
cloud-sql-proxy project-id:region:instance-name --port=5432 &
sleep 3

# Then connect to 127.0.0.1:5432
```

---

### Error: `psycopg2.OperationalError: server does not support SSL, but SSL was required`

**Cause:** `sslmode: require` in settings but using Cloud SQL Proxy (localhost)

**Solution:** Remove SSL requirement from database settings when using proxy:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',  # Proxy connection
        'PORT': '5432',
        # Don't specify OPTIONS with sslmode for proxy connections
    }
}
```

---

## 📊 Verification Checklist

After deployment, verify:

- [ ] App deployed: `gcloud app browse`
- [ ] No 502 errors (check logs: `gcloud app logs read --limit=20`)
- [ ] Database tables exist (connect via Cloud Shell + proxy)
- [ ] User can login
- [ ] Dashboard loads after login
- [ ] No "relation does not exist" errors

---

## 🎯 Quick Deployment Checklist

**Before deploying:**
- [ ] Project structure is flat (not nested)
- [ ] `main.py` exists at root
- [ ] `app.yaml` configured correctly
- [ ] `.gcloudignore` is minimal
- [ ] `settings_production.py` uses correct `BASE_DIR` and `ROOT_URLCONF`
- [ ] Database credentials in `app.yaml` env_variables
- [ ] `requirements.txt` includes `gunicorn`, `psycopg2-binary`

**After deploying:**
- [ ] Run `migrate_db.py` in Cloud Shell
- [ ] Test login at your app URL
- [ ] Check logs for errors

---

## 📞 Common Commands

```bash
# Deploy app
gcloud app deploy --project=PROJECT_ID

# View logs
gcloud app logs read --limit=50 --project=PROJECT_ID

# Browse app
gcloud app browse --project=PROJECT_ID

# Connect to Cloud SQL (Cloud Shell)
cloud-sql-proxy PROJECT_ID:REGION:INSTANCE --port=5432 &

# Stop proxy
pkill cloud-sql-proxy

# Upload file to Cloud Storage
gsutil cp filename.py gs://bucket-name/

# Download from Cloud Storage
gsutil cp gs://bucket-name/filename.py ./

# Sync directory
gsutil -m rsync -r local-dir/ gs://bucket-name/remote-dir/
```

---

## 🔐 Security Notes

1. **Never commit secrets** to Git
2. Use **Environment Variables** in `app.yaml` for sensitive data
3. Set `DEBUG = False` in production
4. Use strong `SECRET_KEY`
5. Configure `ALLOWED_HOSTS` appropriately
6. Use **HTTPS only** (already configured in `app.yaml`)

---

## 📚 Additional Resources

- [App Engine Standard Python Runtime](https://cloud.google.com/appengine/docs/standard/python3)
- [Django on App Engine](https://cloud.google.com/python/django/appengine)
- [Cloud SQL Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy)
- [Troubleshooting App Engine](https://cloud.google.com/appengine/docs/standard/python3/testing-and-deploying-your-app)

---

**Last Updated:** December 2025
**Tested with:** Django 5.0.6, Python 3.11, App Engine Standard




