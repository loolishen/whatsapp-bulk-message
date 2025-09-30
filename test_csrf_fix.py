#!/usr/bin/env python
"""
Test the CSRF fix locally and then deploy
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def test_csrf_fix_locally():
    """Test the CSRF fix locally"""
    print("=== Testing CSRF Fix Locally ===")
    
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
        if 'csrfmiddlewaretoken' in response.content.decode():
            print("   ❌ CSRF token found - @csrf_exempt not working")
            return False
        else:
            print("   ✓ CSRF token removed - @csrf_exempt working")
        
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
        print(f"❌ Test CSRF fix locally failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def deploy_csrf_fix():
    """Deploy the CSRF fix"""
    print("\n=== Deploying CSRF Fix ===")
    
    try:
        import subprocess
        import time
        
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Fix duplicate @csrf_exempt decorator'], capture_output=True, text=True)
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
        print(f"❌ Deploy CSRF fix failed: {e}")
        return False

def test_deployed_csrf_fix():
    """Test the deployed CSRF fix"""
    print("\n=== Testing Deployed CSRF Fix ===")
    
    try:
        import requests
        
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
            print("   ❌ CSRF token still present - @csrf_exempt not working")
            return False
        else:
            print("   ✓ CSRF token removed - @csrf_exempt working")
        
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
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test deployed CSRF fix failed: {e}")
        return False

def main():
    print("🔧 TESTING AND DEPLOYING CSRF FIX")
    print("=" * 50)
    
    # Step 1: Test locally
    if not test_csrf_fix_locally():
        print("\n❌ Local test failed")
        return False
    
    # Step 2: Deploy fix
    if not deploy_csrf_fix():
        print("\n❌ Deploy failed")
        return False
    
    # Step 3: Test deployed fix
    if not test_deployed_csrf_fix():
        print("\n❌ Deployed test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! CSRF fix deployed and working!")
    print("=" * 50)
    print("Your login should now work at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
