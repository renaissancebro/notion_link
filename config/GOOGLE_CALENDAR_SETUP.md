# Google Calendar API Setup Guide

## 1. Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Calendar API**:
   - Go to APIs & Services → Library
   - Search for "Google Calendar API"
   - Click "Enable"

## 2. Create Credentials

### Option A: OAuth 2.0 (Recommended for personal use)

1. Go to APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen if prompted:
   - User Type: External (for personal) or Internal (for organization)
   - Fill in app name, email, etc.
4. Create OAuth client ID:
   - Application type: **Desktop application**
   - Name: "Journal AI Pipeline"
5. Download the JSON file and save as `credentials.json` in your project folder

### Option B: Service Account (For automated systems)

1. Go to APIs & Services → Credentials
2. Click "Create Credentials" → "Service account"
3. Fill in service account details
4. Download the JSON key file
5. Save as `service-account.json` in your project folder

## 3. Add to .env file

Add these lines to your `.env` file:

```bash
# Google Calendar API
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
# Optional: specific calendar ID (default uses primary)
GOOGLE_CALENDAR_ID=primary
```

## 4. Test the Setup

Run the test script:
```bash
python test_calendar.py
```

## 5. First-time Authentication

When you first run the calendar integration:

1. **OAuth Flow**: A browser window will open
2. **Sign in** to your Google account
3. **Grant permissions** to access your calendar
4. A `token.json` file will be created automatically
5. Future runs will use this token (no browser needed)

## Security Notes

- ✅ `credentials.json` - Safe to commit (contains client ID only)
- ❌ `token.json` - Never commit (contains access tokens)
- ❌ `service-account.json` - Never commit (contains private keys)

The `.gitignore` file already protects `token.json` and `*.json` credential files.

## Troubleshooting

**"Access blocked" error**: 
- Your app needs verification if using External user type
- Use Internal user type for organization accounts
- Or add your email as a test user

**"Quota exceeded" error**:
- Check API quotas in Google Cloud Console
- Calendar API has generous free limits

**"Calendar not found" error**:
- Verify the calendar ID in your `.env` file
- Use `primary` for main calendar