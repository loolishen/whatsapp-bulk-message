#!/usr/bin/env python
"""
Get the real error from App Engine logs
"""

import subprocess
import requests
import time
import json
import sys

def get_app_engine_logs():
    """Get detailed logs from App Engine"""
    print("=== Getting App Engine Logs ===")
    
    try:
        # Get recent logs with more detail
        result = subprocess.run([
            'gcloud', 'app', 'logs', 'read', 
            '--service=default', 
            '--limit=100',
            '--format=json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to get logs: {result.stderr}")
            return None
        
        logs = json.loads(result.stdout)
        
        # Filter for error logs
        error_logs = []
        for log in logs:
            if 'severity' in log and log['severity'] in ['ERROR', 'CRITICAL']:
                error_logs.append(log)
            elif 'textPayload' in log and ('error' in log['textPayload'].lower() or 'exception' in log['textPayload'].lower()):
                error_logs.append(log)
        
        print(f"Found {len(error_logs)} error logs")
        
        # Show recent error logs
        for i, log in enumerate(error_logs[-10:]):  # Last 10 errors
            print(f"\n--- Error {i+1} ---")
            print(f"Time: {log.get('timestamp', 'Unknown')}")
            print(f"Severity: {log.get('severity', 'Unknown')}")
            print(f"Text: {log.get('textPayload', 'No text payload')}")
            if 'jsonPayload' in log:
                print(f"JSON: {log['jsonPayload']}")
        
        return error_logs
        
    except Exception as e:
        print(f"❌ Get logs failed: {e}")
        return None

def trigger_login_error():
    """Trigger a login error to get fresh logs"""
    print("\n=== Triggering Login Error ===")
    
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
            print("✓ 500 error triggered - checking logs...")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Trigger login error failed: {e}")
        return False

def check_django_debug():
    """Check if Django debug is enabled"""
    print("\n=== Checking Django Debug Settings ===")
    
    try:
        # Check settings_production.py
        with open('whatsapp_bulk/settings_production.py', 'r') as f:
            content = f.read()
        
        if 'DEBUG = True' in content:
            print("❌ DEBUG is True in production settings")
            return False
        elif 'DEBUG = False' in content:
            print("✓ DEBUG is False in production settings")
            return True
        else:
            print("❓ DEBUG setting not found")
            return False
            
    except Exception as e:
        print(f"❌ Check Django debug failed: {e}")
        return False

def enable_django_debug():
    """Enable Django debug temporarily to get detailed errors"""
    print("\n=== Enabling Django Debug Temporarily ===")
    
    try:
        # Read current settings
        with open('whatsapp_bulk/settings_production.py', 'r') as f:
            content = f.read()
        
        # Replace DEBUG = False with DEBUG = True
        if 'DEBUG = False' in content:
            content = content.replace('DEBUG = False', 'DEBUG = True')
            
            # Write back
            with open('whatsapp_bulk/settings_production.py', 'w') as f:
                f.write(content)
            
            print("✓ DEBUG enabled temporarily")
            return True
        else:
            print("❌ DEBUG setting not found to modify")
            return False
            
    except Exception as e:
        print(f"❌ Enable Django debug failed: {e}")
        return False

def deploy_with_debug():
    """Deploy with debug enabled"""
    print("\n=== Deploying with Debug Enabled ===")
    
    try:
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Enable debug for error diagnosis'], capture_output=True, text=True)
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
        print(f"❌ Deploy with debug failed: {e}")
        return False

def test_with_debug():
    """Test with debug enabled to get detailed error"""
    print("\n=== Testing with Debug Enabled ===")
    
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
        print(f"Status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ Still getting 500 error")
            print(f"Response: {response.text}")
            
            # Get fresh logs
            print("\nGetting fresh logs...")
            error_logs = get_app_engine_logs()
            
            if error_logs:
                print(f"\nFound {len(error_logs)} error logs")
                return False
            else:
                print("No error logs found")
                return False
        else:
            print(f"✓ Status changed to: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Test with debug failed: {e}")
        return False

def main():
    print("🔍 GETTING REAL ERROR FROM APP ENGINE")
    print("=" * 50)
    
    # Step 1: Get current logs
    print("Step 1: Getting current error logs...")
    error_logs = get_app_engine_logs()
    
    # Step 2: Trigger a fresh error
    print("\nStep 2: Triggering fresh error...")
    if not trigger_login_error():
        print("❌ Failed to trigger error")
        return False
    
    # Step 3: Get fresh logs
    print("\nStep 3: Getting fresh logs...")
    time.sleep(5)  # Wait for logs to appear
    error_logs = get_app_engine_logs()
    
    # Step 4: Enable debug if needed
    print("\nStep 4: Checking debug settings...")
    if not check_django_debug():
        print("Enabling debug temporarily...")
        if enable_django_debug():
            if deploy_with_debug():
                test_with_debug()
    
    print("\n" + "=" * 50)
    print("🔍 ERROR DIAGNOSIS COMPLETE")
    print("=" * 50)
    print("Check the error logs above to see the real issue!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
