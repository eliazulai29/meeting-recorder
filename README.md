# Meeting Recorder Bot - Setup Guide

## Prerequisites

- Google Workspace Admin access (Super Admin role recommended)
- Python 3.8+
- Chrome browser installed
- Google Cloud Console access

## 1. Google Workspace Setup

### A. Create Service Account
1. Access Google Cloud Console (console.cloud.google.com):
   ```
   - Create new project "meeting-recorder"
   - Note the project ID for future reference
   ```

2. Enable Required APIs:
   ```
   - Google Calendar API
   - Google Meet API
   - Google Drive API
   - Google People API (for contact access)
   ```

3. Create Service Account:
   ```
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name: meeting-recorder
   - Description: Service account for meeting recording bot
   - Click "Create and Continue"
   - Click "Done"
   ```

4. Generate Service Account Key:
   ```
   - Select the created service account
   - Go to "Keys" tab
   - Add Key > Create new key
   - Choose JSON format
   - Download and save as config/credentials.json
   ```

### B. Configure Domain-Wide Delegation

1. Enable Domain-Wide Delegation:
   ```
   - Go to service account details
   - Edit
   - Enable "Domain-wide Delegation"
   - Save
   ```

2. Configure API Scopes in Admin Console:
   ```
   1. Go to admin.google.com
   2. Security > API Controls > Domain-wide Delegation
   3. Add new:
      - Client ID: [Your service account client ID]
      - OAuth Scopes (add all):
        https://www.googleapis.com/auth/calendar.readonly
        https://www.googleapis.com/auth/calendar.events
        https://www.googleapis.com/auth/drive.file
        https://www.googleapis.com/auth/admin.directory.user.readonly
   ```

### C. Create Bot User and Configure Permissions

1. Create Bot User:
   ```
   Users > Add New User
   - First Name: Meeting
   - Last Name: Bot
   - Email: bots@[your-domain].com
   - Password: [secure-password]
   ```

2. Configure Bot User Permissions:
   ```
   1. Go to Admin roles
   2. Create new custom role:
      - Name: Meeting Bot Role
      - Privileges:
        - Calendar: Read/Write
        - Meet: Read/Write
        - Drive: Read/Write
   3. Assign role to bot user
   ```

### D. Configure Google Meet Settings

1. Navigate to Apps > Google Workspace > Google Meet
2. Configure Meet Safety Settings:
   ```
   In Admin Console:
   - Access: Set to "Anyone within your organization"
   - External Access: Enable "Allow users in your organization to join external meetings"
   - Recording: Enable "Let users record their meetings"
   ```

3. Configure Meet Host Controls:
   ```
   - Quick Access: ON
   - Anonymous users: Allow from your domain
   - Meeting creation: Allow all users
   - Recording: Allow all users
   ```

### E. Configure Calendar Sharing

1. For each user whose meetings need to be recorded:
   ```
   1. Open Google Calendar
   2. Settings > [Calendar Name] > Share with specific people
   3. Add:
      - Email: [Your service account client ID]@[project-id].iam.gserviceaccount.com
      - Permission: "Make changes and manage sharing"
   4. Also share with bot user:
      - Email: bots@[your-domain].com
      - Permission: "Make changes and manage sharing"
   ```

### F. Configure Drive Permissions

1. Create Storage Folder:
   ```
   1. Create a Google Drive folder for recordings
   2. Share with:
      - Bot user (Editor access)
      - Service account (Editor access)
   ```

## 2. Project Setup

