#!/usr/bin/env python3
"""
Google Calendar Setup Helper

This script helps you set up Google Calendar integration by:
1. Renaming your OAuth2 credentials file
2. Testing the calendar connection
3. Creating your first authenticated session
"""

import os
import sys
import shutil
from pathlib import Path

def find_oauth_credentials():
    """Find the downloaded OAuth2 credentials file"""
    possible_files = [
        'client_secret_50479654426-hhmccm1lc3khoj4kqa2hqlsdvoovpicl.apps.googleusercontent.com.json',
        'client_secret*.json'
    ]
    
    for pattern in possible_files:
        if '*' in pattern:
            # Use glob for wildcard patterns
            import glob
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        else:
            if os.path.exists(pattern):
                return pattern
    
    return None

def setup_credentials():
    """Set up Google Calendar credentials"""
    print("🔧 Setting up Google Calendar credentials...")
    
    # Find the OAuth2 file
    oauth_file = find_oauth_credentials()
    
    if not oauth_file:
        print("❌ Could not find OAuth2 credentials file!")
        print("   Expected: client_secret_*.json")
        print("   Make sure you've downloaded it from Google Cloud Console")
        return False
    
    print(f"✅ Found OAuth2 file: {oauth_file}")
    
    # Copy to standard name
    target_file = 'credentials.json'
    if oauth_file != target_file:
        try:
            shutil.copy2(oauth_file, target_file)
            print(f"✅ Copied to {target_file}")
        except Exception as e:
            print(f"❌ Error copying file: {e}")
            return False
    
    # Update .env if it exists
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        if 'GOOGLE_CALENDAR_CREDENTIALS_FILE' not in env_content:
            with open(env_file, 'a') as f:
                f.write(f"\n# Google Calendar\nGOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json\n")
            print("✅ Updated .env file")
    
    return True

def test_calendar():
    """Test the calendar integration"""
    print("\n🧪 Testing Google Calendar integration...")
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from calendar_api.integration import GoogleCalendarIntegration
        
        # Create calendar integration
        calendar = GoogleCalendarIntegration()
        
        if not calendar.is_available():
            print("❌ Calendar integration not available")
            print("   This will trigger OAuth flow on first run")
            return False
        
        # Test listing events
        events = calendar.list_todays_events()
        if 'error' in events:
            print(f"❌ Error: {events['error']}")
            return False
        
        print(f"✅ Successfully connected! Found {events['count']} events for today")
        return True
        
    except Exception as e:
        print(f"❌ Error testing calendar: {e}")
        return False

def main():
    """Main setup process"""
    print("📅 Google Calendar Setup for Journal AI Pipeline")
    print("=" * 60)
    
    # Step 1: Set up credentials
    if not setup_credentials():
        print("\n❌ Setup failed!")
        return
    
    # Step 2: Test integration
    if test_calendar():
        print("\n✅ Google Calendar setup complete!")
        print("\nYou can now run:")
        print("  python run.py test              # Test all components")
        print("  python run.py                   # Run full pipeline")
    else:
        print("\n⚠️ Calendar setup needs OAuth authorization")
        print("   Run 'python run.py test' to complete OAuth flow")

if __name__ == "__main__":
    main()