#!/usr/bin/env python
"""
Setup PostgreSQL database for GCP App Engine
"""

import subprocess
import sys

def create_cloud_sql_instance():
    """Create Cloud SQL PostgreSQL instance"""
    print("CREATING CLOUD SQL POSTGRESQL INSTANCE")
    print("=" * 50)
    
    try:
        # Create Cloud SQL instance
        cmd = [
            'gcloud', 'sql', 'instances', 'create', 'whatsapp-bulk-db',
            '--database-version=POSTGRES_15',
            '--tier=db-f1-micro',
            '--region=us-central1',
            '--storage-type=SSD',
            '--storage-size=10GB',
            '--storage-auto-increase',
            '--backup-start-time=03:00',
            '--enable-bin-log',
            '--maintenance-window-day=SUN',
            '--maintenance-window-hour=04',
            '--maintenance-release-channel=production',
            '--deletion-protection'
        ]
        
        print("Creating Cloud SQL instance...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Cloud SQL instance created successfully")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Failed to create Cloud SQL instance: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to create Cloud SQL instance: {e}")
        return False

def create_database():
    """Create database in the instance"""
    print("\nCREATING DATABASE")
    print("=" * 50)
    
    try:
        # Create database
        cmd = [
            'gcloud', 'sql', 'databases', 'create', 'whatsapp_bulk',
            '--instance=whatsapp-bulk-db'
        ]
        
        print("Creating database...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Database created successfully")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Failed to create database: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to create database: {e}")
        return False

def create_user():
    """Create database user"""
    print("\nCREATING DATABASE USER")
    print("=" * 50)
    
    try:
        # Create user
        cmd = [
            'gcloud', 'sql', 'users', 'create', 'whatsapp_user',
            '--instance=whatsapp-bulk-db',
            '--password=whatsapp_password_123!'
        ]
        
        print("Creating database user...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Database user created successfully")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Failed to create database user: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to create database user: {e}")
        return False

def get_connection_name():
    """Get the connection name for the instance"""
    print("\nGETTING CONNECTION NAME")
    print("=" * 50)
    
    try:
        cmd = [
            'gcloud', 'sql', 'instances', 'describe', 'whatsapp-bulk-db',
            '--format=value(connectionName)'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            connection_name = result.stdout.strip()
            print(f"[OK] Connection name: {connection_name}")
            return connection_name
        else:
            print(f"[ERROR] Failed to get connection name: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to get connection name: {e}")
        return None

def main():
    print("SETTING UP POSTGRESQL FOR GCP")
    print("=" * 50)
    
    # Step 1: Create Cloud SQL instance
    if not create_cloud_sql_instance():
        print("[ERROR] Failed to create Cloud SQL instance")
        return False
    
    # Step 2: Create database
    if not create_database():
        print("[ERROR] Failed to create database")
        return False
    
    # Step 3: Create user
    if not create_user():
        print("[ERROR] Failed to create database user")
        return False
    
    # Step 4: Get connection name
    connection_name = get_connection_name()
    if not connection_name:
        print("[ERROR] Failed to get connection name")
        return False
    
    print("\n" + "=" * 50)
    print("POSTGRESQL SETUP COMPLETED!")
    print("=" * 50)
    print("Connection name:", connection_name)
    print("Database: whatsapp_bulk")
    print("User: whatsapp_user")
    print("Password: whatsapp_password_123!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Update your settings_production.py with PostgreSQL config")
    print("2. Run migrations")
    print("3. Create the tenant user")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
