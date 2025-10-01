#!/usr/bin/env python
"""
Deploy the URL fix for dashboard redirect
"""

import subprocess
import requests
import time
import sys

def deploy_url_fix():
    """Deploy the URL fix"""
    print("🔧 DEPLOYING URL FIX FOR DASHBOARD REDIRECT")
    print("=" * 50)
    
    try:
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Fix dashboard URL redirect - point to actual dashboard view'], capture_output=True, text=True)
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
        print(f"❌ Deploy URL fix failed: {e}")
        return False

def test_url_fix():
    """Test the URL fix"""
    print("\n=== Testing URL Fix ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment
        print("Waiting for deployment to propagate...")
        time.sleep(30)
        
        # Test login POST
        print("Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"✓ Login successful - redirecting to: {redirect_url}")
            
            # Follow the redirect
            print("Following redirect...")
            dashboard_response = requests.get(f"{base_url}{redirect_url}", timeout=10)
            print(f"Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✓ Dashboard accessible after login!")
                return True
            else:
                print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Test URL fix failed: {e}")
        return False

def main():
    print("🔧 FIXING DASHBOARD URL REDIRECT")
    print("=" * 50)
    
    # Deploy URL fix
    if not deploy_url_fix():
        print("❌ Deploy URL fix failed")
        return False
    
    # Test URL fix
    if not test_url_fix():
        print("❌ Test URL fix failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Dashboard redirect fixed!")
    print("=" * 50)
    print("Your login should now work properly:")
    print("1. Login at: https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("2. Username: tenant")
    print("3. Password: Tenant123!")
    print("4. Should redirect to dashboard after login")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
