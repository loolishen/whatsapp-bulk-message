# 🚀 Complete GCP Deployment Guide

## Prerequisites
- Google Cloud Project: `whatsapp-bulk-messaging-473607`
- Cloud Shell access
- GitHub repository with latest code

## Step-by-Step Deployment Process

### **Step 1: Access Cloud Shell**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Open Cloud Shell (click the terminal icon in the top right)
3. Make sure you're in the correct project: `whatsapp-bulk-messaging-473607`

### **Step 2: Navigate to Your Project Directory**
```bash
# Check if you're in the right directory
pwd

# If not in the project directory, navigate to it
cd ~/whatsapp-bulk-messaging/whatsapp-bulk-message

# Verify you're in the right place (should see app.yaml)
ls -la app.yaml
```

### **Step 3: Pull Latest Changes from GitHub**
```bash
# Pull the latest code with OCR fixes
git pull origin main

# Verify the changes are there
cat requirements.txt | grep paddle
```

### **Step 4: Deploy to App Engine**
```bash
# Deploy the application
gcloud app deploy

# When prompted, type 'Y' to continue
```

### **Step 4.5: Setup Database and Users (CRITICAL)**
```bash
# Run the deployment setup script to create database and users
python deploy_setup.py

# Test the login functionality
python test_login.py
```

**Important:** This step is critical! Without running the setup script, you won't be able to log in because no users exist in the database.

### **Step 5: Check Deployment Status**
```bash
# Check if deployment was successful
gcloud app describe

# Get the app URL
gcloud app browse
```

### **Step 6: Monitor Logs (if needed)**
```bash
# Check recent logs for any errors
gcloud app logs read --service=default --limit=20

# Follow logs in real-time
gcloud app logs tail --service=default
```

### **Step 7: Test Your App**
```bash
# Get the app URL
gcloud app browse

# Or manually visit:
# https://whatsapp-bulk-messaging-473607.as.r.appspot.com
```

## 🔧 Troubleshooting Commands

### **If you get permission errors:**
```bash
# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

### **If you get bucket errors:**
```bash
# Create a new staging bucket
gsutil mb gs://whatsapp-bulk-staging-$(date +%s)

# Set the bucket permissions
gsutil iam ch serviceAccount:whatsapp-bulk-messaging-473607@appspot.gserviceaccount.com:objectAdmin gs://whatsapp-bulk-staging-$(date +%s)
```

### **If you need to check your current directory:**
```bash
# Check current directory
pwd

# List files to make sure you're in the right place
ls -la

# Should see: app.yaml, main.py, requirements.txt, etc.
```

## 📋 Quick Reference Commands

```bash
# Navigate to project
cd ~/whatsapp-bulk-messaging/whatsapp-bulk-message

# Pull latest code
git pull origin main

# Deploy
gcloud app deploy

# Check status
gcloud app describe

# View logs
gcloud app logs read --service=default --limit=20

# Open app
gcloud app browse
```

## 🎯 Expected Result

After successful deployment, you should see:
- ✅ **Deployment successful** message
- ✅ **App URL**: `https://whatsapp-bulk-messaging-473607.as.r.appspot.com`
- ✅ **Working app** without crashes
- ✅ **OCR disabled** but core features working

## 📝 Important Notes

- **OCR is now optional** - The app will work without it
- **Receipt processing** - Will show "OCR not available" message
- **Core features** - All other WhatsApp bulk messaging features work normally
- **Future OCR** - Can be re-enabled later with a different OCR solution if needed

## 🚨 Common Issues and Solutions

### Issue: "An app.yaml file is required"
**Solution:** Make sure you're in the correct directory:
```bash
cd ~/whatsapp-bulk-messaging/whatsapp-bulk-message
ls -la app.yaml
```

### Issue: "Permission denied" errors
**Solution:** Enable required APIs and set permissions:
```bash
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

### Issue: "Bucket access denied"
**Solution:** Create a new staging bucket:
```bash
gsutil mb gs://whatsapp-bulk-staging-$(date +%s)
```

### Issue: App crashes with PaddlePaddle errors
**Solution:** This is now fixed! OCR is optional and won't cause crashes.

## 🔄 Re-deployment Process

If you need to redeploy after making changes:

1. **Push changes to GitHub** (from your local machine):
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Pull and deploy** (in Cloud Shell):
   ```bash
   git pull origin main
   gcloud app deploy
   ```

## 🔧 Troubleshooting

### **Login Issues (500 Error)**
If you get a 500 error when trying to login:

1. **Check if database is set up:**
   ```bash
   python test_login.py
   ```

2. **If test fails, run the setup script:**
   ```bash
   python deploy_setup.py
   ```

3. **Verify the setup worked:**
   ```bash
   python test_login.py
   ```

### **Common Issues:**
- **500 Error on Login:** Database not migrated or no users created
- **404 Error:** Wrong URL path or deployment failed
- **Static Files Not Loading:** Run `python manage.py collectstatic --settings=whatsapp_bulk.settings_production`

### **Default Login Credentials:**
- **Username:** `tenant`
- **Password:** `Tenant123!`

## 📞 Support

If you encounter any issues not covered in this guide:
1. Check the logs: `gcloud app logs read --service=default --limit=20`
2. Verify your directory: `pwd` and `ls -la`
3. Ensure all APIs are enabled
4. Check the app status: `gcloud app describe`
5. Run the setup script: `python deploy_setup.py`

---

**Happy Deploying! 🎉**
