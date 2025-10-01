#!/usr/bin/env python
"""
Check App Engine logs for errors
"""

import subprocess
import sys

def check_app_engine_logs():
    """Check App Engine logs"""
    print("CHECKING APP ENGINE LOGS")
    print("=" * 50)
    
    try:
        # Get recent logs
        cmd = ['gcloud', 'app', 'logs', 'tail', '--limit=50']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] App Engine logs retrieved")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Failed to get logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to check logs: {e}")
        return False

def check_app_engine_instances():
    """Check App Engine instances"""
    print("\nCHECKING APP ENGINE INSTANCES")
    print("=" * 50)
    
    try:
        # Get instances
        cmd = ['gcloud', 'app', 'instances', 'list']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] App Engine instances retrieved")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Failed to get instances: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to check instances: {e}")
        return False

def main():
    print("CHECKING APP ENGINE STATUS")
    print("=" * 50)
    
    # Check logs
    if not check_app_engine_logs():
        print("[ERROR] Failed to check logs")
        return False
    
    # Check instances
    if not check_app_engine_instances():
        print("[ERROR] Failed to check instances")
        return False
    
    print("\n" + "=" * 50)
    print("App Engine status check completed!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)