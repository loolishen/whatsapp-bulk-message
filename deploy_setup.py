#!/usr/bin/env python
"""
Production deployment setup script for GCP App Engine
This script ensures the database is properly migrated and users are created
"""

import os
import sys
import django

# Set up Django with production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from django.utils import timezone
from messaging.models import Tenant, TenantUser

def run_migrations():
    """Run Django migrations"""
    print("=== Running Database Migrations ===")
    try:
        # Run makemigrations
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✓ Made migrations")
        
        # Run migrate
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Applied migrations")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

def create_default_user():
    """Create default user for production"""
    print("=== Creating Default User ===")
    
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
            username='khinddemo',
            defaults={'email': 'khinddemo@example.com'}
        )
        
        if created_user:
            user.set_password('d3mo.123')
            user.save()
            print(f"✓ Created user: {user.username}")
        else:
            # Update password for existing user
            user.set_password('d3mo.123')
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

def main():
    print("🚀 Production Deployment Setup")
    print("=" * 50)
    
    # Step 1: Run migrations
    if not run_migrations():
        print("\n❌ Setup failed at migration step")
        return False
    
    # Step 2: Create default user
    if not create_default_user():
        print("\n❌ Setup failed at user creation step")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Production setup completed!")
    print("=" * 50)
    print("Login Credentials:")
    print("  Username: khinddemo")
    print("  Password: d3mo.123")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
