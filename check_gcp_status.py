#!/usr/bin/env python
"""
Script to check GCP deployment status and diagnose 502 errors
Run this locally to check your GCP setup
"""
import subprocess
import sys
import json

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Checking: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def check_gcp_project():
    """Check current GCP project"""
    success, output, error = run_command(
        "gcloud config get-value project",
        "Current GCP Project"
    )
    if success and output.strip():
        project = output.strip()
        print(f"✅ Project: {project}")
        return project
    else:
        print("❌ Could not get project. Run: gcloud config set project YOUR_PROJECT_ID")
        return None

def check_cloud_sql():
    """Check Cloud SQL instance status"""
    success, output, error = run_command(
        "gcloud sql instances list --format=json",
        "Cloud SQL Instances"
    )
    if success:
        try:
            instances = json.loads(output)
            if instances:
                for instance in instances:
                    name = instance.get('name', 'Unknown')
                    state = instance.get('state', 'Unknown')
                    region = instance.get('region', 'Unknown')
                    print(f"\nInstance: {name}")
                    print(f"  Status: {state}")
                    print(f"  Region: {region}")
                    if state == 'RUNNABLE':
                        print("  ✅ Instance is running")
                    else:
                        print(f"  ⚠️  Instance is {state}")
                return True
            else:
                print("❌ No Cloud SQL instances found")
                return False
        except json.JSONDecodeError:
            print("⚠️  Could not parse instance list")
            print(output)
            return False
    return False

def check_app_engine():
    """Check App Engine service status"""
    success, output, error = run_command(
        "gcloud app services list --format=json",
        "App Engine Services"
    )
    if success:
        try:
            services = json.loads(output)
            if services:
                for service in services:
                    name = service.get('id', 'Unknown')
                    print(f"\nService: {name}")
                return True
            else:
                print("❌ No App Engine services found")
                return False
        except json.JSONDecodeError:
            print("⚠️  Could not parse services list")
            return False
    return False

def check_app_versions():
    """Check App Engine versions"""
    success, output, error = run_command(
        "gcloud app versions list --format=json",
        "App Engine Versions"
    )
    if success:
        try:
            versions = json.loads(output)
            if versions:
                print(f"\nFound {len(versions)} version(s):")
                for version in versions[:5]:  # Show first 5
                    v_id = version.get('id', 'Unknown')
                    serving = version.get('servingStatus', 'Unknown')
                    traffic = version.get('trafficSplit', {})
                    print(f"  Version: {v_id}")
                    print(f"    Status: {serving}")
                    print(f"    Traffic: {traffic}")
                return True
            else:
                print("❌ No versions found")
                return False
        except json.JSONDecodeError:
            print("⚠️  Could not parse versions list")
            return False
    return False

def check_recent_logs():
    """Check recent App Engine logs"""
    print("\n" + "="*60)
    print("Recent App Engine Logs (Last 20 entries)")
    print("="*60)
    print("⚠️  This may take a moment...")
    success, output, error = run_command(
        "gcloud app logs read --limit=20 --format=json",
        "Recent Logs"
    )
    if success:
        try:
            logs = json.loads(output)
            if logs:
                print(f"\nFound {len(logs)} log entries")
                errors = [log for log in logs if log.get('severity') in ['ERROR', 'CRITICAL']]
                if errors:
                    print(f"\n❌ Found {len(errors)} ERROR/CRITICAL entries:")
                    for log in errors[:5]:  # Show first 5 errors
                        text = log.get('textPayload', log.get('jsonPayload', {}))
                        timestamp = log.get('timestamp', 'Unknown')
                        print(f"\n  [{timestamp}]")
                        print(f"  {text}")
                else:
                    print("✅ No errors found in recent logs")
            else:
                print("⚠️  No logs found")
        except json.JSONDecodeError:
            print("⚠️  Could not parse logs")
            print("Raw output:")
            print(output[:500])  # First 500 chars
    else:
        print("❌ Could not fetch logs")
        print("Try checking logs in GCP Console:")
        print("https://console.cloud.google.com/logs")

def check_database_connection():
    """Check if we can connect to the database"""
    print("\n" + "="*60)
    print("Database Connection Test")
    print("="*60)
    print("⚠️  This requires Cloud SQL Proxy or direct access")
    print("Checking database configuration in settings_production.py...")
    
    try:
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
        import django
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nThis is likely the cause of your 502 error!")
        print("\nCommon issues:")
        print("  1. Cloud SQL instance not running")
        print("  2. Wrong database credentials")
        print("  3. Network permissions not set")
        print("  4. Database doesn't exist")
        return False

def main():
    print("="*60)
    print("GCP Deployment Status Checker")
    print("Diagnosing 502 Bad Gateway Error")
    print("="*60)
    
    # Check project
    project = check_gcp_project()
    if not project:
        print("\n❌ Cannot proceed without valid GCP project")
        return
    
    # Check Cloud SQL
    sql_ok = check_cloud_sql()
    
    # Check App Engine
    app_ok = check_app_engine()
    
    # Check versions
    versions_ok = check_app_versions()
    
    # Check logs
    check_recent_logs()
    
    # Try database connection (optional)
    print("\n" + "="*60)
    print("Would you like to test database connection?")
    print("(This requires Cloud SQL Proxy or network access)")
    print("="*60)
    # Uncomment to test:
    # check_database_connection()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Project: {'✅' if project else '❌'}")
    print(f"Cloud SQL: {'✅' if sql_ok else '❌'}")
    print(f"App Engine: {'✅' if app_ok else '❌'}")
    print(f"Versions: {'✅' if versions_ok else '❌'}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Check the logs above for ERROR messages")
    print("2. Verify Cloud SQL instance is RUNNING")
    print("3. Check database credentials in settings_production.py")
    print("4. Verify App Engine service account has Cloud SQL Client role")
    print("\nFor detailed logs, visit:")
    print(f"https://console.cloud.google.com/logs?project={project}")

if __name__ == '__main__':
    main()







