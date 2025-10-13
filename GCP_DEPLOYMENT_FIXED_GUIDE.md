# 🚀 Fixed GCP Deployment Guide - WhatsApp Bulk Messaging

## ⚠️ Previous Issues Addressed
- Database connection errors
- Missing dependencies
- Region mismatch causing high costs
- Static files not serving correctly
- Environment variable configuration issues

---

## 📋 Prerequisites Checklist

### 1. Google Cloud Setup
- [ ] Google Cloud Platform account with billing enabled
- [ ] Google Cloud SDK installed and authenticated
- [ ] Project ID: `whatsapp-bulk-messaging-473607` (or your project ID)

### 2. Local Environment
- [ ] Python 3.11 installed
- [ ] Git repository cloned
- [ ] All dependencies installed

---

## 🔧 Step 1: Fix Dependencies & Requirements

### 1.1 Update requirements.txt
```txt
# Core Django
Django==4.2.7
gunicorn==21.2.0
whitenoise==6.6.0

# Database
psycopg2-binary==2.9.7

# Environment & Configuration
python-decouple==3.8

# Image Processing
Pillow==10.0.1
cloudinary==1.36.0

# Data Processing
pandas==2.1.4
numpy==1.24.4
openpyxl==3.1.2

# HTTP Requests
requests==2.31.0

# GCP Services
google-cloud-storage==2.10.0
django-storages==1.14.2

# Production Additions
django-cors-headers==4.3.1
django-extensions==3.2.3

# Remove problematic packages for App Engine
# opencv-python==4.6.0.66  # Comment out - causes deployment issues
# paddleocr==2.7.3         # Comment out - causes deployment issues
# paddlepaddle==2.6.2     # Comment out - causes deployment issues
```

### 1.2 Install Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(Django|gunicorn|psycopg2|cloudinary)"
```

---

## 🗄️ Step 2: Database Setup (Fixed)

### 2.1 Create Cloud SQL Instance
```bash
# Set your project
gcloud config set project whatsapp-bulk-messaging-473607

# Create PostgreSQL instance in asia-southeast1
gcloud sql instances create whatsapp-bulk-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-southeast1 \
  --availability-type=ZONAL \
  --storage-auto-increase \
  --storage-size=10GB \
  --root-password=YourSecurePassword123!

# Wait for instance to be ready
gcloud sql instances describe whatsapp-bulk-db
```

### 2.2 Create Database and User
```bash
# Create database
gcloud sql databases create whatsapp_bulk --instance=whatsapp-bulk-db

# Create user (optional - can use postgres user)
gcloud sql users create whatsapp_user \
  --instance=whatsapp-bulk-db \
  --password=WhatsAppUserPass123!
```

### 2.3 Get Connection Details
```bash
# Get connection name
gcloud sql instances describe whatsapp-bulk-db \
  --format="value(connectionName)"

# Note down: whatsapp-bulk-messaging-473607:asia-southeast1:whatsapp-bulk-db
```

---

## ⚙️ Step 3: Fix App Configuration

### 3.1 Create Production Settings
Create `whatsapp_bulk/settings_production.py`:

```python
import os
from .settings import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = [
    'whatsapp-bulk-messaging-473607.appspot.com',
    'creativeunicorn.com',
    'localhost',  # For local testing
]

# Database configuration for Cloud SQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'whatsapp_bulk',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD', 'YourSecurePassword123!'),
        'HOST': f'/cloudsql/{os.getenv("CLOUD_SQL_CONNECTION_NAME", "whatsapp-bulk-messaging-473607:asia-southeast1:whatsapp-bulk-db")}',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'MAX_CONNS': 5,  # Connection pooling
        }
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

# Media files (use Cloud Storage)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'whatsapp-bulk-messaging-473607-media'
GS_DEFAULT_ACL = 'publicRead'

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'your-production-secret-key-change-this')
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# WhatsApp API configuration
WHATSAPP_API = {
    'api_key': os.getenv('WHATSAPP_API_KEY', ''),
    'base_url': 'https://api.wabot.com/v1',
}

