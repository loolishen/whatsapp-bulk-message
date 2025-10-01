#!/usr/bin/env python
"""
Fix PostgreSQL setup with correct region and password
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

def create_database_user():
    """Create database user with correct password"""
    print("CREATING DATABASE USER")
    print("=" * 50)
    
    # Create user with password that meets PostgreSQL requirements
    cmd = 'gcloud sql users create whatsapp_user --instance=whatsapp-bulk-db --password=WhatsappPassword123!'
    
    if not run_command(cmd, "Creating database user", ignore_errors=True):
        print("[INFO] User may already exist, continuing...")
    
    return True

def run_migrations():
    """Run Django migrations"""
    print("\nRUNNING DJANGO MIGRATIONS")
    print("=" * 50)
    
    # Set environment variable for production settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'whatsapp_bulk.settings_production'
    
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
    
    # Set environment variable for production settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'whatsapp_bulk.settings_production'
    
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
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
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
    print("FIXING POSTGRESQL SETUP")
    print("=" * 50)
    
    # Step 1: Create database user
    if not create_database_user():
        print("[ERROR] User creation failed")
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
    
    # Step 5: Deploy to App Engine
    if not deploy_to_app_engine():
        print("[ERROR] Deployment failed")
        return False
    
    # Step 6: Test login
    if not test_production_login():
        print("[ERROR] Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! PostgreSQL setup fixed!")
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
