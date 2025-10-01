#!/usr/bin/env python
"""
Debug production login issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser

def check_production_user():
    """Check if user exists in production"""
    print("CHECKING PRODUCTION USER")
    print("=" * 50)
    
    try:
        User = get_user_model()
        
        # Check if user exists
        try:
            user = User.objects.get(username='tenant')
            print(f"[OK] User found: {user.username}")
            print(f"[OK] User is active: {user.is_active}")
            print(f"[OK] User email: {user.email}")
        except User.DoesNotExist:
            print("[ERROR] User 'tenant' does not exist!")
            return False
        
        # Check tenant relationship
        try:
            tenant_user = TenantUser.objects.get(user=user)
            tenant = tenant_user.tenant
            print(f"[OK] Tenant relationship found: {user.username} @ {tenant.name}")
            print(f"[OK] Tenant plan: {tenant.plan}")
            print(f"[OK] Tenant role: {tenant_user.role}")
        except TenantUser.DoesNotExist:
            print("[ERROR] No tenant relationship found!")
            return False
        
        # Test authentication
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='tenant', password='Tenant123!')
        if auth_user:
            print(f"[OK] Authentication successful for {auth_user.username}")
            return True
        else:
            print("[ERROR] Authentication failed!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_production_user_if_missing():
    """Create user if missing"""
    print("\nCREATING PRODUCTION USER IF MISSING")
    print("=" * 50)
    
    try:
        User = get_user_model()
        
        # Create or get tenant
        tenant, created_tenant = Tenant.objects.get_or_create(
            name='Demo Tenant',
            defaults={
                'plan': 'pro',
                'creation_date': django.utils.timezone.now(),
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
        
        return True
        
    except Exception as e:
        print(f"[ERROR] User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_view_directly():
    """Test login view directly"""
    print("\nTESTING LOGIN VIEW DIRECTLY")
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
            return True
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            if hasattr(response, 'content'):
                content = response.content.decode()
                if 'error' in content.lower():
                    print("Response contains error message")
                    # Try to extract error message
                    import re
                    error_match = re.search(r'<div class="error-msg">(.*?)</div>', content)
                    if error_match:
                        print(f"Error message: {error_match.group(1)}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Login view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("DEBUGGING PRODUCTION LOGIN")
    print("=" * 50)
    
    # Step 1: Check if user exists
    if not check_production_user():
        print("\n[INFO] User missing, creating...")
        if not create_production_user_if_missing():
            print("[ERROR] Failed to create user")
            return False
    
    # Step 2: Test login view
    if not test_login_view_directly():
        print("[ERROR] Login view test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! Production login should work now!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