# Cloudinary configuration
CLOUDINARY = {
    'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME', ''),
    'api_key': os.getenv('CLOUDINARY_API_KEY', ''),
    'api_secret': os.getenv('CLOUDINARY_API_SECRET', ''),
}

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
}
```

### 3.2 Fix app.yaml (Critical)
```yaml
# Fixed app.yaml for cost optimization
runtime: python311
env: standard

# Environment variables
env_variables:
  DJANGO_SETTINGS_MODULE: "whatsapp_bulk.settings_production"
  SECRET_KEY: "your-production-secret-key-change-this"
  DB_PASSWORD: "YourSecurePassword123!"
  CLOUD_SQL_CONNECTION_NAME: "whatsapp-bulk-messaging-473607:asia-southeast1:whatsapp-bulk-db"
  WHATSAPP_API_KEY: "your-whatsapp-api-key"
  CLOUDINARY_CLOUD_NAME: "your-cloudinary-name"
  CLOUDINARY_API_KEY: "your-cloudinary-key"
  CLOUDINARY_API_SECRET: "your-cloudinary-secret"

# Cloud SQL connection
beta_settings:
  cloud_sql_instances: "whatsapp-bulk-messaging-473607:asia-southeast1:whatsapp-bulk-db"

# Cost-optimized scaling
automatic_scaling:
  min_instances: 0      # Scale to zero when idle
  max_instances: 3      # Cap at 3 instances
  target_cpu_utilization: 0.6
  target_throughput_utilization: 0.6

# Small resources for cost savings
resources:
  cpu: 0.5
  memory_gb: 0.5

# Static files handlers
handlers:
- url: /static
  static_dir: staticfiles
  secure: always

- url: /.*
  script: auto
  secure: always
```

---

## 🗂️ Step 4: Fix Static Files

### 4.1 Collect Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=whatsapp_bulk.settings_production

# Verify static files are created
ls -la staticfiles/
```

### 4.2 Update Django Settings for Static Files
Add to your base `settings.py`:
```python
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'
```

---

## 🚀 Step 5: Deploy to App Engine (Fixed)

### 5.1 Initialize App Engine in Southeast Asia
```bash
# Navigate to your project directory
cd /path/to/your/whatsapp-bulk-message

# Initialize App Engine in asia-southeast1
gcloud app create --region=asia-southeast1

# Verify region
gcloud app describe
```

### 5.2 Deploy Application
```bash
# Deploy the application
gcloud app deploy --quiet

# Check deployment status
gcloud app versions list
```

### 5.3 Run Database Migrations
```bash
# Run migrations on the deployed app
gcloud app deploy --version=migration --no-promote

# Or run migrations via Cloud Shell
gcloud sql connect whatsapp-bulk-db --user=postgres --database=whatsapp_bulk
```

---

## 🗄️ Step 6: Database Migration (Fixed)

### 6.1 Connect to Database
```bash
# Connect to Cloud SQL instance
gcloud sql connect whatsapp-bulk-db --user=postgres --database=whatsapp_bulk
```

### 6.2 Run Migrations
```bash
# In Cloud Shell or local environment with Cloud SQL proxy
python manage.py migrate --settings=whatsapp_bulk.settings_production

# Create superuser
python manage.py createsuperuser --settings=whatsapp_bulk.settings_production
```

### 6.3 Alternative: Run Migrations via App Engine
```bash
# Deploy a temporary version for migrations
gcloud app deploy --version=migration --no-promote

# Run migrations via the deployed app
gcloud app versions migrate migration --service=default
```

---

## 📦 Step 7: Cloud Storage Setup

### 7.1 Create Storage Bucket
```bash
# Create bucket in asia-southeast1
gsutil mb -l asia-southeast1 gs://whatsapp-bulk-messaging-473607-media

# Make bucket public for media files
gsutil iam ch allUsers:objectViewer gs://whatsapp-bulk-messaging-473607-media

# Set lifecycle policy for cost optimization
gsutil lifecycle set lifecycle.json gs://whatsapp-bulk-messaging-473607-media
```

