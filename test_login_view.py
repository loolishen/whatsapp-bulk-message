#!/usr/bin/env python
"""
Test the actual login view to see what's causing the 500 error
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from messaging.views import auth_login
from messaging.models import Tenant, TenantUser
from django.utils import timezone

def test_login_view():
    """Test the actual login view"""
    print("=== Testing Login View ===")
    
    try:
        # Create a test client
        client = Client()
        
        # Test GET request (should return 200)
        print("Testing GET request to /login/...")
        response = client.get('/login/')
        print(f"GET Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ GET request failed: {response.status_code}")
            return False
        
        # Test POST request with correct credentials
        print("\nTesting POST request with correct credentials...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
            'csrfmiddlewaretoken': 'test'  # We'll get the real token
        })
        print(f"POST Response status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login successful - redirected")
            return True
        elif response.status_code == 500:
            print("❌ Login failed with 500 error")
            # Try to get more details about the error
            try:
                print(f"Response content: {response.content.decode()[:500]}")
            except:
                print("Could not decode response content")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_login():
    """Test direct authentication without the view"""
    print("\n=== Testing Direct Authentication ===")
    
    try:
        from django.contrib.auth import authenticate, login
        from django.contrib.auth.models import User
        
        # Test authentication
        user = authenticate(username='tenant', password='Tenant123!')
        if user:
            print(f"✓ Direct authentication successful: {user.username}")
            return True
        else:
            print("❌ Direct authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_user_tenant_relationship():
    """Check if user has proper tenant relationship"""
    print("\n=== Checking User-Tenant Relationship ===")
    
    try:
        User = get_user_model()
        user = User.objects.filter(username='tenant').first()
        
        if not user:
            print("❌ User 'tenant' not found")
            return False
        
        print(f"✓ User found: {user.username}")
        
        # Check if user has tenant_profile
        try:
            tenant_profile = user.tenant_profile
            print(f"✓ User has tenant_profile: {tenant_profile.tenant.name}")
            print(f"✓ Tenant plan: {tenant_profile.tenant.plan}")
            print(f"✓ User role: {tenant_profile.role}")
            return True
        except Exception as e:
            print(f"❌ User has no tenant_profile: {e}")
            return False
            
    except Exception as e:
        print(f"❌ User-tenant relationship check failed: {e}")
        return False

def main():
    print("🧪 TESTING LOGIN VIEW")
    print("=" * 50)
    
    # Test 1: Check user-tenant relationship
    if not check_user_tenant_relationship():
        print("\n❌ User-tenant relationship issue")
        return False
    
    # Test 2: Test direct authentication
    if not test_direct_login():
        print("\n❌ Direct authentication failed")
        return False
    
    # Test 3: Test login view
    if not test_login_view():
        print("\n❌ Login view test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! All login tests passed!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
