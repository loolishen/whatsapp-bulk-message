#!/usr/bin/env python
"""
Check deployment logs to identify the 500 error
"""

import subprocess
import json

def get_app_logs():
    """Get recent logs from the deployed app"""
    print("=== Getting App Engine Logs ===")
    
    try:
        # Get recent logs
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=50',
            '--format=json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = json.loads(result.stdout)
            print(f"✓ Retrieved {len(logs)} log entries")
            
            # Filter for error logs
            error_logs = [log for log in logs if log.get('severity') in ['ERROR', 'CRITICAL']]
            if error_logs:
                print(f"\n=== Found {len(error_logs)} Error Logs ===")
                for log in error_logs[-10:]:  # Show last 10 errors
                    print(f"Time: {log.get('timestamp', 'N/A')}")
                    print(f"Severity: {log.get('severity', 'N/A')}")
                    print(f"Message: {log.get('textPayload', 'N/A')}")
                    print("-" * 50)
            else:
                print("✓ No error logs found")
            
            # Show recent logs
            print(f"\n=== Recent Logs (Last 10) ===")
            for log in logs[-10:]:
                print(f"Time: {log.get('timestamp', 'N/A')}")
                print(f"Severity: {log.get('severity', 'N/A')}")
                print(f"Message: {log.get('textPayload', 'N/A')}")
                print("-" * 30)
            
            return True
        else:
            print(f"❌ Failed to get logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return False

def get_detailed_logs():
    """Get detailed logs with more context"""
    print("\n=== Getting Detailed Logs ===")
    
    try:
        # Get logs with more details
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=100',
            '--format=value(timestamp,severity,textPayload)'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"✓ Retrieved {len(lines)} log lines")
            
            # Look for 500 errors specifically
            error_lines = [line for line in lines if '500' in line or 'ERROR' in line or 'Exception' in line]
            if error_lines:
                print(f"\n=== Found {len(error_lines)} Error Lines ===")
                for line in error_lines[-20:]:  # Show last 20 error lines
                    print(line)
            else:
                print("✓ No 500 errors found in recent logs")
            
            return True
        else:
            print(f"❌ Failed to get detailed logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting detailed logs: {e}")
        return False

def test_deployed_app():
    """Test the deployed app directly"""
    print("\n=== Testing Deployed App ===")
    
    try:
        import requests
        
        # Test the login page
        url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"GET /login/ status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login page accessible")
            
            # Test POST to login
            login_data = {
                'username': 'tenant',
                'password': 'Tenant123!',
                'csrfmiddlewaretoken': 'test'  # This will fail CSRF but we'll see the error
            }
            
            response = requests.post(url, data=login_data, timeout=10)
            print(f"POST /login/ status: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ 500 error confirmed on deployed app")
                print(f"Response content: {response.text[:500]}")
            else:
                print(f"✓ POST request returned: {response.status_code}")
            
        else:
            print(f"❌ Login page failed: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing deployed app: {e}")
        return False

def main():
    print("🔍 CHECKING DEPLOYMENT LOGS")
    print("=" * 50)
    
    # Step 1: Get app logs
    if not get_app_logs():
        print("\n❌ Failed to get app logs")
        return False
    
    # Step 2: Get detailed logs
    if not get_detailed_logs():
        print("\n❌ Failed to get detailed logs")
        return False
    
    # Step 3: Test deployed app
    if not test_deployed_app():
        print("\n❌ Failed to test deployed app")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Log analysis complete!")
    print("=" * 50)
    print("Check the error messages above to identify the issue.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
