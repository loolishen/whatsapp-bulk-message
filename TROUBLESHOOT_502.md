# 🔧 Troubleshooting 502 Bad Gateway Error

## Common Causes of 502 Bad Gateway on App Engine

### 1. ✅ Fixed: Project ID Mismatch
- **Issue**: `app.yaml` had wrong project ID (`473607` instead of `480620`)
- **Fixed**: Updated Cloud SQL connection string in `app.yaml`

### 2. Check Application Logs

View logs to see the actual error:

**Option A: Via GCP Console (Easiest)**
1. Go to: https://console.cloud.google.com/logs
2. Select your project: `whatsapp-bulk-messaging-480620`
3. Filter by: `resource.type="gae_app"`
4. Look for errors in red

**Option B: Via Command Line**
```bash
# View recent logs
gcloud app logs read --limit=50

# Follow logs in real-time
gcloud app logs tail
```

### 3. Common Issues & Fixes

#### Issue: Database Connection Failed
**Symptoms**: Logs show "could not connect to server" or "connection refused"

**Fix**:
1. Verify Cloud SQL instance is running:
   ```bash
   gcloud sql instances list
   ```
2. Check database credentials in `settings_production.py`
3. Verify Cloud SQL connection name matches:
   - Should be: `whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db`

#### Issue: Missing Migrations
**Symptoms**: Logs show "relation does not exist" or "table does not exist"

**Fix**: Run migrations
```bash
# Connect to App Engine and run migrations
gcloud app deploy app.yaml --no-promote
# Then run migrations via Cloud Shell or local connection
```

#### Issue: Import Errors
**Symptoms**: Logs show "ModuleNotFoundError" or "ImportError"

**Fix**:
1. Check `requirements.txt` has all needed packages
2. Verify package versions are compatible
3. Check for missing dependencies

#### Issue: Application Startup Error
**Symptoms**: Logs show Python traceback or startup errors

**Fix**:
1. Check `main.py` - the `ensure_production_user` command might be failing
2. Temporarily comment out the startup command in `main.py`:
   ```python
   # try:
   #     from django.core.management import call_command
   #     call_command('ensure_production_user')
   # except Exception as e:
   #     print(f"Warning: Failed to ensure production user: {e}")
   ```

#### Issue: Static Files Not Collected
**Symptoms**: CSS/JS files return 404

**Fix**: Collect static files before deployment
```bash
python manage.py collectstatic --noinput --settings=whatsapp_bulk.settings_production
```

### 4. Quick Diagnostic Steps

1. **Check if app is deployed**:
   ```bash
   gcloud app versions list
   ```

2. **Check instance status**:
   ```bash
   gcloud app instances list
   ```

3. **Test database connection** (if you have Cloud SQL proxy):
   ```bash
   # Test connection locally
   python manage.py dbshell --settings=whatsapp_bulk.settings_production
   ```

4. **Deploy with verbose logging**:
   ```bash
   gcloud app deploy app.yaml --verbosity=debug
   ```

### 5. Emergency Fix: Deploy with min_instances: 1

If the app keeps failing, temporarily set `min_instances: 1` to keep it running:

```yaml
automatic_scaling:
  min_instances: 1  # Temporary - prevents cold start issues
  max_instances: 3
```

**Note**: This will cost more (~$15-30/month), but helps debug the issue.

### 6. Check These Files

- ✅ `app.yaml` - Project ID matches (should be `480620`)
- ✅ `settings_production.py` - Database connection string correct
- ✅ `main.py` - WSGI application configured
- ✅ `requirements.txt` - All packages listed
- ✅ Static files collected in `staticfiles/` directory

### 7. Next Steps

1. **Check logs first** - This will tell you the exact error
2. **Fix the specific error** based on logs
3. **Redeploy**:
   ```bash
   gcloud app deploy app.yaml
   ```

---

**Most Likely Cause**: Database connection issue or missing migrations. Check the logs to confirm!







