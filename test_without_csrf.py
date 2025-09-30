#!/usr/bin/env python
"""
Test login without CSRF protection to isolate the issue
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model

def test_login_without_csrf():
    """Test login with CSRF protection disabled"""
    print("=== Testing Login Without CSRF ===")
    
    try:
        # Create a test client with CSRF disabled
        client = Client(enforce_csrf_checks=False)
        
        # Test GET /login/
        print("1. Testing GET /login/...")
        response = client.get('/login/', HTTP_HOST='testserver')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test POST /login/ without CSRF
        print("2. Testing POST /login/ without CSRF...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected")
            print(f"   Redirect URL: {response.url}")
            return True
        elif response.status_code == 500:
            print("   ❌ 500 error - not a CSRF issue")
            print(f"   Response: {response.content.decode()[:500]}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication_directly():
    """Test authentication directly without views"""
    print("\n=== Testing Direct Authentication ===")
    
    try:
        from django.contrib.auth import authenticate
        
        # Test authentication
        user = authenticate(username='tenant', password='Tenant123!')
        if user:
            print(f"✓ Direct authentication successful: {user.username}")
            
            # Test tenant relationship
            try:
                tenant_profile = user.tenant_profile
                print(f"✓ Tenant profile: {tenant_profile.tenant.name}")
                return True
            except Exception as e:
                print(f"❌ Tenant profile failed: {e}")
                return False
        else:
            print("❌ Direct authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_view_directly():
    """Test the login view directly"""
    print("\n=== Testing Login View Directly ===")
    
    try:
        from django.test import RequestFactory
        from messaging.views import auth_login
        from django.contrib.auth import get_user_model
        
        factory = RequestFactory()
        
        # Test GET request
        print("1. Testing GET request...")
        request = factory.get('/login/')
        request.META['HTTP_HOST'] = 'testserver'
        
        response = auth_login(request)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ GET request failed: {response.status_code}")
            return False
        
        print("   ✓ GET request successful")
        
        # Test POST request
        print("2. Testing POST request...")
        request = factory.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        })
        request.META['HTTP_HOST'] = 'testserver'
        
        response = auth_login(request)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ POST request successful - redirected")
            return True
        else:
            print(f"   ❌ POST request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 TESTING WITHOUT CSRF")
    print("=" * 50)
    
    # Test 1: Direct authentication
    if not test_authentication_directly():
        print("\n❌ Direct authentication failed")
        return False
    
    # Test 2: Login without CSRF
    if not test_login_without_csrf():
        print("\n❌ Login without CSRF failed")
        return False
    
    # Test 3: Login view directly
    if not test_login_view_directly():
        print("\n❌ Login view test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login works without CSRF!")
    print("=" * 50)
    print("The issue is definitely CSRF-related.")
    print("Solution: Deploy the updated settings and test again.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
