"""
Google Calendar Integration

Handles authentication and event creation for the Journal AI Pipeline.
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_IMPORTS_AVAILABLE = True
except ImportError:
    GOOGLE_IMPORTS_AVAILABLE = False


class GoogleCalendarIntegration:
    """Handles Google Calendar API operations"""
    
    # Scopes needed for calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.credentials_file = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = 'token.json'
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self.service = None
        
        if not GOOGLE_IMPORTS_AVAILABLE:
            print("⚠️ Google Calendar libraries not installed. Run: pip install -r requirements.txt")
            return
            
        self._authenticate()
    
    def _authenticate(self):
        """Handle Google Calendar authentication"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Credentials file not found: {self.credentials_file}")
                    print("Please follow GOOGLE_CALENDAR_SETUP.md to set up credentials")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar authenticated successfully")
        except Exception as e:
            print(f"❌ Failed to create calendar service: {e}")
    
    def is_available(self):
        """Check if Google Calendar integration is ready"""
        return GOOGLE_IMPORTS_AVAILABLE and self.service is not None
    
    def create_event(self, title, start_time, end_time, description="", date_str=None):
        """Create a single calendar event"""
        if not self.is_available():
            return {"error": "Google Calendar not available"}
        
        try:
            # If date_str provided, use it; otherwise use today
            if date_str:
                event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                event_date = datetime.now().date()
            
            # Parse time strings (e.g., "09:00", "10:30")
            start_dt = datetime.combine(
                event_date, 
                datetime.strptime(start_time, '%H:%M').time()
            )
            
            if end_time:
                end_dt = datetime.combine(
                    event_date,
                    datetime.strptime(end_time, '%H:%M').time()
                )
            else:
                # Default to 1 hour duration
                end_dt = start_dt + timedelta(hours=1)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'America/New_York',  # Adjust as needed
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'America/New_York',
                },
            }
            
            result = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": result['id'],
                "event_link": result.get('htmlLink'),
                "title": title,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            }
            
        except HttpError as e:
            return {"error": f"Google Calendar API error: {e}"}
        except Exception as e:
            return {"error": f"Event creation error: {e}"}
    
    def create_events_from_ai_response(self, ai_response, date_str=None):
        """Create multiple events from AI response"""
        if not self.is_available():
            return {"error": "Google Calendar not available"}
        
        events_created = []
        errors = []
        
        # Handle different AI response formats
        calendar_events = []
        
        if isinstance(ai_response, dict):
            if 'response' in ai_response and isinstance(ai_response['response'], dict):
                # Structured response
                response_data = ai_response['response']
                if 'calendar_events' in response_data:
                    calendar_events = response_data['calendar_events']
                elif 'time_blocks' in response_data:
                    # Convert time blocks to events
                    for block in response_data['time_blocks']:
                        if 'time' in block and 'activity' in block:
                            time_range = block['time'].split('-')
                            if len(time_range) == 2:
                                calendar_events.append({
                                    'title': block.get('calendar_title', block['activity']),
                                    'start_time': time_range[0],
                                    'end_time': time_range[1],
                                    'description': f"Activity: {block['activity']}"
                                })
        
        # Create each event
        for event_data in calendar_events:
            result = self.create_event(
                title=event_data.get('title', 'Planned Activity'),
                start_time=event_data.get('start_time'),
                end_time=event_data.get('end_time'),
                description=event_data.get('description', ''),
                date_str=date_str
            )
            
            if 'error' in result:
                errors.append(result['error'])
            else:
                events_created.append(result)
        
        return {
            "events_created": len(events_created),
            "events": events_created,
            "errors": errors,
            "total_attempted": len(calendar_events)
        }
    
    def list_todays_events(self):
        """List today's calendar events"""
        if not self.is_available():
            return {"error": "Google Calendar not available"}
        
        try:
            # Get today's events
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
            end_time = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                "success": True,
                "count": len(events),
                "events": [{
                    "summary": event.get('summary', 'No title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "id": event['id']
                } for event in events]
            }
            
        except HttpError as e:
            return {"error": f"Failed to list events: {e}"}


def test_calendar_integration():
    """Test function for Google Calendar integration"""
    print("🧪 Testing Google Calendar Integration")
    print("=" * 50)
    
    calendar = GoogleCalendarIntegration()
    
    if not calendar.is_available():
        print("❌ Google Calendar integration not available")
        return False
    
    # Test listing today's events
    print("\n1. Testing list today's events:")
    events = calendar.list_todays_events()
    if 'error' in events:
        print(f"   ❌ Error: {events['error']}")
    else:
        print(f"   ✅ Found {events['count']} events for today")
        for event in events['events'][:3]:  # Show first 3
            print(f"      - {event['summary']} at {event['start']}")
    
    # Test creating a sample event
    print("\n2. Testing create event:")
    test_event = calendar.create_event(
        title="Test Event - Journal AI Pipeline",
        start_time="15:00",
        end_time="15:30",
        description="Test event created by Journal AI Pipeline"
    )
    
    if 'error' in test_event:
        print(f"   ❌ Error: {test_event['error']}")
    else:
        print(f"   ✅ Created event: {test_event['title']}")
        print(f"      Event link: {test_event.get('event_link', 'N/A')}")
    
    print("\n✅ Google Calendar integration test complete!")
    return True


if __name__ == "__main__":
    test_calendar_integration()