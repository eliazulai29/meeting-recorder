import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
import threading
from queue import Queue
from pathlib import Path
import time

from .calendar_service import CalendarService
from .meeting_bot import MeetingBot
from .storage_manager import StorageManager
from config.config import Config

logger = logging.getLogger(__name__)


@dataclass
class MeetingSession:
    """Represents an active meeting session"""
    meeting_id: str
    organizer: str
    meet_link: str
    start_time: datetime
    summary: str
    bot: Optional[MeetingBot] = None
    is_recording: bool = False
    chrome_port: Optional[int] = None
    process_thread: Optional[threading.Thread] = None
    status: str = "scheduled"  # scheduled, joining, active, ended, failed
    recording_path: Optional[Path] = None


class MeetingManager:
    def __init__(self):
        """Initialize the meeting manager with safe initialization"""
        try:
            logger.info("Meeting Manager initialization started.")

            # Initialize basic attributes
            self.active_sessions = {}
            self.max_concurrent_meetings = Config.MAX_CONCURRENT_MEETINGS
            self.available_ports = Queue()

            # Initialize ports
            for port in range(9222, 9222 + self.max_concurrent_meetings):
                self.available_ports.put(port)

            # Initialize services with retries
            self._init_services()

            logger.info("Meeting Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Meeting Manager: {str(e)}")
            raise

    def _init_services(self, max_retries=3, retry_delay=2):
        """Initialize services with retry mechanism"""
        for attempt in range(max_retries):
            try:
                # Initialize calendar service
                self.calendar_service = CalendarService()
                self.calendar_service.authenticate()

                # Initialize storage manager
                self.storage_manager = StorageManager()
                if not self.storage_manager.initialize():
                    raise Exception("Storage manager initialization failed")

                return True
            except Exception as e:
                logger.error(f"Service initialization attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise

    def start(self):
        """Start the meeting manager"""
        try:
            logger.info("Starting Meeting Manager")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._main_loop())
        except KeyboardInterrupt:
            logger.info("Shutting down Meeting Manager")
            self._cleanup()
        except Exception as e:
            logger.error(f"Meeting Manager error: {str(e)}")
            self._cleanup()
            raise

    async def _main_loop(self):
        """Main loop for checking and managing meetings"""
        while True:
            try:
                # Get upcoming meetings
                meetings = self.calendar_service.get_upcoming_meetings(time_window_minutes=15)
                logger.info(f"Found {len(meetings)} upcoming meetings")

                # Process each meeting
                for meeting in meetings:
                    await self._process_meeting(meeting)

                # Cleanup completed sessions
                await self._cleanup_completed_sessions()

                # Wait before next check
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(60)

    async def _process_meeting(self, meeting):
        """Process a single meeting"""
        try:
            meeting_id = meeting['id']

            if meeting_id not in self.active_sessions:
                if self.available_ports.empty():
                    logger.warning(f"No available ports for meeting {meeting_id}")
                    return

                # Create new session
                session = MeetingSession(
                    meeting_id=meeting_id,
                    organizer=meeting['organizer'],
                    meet_link=meeting['meet_link'],
                    start_time=datetime.fromisoformat(meeting['start']['dateTime'].replace('Z', '+00:00')),
                    summary=meeting.get('summary', 'Untitled Meeting'),
                    chrome_port=self.available_ports.get()
                )

                # Get recording path
                session.recording_path = self.storage_manager.get_temp_recording_path(meeting_id)

                # Schedule the meeting
                self._schedule_meeting(session)
                self.active_sessions[meeting_id] = session
                logger.info(f"Scheduled new meeting: {meeting_id}")

        except Exception as e:
            logger.error(f"Error processing meeting {meeting.get('id')}: {str(e)}")

    def _schedule_meeting(self, session: MeetingSession):
        """Schedule a meeting session"""
        try:
            def meeting_worker():
                try:
                    session.status = "joining"

                    # Initialize bot
                    session.bot = MeetingBot(
                        chrome_port=session.chrome_port,
                        recording_path=session.recording_path
                    )

                    if not session.bot.setup_driver():
                        logger.error(f"Failed to setup driver for meeting {session.meeting_id}")
                        session.status = "failed"
                        return

                    # Login and join meeting
                    if not session.bot.login_to_google():
                        logger.error(f"Failed to login for meeting {session.meeting_id}")
                        session.status = "failed"
                        return

                    if session.bot.join_meeting(session.meet_link):
                        session.status = "active"
                        logger.info(f"Successfully joined meeting {session.meeting_id}")

                        # Keep the session alive
                        while session.status == "active":
                            if not session.bot.is_meeting_active():
                                break
                            time.sleep(30)
                    else:
                        session.status = "failed"
                        logger.error(f"Failed to join meeting {session.meeting_id}")

                except Exception as e:
                    logger.error(f"Error in meeting worker for {session.meeting_id}: {str(e)}")
                    session.status = "failed"
                finally:
                    self._end_session(session)

            # Calculate when to start the meeting
            now = datetime.now(session.start_time.tzinfo)
            start_delay = (session.start_time - now - timedelta(minutes=1)).total_seconds()

            if start_delay > 0:
                # Schedule the meeting
                timer = threading.Timer(start_delay, meeting_worker)
                session.process_thread = timer
                timer.start()
                logger.info(f"Meeting {session.meeting_id} scheduled to start in {start_delay} seconds")
            else:
                # Start immediately if meeting time has passed
                thread = threading.Thread(target=meeting_worker)
                session.process_thread = thread
                thread.start()
                logger.info(f"Meeting {session.meeting_id} starting immediately")

        except Exception as e:
            logger.error(f"Error scheduling meeting {session.meeting_id}: {str(e)}")
            session.status = "failed"

    async def _cleanup_completed_sessions(self):
        """Clean up completed or failed sessions"""
        try:
            completed_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.status in ["ended", "failed"]
            ]

            for session_id in completed_sessions:
                session = self.active_sessions[session_id]
                self._end_session(session)
                del self.active_sessions[session_id]

        except Exception as e:
            logger.error(f"Error cleaning up completed sessions: {str(e)}")

    def _end_session(self, session: MeetingSession):
        """End a meeting session and cleanup resources"""
        try:
            if session.bot:
                session.bot.close()

            if session.chrome_port:
                self.available_ports.put(session.chrome_port)

            if session.process_thread and session.process_thread.is_alive():
                session.process_thread.join(timeout=1)

            session.status = "ended"
            logger.info(f"Ended session for meeting {session.meeting_id}")

        except Exception as e:
            logger.error(f"Error ending session {session.meeting_id}: {str(e)}")

    def _cleanup(self):
        """Cleanup all active sessions"""
        try:
            for session in self.active_sessions.values():
                self._end_session(session)
            self.active_sessions.clear()
            logger.info("Cleaned up all active sessions")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")