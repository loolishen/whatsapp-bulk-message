#!/usr/bin/env python
"""
Deploy and fix database - complete solution
"""

import subprocess
import requests
import time
import sys
import os

def run_database_fix():
    """Run the database fix script"""
    print("FIXING PRODUCTION DATABASE")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'fix_gcp_database.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("[OK] Database fix successful")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Database fix failed: {result.stderr}")
            print("Database fix output:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"[ERROR] Database fix failed: {e}")
        return False

def deploy_to_app_engine():
    """Deploy to Google App Engine"""
    print("\nDEPLOYING TO APP ENGINE")
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
    print("COMPLETE DEPLOYMENT WITH DATABASE FIX")
    print("=" * 50)
    
    # Step 1: Fix database
    if not run_database_fix():
        print("[ERROR] Database fix failed")
        return False
    
    # Step 2: Deploy to App Engine
    if not deploy_to_app_engine():
        print("[ERROR] Deployment failed")
        return False
    
    # Step 3: Test login
    if not test_production_login():
        print("[ERROR] Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! Complete deployment successful!")
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
