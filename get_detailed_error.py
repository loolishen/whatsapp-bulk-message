#!/usr/bin/env python
"""
Get detailed error information from the deployed app
"""

import subprocess
import json

def get_app_logs():
    """Get detailed app logs"""
    print("=== Getting App Engine Logs ===")
    
    try:
        # Get recent logs
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=20',
            '--format=json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = json.loads(result.stdout)
            print(f"✓ Retrieved {len(logs)} log entries")
            
            # Show recent logs
            print(f"\n=== Recent Logs ===")
            for log in logs[-10:]:
                timestamp = log.get('timestamp', 'N/A')
                severity = log.get('severity', 'N/A')
                message = log.get('textPayload', 'N/A')
                print(f"Time: {timestamp}")
                print(f"Severity: {severity}")
                print(f"Message: {message}")
                print("-" * 50)
            
            return True
        else:
            print(f"❌ Failed to get logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return False

def get_error_logs():
    """Get error logs specifically"""
    print("\n=== Getting Error Logs ===")
    
    try:
        # Get logs with error filter
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=50',
            '--format=value(timestamp,severity,textPayload)'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"✓ Retrieved {len(lines)} log lines")
            
            # Filter for error lines
            error_lines = [line for line in lines if any(keyword in line.upper() for keyword in ['ERROR', 'EXCEPTION', 'TRACEBACK', '500'])]
            if error_lines:
                print(f"\n=== Found {len(error_lines)} Error Lines ===")
                for line in error_lines[-20:]:  # Show last 20 error lines
                    print(line)
            else:
                print("✓ No error lines found")
            
            return True
        else:
            print(f"❌ Failed to get error logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting error logs: {e}")
        return False

def test_login_with_debug():
    """Test login and capture detailed error"""
    print("\n=== Testing Login with Debug ===")
    
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
        print(f"Status: {response.status_code}")
        
        if response.status_code == 500:
            print("500 error confirmed - checking response details...")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response content: {response.text}")
            
            # Check if there's a traceback in the response
            if "Traceback" in response.text or "Exception" in response.text:
                print("\n=== Python Traceback Found ===")
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if "Traceback" in line or "Exception" in line or "Error" in line:
                        print(f"Line {i}: {line}")
                        # Show a few lines after the error
                        for j in range(1, 10):
                            if i + j < len(lines):
                                print(f"Line {i+j}: {lines[i + j]}")
                        break
        else:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 GETTING DETAILED ERROR INFORMATION")
    print("=" * 50)
    
    # Step 1: Get app logs
    get_app_logs()
    
    # Step 2: Get error logs
    get_error_logs()
    
    # Step 3: Test login with debug
    test_login_with_debug()
    
    print("\n" + "=" * 50)
    print("🔍 Error analysis complete!")
    print("=" * 50)
    print("Check the output above for the specific error details.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    main()