1. Clone and Setup Environment:
   ```bash
   git clone [repository-url]
   cd meeting-recorder
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment:
   ```bash
   # Create .env file:
   BOT_EMAIL=bots@[your-domain].com
   BOT_PASSWORD=[your-bot-password]
   STORAGE_FOLDER_ID=[google-drive-folder-id]
   SERVICE_ACCOUNT_FILE=config/credentials.json
   ```

## 3. Verification Steps

Run these checks to verify setup:

1. Service Account Access:
   ```bash
   python -m tests.verify_service_account
   ```

2. Calendar Access:
   ```bash
   python -m tests.verify_calendar_access
   ```

3. Meet Access:
   ```bash
   python -m tests.verify_meet_access
   ```

## 4. Troubleshooting

Common issues and solutions:

1. Calendar Access Issues:
   - Verify service account has correct scopes
   - Check calendar sharing permissions
   - Verify bot user has calendar access

2. Meet Join Issues:
   - Check Meet settings in Admin Console
   - Verify bot user has meeting creation rights
   - Check network/firewall settings

3. Recording Issues:
   - Verify Drive permissions
   - Check storage quota
   - Verify Meet recording settings

## 5. Security Notes

Important security considerations:

1. Service Account:
   - Keep credentials.json secure
   - Regularly rotate service account keys
   - Monitor API usage

2. Bot Account:
   - Use strong password
   - Enable 2FA if required
   - Regularly audit access logs

3. Monitoring:
   - Setup alerts for failed recordings
   - Monitor storage usage
   - Track API quota usage



# Process Overview
                                      
Meeting Discovery      Meeting Workers         Storage Manager
[Calendar Service] -> [Meeting Instances] -> [Recording Storage]
     |                      |                      |
     |                      |                      |
Monitors calendars     Each meeting           Handles saving
for upcoming        gets its own Chrome     and organizing
meetings            instance & process      recordings



Meeting Recorder Bot - Setup Guide
[Previous sections remain the same until Google Cloud Setup]
A. Google Cloud Project Setup

Create Project in Google Cloud Console:
Copy- Go to console.cloud.google.com
- Create new project "meeting-recorder"
- Note the project ID

Enable Required APIs:
Copy- Go to "APIs & Services" > "Enable APIs and Services"
- Search and enable each:
  - Google Calendar API
  - Google Meet API
  - Google Drive API
  - Google People API (required for authentication)

Create Service Account:
Copy- Go to IAM & Admin > Service Accounts
- Click "Create Service Account"
- Name: meeting-recorder-bot
- Description: Service account for meeting recording bot
- Click "Create and Continue"

Configure Service Account Roles:
Copy- In IAM & Admin > Service Accounts
- Click on your service account
- Go to "PERMISSIONS" tab
- Click "GRANT ACCESS"
- Add these specific roles:
  - Service Account Token Creator
  - Service Account User

Generate Service Account Key:
Copy- Go to "KEYS" tab
- Add Key > Create new key
- Choose JSON format
- Save as config/credentials.json


B. Configure Domain-Wide Delegation

Enable Domain-Wide Delegation:
Copy- Go to service account details
- Edit
- Enable "Domain-wide Delegation"
- Save

Configure API Scopes in Admin Console:
Copy1. Go to admin.google.com
2. Security > API Controls > Domain-wide Delegation
3. Add new:
   - Client ID: [Your service account client ID - found in credentials.json]
   - Add exactly these OAuth Scopes:
     https://www.googleapis.com/auth/calendar.readonly
     https://www.googleapis.com/auth/calendar.events
     https://www.googleapis.com/auth/drive.file


C. Google Meet Settings Configuration

Navigate to Apps > Google Workspace > Google Meet
Configure Video Settings:
Copy- Recording: Set "Let people record their meetings" to ON
- Default video recording quality: Set to "Record at highest available resolution"

Configure Meet Safety Settings:
CopyDomain:
- Set to "All users (including users not signed in)"

Access:
- Allow "Any meetings, including meetings created with personal accounts"

Joining:
- Turn OFF "Host must join before anyone else can join"
- Set Meeting access type to "Trusted"

Host Management:
- Turn OFF "Start video calls with host management turned on"

Additional Settings:
Copy- Client logs upload: Enable
- Reactions: Enable
- Chat: Enable for all users
- Integrations: Enable "Let users join calls in other Google Workspace apps"


[Rest of the sections remain the same]
Configuration Validation Checklist
Before running the bot, verify:

Service Account Setup:
Copy✓ Service account created
✓ Domain-wide delegation enabled
✓ Correct OAuth scopes added
✓ Required roles assigned:
  - Service Account Token Creator
  - Service Account User

API Enablement:
Copy✓ Google Calendar API
✓ Google Meet API
✓ Google Drive API
✓ Google People API

Google Meet Settings:
Copy✓ Recording enabled
✓ Host restrictions disabled
✓ External access allowed
✓ Meeting creation allowed

Bot Account:
Copy✓ Bot user created
✓ Meet access enabled
✓ Calendar access enabled
✓ Drive access enabled

Environment Configuration:
Copy✓ credentials.json in correct location
✓ .env file configured
✓ Python environment setup
✓ Required packages installed