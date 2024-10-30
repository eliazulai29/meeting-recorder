from google.oauth2 import service_account  # Add this import
from googleapiclient.discovery import build
import logging
from datetime import datetime, timedelta
from config.config import Config

logger = logging.getLogger(__name__)


class CalendarService:
    def __init__(self):
        self.service = None
        self.calendars = {}

    def authenticate(self):
        """Handle Google Calendar authentication using service account"""
        try:
            logger.info("Authenticating with service account...")
            credentials = service_account.Credentials.from_service_account_file(
                str(Config.CREDENTIALS_PATH),
                scopes=Config.SCOPES,
                subject='bots@natalieli.com'  # Impersonate the bot account
            )

            logger.info("Building calendar service...")
            self.service = build('calendar', 'v3', credentials=credentials)
            self._load_calendars()
            logger.info("Successfully authenticated with Google Calendar using service account")

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def _load_calendars(self):
        """Load and cache calendar information with detailed logging"""
        try:
            logger.info("=== Loading Calendars ===")
            calendar_list = self.service.calendarList().list().execute()

            logger.info(f"Found {len(calendar_list.get('items', []))} calendars")
            for calendar in calendar_list['items']:
                calendar_id = calendar['id']
                summary = calendar.get('summary', '')
                access_role = calendar.get('accessRole', '')

                logger.info(f"""
                Calendar Details:
                - ID: {calendar_id}
                - Summary: {summary}
                - Access Role: {access_role}
                - Primary: {calendar.get('primary', False)}
                - Selected: {calendar.get('selected', False)}
                """)

                self.calendars[calendar_id] = {
                    'summary': summary,
                    'access_role': access_role,
                    'primary': calendar.get('primary', False)
                }

            logger.info("=== Calendar Loading Complete ===")

        except Exception as e:
            logger.error(f"Error loading calendars: {str(e)}")

    def get_upcoming_meetings(self, time_window_minutes=15):
        """Get upcoming Google Meet meetings with enhanced logging"""
        try:
            now = datetime.utcnow()
            time_window = now + timedelta(minutes=time_window_minutes)
            meetings = []

            logger.info(f"Checking meetings between {now} and {time_window}")

            # Create a list of calendars to check - both from self.calendars and AUTHORIZED_USERS
            calendars_to_check = list(self.calendars.keys()) + Config.AUTHORIZED_USERS
            logger.info(f"Checking calendars: {calendars_to_check}")

            # Check each calendar
            for calendar_id in calendars_to_check:
                try:
                    logger.info(f"Checking calendar: {calendar_id}")

                    events_result = self.service.events().list(
                        calendarId=calendar_id,
                        timeMin=now.isoformat() + 'Z',
                        timeMax=time_window.isoformat() + 'Z',
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()

                    events = events_result.get('items', [])
                    logger.info(f"Found {len(events)} events in calendar {calendar_id}")

                    for event in events:
                        organizer = event.get('organizer', {}).get('email')
                        summary = event.get('summary', 'Untitled')
                        logger.info(f"Checking event: {summary} by {organizer}")

                        # Check for Meet link
                        conference_data = event.get('conferenceData', {})
                        if conference_data and conference_data.get('conferenceId'):
                            meet_link = next(
                                (e['uri'] for e in conference_data.get('entryPoints', [])
                                 if e.get('entryPointType') == 'video'),
                                None
                            )

                            if meet_link:
                                meeting_info = {
                                    'id': event['id'],
                                    'summary': summary,
                                    'start': event['start'],
                                    'meet_link': meet_link,
                                    'organizer': organizer,
                                    'calendar_id': calendar_id
                                }
                                meetings.append(meeting_info)
                                logger.info(f"Found valid meeting: {summary} by {organizer}")
                            else:
                                logger.info(f"No valid meet link found for event: {summary}")
                        else:
                            logger.info(f"No conference data found for event: {summary}")

                except Exception as e:
                    logger.error(f"Error checking calendar {calendar_id}: {str(e)}")
                    continue

            logger.info(f"Total meetings found: {len(meetings)}")
            return meetings

        except Exception as e:
            logger.error(f"Error getting upcoming meetings: {str(e)}")
            return []

    def debug_calendars(self):
        """Print debug information about available calendars"""
        logger.info("=== Calendar Debug Information ===")
        for cal_id, cal_info in self.calendars.items():
            logger.info(f"""
            Calendar ID: {cal_id}
            Summary: {cal_info['summary']}
            Access Role: {cal_info['access_role']}
            Primary: {cal_info['primary']}
            """)
        logger.info("===============================")

    def verify_calendar_access(self):
        """Debug calendar access"""
        try:
            logger.info("=== Verifying Calendar Access ===")
            # List all authorized calendars
            calendar_list = self.service.calendarList().list().execute()

            logger.info(f"Total calendars accessible: {len(calendar_list.get('items', []))}")
            for calendar in calendar_list['items']:
                logger.info(f"""
                Calendar found:
                - Email: {calendar.get('id')}
                - Name: {calendar.get('summary')}
                - Access Role: {calendar.get('accessRole')}
                - Can see events: {calendar.get('accessRole') in ['owner', 'writer', 'reader']}
                """)

            # Try to access specific calendars we want to monitor
            for user_email in Config.AUTHORIZED_USERS:
                try:
                    logger.info(f"Attempting to access calendar for: {user_email}")
                    events = self.service.events().list(
                        calendarId=user_email,
                        maxResults=1
                    ).execute()
                    logger.info(f"Successfully accessed calendar for {user_email}")
                except Exception as e:
                    logger.error(f"Failed to access calendar for {user_email}: {str(e)}")

            logger.info("=== Calendar Access Verification Complete ===")
        except Exception as e:
            logger.error(f"Calendar verification failed: {str(e)}")