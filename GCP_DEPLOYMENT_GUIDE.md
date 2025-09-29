# 🚀 Complete GCP Deployment Guide for WhatsApp Bulk Messaging

## Prerequisites
- Google Cloud Platform account
- Google Cloud SDK installed locally
- Your domain name (optional)
- GitHub repository (already set up)

## Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Project name: `whatsapp-bulk-messaging`
4. Click "Create"

### 1.2 Enable Required APIs
```bash
# Enable App Engine API
gcloud services enable appengine.googleapis.com

# Enable Cloud SQL API
gcloud services enable sqladmin.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com
```

## Step 2: Configure Your Application

### 2.1 Update app.yaml
Your `app.yaml` is already configured! It's perfect for GCP deployment.

### 2.2 Create Cloud SQL Database
1. Go to Cloud SQL in GCP Console
2. Click "Create Instance"
3. Choose "PostgreSQL" (recommended) or "MySQL"
4. Instance ID: `whatsapp-bulk-db`
5. Set root password
6. Choose region close to your users
7. Click "Create"

### 2.3 Get Database Connection Details
After creating the database:
1. Click on your database instance
2. Go to "Connections" tab
3. Note down:
   - **Connection name**: `your-project:region:instance-name`
   - **Public IP**: `xxx.xxx.xxx.xxx`
   - **Private IP**: `10.x.x.x` (if using VPC)

## Step 3: Configure Environment Variables

### 3.1 Using Secret Manager (Recommended)
```bash
# Create secrets
gcloud secrets create django-secret-key --data-file=- <<< "your-super-secret-key-here"
gcloud secrets create database-password --data-file=- <<< "your-db-password"
gcloud secrets create whatsapp-api-key --data-file=- <<< "your-whatsapp-api-key"
gcloud secrets create cloudinary-api-key --data-file=- <<< "your-cloudinary-api-key"
```

### 3.2 Update settings.py for GCP
Create a new file `whatsapp_bulk/settings_gcp.py`:

```python
import os
from .settings import *

# GCP-specific settings
DEBUG = False
ALLOWED_HOSTS = ['your-app-id.appspot.com', 'your-domain.com']

# Database configuration for Cloud SQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'whatsapp_bulk',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': f'/cloudsql/{os.getenv("CLOUD_SQL_CONNECTION_NAME")}',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = 'static'

# Media files (use Cloud Storage)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'your-bucket-name'
GS_DEFAULT_ACL = 'publicRead'

# Secret key from Secret Manager
SECRET_KEY = os.getenv('SECRET_KEY')

# WhatsApp API configuration
WHATSAPP_API = {
    'api_key': os.getenv('WHATSAPP_API_KEY'),
    'base_url': 'https://api.wabot.com/v1',
}

# Cloudinary configuration
CLOUDINARY = {
    'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.getenv('CLOUDINARY_API_KEY'),
    'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
}
```

## Step 4: Update app.yaml for GCP

Update your existing `app.yaml`:

```yaml
runtime: python39

env_variables:
  DJANGO_SETTINGS_MODULE: whatsapp_bulk.settings_gcp
  SECRET_KEY: "your-secret-key-here"
  DB_PASSWORD: "your-db-password"
  CLOUD_SQL_CONNECTION_NAME: "your-project:region:instance-name"
  WHATSAPP_API_KEY: "your-whatsapp-api-key"
  CLOUDINARY_CLOUD_NAME: "your-cloudinary-name"
  CLOUDINARY_API_KEY: "your-cloudinary-key"
  CLOUDINARY_API_SECRET: "your-cloudinary-secret"

# Cloud SQL connection
beta_settings:
  cloud_sql_instances: "your-project:region:instance-name"

# Automatic scaling
automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

# Static files
handlers:
- url: /static
  static_dir: static/
  secure: always

- url: /.*
  script: auto
  secure: always
```

## Step 5: Deploy to Google App Engine

### 5.1 Initialize App Engine
```bash
# Navigate to your project directory
cd /path/to/your/whatsapp-bulk-message

# Initialize App Engine
gcloud app create --region=us-central

# Deploy your application
gcloud app deploy
```

