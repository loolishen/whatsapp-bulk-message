#!/usr/bin/env python
"""
Complete PostgreSQL setup for GCP App Engine
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description):
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
            print(f"[ERROR] {description} failed")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] {description} failed: {e}")
        return False

def setup_cloud_sql():
    """Setup Cloud SQL PostgreSQL instance"""
    print("SETTING UP CLOUD SQL POSTGRESQL")
    print("=" * 50)
    
    commands = [
        # Create Cloud SQL instance
        ('gcloud sql instances create whatsapp-bulk-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=us-central1 --storage-type=SSD --storage-size=10GB --storage-auto-increase --backup-start-time=03:00 --enable-bin-log --maintenance-window-day=SUN --maintenance-window-hour=04 --maintenance-release-channel=production --deletion-protection', 
         "Creating Cloud SQL instance"),
        
        # Create database
        ('gcloud sql databases create whatsapp_bulk --instance=whatsapp-bulk-db',
         "Creating database"),
        
        # Create user
        ('gcloud sql users create whatsapp_user --instance=whatsapp-bulk-db --password=whatsapp_password_123!',
         "Creating database user"),
    ]
    
    for cmd, description in commands:
        if not run_command(cmd, description):
            print(f"[ERROR] Failed at: {description}")
            return False
        
        # Wait a bit between commands
        time.sleep(10)
    
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
    print("COMPLETE POSTGRESQL SETUP FOR GCP")
    print("=" * 50)
    
    # Step 1: Setup Cloud SQL
    if not setup_cloud_sql():
        print("[ERROR] Cloud SQL setup failed")
        return False
    
    # Step 2: Run migrations
    if not run_migrations():
        print("[ERROR] Migrations failed")
        return False
    
    # Step 3: Create production user
    if not create_production_user():
        print("[ERROR] User creation failed")
        return False
    
    # Step 4: Deploy to App Engine
    if not deploy_to_app_engine():
        print("[ERROR] Deployment failed")
        return False
    
    # Step 5: Test login
    if not test_production_login():
        print("[ERROR] Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! Complete PostgreSQL setup completed!")
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
