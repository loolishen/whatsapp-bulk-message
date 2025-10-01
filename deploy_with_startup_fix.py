#!/usr/bin/env python
"""
Deploy with startup fix to ensure user exists in App Engine database
"""

import subprocess
import requests
import time
import sys
import os

def deploy_to_app_engine():
    """Deploy to Google App Engine"""
    print("DEPLOYING TO APP ENGINE WITH STARTUP FIX")
    print("=" * 50)
    
    try:
        # Deploy to App Engine
        print("Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Deployment successful")
            print("Deployment output:")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Deployment failed: {result.stderr}")
            print("Deployment output:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"[ERROR] Deploy failed: {e}")
        return False

def test_production_login():
    """Test production login"""
    print("\nTESTING PRODUCTION LOGIN")
    print("=" * 50)
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment and startup
        print("Waiting for deployment to propagate and startup to complete...")
        time.sleep(60)  # Give more time for startup
        
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
            print(f"[OK] Login successful - redirecting to: {redirect_url}")
            
            # Follow the redirect
            print("Following redirect...")
            dashboard_response = requests.get(f"{base_url}{redirect_url}", timeout=10)
            print(f"Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("[OK] Dashboard accessible after login!")
                print("[OK] SUCCESS! Login and dashboard are working!")
                return True
            else:
                print(f"[ERROR] Dashboard failed: {dashboard_response.status_code}")
                print(f"Dashboard response: {dashboard_response.text[:500]}")
                return False
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test login failed: {e}")
        return False

def main():
    print("DEPLOYMENT WITH STARTUP FIX")
    print("=" * 50)
    
    # Step 1: Deploy to App Engine
    if not deploy_to_app_engine():
        print("[ERROR] Deployment failed")
        return False
    
    # Step 2: Test login
    if not test_production_login():
        print("[ERROR] Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! Deployment with startup fix successful!")
    print("=" * 50)
    print("Your app is fully functional at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
