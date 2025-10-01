#!/usr/bin/env python
"""
Get simple logs from App Engine
"""

import subprocess
import requests
import time
import sys

def get_simple_logs():
    """Get logs in simple text format"""
    print("=== Getting Simple App Engine Logs ===")
    
    try:
        # Get recent logs in text format
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=50'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to get logs: {result.stderr}")
            return None
        
        logs = result.stdout
        print("Raw logs:")
        print(logs)
        
        # Look for error patterns
        error_lines = []
        for line in logs.split('\n'):
            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed', '500']):
                error_lines.append(line)
        
        if error_lines:
            print(f"\n=== Found {len(error_lines)} Error Lines ===")
            for i, line in enumerate(error_lines[-10:]):  # Last 10 errors
                print(f"{i+1}. {line}")
        else:
            print("No error lines found")
        
        return error_lines
        
    except Exception as e:
        print(f"❌ Get simple logs failed: {e}")
        return None

def get_detailed_logs():
    """Get more detailed logs"""
    print("\n=== Getting Detailed Logs ===")
    
    try:
        # Get logs with more detail
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=100',
            '--severity=ERROR'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to get detailed logs: {result.stderr}")
            return None
        
        logs = result.stdout
        print("Detailed error logs:")
        print(logs)
        
        return logs
        
    except Exception as e:
        print(f"❌ Get detailed logs failed: {e}")
        return None

def trigger_and_capture():
    """Trigger error and capture logs immediately"""
    print("\n=== Triggering Error and Capturing Logs ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Make a login POST request
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        print("Making login POST request...")
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 500:
            print("✓ 500 error triggered")
            
            # Wait a moment for logs to appear
            print("Waiting for logs to appear...")
            time.sleep(3)
            
            # Get logs immediately
            print("Getting logs immediately...")
            logs = get_simple_logs()
            
            if logs:
                print("✓ Logs captured")
                return True
            else:
                print("❌ No logs captured")
                return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Trigger and capture failed: {e}")
        return False

def check_app_engine_status():
    """Check App Engine service status"""
    print("\n=== Checking App Engine Status ===")
    
    try:
        result = subprocess.run([
            'gcloud', 'app', 'services', 'list'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("App Engine services:")
            print(result.stdout)
        else:
            print(f"❌ Failed to get services: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Check App Engine status failed: {e}")

def check_app_versions():
    """Check App Engine versions"""
    print("\n=== Checking App Engine Versions ===")
    
    try:
        result = subprocess.run([
            'gcloud', 'app', 'versions', 'list'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("App Engine versions:")
            print(result.stdout)
        else:
            print(f"❌ Failed to get versions: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Check App Engine versions failed: {e}")

def main():
    print("🔍 GETTING SIMPLE LOGS FROM APP ENGINE")
    print("=" * 50)
    
    # Step 1: Check App Engine status
    check_app_engine_status()
    
    # Step 2: Check versions
    check_app_versions()
    
    # Step 3: Get current logs
    print("\nStep 1: Getting current logs...")
    get_simple_logs()
    
    # Step 4: Get detailed error logs
    print("\nStep 2: Getting detailed error logs...")
    get_detailed_logs()
    
    # Step 5: Trigger error and capture
    print("\nStep 3: Triggering error and capturing logs...")
    trigger_and_capture()
    
    print("\n" + "=" * 50)
    print("🔍 LOG ANALYSIS COMPLETE")
    print("=" * 50)
    print("Check the logs above to see the real issue!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
