#!/usr/bin/env python
"""
Test login error locally to identify the issue
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser

def test_login_error():
    """Test login and capture the exact error"""
    print("=== Testing Login Error ===")
    
    try:
        client = Client()
        
        # Test GET /login/
        print("1. Testing GET /login/...")
        response = client.get('/login/', HTTP_HOST='testserver')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test POST /login/ and capture any errors
        print("2. Testing POST /login/...")
        try:
            response = client.post('/login/', {
                'username': 'tenant',
                'password': 'Tenant123!',
            }, HTTP_HOST='testserver')
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✓ Login successful - redirected")
                return True
            elif response.status_code == 500:
                print("   ❌ 500 error - checking response")
                print(f"   Response: {response.content.decode()[:1000]}")
                return False
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.content.decode()[:500]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception during POST: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication_directly():
    """Test authentication directly"""
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
    """Test the login view directly with proper request setup"""
    print("\n=== Testing Login View Directly ===")
    
    try:
        from django.test import RequestFactory
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        from messaging.views import auth_login
        
        factory = RequestFactory()
        
        # Test GET request
        print("1. Testing GET request...")
        request = factory.get('/login/')
        request.META['HTTP_HOST'] = 'testserver'
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
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
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add auth middleware
        auth_middleware = AuthenticationMiddleware(lambda req: None)
        auth_middleware.process_request(request)
        
        try:
            response = auth_login(request)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✓ POST request successful - redirected")
                return True
            else:
                print(f"   ❌ POST request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception during POST: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Login view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_setup():
    """Check if database is properly set up"""
    print("\n=== Checking Database Setup ===")
    
    try:
        # Check if user exists
        User = get_user_model()
        user = User.objects.filter(username='tenant').first()
        if user:
            print(f"✓ User exists: {user.username}")
        else:
            print("❌ User not found")
            return False
        
        # Check if tenant exists
        tenant = Tenant.objects.filter(name='Demo Tenant').first()
        if tenant:
            print(f"✓ Tenant exists: {tenant.name}")
        else:
            print("❌ Tenant not found")
            return False
        
        # Check tenant-user relationship
        tenant_user = TenantUser.objects.filter(user=user, tenant=tenant).first()
        if tenant_user:
            print(f"✓ TenantUser relationship exists")
        else:
            print("❌ TenantUser relationship not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 TESTING LOGIN ERROR LOCALLY")
    print("=" * 50)
    
    # Test 1: Database setup
    if not check_database_setup():
        print("\n❌ Database setup check failed")
        return False
    
    # Test 2: Direct authentication
    if not test_authentication_directly():
        print("\n❌ Direct authentication failed")
        return False
    
    # Test 3: Login view directly
    if not test_login_view_directly():
        print("\n❌ Login view test failed")
        return False
    
    # Test 4: Login error
    if not test_login_error():
        print("\n❌ Login error test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! All tests passed!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