### 7.2 Create Lifecycle Policy
Create `lifecycle.json`:
```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90}
    }
  ]
}
```

---

## 🔧 Step 8: Fix Common Deployment Issues

### 8.1 Handle Import Errors
Add to your `main.py` or `wsgi.py`:
```python
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 8.2 Fix Static Files Issues
```bash
# Ensure static files are collected
python manage.py collectstatic --noinput

# Check if staticfiles directory exists
ls -la staticfiles/

# Verify app.yaml static_dir matches
grep -A 2 "static_dir" app.yaml
```

### 8.3 Fix Database Connection Issues
```bash
# Test database connection
gcloud sql connect whatsapp-bulk-db --user=postgres

# Check if database exists
\list

# Create database if needed
CREATE DATABASE whatsapp_bulk;
```

---

## 🧪 Step 9: Testing & Verification

### 9.1 Test Deployment
```bash
# Get your app URL
gcloud app browse

# Test static files
curl https://whatsapp-bulk-messaging-473607.appspot.com/static/admin/css/base.css

# Test database connection
curl https://whatsapp-bulk-messaging-473607.appspot.com/admin/
```

### 9.2 Check Logs
```bash
# View recent logs
gcloud app logs tail -s default

# View specific error logs
gcloud app logs read --service=default --severity=ERROR
```

### 9.3 Verify All Services
```bash
# Check App Engine
gcloud app describe

# Check Cloud SQL
gcloud sql instances list

# Check Storage
gsutil ls gs://whatsapp-bulk-messaging-473607-media
```

---

## 🚨 Step 10: Troubleshooting Common Issues

### Issue 1: Database Connection Error
```bash
# Check Cloud SQL instance status
gcloud sql instances describe whatsapp-bulk-db

# Test connection
gcloud sql connect whatsapp-bulk-db --user=postgres
```

### Issue 2: Static Files Not Loading
```bash
# Re-collect static files
python manage.py collectstatic --noinput --clear

# Check app.yaml handlers
grep -A 5 "handlers:" app.yaml
```

### Issue 3: 500 Internal Server Error
```bash
# Check logs for specific errors
gcloud app logs read --service=default --severity=ERROR

# Check environment variables
gcloud app versions describe VERSION_ID --service=default
```

### Issue 4: Import Errors
```bash
# Check requirements.txt
pip install -r requirements.txt

# Remove problematic packages
pip uninstall opencv-python paddleocr paddlepaddle
```

---

## 💰 Step 11: Cost Optimization Verification

### 11.1 Verify Region Alignment
```bash
# Check App Engine region
gcloud app describe | grep locationId

# Check Cloud SQL region
gcloud sql instances describe whatsapp-bulk-db | grep region

# Check Storage bucket region
gsutil ls -L -b gs://whatsapp-bulk-messaging-473607-media | grep Location
```

### 11.2 Set Up Billing Alerts
```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="WhatsApp App Budget" \
  --budget-amount=200 \
  --threshold-rule-percentages=0.5,0.8,1.0
```

---

## ✅ Final Verification Checklist

- [ ] App Engine deployed in `asia-southeast1`
- [ ] Cloud SQL instance in `asia-southeast1`
- [ ] Storage bucket in `asia-southeast1`
- [ ] Database migrations completed
- [ ] Static files serving correctly
- [ ] Environment variables configured
- [ ] Cost optimization settings applied
- [ ] Billing alerts configured

---

## 🎯 Expected Results

After following this guide:
- **Monthly costs reduced** from RM 1,500+ to RM 200-400
- **All services in Southeast Asia** for optimal performance
- **Database connection issues resolved**
- **Static files serving correctly**
- **Production-ready deployment**

---

## 📞 Support Commands

```bash
# Quick health check
gcloud app describe && gcloud sql instances list && gsutil ls

# View all logs
gcloud app logs tail -s default

# Check costs
gcloud billing budgets list
```

Your WhatsApp Bulk Messaging app is now properly deployed and optimized for cost and performance! 🎉
