#!/usr/bin/env python
"""
Setup PostgreSQL for Cloud Shell development
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description, ignore_errors=False):
    """Run a command and return success status"""
    print(f"\n{description}")
    print("-" * 30)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"[OK] {description} successful")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            if ignore_errors:
                print(f"[INFO] {description} - continuing anyway")
                if result.stderr:
                    print(result.stderr)
                return True
            else:
                print(f"[ERROR] {description} failed")
                if result.stderr:
                    print(result.stderr)
                return False
            
    except Exception as e:
        if ignore_errors:
            print(f"[INFO] {description} - continuing anyway: {e}")
            return True
        else:
            print(f"[ERROR] {description} failed: {e}")
            return False

def authorize_cloud_shell_ip():
    """Authorize Cloud Shell IP for Cloud SQL access"""
    print("AUTHORIZING CLOUD SHELL IP")
    print("=" * 50)
    
    # Get current external IP
    try:
        result = subprocess.run(['curl', '-s', 'ifconfig.me'], capture_output=True, text=True)
        if result.returncode == 0:
            external_ip = result.stdout.strip()
            print(f"External IP: {external_ip}")
            
            # Authorize this IP
            cmd = f'gcloud sql instances patch whatsapp-bulk-db --authorized-networks={external_ip}'
            if run_command(cmd, f"Authorizing IP {external_ip}"):
                print("[OK] IP authorized successfully")
                return True
            else:
                print("[WARNING] IP authorization failed, but continuing...")
                return True
        else:
            print("[WARNING] Could not get external IP, continuing...")
            return True
    except Exception as e:
        print(f"[WARNING] IP authorization failed: {e}, continuing...")
        return True

def run_migrations():
    """Run Django migrations using Cloud Shell settings"""
    print("\nRUNNING DJANGO MIGRATIONS")
    print("=" * 50)
    
    # Set environment variable for Cloud Shell settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'whatsapp_bulk.settings_cloudshell'
    
    commands = [
        ('python manage.py makemigrations', "Making migrations"),
        ('python manage.py migrate', "Running migrations"),
    ]
    
    for cmd, description in commands:
        if not run_command(cmd, description):
            print(f"[ERROR] Failed at: {description}")
            return False
    
    return True

def create_production_user():
    """Create production user in PostgreSQL"""
    print("\nCREATING PRODUCTION USER")
    print("=" * 50)
    
    # Set environment variable for Cloud Shell settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'whatsapp_bulk.settings_cloudshell'
    
    # Run the user creation script
    if not run_command('python create_user_for_production.py', "Creating production user"):
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTESTING DATABASE CONNECTION")
    print("=" * 50)
    
    try:
        import os
        import django
        
        # Setup Django with Cloud Shell settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_cloudshell')
        django.setup()
        
        from django.db import connection
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"[OK] Database connection successful: {result}")
            return True
            
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def test_login_locally():
    """Test login locally"""
    print("\nTESTING LOGIN LOCALLY")
    print("=" * 50)
    
    try:
        import os
        import django
        
        # Setup Django with Cloud Shell settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_cloudshell')
        django.setup()
        
        from django.test import Client
        
        client = Client()
        
        # Test POST request to login
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = client.post('/login/', data=login_data)
        print(f"POST /login/ Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.get('Location', '')
            print(f"[OK] Login successful - redirecting to: {redirect_url}")
            
            # Test dashboard access
            dashboard_response = client.get(redirect_url)
            print(f"Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("[OK] Dashboard accessible after login!")
                return True
            else:
                print(f"[ERROR] Dashboard failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Login test failed: {e}")
        return False

def deploy_to_app_engine():
    """Deploy to App Engine"""
    print("\nDEPLOYING TO APP ENGINE")
    print("=" * 50)
    
    if not run_command('gcloud app deploy --quiet', "Deploying to App Engine"):
        return False
    
    return True

def test_production_login():
    """Test production login"""
    print("\nTESTING PRODUCTION LOGIN")
    print("=" * 50)
    
    # Wait for deployment
    print("Waiting for deployment to propagate...")
    time.sleep(60)
    
    if not run_command('python test_final_login.py', "Testing production login"):
        return False
    
    return True

def main():
    print("SETTING UP POSTGRESQL FOR CLOUD SHELL")
    print("=" * 50)
    
    # Step 1: Authorize Cloud Shell IP
    if not authorize_cloud_shell_ip():
        print("[ERROR] IP authorization failed")
        return False
    
    # Step 2: Test database connection
    if not test_database_connection():
        print("[ERROR] Database connection failed")
        return False
    
    # Step 3: Run migrations
    if not run_migrations():
        print("[ERROR] Migrations failed")
        return False
    
    # Step 4: Create production user
    if not create_production_user():
        print("[ERROR] User creation failed")
        return False
    
    # Step 5: Test login locally
    if not test_login_locally():
        print("[ERROR] Local login test failed")
        return False
    
    # Step 6: Deploy to App Engine
    if not deploy_to_app_engine():
        print("[ERROR] Deployment failed")
        return False
    
    # Step 7: Test production login
    if not test_production_login():
        print("[ERROR] Production login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! PostgreSQL setup completed!")
    print("=" * 50)
    print("Your app is fully functional at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
