# Meeting Recorder Bot - Setup Guide

## Overview
A bot system that:
1. Monitors Google Calendar for meetings
2. Automatically joins meetings using Chrome browser
3. Records meetings to local storage
4. Exits and saves recording when meeting ends

## Setup Phases

### Phase 1: Google Cloud Project Setup (Required First)
1. Create Project:
   ```
   1. Go to console.cloud.google.com
   2. Create new project "meeting-recorder"
   3. Note the project ID
   ```

2. Enable Required APIs:
   ```
   1. Go to "APIs & Services" > "Enable APIs and Services"
   2. Search and enable each:
      - Google Calendar API
      - Google Meet API
   3. Wait for each API to fully enable before proceeding
   ```

3. Create Service Account:
   ```
   1. Go to IAM & Admin > Service Accounts
   2. Click "Create Service Account"
      - Name: meeting-recorder-bot
      - Description: Service account for meeting recording bot
   3. Click "Create and Continue"
   4. Add roles:
      - Service Account Token Creator
      - Service Account User
   5. Click "Done"
   ```

4. Generate and Download Credentials:
   ```
   1. Select your service account
   2. Go to "Keys" tab
   3. Add Key > Create new key
   4. Choose JSON format
   5. Save as config/credentials.json in your project
   ```

### Phase 2: Google Workspace Admin Setup
1. Configure Domain-Wide Delegation:
   ```
   1. Go to admin.google.com > Security > API Controls
   2. Find "Domain-wide Delegation"
   3. Add new:
      - Client ID: [Your service account client ID from credentials.json]
      - OAuth Scopes:
        https://www.googleapis.com/auth/calendar.readonly
        https://www.googleapis.com/auth/calendar.events
   ```

2. Create Bot User:
   ```
   1. Go to Users > Add New User
      - Email: bots@[your-domain].com
      - Set secure password
   2. Store these credentials safely - needed for .env file
   ```

3. Configure Google Meet Settings:
   ```
   1. Go to Apps > Google Workspace > Google Meet
   2. Configure Settings:
      - Access: "Anyone within your organization"
      - Recording: Enable "Let users record their meetings"
      - Host Management: Turn OFF
      - Quick Access: ON
   ```

### Phase 3: Project Setup
1. System Requirements:
   ```
   - Python 3.8+
   - Chrome browser
   - Git
   ```

2. Clone and Setup:
   ```bash
   # Clone repository
   git clone [repository-url]
   cd meeting-recorder

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. Create Required Directories:
   ```bash
   mkdir -p config logs recordings
   ```

4. Configure Environment:
   ```bash
   # Create .env file with:
   BOT_EMAIL=bots@[your-domain].com
   BOT_PASSWORD=[your-bot-password]
   ```

5. Place Credentials:
   ```
   Move credentials.json to config/credentials.json
   ```

### Phase 4: Testing and Verification
1. Verify Service Account:
   ```bash
   # Run service account test
   python -m tests.verify_service_account
   
   # Expected output:
   "Service account authenticated successfully"
   ```

2. Verify Calendar Access:
   ```bash
   # Run calendar access test
   python -m tests.verify_calendar_access
   
   # Expected output:
   "Successfully fetched calendar events"
   ```

3. Test Meeting Join:
   ```bash
   # Create a test meeting
   1. Create a meeting using authorized user
   2. Run the bot
   3. Verify bot joins successfully
   ```

## Project Structure
```
meeting-recorder/
├── config/
│   ├── __init__.py
│   ├── config.py
│   └── credentials.json
├── services/
│   ├── __init__.py
│   ├── calendar_service.py
│   ├── meeting_bot.py
│   └── meeting_manager.py
├── logs/
├── recordings/
├── .env
├── requirements.txt
└── main.py
```

## Troubleshooting Guide

### 1. Service Account Issues
If service account authentication fails:
1. Verify credentials.json is correct and in config/
2. Check Domain-wide Delegation is enabled
3. Verify OAuth scopes are exactly as specified

### 2. Calendar Access Issues
If bot can't see meetings:
1. Verify service account has calendar API enabled
2. Check calendar sharing permissions
3. Ensure meetings have Google Meet links

### 3. Meeting Join Issues
If bot can't join meetings:
1. Verify BOT_EMAIL and BOT_PASSWORD in .env
2. Check Meet settings in Admin Console
3. Ensure Chrome is installed and updated

### 4. Recording Issues
If recording fails:
1. Check 'recordings' directory exists and is writable
2. Verify Chrome has necessary permissions
3. Check available disk space

## Running the Bot

1. Start the Bot:
   ```bash
   python main.py
   ```

2. Monitor Logs:
   ```bash
   tail -f logs/bot.log
   ```

3. View Recordings:
   ```
   All recordings are saved in ./recordings directory
   Format: meeting_[ID]_[TIMESTAMP].webm
   ```

## Security Notes

1. Credential Security:
   - Keep credentials.json secure
   - Never commit .env or credentials.json
   - Regularly rotate service account keys

2. Bot Account:
   - Use strong password
   - Regularly update password
   - Monitor access logs

3. Recording Storage:
   - Regularly backup recordings
   - Monitor storage usage
   - Implement cleanup policy