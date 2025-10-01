# PostgreSQL Setup Guide for GCP App Engine

## Step-by-Step Instructions

### Step 1: Create Cloud SQL PostgreSQL Instance

```bash
# Create Cloud SQL instance
gcloud sql instances create whatsapp-bulk-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --maintenance-release-channel=production \
  --deletion-protection
```

### Step 2: Create Database

```bash
# Create database
gcloud sql databases create whatsapp_bulk --instance=whatsapp-bulk-db
```

### Step 3: Create Database User

```bash
# Create user
gcloud sql users create whatsapp_user \
  --instance=whatsapp-bulk-db \
  --password=whatsapp_password_123!
```

### Step 4: Get Connection Name

```bash
# Get connection name
gcloud sql instances describe whatsapp-bulk-db --format=value(connectionName)
```

### Step 5: Update Settings

The `settings_production.py` file has been updated with:
- PostgreSQL database configuration
- Cloud SQL connection string
- SSL requirements

### Step 6: Update app.yaml

The `app.yaml` file has been updated with:
- Cloud SQL instance connection
- Environment variables

### Step 7: Run Migrations

```bash
# Set environment
export DJANGO_SETTINGS_MODULE=whatsapp_bulk.settings_production

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### Step 8: Create Production User

```bash
# Create user
python create_user_for_production.py
```

### Step 9: Deploy to App Engine

```bash
# Deploy
gcloud app deploy --quiet
```

### Step 10: Test Login

```bash
# Test
python test_final_login.py
```

## Quick Setup (All-in-One)

```bash
# Run the complete setup script
python complete_postgresql_setup.py
```

## Database Configuration

- **Instance**: whatsapp-bulk-db
- **Database**: whatsapp_bulk
- **User**: whatsapp_user
- **Password**: whatsapp_password_123!
- **Connection**: whatsapp-bulk-messaging-473607:us-central1:whatsapp-bulk-db

## Troubleshooting

### If Cloud SQL instance creation fails:
- Check if you have the necessary permissions
- Ensure the region is available
- Try a different instance name

### If migrations fail:
- Check database connection
- Verify user permissions
- Check if database exists

### If login still fails:
- Verify user exists in PostgreSQL
- Check App Engine logs
- Ensure Cloud SQL connection is working

## Verification Commands

```bash
# Check Cloud SQL instances
gcloud sql instances list

# Check databases
gcloud sql databases list --instance=whatsapp-bulk-db

# Check users
gcloud sql users list --instance=whatsapp-bulk-db

# Test connection
gcloud sql connect whatsapp-bulk-db --user=whatsapp_user --database=whatsapp_bulk
```
