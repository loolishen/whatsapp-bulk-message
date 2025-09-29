#!/usr/bin/env python
"""
Test with proper Host header
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.test import Client
from django.conf import settings

def test_with_host_header():
    """Test with proper Host header"""
    print("=== Testing with Host Header ===")
    
    try:
        client = Client()
        
        # Test with proper Host header
        print("Testing with Host header...")
        response = client.get('/login/', HTTP_HOST='whatsapp-bulk-messaging-473607.as.r.appspot.com')
        print(f"GET /login/ with Host header status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login page works with Host header")
            return True
        else:
            print(f"❌ Login page failed: {response.status_code}")
            print(f"Response content: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Host header test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_allowed_hosts():
    """Test ALLOWED_HOSTS configuration"""
    print("\n=== Testing ALLOWED_HOSTS ===")
    
    try:
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Test different host patterns
        hosts_to_test = [
            'whatsapp-bulk-messaging-473607.as.r.appspot.com',
            'localhost',
            '127.0.0.1',
            'testserver',  # Django test default
        ]
        
        client = Client()
        
        for host in hosts_to_test:
            print(f"Testing with Host: {host}")
            response = client.get('/login/', HTTP_HOST=host)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✓ Host {host} works")
                return True
            else:
                print(f"  ❌ Host {host} failed: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ ALLOWED_HOSTS test failed: {e}")
        return False

def test_django_urls():
    """Test Django URL configuration"""
    print("\n=== Testing Django URL Configuration ===")
    
    try:
        from django.urls import reverse, resolve
        from django.test import RequestFactory
        
        # Test URL resolution
        print("Testing URL resolution...")
        try:
            login_url = reverse('auth_login')
            print(f"✓ auth_login URL: {login_url}")
        except Exception as e:
            print(f"❌ auth_login URL resolution failed: {e}")
            return False
        
        try:
            dashboard_url = reverse('dashboard')
            print(f"✓ dashboard URL: {dashboard_url}")
        except Exception as e:
            print(f"❌ dashboard URL resolution failed: {e}")
            return False
        
        # Test URL patterns
        print("\nTesting URL patterns...")
        from messaging.urls import urlpatterns
        
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name:
                print(f"  - {pattern.name}: {pattern.pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django URLs test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_settings():
    """Test Django settings in detail"""
    print("\n=== Testing Django Settings in Detail ===")
    
    try:
        print(f"DEBUG: {settings.DEBUG}")
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
        print(f"MIDDLEWARE: {settings.MIDDLEWARE}")
        print(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
        
        # Check if the app is properly configured
        if 'messaging' in settings.INSTALLED_APPS:
            print("✓ messaging app is installed")
        else:
            print("❌ messaging app is not installed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Django settings test failed: {e}")
        return False

def main():
    print("🔍 TESTING WITH PROPER HOST HEADER")
    print("=" * 50)
    
    # Test 1: Django settings
    if not test_django_settings():
        print("\n❌ Django settings test failed")
        return False
    
    # Test 2: Django URLs
    if not test_django_urls():
        print("\n❌ Django URLs test failed")
        return False
    
    # Test 3: ALLOWED_HOSTS
    if not test_allowed_hosts():
        print("\n❌ ALLOWED_HOSTS test failed")
        return False
    
    # Test 4: Host header
    if not test_with_host_header():
        print("\n❌ Host header test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! All tests passed!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
