#!/usr/bin/env python
"""
Test login with proper CSRF handling
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.test import Client
from django.urls import reverse

def test_login_with_csrf():
    """Test login with proper CSRF token"""
    print("=== Testing Login with CSRF ===")
    
    try:
        client = Client()
        
        # First, get the login page to get CSRF token
        print("Getting login page...")
        response = client.get('/login/')
        print(f"GET /login/ status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Login page failed: {response.status_code}")
            print(f"Response content: {response.content.decode()[:500]}")
            return False
        
        # Extract CSRF token from the response
        from django.middleware.csrf import get_token
        csrf_token = get_token(response.wsgi_request)
        print(f"✓ CSRF token obtained: {csrf_token[:20]}...")
        
        # Now test POST with proper CSRF token
        print("\nTesting POST with CSRF token...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
            'csrfmiddlewaretoken': csrf_token
        })
        
        print(f"POST /login/ status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login successful - redirected")
            print(f"Redirect URL: {response.url}")
            return True
        elif response.status_code == 500:
            print("❌ Login failed with 500 error")
            print(f"Response content: {response.content.decode()[:500]}")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response content: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ CSRF login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_routing():
    """Test URL routing"""
    print("\n=== Testing URL Routing ===")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test different URL patterns
        urls_to_test = [
            '/login/',
            '/login',
            '/',
        ]
        
        for url in urls_to_test:
            print(f"Testing URL: {url}")
            response = client.get(url)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✓ URL {url} works")
            elif response.status_code == 302:
                print(f"  ✓ URL {url} redirects (expected)")
            else:
                print(f"  ❌ URL {url} failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL routing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_settings():
    """Test Django settings"""
    print("\n=== Testing Django Settings ===")
    
    try:
        from django.conf import settings
        
        print(f"✓ DEBUG: {settings.DEBUG}")
        print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"✓ LOGIN_URL: {settings.LOGIN_URL}")
        print(f"✓ LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
        print(f"✓ ROOT_URLCONF: {settings.ROOT_URLCONF}")
        
        # Check if CSRF is enabled
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE
        print(f"✓ CSRF Middleware enabled: {csrf_middleware}")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False

def main():
    print("🔍 TESTING CSRF AND URL ROUTING")
    print("=" * 50)
    
    # Test 1: Django settings
    if not test_django_settings():
        print("\n❌ Settings test failed")
        return False
    
    # Test 2: URL routing
    if not test_url_routing():
        print("\n❌ URL routing test failed")
        return False
    
    # Test 3: CSRF login
    if not test_login_with_csrf():
        print("\n❌ CSRF login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! All tests passed!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
