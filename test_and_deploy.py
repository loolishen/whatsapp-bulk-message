#!/usr/bin/env python
"""
Test user and deploy
"""

import subprocess
import requests
import time
import sys

def test_user_locally():
    """Test user authentication locally"""
    print("=== Testing User Locally ===")
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
        django.setup()
        
        from django.contrib.auth.models import User
        from django.contrib.auth import authenticate
        
        username = 'tenant'
        password = 'Tenant123!'
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            print(f"User exists: {user.username}, active: {user.is_active}")
        except User.DoesNotExist:
            print(f"User {username} does not exist - creating...")
            user = User.objects.create_user(username=username, password=password)
            user.is_active = True
            user.save()
            print(f"User {username} created")
        
        # Test authentication
        user = authenticate(username=username, password=password)
        if user:
            print(f"Authentication successful: {user.username}")
            return True
        else:
            print("Authentication failed")
            return False
            
    except Exception as e:
        print(f"Test user locally failed: {e}")
        return False

def deploy_to_app_engine():
    """Deploy to App Engine"""
    print("\n=== Deploying to App Engine ===")
    
    try:
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Deployment successful")
            return True
        else:
            print(f"Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Deploy to App Engine failed: {e}")
        return False

def test_deployed_login():
    """Test the deployed login"""
    print("\n=== Testing Deployed Login ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment
        print("Waiting for deployment...")
        time.sleep(30)
        
        # Test login POST
        print("Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            print("SUCCESS! Login working - returns 302 redirect")
            return True
        elif response.status_code == 200:
            print("Login returned 200 - checking for error message...")
            if 'Invalid credentials' in response.text:
                print("Error: Invalid credentials")
            elif 'Username and password are required' in response.text:
                print("Error: Missing username/password")
            else:
                print("Unknown error - showing response preview:")
                print(response.text[:300])
            return False
        else:
            print(f"Login failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Test deployed login failed: {e}")
        return False

def main():
    print("TESTING USER AND DEPLOYING")
    print("=" * 50)
    
    # Test user locally
    if not test_user_locally():
        print("Local user test failed")
        return False
    
    # Deploy to App Engine
    if not deploy_to_app_engine():
        print("Deploy to App Engine failed")
        return False
    
    # Test deployed login
    if not test_deployed_login():
        print("Deployed login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! Login is working!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
