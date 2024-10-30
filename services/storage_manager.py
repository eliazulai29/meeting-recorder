from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import logging
from pathlib import Path
from config.config import Config
import os
import time

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self):
        self.drive_service = None
        self.temp_path = Path("temp_recordings")
        self.temp_path.mkdir(exist_ok=True)
        self._init_retries = 3
        self._retry_delay = 2

    def setup_drive_service(self):
        """Setup Google Drive service with retries"""
        for attempt in range(self._init_retries):
            try:
                logger.info(f"Attempting to initialize Drive service (attempt {attempt + 1})")
                credentials = service_account.Credentials.from_service_account_file(
                    str(Config.CREDENTIALS_PATH),
                    scopes=['https://www.googleapis.com/auth/drive.file'],
                    subject=Config.BOT_EMAIL
                )
                self.drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
                logger.info("Drive service initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Drive service initialization attempt {attempt + 1} failed: {str(e)}")
                if attempt < self._init_retries - 1:
                    time.sleep(self._retry_delay)
                else:
                    raise

    def initialize(self):
        """Safe initialization method"""
        try:
            self.setup_drive_service()
            return True
        except Exception as e:
            logger.error(f"Storage Manager initialization failed: {str(e)}")
            return False

    def get_temp_recording_path(self, meeting_id: str) -> Path:
        """Get temporary recording path for a meeting"""
        return self.temp_path / f"{meeting_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"

    def cleanup_temp_recording(self, recording_path: Path):
        """Clean up temporary recording file"""
        try:
            if recording_path.exists():
                recording_path.unlink()
                logger.info(f"Cleaned up temporary recording: {recording_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup temporary recording {recording_path}: {str(e)}")