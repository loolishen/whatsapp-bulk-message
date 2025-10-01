#!/usr/bin/env python
"""
Test if the user exists in the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def test_user_exists():
    """Test if the user exists and can be authenticated"""
    print("🔍 TESTING USER EXISTS")
    print("=" * 50)
    
    try:
        # Check if user exists
        username = 'tenant'
        password = 'Tenant123!'
        
        print(f"Checking if user '{username}' exists...")
        try:
            user = User.objects.get(username=username)
            print(f"✓ User exists: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Is active: {user.is_active}")
            print(f"  - Is staff: {user.is_staff}")
            print(f"  - Is superuser: {user.is_superuser}")
            print(f"  - Date joined: {user.date_joined}")
            print(f"  - Last login: {user.last_login}")
        except User.DoesNotExist:
            print(f"❌ User '{username}' does not exist")
            return False
        
        # Test authentication
        print(f"\nTesting authentication...")
        user = authenticate(username=username, password=password)
        if user:
            print(f"✓ Authentication successful: {user.username}")
            return True
        else:
            print(f"❌ Authentication failed for '{username}'")
            return False
            
    except Exception as e:
        print(f"❌ Test user exists failed: {e}")
        return False

def create_test_user():
    """Create the test user if it doesn't exist"""
    print("\n🔧 CREATING TEST USER")
    print("=" * 50)
    
    try:
        username = 'tenant'
        password = 'Tenant123!'
        email = 'tenant@example.com'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists")
            return True
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_active = True
        user.save()
        
        print(f"✓ User '{username}' created successfully")
        
        # Test authentication
        user = authenticate(username=username, password=password)
        if user:
            print(f"✓ Authentication test successful")
            return True
        else:
            print(f"❌ Authentication test failed")
            return False
            
    except Exception as e:
        print(f"❌ Create test user failed: {e}")
        return False

def main():
    print("🔍 TESTING USER AUTHENTICATION")
    print("=" * 50)
    
    # Test if user exists
    if not test_user_exists():
        print("\nUser doesn't exist, creating...")
        if not create_test_user():
            print("❌ Failed to create user")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! User authentication working!")
    print("=" * 50)
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
