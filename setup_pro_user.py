#!/usr/bin/env python
"""
Complete setup script to create a pro plan user with credentials:
- Username: tenant
- Password: Tenant123!
- Plan: pro
- Role: owner
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')

try:
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import execute_from_command_line

def run_migrations():
    """Run Django migrations to ensure database is set up"""
    print("\n=== Running Migrations ===")
    try:
        # Run makemigrations first
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✓ Made migrations")
        
        # Run migrate
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Applied migrations")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

def create_pro_user():
    """Create the pro plan user"""
    print("\n=== Creating Pro Plan User ===")
    
    try:
        from messaging.models import Tenant, TenantUser
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
            # Update password for existing user
            user.set_password('Tenant123!')
            user.save()
            print(f"✓ Updated password for existing user: {user.username}")
        
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
        print(f"✗ User creation failed: {e}")
        return False

def verify_setup():
    """Verify the setup was successful"""
    print("\n=== Verification ===")
    
    try:
        from messaging.models import Tenant, TenantUser
        User = get_user_model()
        
        # Check users
        users = User.objects.filter(username='tenant')
        if users.exists():
            user = users.first()
            print(f"✓ User found: {user.username} (email: {user.email})")
            
            # Check if password works
            if user.check_password('Tenant123!'):
                print("✓ Password verification successful")
            else:
                print("✗ Password verification failed")
        else:
            print("✗ User not found")
            return False
        
        # Check tenants
        tenants = Tenant.objects.filter(name='Demo Tenant')
        if tenants.exists():
            tenant = tenants.first()
            print(f"✓ Tenant found: {tenant.name} (plan: {tenant.plan})")
        else:
            print("✗ Tenant not found")
            return False
        
        # Check tenant-user links
        tenant_users = TenantUser.objects.filter(user=user, tenant=tenant)
        if tenant_users.exists():
            tu = tenant_users.first()
            print(f"✓ TenantUser link found: {tu.user.username} @ {tu.tenant.name} (role: {tu.role})")
        else:
            print("✗ TenantUser link not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    print("🚀 Setting up Pro Plan User")
    print("=" * 50)
    
    # Step 1: Run migrations
    if not run_migrations():
        print("\n❌ Setup failed at migration step")
        return False
    
    # Step 2: Create user
    if not create_pro_user():
        print("\n❌ Setup failed at user creation step")
        return False
    
    # Step 3: Verify setup
    if not verify_setup():
        print("\n❌ Setup failed at verification step")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Pro plan login created successfully!")
    print("=" * 50)
    print("Login Credentials:")
    print("  Username: tenant")
    print("  Password: Tenant123!")
    print("  Tenant: Demo Tenant")
    print("  Plan: pro")
    print("  Role: owner")
    print("=" * 50)
    print("\nYou can now log in to the application using these credentials.")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
