# 🔍 Diagnosing 502 Bad Gateway - Step by Step

## Key Difference: Local vs Production

**Local (works):**
- Uses `settings_local` → SQLite database (`db.sqlite3`)
- No network connection needed
- Simple file-based database

**Production (502 error):**
- Uses `settings_production` → PostgreSQL via Cloud SQL
- Requires network connection to Cloud SQL
- More complex setup

## Most Likely Causes (in order)

### 1. 🗄️ Database Connection Issue (90% likely)

**Symptoms:**
- App can't connect to Cloud SQL
- Database credentials wrong
- Cloud SQL instance not running
- Network permissions not set

**How to Check:**
1. Go to: https://console.cloud.google.com/sql/instances
2. Verify `whatsapp-bulk-db` is **RUNNING** (green status)
3. Check the connection name matches: `whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db`

**How to Fix:**
```bash
# Check Cloud SQL status
gcloud sql instances list

# Test database connection (if you have Cloud SQL proxy)
gcloud sql connect whatsapp-bulk-db --user=whatsapp_user --database=whatsapp_bulk
```

### 2. 📊 Missing Migrations (80% likely)

**Symptoms:**
- Database exists but tables don't
- Logs show "relation does not exist" or "table does not exist"

**How to Fix:**
You need to run migrations on the production database. Options:

**Option A: Via Cloud Shell (Recommended)**
1. Go to: https://shell.cloud.google.com/
2. Clone your repo or upload files
3. Run:
   ```bash
   python manage.py migrate --settings=whatsapp_bulk.settings_production
   ```

**Option B: Via Local Machine with Cloud SQL Proxy**
1. Install Cloud SQL Proxy
2. Connect to database
3. Run migrations locally pointing to production DB

### 3. 🐍 Application Startup Error (60% likely)

**Symptoms:**
- `ensure_production_user` command fails
- Import errors
- Missing packages

**How to Check:**
Check the logs in GCP Console - they'll show the exact error.

**How to Fix:**
I've already updated `main.py` to remove the startup command that might be causing issues.

### 4. 🔐 Database Credentials Wrong (50% likely)

**Check:**
- Password in `settings_production.py` matches Cloud SQL user password
- Username matches: `whatsapp_user`
- Database name matches: `whatsapp_bulk`

## Quick Diagnostic Steps

### Step 1: Check GCP Logs (MOST IMPORTANT)

1. Go to: https://console.cloud.google.com/logs?project=whatsapp-bulk-messaging-480620
2. Filter by:
   - Resource type: `gae_app`
   - Service: `default`
3. Look for **red error messages**
4. The error message will tell you exactly what's wrong!

### Step 2: Verify Cloud SQL is Running

1. Go to: https://console.cloud.google.com/sql/instances
2. Check if `whatsapp-bulk-db` shows **RUNNING** status
3. If it's stopped, start it

### Step 3: Test Database Connection

If you can access Cloud Shell:
```bash
# Connect to database
gcloud sql connect whatsapp-bulk-db --user=whatsapp_user --database=whatsapp_bulk

# If connection works, check if tables exist
\dt
```

### Step 4: Check App Engine Service Account Permissions

The App Engine service account needs permission to connect to Cloud SQL:

1. Go to: https://console.cloud.google.com/iam-admin/iam
2. Find: `whatsapp-bulk-messaging-480620@appspot.gserviceaccount.com`
3. Verify it has: **Cloud SQL Client** role

## Emergency Fix: Test with SQLite First

To verify it's a database issue, temporarily modify `settings_production.py` to use SQLite:

```python
# Temporarily use SQLite to test
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**If this works**, then it's definitely a Cloud SQL connection issue.

## Next Steps

1. **Check the logs first** - This will tell you the exact error
2. **Verify Cloud SQL is running**
3. **Check database credentials**
4. **Run migrations if needed**

---

**Most Likely**: Database connection issue. Check the logs to confirm!







