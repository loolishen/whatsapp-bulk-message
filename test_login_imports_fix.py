#!/usr/bin/env python
"""
Test the login imports fix
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def test_login_imports_fix():
    """Test the login imports fix"""
    print("=== Testing Login Imports Fix ===")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Test 1: Get login page
        print("1. Testing login page...")
        response = client.get('/login/', HTTP_HOST='testserver')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test 2: Check for CSRF token
        print("2. Checking for CSRF token...")
        content = response.content.decode()
        if 'csrfmiddlewaretoken' in content:
            print("   ❌ CSRF token found")
            return False
        else:
            print("   ✓ CSRF token removed")
        
        # Test 3: Test login POST
        print("3. Testing login POST...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected!")
            print(f"   Redirect URL: {response.get('Location', 'N/A')}")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test login imports fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def deploy_login_imports_fix():
    """Deploy the login imports fix"""
    print("\n=== Deploying Login Imports Fix ===")
    
    try:
        import subprocess
        
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Fix missing imports in auth_login function'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        # Push changes
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✓ Changes pushed to GitHub")
        
        # Deploy to App Engine
        print("Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Deploy login imports fix failed: {e}")
        return False

def test_deployed_login_imports_fix():
    """Test the deployed login imports fix"""
    print("\n=== Testing Deployed Login Imports Fix ===")
    
    try:
        import requests
        import time
        
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment to propagate
        print("Waiting for deployment to propagate...")
        time.sleep(30)
        
        # Test login page
        print("1. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Check for CSRF token
        print("2. Checking for CSRF token...")
        if 'csrfmiddlewaretoken' in response.text:
            print("   ❌ CSRF token still present")
            return False
        else:
            print("   ✓ CSRF token removed")
        
        # Test login POST
        print("3. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected!")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            
            # Test dashboard access
            print("4. Testing dashboard access...")
            dashboard_response = requests.get(f"{base_url}/", cookies=response.cookies, timeout=10)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✓ Dashboard accessible")
                return True
            else:
                print(f"   ❌ Dashboard failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test deployed login imports fix failed: {e}")
        return False

def main():
    print("🔧 TESTING AND DEPLOYING LOGIN IMPORTS FIX")
    print("=" * 50)
    
    # Step 1: Test locally
    if not test_login_imports_fix():
        print("\n❌ Local test failed")
        return False
    
    # Step 2: Deploy
    if not deploy_login_imports_fix():
        print("\n❌ Deploy failed")
        return False
    
    # Step 3: Test deployed
    if not test_deployed_login_imports_fix():
        print("\n❌ Deployed test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login imports fix deployed and working!")
    print("=" * 50)
    print("Your login and dashboard should now work at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
