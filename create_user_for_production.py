#!/usr/bin/env python
"""
Create the tenant user for production deployment
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from messaging.models import Tenant, TenantUser

def create_production_user():
    """Create the production user with tenant relationship"""
    print("CREATING PRODUCTION USER")
    print("=" * 50)
    
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
            print(f"[OK] Created tenant: {tenant.name} (plan: {tenant.plan})")
        else:
            print(f"[OK] Found existing tenant: {tenant.name} (plan: {tenant.plan})")
        
        # Create or get user
        user, created_user = User.objects.get_or_create(
            username='tenant',
            defaults={'email': 'tenant@example.com'}
        )
        
        if created_user:
            user.set_password('Tenant123!')
            user.is_active = True
            user.save()
            print(f"[OK] Created user: {user.username}")
        else:
            # Update password for existing user
            user.set_password('Tenant123!')
            user.is_active = True
            user.save()
            print(f"[OK] Updated password for existing user: {user.username}")
        
        # Create or get TenantUser link
        tenant_user, created_link = TenantUser.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={'role': 'owner'}
        )
        
        if created_link:
            print(f"[OK] Created tenant-user link: {user.username} @ {tenant.name} (role: {tenant_user.role})")
        else:
            print(f"[OK] Found existing tenant-user link: {user.username} @ {tenant.name} (role: {tenant_user.role})")
        
        # Test authentication
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='tenant', password='Tenant123!')
        if auth_user:
            print(f"[OK] Authentication test successful for {auth_user.username}")
        else:
            print(f"[ERROR] Authentication test failed")
            return False
        
        print(f"\n[OK] User setup completed successfully!")
        print(f"Username: tenant")
        print(f"Password: Tenant123!")
        print(f"Tenant: {tenant.name} (plan: {tenant.plan})")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("PRODUCTION USER SETUP")
    print("=" * 50)
    
    if create_production_user():
        print("\n" + "=" * 50)
        print("SUCCESS! Production user is ready!")
        print("=" * 50)
        return True
    else:
        print("\n" + "=" * 50)
        print("FAILED! User creation failed!")
        print("=" * 50)
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
