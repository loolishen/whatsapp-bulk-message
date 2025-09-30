#!/usr/bin/env python
"""
Test to isolate whether the error is in login or dashboard
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def test_login_function_directly():
    """Test the login function directly without redirect"""
    print("=== Testing Login Function Directly ===")
    
    try:
        from django.test import Client
        from django.test import RequestFactory
        from messaging.views import auth_login
        
        # Test 1: Test with Django test client
        print("1. Testing with Django test client...")
        client = Client()
        
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login function works - returns 302 redirect")
            redirect_url = response.get('Location', 'N/A')
            print(f"   Redirect URL: {redirect_url}")
            
            # Test 2: Test dashboard access after login
            print("2. Testing dashboard access after login...")
            dashboard_response = client.get('/', HTTP_HOST='testserver')
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✓ Dashboard accessible after login")
                return True
            else:
                print(f"   ❌ Dashboard failed: {dashboard_response.status_code}")
                print(f"   Dashboard Response: {dashboard_response.content.decode()[:500]}")
                return False
        else:
            print(f"   ❌ Login function failed: {response.status_code}")
            print(f"   Login Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test login function directly failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_function_directly():
    """Test the dashboard function directly"""
    print("\n=== Testing Dashboard Function Directly ===")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from messaging.views import dashboard, _get_tenant
        
        # Create a mock request with authenticated user
        factory = RequestFactory()
        request = factory.get('/')
        
        # Get the tenant user
        user = User.objects.get(username='tenant')
        request.user = user
        
        # Test _get_tenant function
        print("1. Testing _get_tenant function...")
        tenant = _get_tenant(request)
        if tenant:
            print(f"   ✓ _get_tenant works: {tenant.name}")
        else:
            print("   ❌ _get_tenant failed")
            return False
        
        # Test dashboard function
        print("2. Testing dashboard function...")
        try:
            response = dashboard(request)
            print(f"   ✓ Dashboard function works: {response.status_code}")
            return True
        except Exception as e:
            print(f"   ❌ Dashboard function failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Test dashboard function directly failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_without_redirect():
    """Test login without redirect to see if it's the redirect causing the issue"""
    print("\n=== Testing Login Without Redirect ===")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from messaging.views import auth_login
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        })
        request.META['HTTP_HOST'] = 'testserver'
        
        # Add session middleware
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        auth_middleware = AuthenticationMiddleware(lambda req: None)
        auth_middleware.process_request(request)
        
        # Test the auth_login function directly
        print("Testing auth_login function directly...")
        try:
            response = auth_login(request)
            print(f"✓ auth_login function works: {response.status_code}")
            
            if hasattr(response, 'status_code') and response.status_code == 302:
                print("✓ Login function returns redirect as expected")
                return True
            else:
                print(f"❌ Login function returned unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ auth_login function failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Test login without redirect failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_deployed_login_vs_dashboard():
    """Test deployed app to see if it's login or dashboard"""
    print("\n=== Testing Deployed Login vs Dashboard ===")
    
    try:
        import requests
        
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test 1: Login page
        print("1. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test 2: Login POST
        print("2. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login POST successful - redirected")
            redirect_url = response.headers.get('Location', 'N/A')
            print(f"   Redirect URL: {redirect_url}")
            
            # Test 3: Dashboard access
            print("3. Testing dashboard access...")
            dashboard_response = requests.get(f"{base_url}/", cookies=response.cookies, timeout=10)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✓ Dashboard accessible")
                return True
            else:
                print(f"   ❌ Dashboard failed: {dashboard_response.status_code}")
                print(f"   Dashboard Response: {dashboard_response.text[:500]}")
                return False
        else:
            print(f"   ❌ Login POST failed: {response.status_code}")
            print(f"   Login Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test deployed login vs dashboard failed: {e}")
        return False

def main():
    print("🔍 TESTING LOGIN VS DASHBOARD ERROR")
    print("=" * 50)
    
    # Step 1: Test login function directly
    if not test_login_function_directly():
        print("\n❌ Test login function directly failed")
        return False
    
    # Step 2: Test dashboard function directly
    if not test_dashboard_function_directly():
        print("\n❌ Test dashboard function directly failed")
        return False
    
    # Step 3: Test login without redirect
    if not test_login_without_redirect():
        print("\n❌ Test login without redirect failed")
        return False
    
    # Step 4: Test deployed app
    if not test_deployed_login_vs_dashboard():
        print("\n❌ Test deployed login vs dashboard failed")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Login vs Dashboard testing complete!")
    print("=" * 50)
    print("This will help identify whether the error is in:")
    print("1. The login function itself")
    print("2. The dashboard function")
    print("3. The redirect process")
    print("4. The deployed environment")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