### 5.2 Set Up Custom Domain (Optional)
1. Go to App Engine → Settings → Custom Domains
2. Add your domain: `creativeunicorn.com`
3. Follow the verification steps
4. Update `ALLOWED_HOSTS` in settings

## Step 6: Set Up Cloud Storage for Media Files

### 6.1 Create Storage Bucket
```bash
# Create bucket
gsutil mb gs://your-whatsapp-bulk-bucket

# Make it public (for media files)
gsutil iam ch allUsers:objectViewer gs://your-whatsapp-bulk-bucket
```

### 6.2 Install Cloud Storage Library
Add to `requirements.txt`:
```
google-cloud-storage==2.10.0
```

## Step 7: Database Migration

### 7.1 Run Migrations
```bash
# Deploy first
gcloud app deploy

# Then run migrations
gcloud app deploy --version=migration --no-promote
```

### 7.2 Create Superuser
```bash
# Connect to your app
gcloud app logs tail -s default

# Or use Cloud Shell to run Django commands
gcloud app versions list
```

## Step 8: Configure WhatsApp Webhook

### 8.1 Update Webhook URL
Your webhook URL will be:
```
https://your-app-id.appspot.com/webhook/whatsapp/
```

### 8.2 Update WhatsApp API Settings
1. Go to your WhatsApp API provider dashboard
2. Update webhook URL to the new GCP URL
3. Verify the webhook is working

## Step 9: Monitoring and Maintenance

### 9.1 Set Up Monitoring
1. Go to Cloud Monitoring
2. Set up alerts for:
   - High error rates
   - High response times
   - Database connections

### 9.2 Logs
```bash
# View logs
gcloud app logs tail -s default

# View specific logs
gcloud app logs read --service=default --version=1
```

## Step 10: Security Best Practices

### 10.1 Use Secret Manager
```bash
# Store sensitive data in Secret Manager
gcloud secrets create secret-name --data-file=secret-file.txt

# Access in app.yaml
env_variables:
  SECRET_VALUE: "projects/your-project/secrets/secret-name/versions/latest"
```

### 10.2 Enable IAM
1. Go to IAM & Admin → IAM
2. Add service accounts with minimal permissions
3. Use least privilege principle

## Troubleshooting

### Common Issues:

**Issue: Database Connection Error**
- Check Cloud SQL instance is running
- Verify connection name format
- Ensure App Engine has access to Cloud SQL

**Issue: Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` setting
- Verify `app.yaml` handlers

**Issue: 500 Internal Server Error**
- Check logs: `gcloud app logs tail -s default`
- Verify all environment variables are set
- Check database migrations

**Issue: WhatsApp Webhook Not Working**
- Verify webhook URL is accessible
- Check SSL certificate
- Test with curl: `curl -X POST https://your-app.appspot.com/webhook/whatsapp/`

## Cost Optimization

### 10.1 App Engine Settings
```yaml
# In app.yaml
automatic_scaling:
  min_instances: 0  # Scale to zero when not in use
  max_instances: 5  # Limit max instances
  target_cpu_utilization: 0.8
```

### 10.2 Database Optimization
- Use Cloud SQL with appropriate machine type
- Enable connection pooling
- Monitor query performance

## Deployment Commands

```bash
# Deploy new version
gcloud app deploy

# Deploy specific service
gcloud app deploy app.yaml

# View deployed versions
gcloud app versions list

# Switch traffic to new version
gcloud app services set-traffic default --splits=version=1.0.0=1

# Rollback to previous version
gcloud app services set-traffic default --splits=version=0.9.0=1
```

## Your App Will Be Available At:
- **App Engine URL**: `https://your-app-id.appspot.com`
- **Custom Domain**: `https://creativeunicorn.com` (if configured)

## Next Steps After Deployment:
1. Test all functionality
2. Set up monitoring alerts
3. Configure backup strategy
4. Set up CI/CD pipeline
5. Configure custom domain

Your Django app is now ready for production on Google Cloud Platform! 🎉
