# 🚨 Quick Fix for 502 Bad Gateway

## Immediate Steps to Identify the Issue

### Step 1: Check GCP Logs (2 minutes)

**This will tell you EXACTLY what's wrong!**

1. Go to: https://console.cloud.google.com/logs?project=whatsapp-bulk-messaging-480620
2. In the search box, type: `resource.type="gae_app"`
3. Click "Run Query"
4. Look for **RED error messages**
5. **Copy the error message** - this tells us what's wrong!

### Step 2: Run Diagnostic Script

I've created a script to check your setup:

```bash
python check_gcp_status.py
```

This will check:
- ✅ Cloud SQL instance status
- ✅ App Engine services
- ✅ Recent error logs
- ✅ Database connection (if possible)

### Step 3: Most Common Fixes

#### Fix #1: Cloud SQL Not Running

**Check:**
1. Go to: https://console.cloud.google.com/sql/instances
2. Find `whatsapp-bulk-db`
3. If status is **STOPPED**, click "START"

**Fix:**
```bash
gcloud sql instances start whatsapp-bulk-db
```

#### Fix #2: Missing Migrations

**Symptoms:** Logs show "relation does not exist" or "table does not exist"

**Fix:** Run migrations via Cloud Shell:
1. Go to: https://shell.cloud.google.com/
2. Clone your repo or upload files
3. Run:
   ```bash
   python manage.py migrate --settings=whatsapp_bulk.settings_production
   ```

#### Fix #3: Wrong Database Credentials

**Check `whatsapp_bulk/settings_production.py` line 66:**
- Password: `P@##w0rd` - Does this match your Cloud SQL user password?
- Username: `whatsapp_user` - Is this correct?
- Database: `whatsapp_bulk` - Does this database exist?

**Fix:** Update credentials to match your Cloud SQL setup.

#### Fix #4: App Engine Service Account Missing Permissions

**Check:**
1. Go to: https://console.cloud.google.com/iam-admin/iam?project=whatsapp-bulk-messaging-480620
2. Find: `whatsapp-bulk-messaging-480620@appspot.gserviceaccount.com`
3. Verify it has: **Cloud SQL Client** role

**Fix:** Add Cloud SQL Client role:
```bash
gcloud projects add-iam-policy-binding whatsapp-bulk-messaging-480620 \
  --member="serviceAccount:whatsapp-bulk-messaging-480620@appspot.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

#### Fix #5: Database Doesn't Exist

**Check:**
1. Go to: https://console.cloud.google.com/sql/instances/whatsapp-bulk-db/databases
2. Verify `whatsapp_bulk` database exists

**Fix:** Create database:
```bash
gcloud sql databases create whatsapp_bulk --instance=whatsapp-bulk-db
```

## Quick Test: Use SQLite Temporarily

To confirm it's a database issue, temporarily modify `settings_production.py`:

```python
# Temporarily use SQLite (lines 61-73)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Then redeploy:
```bash
gcloud app deploy app.yaml
```

**If this works** → It's definitely a Cloud SQL connection issue.
**If this still fails** → It's a Python/import issue.

## What to Share for Help

If you're still stuck, share:
1. **The error message from GCP logs** (Step 1)
2. **Output from `check_gcp_status.py`** (Step 2)
3. **Cloud SQL instance status** (running/stopped)

This will help identify the exact issue!







