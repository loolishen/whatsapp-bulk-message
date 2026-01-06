# 🚀 Django on Google App Engine - Complete Deployment Package

This package contains everything you need to deploy Django applications to Google App Engine Standard with Cloud SQL PostgreSQL.

---

## 📦 What's Included

| File | Purpose |
|------|---------|
| `DEPLOYMENT_GUIDE.md` | **Complete deployment guide** with configuration files, step-by-step instructions, and troubleshooting |
| `QUICK_TROUBLESHOOTING.md` | **Quick reference** for common errors and fast fixes |
| `deploy_local.bat` | **Windows script** to deploy from your local machine |
| `deploy_to_gcp.sh` | **Cloud Shell script** to run database migrations automatically |
| `migrate_db.py` | **Python script** for database migrations (already in your project) |

---

## 🎯 Quick Start Guide

### **First Time Setup:**

1. **Read the full guide:**
   ```
   Open: DEPLOYMENT_GUIDE.md
   ```

2. **Configure your project** according to the guide:
   - Flatten project structure
   - Create `main.py`
   - Update `app.yaml`
   - Configure `settings_production.py`

3. **Deploy!**

### **For Future Deployments:**

#### **On Windows (Local Machine):**

```cmd
REM Edit deploy_local.bat with your project details
deploy_local.bat
```

This will:
✅ Upload your code to Cloud Storage
✅ Deploy to App Engine

#### **In Google Cloud Shell:**

```bash
# Edit deploy_to_gcp.sh with your project details
chmod +x deploy_to_gcp.sh
./deploy_to_gcp.sh
```

This will:
✅ Download your code
✅ Start Cloud SQL Proxy
✅ Run all database migrations
✅ Verify setup
✅ Clean up

---

## 🔧 When Things Go Wrong

**See an error?** Check `QUICK_TROUBLESHOOTING.md` for fast solutions!

Common issues:
- 502 Bad Gateway → Check `QUICK_TROUBLESHOOTING.md` #1
- 500 Internal Server Error → Check `QUICK_TROUBLESHOOTING.md` #3
- ModuleNotFoundError → Check `QUICK_TROUBLESHOOTING.md` #2
- Database errors → Check `QUICK_TROUBLESHOOTING.md` #4, #5

---

## 📚 Document Guide

### When to use each document:

| Scenario | Use This Document |
|----------|-------------------|
| First time deploying | `DEPLOYMENT_GUIDE.md` |
| Quick error lookup | `QUICK_TROUBLESHOOTING.md` |
| Routine deployment | `deploy_local.bat` + `deploy_to_gcp.sh` |
| Understanding configuration | `DEPLOYMENT_GUIDE.md` (Configuration section) |
| Database migration issues | `DEPLOYMENT_GUIDE.md` (Troubleshooting section) |

---

## 🎓 Learning Path

**If you're new to App Engine:**

1. **Start here:** Read `DEPLOYMENT_GUIDE.md` from top to bottom
2. **Configure your project** following the "Essential Configuration Files" section
3. **Do a test deployment** following the "Deployment Process" section
4. **Bookmark:** `QUICK_TROUBLESHOOTING.md` for quick reference

**If you've deployed before:**

1. **Keep handy:** `QUICK_TROUBLESHOOTING.md`
2. **Use scripts:** `deploy_local.bat` and `deploy_to_gcp.sh`
3. **Reference:** `DEPLOYMENT_GUIDE.md` for detailed explanations

---

## ✅ Pre-Deployment Checklist

Before running any deployment scripts, verify:

- [ ] Project structure is **flat** (not nested)
- [ ] `main.py` exists at root
- [ ] `app.yaml` configured correctly
- [ ] `settings_production.py` updated
- [ ] Database credentials set
- [ ] `.gcloudignore` is minimal
- [ ] All scripts have correct PROJECT_ID

---

## 🔐 Security Reminders

1. **Never commit** `deploy_local.bat` or `deploy_to_gcp.sh` with real credentials
2. **Use environment variables** or GCP Secret Manager for sensitive data
3. **Review** `app.yaml` before committing
4. **Set** `DEBUG = False` in production

