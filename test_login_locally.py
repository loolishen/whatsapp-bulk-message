#!/usr/bin/env python
"""
Test login locally to verify the fixes work
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from messaging.models import Tenant, TenantUser

def test_authentication():
    """Test authentication directly"""
    print("TESTING AUTHENTICATION")
    print("=" * 50)
    
    try:
        # Test direct authentication
        user = authenticate(username='tenant', password='Tenant123!')
        if user:
            print(f"[OK] Authentication successful for {user.username}")
            print(f"[OK] User is active: {user.is_active}")
            return True
        else:
            print("[ERROR] Authentication failed")
            return False
    except Exception as e:
        print(f"[ERROR] Authentication test failed: {e}")
        return False

def test_login_view():
    """Test the login view"""
    print("\nTESTING LOGIN VIEW")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Test GET request to login page
        response = client.get('/login/')
        print(f"GET /login/ Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] Login page not accessible: {response.status_code}")
            return False
        
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
            if hasattr(response, 'content'):
                print(f"Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Login view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tenant_relationship():
    """Test tenant relationship"""
    print("\nTESTING TENANT RELATIONSHIP")
    print("=" * 50)
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(username='tenant')
        print(f"[OK] User found: {user.username}")
        
        # Check tenant relationship
        if hasattr(user, 'tenant_profile'):
            tenant = user.tenant_profile.tenant
            print(f"[OK] Tenant found: {tenant.name} (plan: {tenant.plan})")
            return True
        else:
            print("[ERROR] User has no tenant_profile")
            return False
            
    except Exception as e:
        print(f"[ERROR] Tenant relationship test failed: {e}")
        return False

def main():
    print("LOCAL LOGIN TEST")
    print("=" * 50)
    
    # Test 1: Authentication
    if not test_authentication():
        print("[ERROR] Authentication test failed")
        return False
    
    # Test 2: Tenant relationship
    if not test_tenant_relationship():
        print("[ERROR] Tenant relationship test failed")
        return False
    
    # Test 3: Login view
    if not test_login_view():
        print("[ERROR] Login view test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! All tests passed!")
    print("=" * 50)
    print("The login should work correctly now.")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
