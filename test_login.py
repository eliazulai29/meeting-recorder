# test_login.py
import logging
from services.meeting_bot import MeetingBot
import time

logging.basicConfig(level=logging.INFO)


def test_login():
    bot = MeetingBot()
    try:
        if not bot.setup_driver():
            print("Failed to setup driver")
            return

        if bot.login_to_google():
            print("Login successful!")
            time.sleep(5)  # Keep browser open to verify
        else:
            print("Login failed!")
    finally:
        bot.close()


if __name__ == "__main__":
    test_login()