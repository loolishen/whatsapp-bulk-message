#!/usr/bin/env python
"""
Check App Engine logs to see what's causing the 500 error
"""

import subprocess
import requests
import time

def check_app_engine_logs():
    """Check App Engine logs for errors"""
    print("=== Checking App Engine Logs ===")
    
    try:
        # Get recent logs
        print("1. Getting recent App Engine logs...")
        result = subprocess.run(['gcloud', 'app', 'logs', 'read', '--service=default', '--limit=20'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Logs retrieved successfully")
            print("\nRecent logs:")
            print(result.stdout)
        else:
            print(f"❌ Failed to get logs: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Check App Engine logs failed: {e}")
        return False

def test_login_with_detailed_error():
    """Test login and capture detailed error"""
    print("\n=== Testing Login with Detailed Error ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test login POST with detailed error capture
        print("Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ 500 error on login")
            print(f"Response: {response.text}")
            
            # Check if there are any error details in the response
            if 'error' in response.text.lower() or 'exception' in response.text.lower():
                print("Error details found in response")
            else:
                print("No error details in response - check App Engine logs")
            
            return False
        else:
            print(f"✓ Login successful: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Test login with detailed error failed: {e}")
        return False

def check_deployed_code():
    """Check what code is actually deployed"""
    print("\n=== Checking Deployed Code ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
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
        
        # Check if the form action is correct
        print("3. Checking form action...")
        if 'method="post"' in response.text:
            print("   ✓ Form method is POST")
        else:
            print("   ❌ Form method not POST")
        
        return True
        
    except Exception as e:
        print(f"❌ Check deployed code failed: {e}")
        return False

def force_deploy_with_logs():
    """Force deploy and check logs"""
    print("\n=== Force Deploy with Logs ===")
    
    try:
        import time
        
        # Create timestamp file
        timestamp = str(int(time.time() * 1000))
        with open('debug_deploy.txt', 'w') as f:
            f.write(f"Debug deploy: {timestamp}")
        
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', f'Debug deploy - {timestamp}'], capture_output=True, text=True)
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
            
            # Wait for deployment
            print("Waiting for deployment to propagate...")
            time.sleep(30)
            
            # Check logs after deployment
            print("Checking logs after deployment...")
            result = subprocess.run(['gcloud', 'app', 'logs', 'read', '--service=default', '--limit=10'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Recent logs after deployment:")
                print(result.stdout)
            
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Force deploy with logs failed: {e}")
        return False

def main():
    print("🔍 CHECKING APP ENGINE LOGS AND DEBUGGING 500 ERROR")
    print("=" * 50)
    
    # Step 1: Check deployed code
    if not check_deployed_code():
        print("\n❌ Check deployed code failed")
        return False
    
    # Step 2: Test login with detailed error
    if not test_login_with_detailed_error():
        print("\n❌ Test login with detailed error failed")
    
    # Step 3: Check App Engine logs
    if not check_app_engine_logs():
        print("\n❌ Check App Engine logs failed")
        return False
    
    # Step 4: Force deploy with logs
    if not force_deploy_with_logs():
        print("\n❌ Force deploy with logs failed")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Log checking and debugging complete!")
    print("=" * 50)
    print("Check the logs above for the specific error details.")
    print("The 500 error is likely caused by a missing import or configuration issue.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    main()
