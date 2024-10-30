import logging
from services.meeting_manager import MeetingManager
from config.config import Config
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info("Bot is starting the main process.")

            # Initialize manager
            manager = MeetingManager()

            # Start the manager
            manager.start()
            return

        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Shutting down.")
                sys.exit(1)
        finally:
            logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()