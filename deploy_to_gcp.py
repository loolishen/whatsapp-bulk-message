#!/usr/bin/env python
"""
Complete GCP deployment script
"""

import os
import sys
import subprocess
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser
from django.utils import timezone

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def collect_static_files():
    """Collect static files for production"""
    print("\n=== Collecting Static Files ===")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--settings=whatsapp_bulk.settings_production'])
        print("✓ Static files collected successfully")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("\n=== Running Database Migrations ===")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--settings=whatsapp_bulk.settings_production'])
        print("✓ Database migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Database migrations failed: {e}")
        return False

def create_default_user():
    """Create default user for production"""
    print("\n=== Creating Default User ===")
    try:
        User = get_user_model()
        
        # Create or get tenant
        tenant, created_tenant = Tenant.objects.get_or_create(
            name='Demo Tenant',
            defaults={
                'plan': 'pro',
                'creation_date': timezone.now(),
            }
        )
        
        if created_tenant:
            print(f"✓ Created tenant: {tenant.name} (plan: {tenant.plan})")
        else:
            print(f"✓ Found existing tenant: {tenant.name} (plan: {tenant.plan})")
        
        # Create or get user
        user, created_user = User.objects.get_or_create(
            username='tenant',
            defaults={'email': 'tenant@example.com'}
        )
        
        if created_user:
            user.set_password('Tenant123!')
            user.save()
            print(f"✓ Created user: {user.username}")
        else:
            user.set_password('Tenant123!')
            user.save()
            print(f"✓ Updated user: {user.username}")
        
        # Create or get TenantUser link
        tenant_user, created_link = TenantUser.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={'role': 'owner'}
        )
        
        if created_link:
            print(f"✓ Created tenant-user link: {user.username} @ {tenant.name} (role: {tenant_user.role})")
        else:
            print(f"✓ Found existing tenant-user link: {user.username} @ {tenant.name} (role: {tenant_user.role})")
        
        return True
        
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def deploy_to_app_engine():
    """Deploy to Google App Engine"""
    print("\n=== Deploying to App Engine ===")
    try:
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Deployment to App Engine completed successfully")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Deployment failed with exception: {e}")
        return False

def main():
    print("🚀 COMPLETE GCP DEPLOYMENT")
    print("=" * 50)
    
    # Step 1: Collect static files
    if not collect_static_files():
        print("\n❌ Static files collection failed")
        return False
    
    # Step 2: Run migrations
    if not run_migrations():
        print("\n❌ Database migrations failed")
        return False
    
    # Step 3: Create default user
    if not create_default_user():
        print("\n❌ User creation failed")
        return False
    
    # Step 4: Deploy to App Engine
    if not deploy_to_app_engine():
        print("\n❌ App Engine deployment failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Complete deployment finished!")
    print("=" * 50)
    print("Your app is now deployed and ready!")
    print("Login Credentials:")
    print("  Username: tenant")
    print("  Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

