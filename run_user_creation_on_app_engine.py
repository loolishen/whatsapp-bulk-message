#!/usr/bin/env python
"""
Run user creation command on App Engine
"""

import subprocess
import sys
import time

def run_user_creation_on_app_engine():
    """Run user creation command on App Engine"""
    print("RUNNING USER CREATION ON APP ENGINE")
    print("=" * 50)
    
    try:
        # Run the management command on App Engine
        cmd = ['gcloud', 'app', 'services', 'exec', 'default', '--', 'python', 'manage.py', 'ensure_production_user']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] User creation command executed successfully")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] User creation command failed: {result.stderr}")
            print("Command output:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to run user creation command: {e}")
        return False

def test_production_login():
    """Test production login after user creation"""
    print("\nTESTING PRODUCTION LOGIN")
    print("=" * 50)
    
    # Wait a bit for the command to complete
    print("Waiting for user creation to complete...")
    time.sleep(30)
    
    try:
        import requests
        
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
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
                return False
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test login failed: {e}")
        return False

def main():
    print("RUNNING USER CREATION ON APP ENGINE")
    print("=" * 50)
    
    # Step 1: Run user creation on App Engine
    if not run_user_creation_on_app_engine():
        print("[ERROR] User creation failed")
        return False
    
    # Step 2: Test login
    if not test_production_login():
        print("[ERROR] Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS! User creation and login working!")
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
