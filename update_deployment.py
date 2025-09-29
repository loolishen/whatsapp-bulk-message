#!/usr/bin/env python3
"""
Quick deployment update script
Run this after making changes to update your cPanel deployment
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e.stderr}")
        return None

def main():
    print("🚀 Updating Deployment")
    print("=" * 40)
    
    # 1. Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # 2. Check for any issues
    run_command("python manage.py check", "Checking for issues")
    
    # 3. Git operations
    print("\n📝 Git Operations:")
    print("1. Add all changes: git add .")
    print("2. Commit changes: git commit -m 'Your update message'")
    print("3. Push to GitHub: git push origin main")
    
    print("\n🌐 cPanel Update:")
    print("1. Go to cPanel → Git Version Control")
    print("2. Click 'Pull' on your repository")
    print("3. Go to Python App and click 'Restart'")
    
    print("\n✅ Update process ready!")
    print("Follow the steps above to complete your deployment update.")

if __name__ == "__main__":
    main()
