# GCP Deployment Guide with Automatic Migrations

## Quick Deploy (Recommended)

### Option 1: Deploy + Manual Migration in Cloud Shell

1. **Deploy the app:**
   ```bash
   gcloud app deploy app.yaml --project=whatsapp-bulk-messaging-480620 --promote --quiet
   ```

2. **Run migrations in Cloud Shell:**
   ```bash
   # Start Cloud SQL Proxy
   cloud-sql-proxy whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db --port=5432 &
   sleep 5
   
   # Run migration script
   python3 migrate_db.py
   
   # Stop proxy
   pkill cloud-sql-proxy
   ```

### Option 2: Deploy with Cloud Build (Automated)

This will deploy AND run migrations automatically:

```bash
gcloud builds submit --config=cloudbuild.yaml --project=whatsapp-bulk-messaging-480620
```

## Manual Migration Steps

If you need to run migrations separately:

1. **Start Cloud SQL Proxy:**
   ```bash
   cloud-sql-proxy whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db --port=5432 &
   ```

2. **Run migrations:**
   ```bash
   python3 migrate_db.py
   ```

3. **Stop proxy:**
   ```bash
   pkill cloud-sql-proxy
   ```

## Login Credentials

After successful deployment and migration:

- **URL:** https://whatsapp-bulk-messaging-480620.as.r.appspot.com/login/
- **Username:** `tenant`
- **Password:** `Tenant123!`

## Troubleshooting

### Check if migrations are applied:

```bash
# In Cloud Shell
cloud-sql-proxy whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db --port=5432 &
sleep 3

python3 << 'EOF'
import psycopg2
conn = psycopg2.connect(host='127.0.0.1', port=5432, database='whatsapp_bulk', user='whatsapp_user', password='P@##w0rd')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'messaging_%' ORDER BY table_name;")
print("=== DATABASE TABLES ===")
for row in cur.fetchall():
    print(f"  ✓ {row[0]}")
cur.close()
conn.close()
EOF

pkill cloud-sql-proxy
```

### View application logs:

```bash
gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620
```

### Check App Engine status:

```bash
gcloud app versions list --project=whatsapp-bulk-messaging-480620
```

## Files Overview

- `migrate_db.py` - Migration runner script
- `deploy.sh` - Deployment helper script (Unix/Mac/Linux)
- `cloudbuild.yaml` - Cloud Build configuration for automated deployment
- `DEPLOYMENT.md` - This file
- `app.yaml` - App Engine configuration
- `requirements.txt` - Python dependencies
- `settings_production.py` - Production Django settings

## Cost Optimization

Current configuration in `app.yaml`:
- **Scaling:** 0-3 instances (min=0 for cost savings)
- **CPU:** 0.5 cores
- **Memory:** 0.5 GB
- **Estimated cost:** $30-80/month depending on traffic

To further reduce costs:
- Keep `min_instances: 0` (cold starts acceptable)
- Use Cloud Scheduler to keep instance warm during business hours only
- Monitor usage in GCP Console > App Engine > Dashboard






