from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
from pathlib import Path
from config.config import Config

logger = logging.getLogger(__name__)


class MeetingBot:
    def __init__(self, chrome_port: int, recording_path: Path):
        self.driver = None
        self.chrome_port = chrome_port
        self.recording_path = recording_path

    def setup_driver(self) -> bool:
        """Setup Chrome driver with minimal options for local testing"""
        try:
            options = Options()

            # Basic options
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")

            # Add necessary permissions
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.media_stream_mic": 1,
                "profile.default_content_setting_values.media_stream_camera": 1,
                "profile.default_content_settings.popups": 0
            })

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

            logger.info("Browser started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup driver: {str(e)}")
            return False

    def login_to_google(self) -> bool:
        """Simplified login process"""
        try:
            # Go directly to Google login
            logger.info("Starting login process...")
            self.driver.get("https://accounts.google.com/signin")
            time.sleep(3)

            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_field.send_keys(Config.BOT_EMAIL)
            email_field.send_keys(Keys.RETURN)
            logger.info(f"Entered email: {Config.BOT_EMAIL}")
            time.sleep(3)

            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_field.send_keys(Config.BOT_PASSWORD)
            password_field.send_keys(Keys.RETURN)
            logger.info("Entered password")
            time.sleep(5)

            # Verify login by going to Meet
            self.driver.get("https://meet.google.com")
            time.sleep(3)

            if "meet.google.com" in self.driver.current_url:
                logger.info("Successfully logged in")
                return True
            else:
                logger.error(f"Login failed, current URL: {self.driver.current_url}")
                return False

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def join_meeting(self, meet_link: str) -> bool:
        """Simplified meeting join process"""
        try:
            # Go directly to the meeting link
            logger.info(f"Joining meeting: {meet_link}")
            self.driver.get(meet_link)
            time.sleep(5)

            # Take screenshot for debugging
            self.driver.save_screenshot("meeting_page.png")
            logger.info(f"Current URL: {self.driver.current_url}")

            # Look for any button containing "Join" or "Ask to join"
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    if button.is_displayed():
                        text = button.text.lower()
                        if "join" in text:
                            logger.info(f"Found join button with text: {text}")
                            button.click()
                            logger.info("Clicked join button")
                            time.sleep(3)
                            return True
                except:
                    continue

            logger.error("Could not find join button")
            return False

        except Exception as e:
            logger.error(f"Failed to join meeting: {str(e)}")
            return False

    def is_meeting_active(self) -> bool:
        """Simple check if meeting is active"""
        try:
            return "meet.google.com" in self.driver.current_url
        except:
            return False

    def close(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")