#!/usr/bin/env python
"""
Test script to verify login functionality
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

def test_login():
    """Test login functionality"""
    print("=== Testing Login Functionality ===")
    
    try:
        User = get_user_model()
        
        # Test user authentication
        user = authenticate(username='tenant', password='Tenant123!')
        
        if user:
            print(f"✓ Login successful for user: {user.username}")
            print(f"✓ User email: {user.email}")
            print(f"✓ User is active: {user.is_active}")
            return True
        else:
            print("✗ Login failed - invalid credentials")
            return False
            
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        return False

def test_user_exists():
    """Test if user exists in database"""
    print("=== Testing User Existence ===")
    
    try:
        User = get_user_model()
        
        # Check if user exists
        users = User.objects.filter(username='tenant')
        if users.exists():
            user = users.first()
            print(f"✓ User found: {user.username}")
            print(f"✓ User email: {user.email}")
            print(f"✓ User is active: {user.is_active}")
            return True
        else:
            print("✗ User not found in database")
            return False
            
    except Exception as e:
        print(f"✗ User existence test failed: {e}")
        return False

def main():
    print("🧪 Testing Login Functionality")
    print("=" * 50)
    
    # Test 1: Check if user exists
    if not test_user_exists():
        print("\n❌ User does not exist - run deploy_setup.py first")
        return False
    
    # Test 2: Test login
    if not test_login():
        print("\n❌ Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login functionality is working!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
