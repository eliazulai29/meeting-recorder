from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_authenticate(user_email):
    try:
        creds_path = Config.CREDENTIALS_PATH
        logger.info(f"Authenticating for user: {user_email}")

        # Load credentials with impersonation
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=Config.SCOPES,
            subject=user_email
        )
        service = build('calendar', 'v3', credentials=creds)
        logger.info("Successfully authenticated. Listing calendars...")

        calendar_list = service.calendarList().list().execute()
        for calendar in calendar_list['items']:
            logger.info(f"Calendar: {calendar['summary']} (ID: {calendar['id']})")

    except Exception as e:
        logger.error(f"Authentication test failed: {e}")

# Test with an authorized user
test_authenticate('eli1@natalieli.com')
