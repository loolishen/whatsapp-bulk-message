#!/usr/bin/env python
"""
Database migration script for GCP App Engine
Run this after deploying to apply all Django migrations
"""
import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser

print("=" * 70)
print("DATABASE MIGRATION FOR GCP")
print("=" * 70)

try:
    # Run all migrations
    print("\n1. Running database migrations...")
    call_command('migrate', '--noinput', verbosity=2)
    print("✅ All migrations applied successfully!")
    
    # Ensure production user exists
    print("\n2. Setting up production user...")
    User = get_user_model()
    
    # Get or create tenant
    tenant, created = Tenant.objects.get_or_create(
        name='Demo Tenant',
        defaults={'plan': 'pro'}
    )
    if created:
        print(f"✅ Created tenant: {tenant.name} (ID: {tenant.tenant_id})")
    else:
        print(f"✅ Tenant exists: {tenant.name} (ID: {tenant.tenant_id})")
    
    # Get or create user
    user, user_created = User.objects.get_or_create(
        username='tenant',
        defaults={
            'email': 'tenant@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Set password
    user.set_password('Tenant123!')
    user.is_active = True
    user.save()
    
    if user_created:
        print(f"✅ Created user: {user.username}")
    else:
        print(f"✅ Updated user: {user.username}")
    
    # Link user to tenant
    tenant_user, link_created = TenantUser.objects.get_or_create(
        user=user,
        defaults={'tenant': tenant, 'role': 'owner'}
    )
    
    if link_created:
        print(f"✅ Linked user to tenant")
    else:
        print(f"✅ User already linked to tenant")
    
    print("\n" + "=" * 70)
    print("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n🔐 Login credentials:")
    print("   URL: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/login/")
    print("   Username: tenant")
    print("   Password: Tenant123!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)






