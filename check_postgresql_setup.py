#!/usr/bin/env python
"""
Check PostgreSQL setup status
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return result"""
    print(f"\n{description}")
    print("-" * 30)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"[OK] {description} successful")
            if result.stdout:
                print(result.stdout)
            return True, result.stdout
        else:
            print(f"[ERROR] {description} failed")
            if result.stderr:
                print(result.stderr)
            return False, result.stderr
            
    except Exception as e:
        print(f"[ERROR] {description} failed: {e}")
        return False, str(e)

def check_cloud_sql():
    """Check Cloud SQL instance status"""
    print("CHECKING CLOUD SQL INSTANCE")
    print("=" * 50)
    
    success, output = run_command('gcloud sql instances list', "Listing Cloud SQL instances")
    
    if success and 'whatsapp-bulk-db' in output:
        print("[OK] whatsapp-bulk-db instance found")
        
        # Get detailed info
        success, output = run_command('gcloud sql instances describe whatsapp-bulk-db', "Getting instance details")
        if success:
            if 'RUNNABLE' in output:
                print("[OK] Instance is running")
            else:
                print("[WARNING] Instance may not be running")
    else:
        print("[ERROR] whatsapp-bulk-db instance not found")
        return False
    
    return True

def check_database():
    """Check database status"""
    print("\nCHECKING DATABASE")
    print("=" * 50)
    
    success, output = run_command('gcloud sql databases list --instance=whatsapp-bulk-db', "Listing databases")
    
    if success and 'whatsapp_bulk' in output:
        print("[OK] whatsapp_bulk database found")
    else:
        print("[WARNING] whatsapp_bulk database not found")
    
    return True

def check_user():
    """Check database user status"""
    print("\nCHECKING DATABASE USER")
    print("=" * 50)
    
    success, output = run_command('gcloud sql users list --instance=whatsapp-bulk-db', "Listing users")
    
    if success and 'whatsapp_user' in output:
        print("[OK] whatsapp_user found")
    else:
        print("[WARNING] whatsapp_user not found")
    
    return True

def check_django_connection():
    """Check Django database connection"""
    print("\nCHECKING DJANGO CONNECTION")
    print("=" * 50)
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
        django.setup()
        
        from django.db import connection
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"[OK] Django database connection successful: {result}")
            return True
            
    except Exception as e:
        print(f"[ERROR] Django database connection failed: {e}")
        return False

def check_django_tables():
    """Check if Django tables exist"""
    print("\nCHECKING DJANGO TABLES")
    print("=" * 50)
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
        django.setup()
        
        from django.db import connection
        
        # Check if auth_user table exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'auth_user'")
            result = cursor.fetchone()
            
            if result[0] > 0:
                print("[OK] Django tables exist")
                
                # Check if tenant user exists
                cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username = 'tenant'")
                user_count = cursor.fetchone()[0]
                
                if user_count > 0:
                    print("[OK] tenant user exists in database")
                else:
                    print("[WARNING] tenant user not found in database")
                
                return True
            else:
                print("[WARNING] Django tables not found - migrations needed")
                return False
                
    except Exception as e:
        print(f"[ERROR] Failed to check Django tables: {e}")
        return False

def main():
    print("CHECKING POSTGRESQL SETUP STATUS")
    print("=" * 50)
    
    # Check all components
    checks = [
        check_cloud_sql,
        check_database,
        check_user,
        check_django_connection,
        check_django_tables,
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("SUCCESS! All checks passed!")
        print("Your PostgreSQL setup is ready.")
    else:
        print("SOME ISSUES FOUND!")
        print("Run 'python setup_existing_postgresql.py' to fix them.")
    print("=" * 50)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
