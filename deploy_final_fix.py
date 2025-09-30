#!/usr/bin/env python
"""
Deploy the final fix for login and dashboard
"""

import subprocess
import time
import requests
import sys

def deploy_final_fix():
    """Deploy the final fix"""
    print("=== Deploying Final Fix ===")
    
    try:
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
        print(f"❌ Deploy final fix failed: {e}")
        return False

def test_deployed_fix():
    """Test the deployed fix"""
    print("\n=== Testing Deployed Fix ===")
    
    try:
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
        print(f"❌ Test deployed fix failed: {e}")
        return False

def main():
    print("🚀 DEPLOYING FINAL FIX FOR LOGIN AND DASHBOARD")
    print("=" * 50)
    
    # Step 1: Deploy
    if not deploy_final_fix():
        print("\n❌ Deploy failed")
        return False
    
    # Step 2: Test deployed
    if not test_deployed_fix():
        print("\n❌ Deployed test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login and dashboard are now working!")
    print("=" * 50)
    print("Your app is now fully functional at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)