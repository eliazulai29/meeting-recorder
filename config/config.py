import logging
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

class Config:
    # Paths
    CREDENTIALS_PATH = BASE_DIR / 'config' / 'credentials.json'
    TOKEN_PATH = BASE_DIR / 'config' / 'token.pickle'

    # Google Workspace Auth
    BOT_EMAIL = os.getenv('BOT_EMAIL', 'bots@natalieli.com')
    BOT_PASSWORD = os.getenv('BOT_PASSWORD')

    # Workspace settings
    WORKSPACE_DOMAIN = 'natalieli.com'
    AUTHORIZED_USERS = ['eli1@natalieli.com', 'eli2@natalieli.com']

    # Application settings
    CALENDAR_CHECK_INTERVAL = 30  # seconds
    JOIN_BEFORE_MINUTES = 5
    MAX_CONCURRENT_MEETINGS = 40
    PRODUCTION_MODE = os.getenv('PRODUCTION_MODE', 'False').lower() == 'true'

    # API Settings
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/drive.file'
    ]

    @classmethod
    def is_authorized_user(cls, email):
        """Check if email is authorized"""
        return email in cls.AUTHORIZED_USERS or email.endswith(f'@{cls.WORKSPACE_DOMAIN}')

    @classmethod
    def get_monitored_calendars(cls):
        """Get list of calendars to monitor"""
        return cls.AUTHORIZED_USERS

# Debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Config - BOT_EMAIL: {Config.BOT_EMAIL}")
logger.info(f"Config - AUTHORIZED_USERS: {Config.AUTHORIZED_USERS}")
logger.info(f"Config - SCOPES: {Config.SCOPES}")
logger.info(f"Config - MAX_CONCURRENT_MEETINGS: {Config.MAX_CONCURRENT_MEETINGS}")