#!/usr/bin/env python3
"""
Check database migration status and diagnose issues
"""
import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

print("=" * 70)
print("DATABASE MIGRATION STATUS CHECK")
print("=" * 70)

try:
    # Check database connection
    print("\n1. Testing database connection...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version[:50]}...")
    
    # Check applied migrations
    print("\n2. Checking applied migrations...")
    recorder = MigrationRecorder(connection)
    applied_migrations = recorder.applied_migrations()
    
    messaging_migrations = [m for m in applied_migrations if m[0] == 'messaging']
    messaging_migrations.sort()
    
    print(f"\n✅ Found {len(messaging_migrations)} messaging migrations:")
    for app, name in messaging_migrations[-10:]:  # Show last 10
        print(f"   - {name}")
    
    # Check if contest table has keyword fields
    print("\n3. Checking Contest table structure...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'messaging_contest'
            ORDER BY column_name;
        """)
        columns = cursor.fetchall()
        
        has_keywords = False
        has_auto_reply = False
        has_priority = False
        
        print("\n   Contest table columns:")
        for col_name, col_type in columns:
            print(f"   - {col_name} ({col_type})")
            if col_name == 'keywords':
                has_keywords = True
            if col_name == 'auto_reply_message':
                has_auto_reply = True
            if col_name == 'auto_reply_priority':
                has_priority = True
    
    print("\n4. Keyword fields check:")
    if has_keywords:
        print("   ✅ keywords field exists")
    else:
        print("   ❌ keywords field MISSING - migration not applied!")
    
    if has_auto_reply:
        print("   ✅ auto_reply_message field exists")
    else:
        print("   ❌ auto_reply_message field MISSING - migration not applied!")
    
    if has_priority:
        print("   ✅ auto_reply_priority field exists")
    else:
        print("   ❌ auto_reply_priority field MISSING - migration not applied!")
    
    # Check if PromptReply table still exists
    print("\n5. Checking for PromptReply table...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'messaging_promptreply'
            );
        """)
        promptreply_exists = cursor.fetchone()[0]
        
        if promptreply_exists:
            print("   ⚠️  PromptReply table still exists (should be deleted)")
        else:
            print("   ✅ PromptReply table deleted successfully")
    
    # Check total contests
    print("\n6. Checking contests...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM messaging_contest;")
        contest_count = cursor.fetchone()[0]
        print(f"   ✅ Total contests: {contest_count}")
        
        if contest_count > 0:
            cursor.execute("""
                SELECT name, keywords, auto_reply_priority 
                FROM messaging_contest 
                LIMIT 5;
            """)
            contests = cursor.fetchall()
            print("\n   Sample contests:")
            for name, keywords, priority in contests:
                print(f"   - {name}: keywords={keywords}, priority={priority}")
    
    print("\n" + "=" * 70)
    if has_keywords and has_auto_reply and has_priority and not promptreply_exists:
        print("✅ DATABASE MIGRATION SUCCESSFUL!")
        print("   All keyword fields are present and PromptReply is removed.")
    else:
        print("⚠️  DATABASE MIGRATION INCOMPLETE!")
        print("   Need to run migration 0012_contest_keywords_autoreply")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


