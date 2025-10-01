#!/usr/bin/env python
"""
Setup existing PostgreSQL database for GCP App Engine
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

def check_cloud_sql_instance():
    """Check if Cloud SQL instance exists and is running"""
    print("CHECKING CLOUD SQL INSTANCE")
    print("=" * 50)
    
    try:
        # Check if instance exists
        result = subprocess.run(['gcloud', 'sql', 'instances', 'describe', 'whatsapp-bulk-db'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Cloud SQL instance exists")
            # Check if it's running
            if 'RUNNABLE' in result.stdout:
                print("[OK] Cloud SQL instance is running")
                return True
            else:
                print("[INFO] Cloud SQL instance exists but may not be running")
                return True
        else:
            print("[ERROR] Cloud SQL instance does not exist")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to check Cloud SQL instance: {e}")
        return False

def setup_database_and_user():
    """Setup database and user (ignore if they already exist)"""
    print("\nSETTING UP DATABASE AND USER")
    print("=" * 50)
    
    commands = [
        # Create database (ignore if exists)
        ('gcloud sql databases create whatsapp_bulk --instance=whatsapp-bulk-db', 
         "Creating database", True),
        
        # Create user (ignore if exists)
        ('gcloud sql users create whatsapp_user --instance=whatsapp-bulk-db --password=whatsapp_password_123!', 
         "Creating database user", True),
    ]
    
    for cmd, description, ignore_errors in commands:
        if not run_command(cmd, description, ignore_errors):
            if not ignore_errors:
                print(f"[ERROR] Failed at: {description}")
                return False
        
        # Wait a bit between commands
        time.sleep(5)
    
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
    print("SETTING UP EXISTING POSTGRESQL DATABASE")
    print("=" * 50)
    
    # Step 1: Check Cloud SQL instance
    if not check_cloud_sql_instance():
        print("[ERROR] Cloud SQL instance not found")
        return False
    
    # Step 2: Setup database and user
    if not setup_database_and_user():
        print("[ERROR] Database setup failed")
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
