#!/usr/bin/env python3
"""
GitHub Setup Script
This script helps you set up GitHub integration for your project
"""

import os
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
    print("🐙 GitHub Setup for WhatsApp Bulk Messaging")
    print("=" * 50)
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        print("📁 Initializing Git repository...")
        run_command("git init", "Initializing Git")
    else:
        print("✅ Git repository already initialized")
    
    # Add all files
    run_command("git add .", "Adding all files to Git")
    
    # Check if there are any changes
    result = run_command("git status --porcelain", "Checking for changes")
    if not result or result.strip() == "":
        print("ℹ️  No changes to commit")
    else:
        print("📝 Files ready to commit:")
        print(result)
    
    print("\n🚀 Next Steps:")
    print("1. Create a GitHub repository at https://github.com/new")
    print("2. Name it: whatsapp-bulk-message")
    print("3. Don't initialize with README (you already have files)")
    print("4. Copy the repository URL")
    print("5. Run these commands:")
    print("   git commit -m 'Initial commit'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/YOUR_USERNAME/whatsapp-bulk-message.git")
    print("   git push -u origin main")
    
    print("\n📋 After GitHub setup:")
    print("1. Follow CPANEL_SETUP_GUIDE.md for cPanel deployment")
    print("2. Use update_deployment.py for future updates")
    
    print("\n✨ Setup complete! Your project is ready for deployment.")

if __name__ == "__main__":
    main()
