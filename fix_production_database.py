#!/usr/bin/env python
"""
Fix production database - ensure user exists in the correct database
"""

import os
import sys
import django

# Setup Django with production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from messaging.models import Tenant, TenantUser

def check_database_connection():
    """Check which database we're connected to"""
    print("CHECKING DATABASE CONNECTION")
    print("=" * 50)
    
    try:
        from django.db import connection
        from django.conf import settings
        
        print(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
        print(f"Database name: {settings.DATABASES['default']['NAME']}")
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Database connection test: {result}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def ensure_production_user():
    """Ensure user exists in production database"""
    print("\nENSURING PRODUCTION USER EXISTS")
    print("=" * 50)
    
    try:
        User = get_user_model()
        
        # Delete existing user if it exists (to ensure clean state)
        try:
            existing_user = User.objects.get(username='tenant')
            existing_user.delete()
            print("[OK] Deleted existing user")
        except User.DoesNotExist:
            print("[OK] No existing user to delete")
        
        # Create tenant
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
        
        # Create user
        user = User.objects.create_user(
            username='tenant',
            email='tenant@example.com',
            password='Tenant123!'
        )
        user.is_active = True
        user.save()
        print(f"[OK] Created user: {user.username}")
        
        # Create tenant-user link
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
            return True
        else:
            print("[ERROR] Authentication test failed")
            return False
        
    except Exception as e:
        print(f"[ERROR] User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_after_fix():
    """Test login after fixing the database"""
    print("\nTESTING LOGIN AFTER FIX")
    print("=" * 50)
    
    try:
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
        import traceback
        traceback.print_exc()
        return False

def main():
    print("FIXING PRODUCTION DATABASE")
    print("=" * 50)
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("[ERROR] Database connection failed")
        return False
    
    # Step 2: Ensure user exists
    if not ensure_production_user():
        print("[ERROR] Failed to ensure user exists")
        return False
    
    # Step 3: Test login
    if not test_login_after_fix():
        print("[ERROR] Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! Production database fixed!")
    print("=" * 50)
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
