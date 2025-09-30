#!/usr/bin/env python
"""
Test production deployment
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

def test_production_setup():
    """Test production setup"""
    print("=== Testing Production Setup ===")
    
    try:
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✓ Database connection: {result}")
        
        # Test user exists
        User = get_user_model()
        user = User.objects.filter(username='tenant').first()
        if user:
            print(f"✓ User exists: {user.username}")
        else:
            print("❌ User not found")
            return False
        
        # Test tenant exists
        tenant = Tenant.objects.filter(name='Demo Tenant').first()
        if tenant:
            print(f"✓ Tenant exists: {tenant.name}")
        else:
            print("❌ Tenant not found")
            return False
        
        # Test tenant-user relationship
        tenant_user = TenantUser.objects.filter(user=user, tenant=tenant).first()
        if tenant_user:
            print(f"✓ TenantUser relationship exists: {user.username} @ {tenant.name}")
        else:
            print("❌ TenantUser relationship not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Production setup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_endpoints():
    """Test login endpoints"""
    print("\n=== Testing Login Endpoints ===")
    
    try:
        client = Client()
        
        # Test GET /login/
        response = client.get('/login/', HTTP_HOST='testserver')
        print(f"GET /login/ status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login page accessible")
        else:
            print(f"❌ Login page failed: {response.status_code}")
            return False
        
        # Test POST /login/ with correct credentials
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
            'csrfmiddlewaretoken': 'test'
        }, HTTP_HOST='testserver')
        
        print(f"POST /login/ status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login successful - redirected")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login endpoints test failed: {e}")
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
        print(f"✓ STATIC_URL: {settings.STATIC_URL}")
        print(f"✓ STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"✓ LOGIN_URL: {settings.LOGIN_URL}")
        print(f"✓ LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
        
        # Check if static files directory exists
        if os.path.exists(settings.STATIC_ROOT):
            print(f"✓ Static files directory exists: {settings.STATIC_ROOT}")
        else:
            print(f"❌ Static files directory missing: {settings.STATIC_ROOT}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Django settings test failed: {e}")
        return False

def main():
    print("🧪 TESTING PRODUCTION DEPLOYMENT")
    print("=" * 50)
    
    # Test 1: Django settings
    if not test_django_settings():
        print("\n❌ Django settings test failed")
        return False
    
    # Test 2: Production setup
    if not test_production_setup():
        print("\n❌ Production setup test failed")
        return False
    
    # Test 3: Login endpoints
    if not test_login_endpoints():
        print("\n❌ Login endpoints test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Production deployment is working!")
    print("=" * 50)
    print("You can now deploy to GCP with confidence!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

