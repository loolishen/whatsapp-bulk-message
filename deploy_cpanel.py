#!/usr/bin/env python3
"""
cPanel Deployment Script
This script helps deploy your Django app to cPanel hosting
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e.stderr}")
        return None

def main():
    print("🚀 cPanel Deployment Setup")
    print("=" * 50)
    
    # 1. Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # 2. Create requirements.txt if it doesn't exist
    if not os.path.exists("requirements.txt"):
        run_command("pip freeze > requirements.txt", "Creating requirements.txt")
    
    # 3. Create .htaccess for cPanel
    htaccess_content = """RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /whatsapp_bulk/wsgi.py/$1 [QSA,L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"

# Cache static files
<FilesMatch "\\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
</FilesMatch>
"""
    
    with open(".htaccess", "w") as f:
        f.write(htaccess_content)
    print("✅ Created .htaccess file")
    
    # 4. Create wsgi.py for cPanel
    wsgi_content = """import os
import sys
from django.core.wsgi import get_wsgi_application

# Add your project directory to the Python path
sys.path.insert(0, '/home/yourusername/public_html/whatsapp-bulk-message')
sys.path.insert(0, '/home/yourusername/public_html/whatsapp-bulk-message/whatsapp_bulk')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')

application = get_wsgi_application()
"""
    
    with open("wsgi.py", "w") as f:
        f.write(wsgi_content)
    print("✅ Created wsgi.py file")
    
    # 5. Create deployment instructions
    instructions = """
📋 cPanel Deployment Instructions
================================

1. UPLOAD FILES TO CPANEL:
   - Upload all project files to: /public_html/whatsapp-bulk-message/
   - Or create a subdomain and upload there

2. SET UP PYTHON APP IN CPANEL:
   - Go to "Python App" in cPanel
   - Create new Python app
   - Python version: 3.9 or higher
   - App directory: /public_html/whatsapp-bulk-message
   - App URL: your-domain.com (or subdomain)
   - Application startup file: wsgi.py

3. INSTALL DEPENDENCIES:
   - In cPanel Python App, go to "Terminal"
   - Run: pip install -r requirements.txt

4. SET UP DATABASE:
   - Create MySQL database in cPanel
   - Update database settings in settings.py
   - Run: python manage.py migrate

5. CONFIGURE ENVIRONMENT VARIABLES:
   - In cPanel Python App settings
   - Add: DEBUG=False
   - Add: SECRET_KEY=your-secret-key-here
   - Add: ALLOWED_HOSTS=your-domain.com

6. COLLECT STATIC FILES:
   - Run: python manage.py collectstatic --noinput

7. RESTART APPLICATION:
   - Restart the Python app in cPanel

8. TEST YOUR DEPLOYMENT:
   - Visit your domain
   - Check if all features work

🔧 GITHUB INTEGRATION:
- Connect your cPanel to GitHub
- Set up auto-deployment on push
- Your app will update automatically when you push to GitHub

📞 SUPPORT:
- Check cPanel error logs if issues occur
- Ensure all file permissions are correct (755 for directories, 644 for files)
"""
    
    with open("DEPLOYMENT_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    print("✅ Created deployment instructions")
    print("\n🎉 Setup complete! Check DEPLOYMENT_INSTRUCTIONS.txt for next steps")

if __name__ == "__main__":
    main()
