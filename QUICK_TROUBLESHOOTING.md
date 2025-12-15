# Quick Troubleshooting Guide - Django on App Engine

## 🚨 Common Errors & Fast Fixes

---

### 1️⃣ `502 Bad Gateway`

**What it means:** App Engine can't start your app

**Quick fix:**
```bash
# Check logs
gcloud app logs read --limit=20

# Common causes:
# - Missing main.py
# - Wrong entrypoint in app.yaml
# - Import errors
```

---

### 2️⃣ `ModuleNotFoundError: No module named 'X'`

**What it means:** Python can't find your module

**Quick fix:**
- If `whatsapp_bulk` or project name: **Flatten your structure**
- If third-party package: Add to `requirements.txt`
- If your app: Check `.gcloudignore` isn't excluding it

---

### 3️⃣ `500 Internal Server Error` (after login or on dashboard)

**What it means:** Database tables missing

**Quick fix:**
```bash
# In Cloud Shell:
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &
cd ~/app-full
python3 migrate_db.py
pkill cloud-sql-proxy
```

---

### 4️⃣ `relation "table_name" does not exist`

**What it means:** Django migrations not run

**Quick fix:** Run migrations (same as #3 above)

---

### 5️⃣ `DuplicateTable` error during migration

**What it means:** Tables exist but Django doesn't know about them

**Quick fix - NUCLEAR OPTION:**
```bash
# Drop all tables and rebuild
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &

python3 << 'EOF'
import psycopg2
conn = psycopg2.connect(host='127.0.0.1', port=5432, database='DB_NAME', user='DB_USER', password='PASSWORD')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'messaging_%';")
for row in cur.fetchall():
    cur.execute(f"DROP TABLE IF EXISTS {row[0]} CASCADE;")
cur.execute("DELETE FROM django_migrations WHERE app = 'messaging';")
conn.commit()
cur.close()
conn.close()
EOF

python3 migrate_db.py
pkill cloud-sql-proxy
```

---

### 6️⃣ `Connection timed out` to Cloud SQL

**What it means:** Direct IP connection expired (5-min limit)

**Quick fix:** Use Cloud SQL Proxy instead
```bash
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &
# Now connect to 127.0.0.1:5432
```

---

### 7️⃣ `.gcloudignore` excluding important files

**What it means:** Your code isn't being deployed

**Quick fix:** Use this minimal `.gcloudignore`:
```
.gcloudignore
.git/
.gitignore
.env
venv/
__pycache__/
*.pyc
*.sqlite3
```

---

## 🎯 Fast Deployment Flow

### **Local Machine (Windows):**
```cmd
cmd /c "gcloud app deploy --project=PROJECT_ID"
```

### **Cloud Shell (after deploy):**
```bash
# 1. Upload code from local
gsutil -m rsync -r -x ".git/*|__pycache__/*|*.pyc|venv/*" . gs://BUCKET/source/

# 2. In Cloud Shell, download code
cd ~/ && rm -rf app-full && mkdir app-full && cd app-full
gsutil -m rsync -r gs://BUCKET/source/ .

# 3. Run migrations
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &
sleep 5
pip3 install --user django psycopg2-binary
python3 migrate_db.py
pkill cloud-sql-proxy
```

---

## 📋 Pre-Flight Checklist

Before deploying, check:
- [ ] `main.py` exists at root
- [ ] `app.yaml` has `entrypoint: gunicorn -b :$PORT main:application`
- [ ] Project structure is FLAT (not nested)
- [ ] `.gcloudignore` is minimal
- [ ] `settings_production.py`: `BASE_DIR = Path(__file__).resolve().parent` (single parent)
- [ ] `settings_production.py`: `ROOT_URLCONF = 'urls'` (not 'project.urls')

---

## 🔍 Essential Commands

```bash
# Deploy
gcloud app deploy --project=PROJECT_ID

# View recent logs
gcloud app logs read --limit=20 --project=PROJECT_ID

# View errors only
gcloud app logs read --limit=50 | grep -i error

# Browse app
gcloud app browse --project=PROJECT_ID

# Cloud Shell: Start proxy
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &

# Cloud Shell: Stop proxy
pkill cloud-sql-proxy

# Cloud Shell: Check database tables
psql -h 127.0.0.1 -U DB_USER -d DB_NAME -c "\dt"
```

---

## 💡 Pro Tips

1. **Always use Cloud SQL Proxy** for database operations (not direct IP)
2. **Check logs immediately** after deployment: `gcloud app logs read --limit=20`
3. **Deploy first, migrate second** - don't try to do both at once
4. **Keep `.gcloudignore` minimal** - it's easy to accidentally exclude needed files
5. **Use flat structure** - App Engine Standard doesn't like nested Django projects

---

## 🆘 Still Stuck?

1. Check logs: `gcloud app logs read --limit=50`
2. Verify deployment: `gcloud app browse`
3. Test database connection in Cloud Shell
4. Ensure all tables exist: `\dt` in psql
5. Verify user exists: `SELECT * FROM auth_user;`

---

**Remember:** Most errors are either:
- Missing files (check `.gcloudignore`)
- Wrong project structure (flatten it)
- Missing database tables (run migrations)