---

## 🆘 Getting Help

**Error messages:**
1. Check `QUICK_TROUBLESHOOTING.md`
2. Check deployment logs: `gcloud app logs read --limit=50`
3. Search `DEPLOYMENT_GUIDE.md` for specific error text

**Configuration questions:**
1. See "Essential Configuration Files" in `DEPLOYMENT_GUIDE.md`
2. Compare your files with the examples

**Migration issues:**
1. See "Troubleshooting Guide" in `DEPLOYMENT_GUIDE.md`
2. Check database connection using Cloud SQL Proxy

---

## 📝 Customization

### Customize deployment scripts:

**`deploy_local.bat` (Windows):**
```batch
set PROJECT_ID=your-project-id
set GCS_BUCKET=staging.your-project-id.appspot.com
```

**`deploy_to_gcp.sh` (Cloud Shell):**
```bash
PROJECT_ID="your-project-id"
REGION="your-region"
INSTANCE_NAME="your-db-instance"
DB_NAME="your-database"
DB_USER="your-user"
DB_PASSWORD="your-password"
```

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ `gcloud app browse` loads your app
✅ No 502 or 500 errors
✅ Login page loads
✅ Users can login
✅ Dashboard loads after login
✅ No database errors in logs

---

## 🔄 Deployment Workflow Summary

```
┌─────────────────┐
│ Local Machine   │
│ (Windows)       │
├─────────────────┤
│ 1. Code changes │
│ 2. Run:         │
│    deploy_local │
│    .bat         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Google Cloud    │
│ Platform        │
├─────────────────┤
│ - App deployed  │
│ - Code in GCS   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cloud Shell     │
├─────────────────┤
│ 3. Run:         │
│    ./deploy_to  │
│    _gcp.sh      │
├─────────────────┤
│ - Migrations    │
│ - Setup done    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ✅ LIVE APP!   │
└─────────────────┘
```

---

## 📞 Important Commands Reference

```bash
# IMPORTANT: if you are editing code locally but deploying from Cloud Shell,
# make sure Cloud Shell has the latest code. Old code = old bugs still showing.
#
# Recommended approach:
# 1) Sync local -> Cloud Shell (example uses a GCS bucket as the bridge)
# 2) Deploy from Cloud Shell
#
# (If you are already developing directly in Cloud Shell, you can skip the sync step.)

# Deploy (Windows CMD)
deploy_local.bat

# Deploy (Linux/Mac)
gcloud app deploy --project=PROJECT_ID

# Verify which version is live
gcloud app versions list --service=default --project=PROJECT_ID

# Tail live logs while testing
gcloud app logs tail -s default --project=PROJECT_ID

# Migrate (Cloud Shell)
./deploy_to_gcp.sh

# View logs
gcloud app logs read --limit=50

# Browse app
gcloud app browse

# Start Cloud SQL Proxy (Cloud Shell)
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &

# Stop Cloud SQL Proxy
pkill cloud-sql-proxy
```

---

## 🧯 If you fixed something locally but production still shows the old error

Example symptom:
- You fixed a template bug locally, but App Engine still throws the same `NoReverseMatch` error.

This almost always means **your new code was not deployed** (or you deployed from an old folder).

Checklist:
- Confirm your local repo contains the fix (e.g. no `{% url '' %}` left in templates)
- Deploy from the *same folder* that contains the fix
- After deploy, confirm a *new version* exists:
  - `gcloud app versions list --service=default --project=PROJECT_ID`
- Hard refresh the page (Ctrl+F5) after deploy

---

## 🎉 You're Ready!

With these documents and scripts, you have everything you need to:
- ✅ Deploy Django apps to App Engine
- ✅ Manage database migrations
- ✅ Troubleshoot common issues
- ✅ Automate future deployments

**Good luck with your deployments!** 🚀

---

**Package Version:** 1.0  
**Last Updated:** December 2025  
**Tested With:** Django 5.0.6, Python 3.11, App Engine Standard

