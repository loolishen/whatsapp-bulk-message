#!/usr/bin/env python
"""
Check deployed logs to see what's happening with login
"""

import subprocess
import requests
import time
import sys

def check_app_engine_logs():
    """Check App Engine logs for login errors"""
    print("=== Checking App Engine Logs ===")
    
    try:
        # Get recent logs
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=50'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to get logs: {result.stderr}")
            return None
        
        logs = result.stdout
        print("Recent logs:")
        print(logs)
        
        # Look for login-related logs
        login_logs = []
        for line in logs.split('\n'):
            if 'login' in line.lower() or 'authentication' in line.lower() or 'tenant' in line.lower():
                login_logs.append(line)
        
        if login_logs:
            print(f"\n=== Found {len(login_logs)} Login-Related Logs ===")
            for i, line in enumerate(login_logs[-10:]):
                print(f"{i+1}. {line}")
        else:
            print("No login-related logs found")
        
        return login_logs
        
    except Exception as e:
        print(f"Check App Engine logs failed: {e}")
        return None

def trigger_login_and_check_logs():
    """Trigger a login and immediately check logs"""
    print("\n=== Triggering Login and Checking Logs ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Make a login POST request
        print("Making login POST request...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        # Wait a moment for logs to appear
        print("Waiting for logs to appear...")
        time.sleep(5)
        
        # Get fresh logs
        print("Getting fresh logs...")
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=20'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = result.stdout
            print("Fresh logs after login attempt:")
            print(logs)
            
            # Look for our debug messages
            debug_logs = []
            for line in logs.split('\n'):
                if 'Login attempt' in line or 'Authentication result' in line or 'Login successful' in line or 'Login failed' in line:
                    debug_logs.append(line)
            
            if debug_logs:
                print(f"\n=== Found {len(debug_logs)} Debug Logs ===")
                for i, line in enumerate(debug_logs):
                    print(f"{i+1}. {line}")
            else:
                print("No debug logs found - our logging might not be working")
        else:
            print(f"Failed to get fresh logs: {result.stderr}")
        
        return response.status_code == 302
        
    except Exception as e:
        print(f"Trigger login and check logs failed: {e}")
        return False

def test_different_credentials():
    """Test with different credentials to see if it's a user issue"""
    print("\n=== Testing Different Credentials ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test with wrong password
        print("Testing with wrong password...")
        login_data = {
            'username': 'tenant',
            'password': 'wrongpassword',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Wrong password status: {response.status_code}")
        
        if response.status_code == 200 and 'Invalid credentials' in response.text:
            print("✓ Wrong password correctly shows 'Invalid credentials'")
        else:
            print("❌ Wrong password not handled correctly")
        
        # Test with wrong username
        print("Testing with wrong username...")
        login_data = {
            'username': 'wronguser',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Wrong username status: {response.status_code}")
        
        if response.status_code == 200 and 'Invalid credentials' in response.text:
            print("✓ Wrong username correctly shows 'Invalid credentials'")
        else:
            print("❌ Wrong username not handled correctly")
        
        return True
        
    except Exception as e:
        print(f"Test different credentials failed: {e}")
        return False

def main():
    print("CHECKING DEPLOYED LOGIN LOGS")
    print("=" * 50)
    
    # Check current logs
    check_app_engine_logs()
    
    # Trigger login and check logs
    if not trigger_login_and_check_logs():
        print("Login still not working")
    
    # Test different credentials
    test_different_credentials()
    
    print("\n" + "=" * 50)
    print("LOG ANALYSIS COMPLETE")
    print("=" * 50)
    print("Check the logs above to see what's happening with login!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
