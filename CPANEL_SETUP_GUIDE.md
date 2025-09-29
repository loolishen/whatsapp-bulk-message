# 🚀 Complete GoDaddy cPanel + GitHub Deployment Guide

## Prerequisites
- GoDaddy hosting with cPanel and Python support
- GitHub account
- Your domain name (e.g., creativeunicorn.com)

## Step 1: Prepare Your Local Project

### 1.1 Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit"
```

### 1.2 Create GitHub Repository
1. Go to GitHub.com
2. Create a new repository named `whatsapp-bulk-message`
3. Don't initialize with README (you already have files)

### 1.3 Connect Local to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-bulk-message.git
git branch -M main
git push -u origin main
```

## Step 2: GoDaddy cPanel Setup

### 2.1 Upload Files to cPanel
1. **Option A: File Manager**
   - Log into your GoDaddy account
   - Go to cPanel → File Manager
   - Navigate to `public_html`
   - Create folder: `repositories/whatsapp-crm`
   - Upload all your project files

2. **Option B: Git Integration (Recommended)**
   - Log into your GoDaddy account
   - Go to cPanel → Git Version Control
   - Click "Create Repository"
   - Enable "Clone a Repository" toggle
   - Clone URL: `https://github.com/loolishen/whatsapp-bulk-message.git`
   - Repository Path: `/home/yourusername/public_html/repositories/whatsapp-crm`
   - Repository Name: `whatsapp-bulk-message`

### 2.2 Set Up Python App
1. Go to cPanel → **Python App**
2. Click **Create Application**
3. Fill in:
   - **Python Version**: 3.9 or higher
   - **Application Root**: `/home/yourusername/public_html/repositories/whatsapp-crm`
   - **Application URL**: `creativeunicorn.com/repositories/whatsapp-crm`
   - **Application Startup File**: `wsgi.py`
   - **Application Entry Point**: `application`

### 2.3 Install Dependencies
1. In cPanel Python App, click **Terminal**
2. Run:
```bash
cd /home/yourusername/public_html/repositories/whatsapp-crm
pip install -r requirements.txt
```

### 2.4 Set Up Database
1. Go to cPanel → **MySQL Databases**
2. Create a new database: `yourusername_whatsapp_crm`
3. Create a user and assign to database
4. Update `settings.py` with database credentials

### 2.5 Configure Environment Variables
In cPanel Python App settings, add:
- `DEBUG=False`
- `SECRET_KEY=your-secret-key-here`
- `ALLOWED_HOSTS=creativeunicorn.com`
- `DB_NAME=yourusername_whatsapp_crm`
- `DB_USER=yourusername_dbuser`
- `DB_PASSWORD=your-db-password`
- `DB_HOST=localhost`

### 2.6 Run Migrations
In Terminal:
```bash
cd /home/yourusername/public_html/repositories/whatsapp-crm
python manage.py migrate
python manage.py collectstatic --noinput
```

### 2.7 Restart Application
Click **Restart** in your Python App

## Step 3: GitHub Integration for Auto-Deployment

### 3.1 Set Up GitHub Actions (Optional)
The `.github/workflows/deploy.yml` file is already created for you.

### 3.2 Manual Deployment Process
Every time you make changes:

1. **Commit and Push to GitHub:**
```bash
git add .
git commit -m "Your changes description"
git push origin main
```

2. **Update cPanel (if using Git):**
   - Go to cPanel → Git Version Control
   - Find your repository and click **Pull** or **Update**

3. **Restart Python App:**
   - Go to Python App
   - Click **Restart**

## Step 4: Testing Your Deployment

### 4.1 Basic Tests
1. Visit `https://creativeunicorn.com/repositories/whatsapp-crm/`
2. Check if homepage loads
3. Test contest manager functionality
4. Verify all pages work

### 4.2 Common Issues & Solutions

**Issue: 500 Internal Server Error**
- Check cPanel error logs
- Verify all environment variables are set
- Ensure database is properly configured

**Issue: Static files not loading**
- Run: `python manage.py collectstatic --noinput`
- Check file permissions (755 for directories, 644 for files)

**Issue: Database connection error**
- Verify database credentials
- Check if database user has proper permissions
- Ensure database exists

## Step 5: Maintenance & Updates

### 5.1 Regular Updates
1. Make changes locally
2. Test locally: `python manage.py runserver`
3. Commit and push to GitHub
4. Update cPanel (pull from Git or upload files)
5. Restart Python app

### 5.2 Backup Strategy
1. **Database Backup:**
   - Go to cPanel → phpMyAdmin
   - Export your database regularly

2. **File Backup:**
   - Your files are already in GitHub
   - cPanel also provides backup tools

## Step 6: Security Considerations

### 6.1 Environment Variables
- Never commit `.env` files
- Use cPanel environment variables for sensitive data
- Keep `SECRET_KEY` secure

### 6.2 File Permissions
- Directories: 755
- Files: 644
- Python files: 644

### 6.3 SSL Certificate
- Enable SSL in cPanel
- Force HTTPS redirects

## Troubleshooting

### Common Commands
```bash
# Check Python app logs
tail -f /home/yourusername/logs/python_app.log

# Check Django logs
tail -f /home/yourusername/logs/django.log

# Restart Python app
# (Use cPanel interface)

# Check file permissions
find /home/yourusername/public_html/repositories/whatsapp-crm -type d -exec chmod 755 {} \;
find /home/yourusername/public_html/repositories/whatsapp-crm -type f -exec chmod 644 {} \;
```

## Support

If you encounter issues:
1. Check cPanel error logs
2. Verify all steps were completed
3. Test locally first
4. Check file permissions
5. Verify environment variables

Your Django app should now be live at `https://creativeunicorn.com/repositories/whatsapp-crm/` and automatically update when you push to GitHub!

## GoDaddy-Specific Notes

- **File Manager**: GoDaddy's file manager may have slightly different navigation
- **Python Apps**: Make sure your hosting plan supports Python applications
- **Database**: GoDaddy uses MySQL databases with specific naming conventions
- **SSL**: Enable SSL certificate through GoDaddy's SSL management
- **Domain**: Your app will be accessible at `creativeunicorn.com/repositories/whatsapp-crm/`
