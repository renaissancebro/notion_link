"""
Google Calendar Integration

Handles authentication and event creation for the Journal AI Pipeline.
"""

import os
import json
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
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
    TIMEZONE = 'America/Chicago'
    
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
            
            tz = ZoneInfo(self.TIMEZONE)
            start_dt = start_dt.replace(tzinfo=tz)
            end_dt = end_dt.replace(tzinfo=tz)

            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': self.TIMEZONE,
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': self.TIMEZONE,
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
    
    def _extract_plan_payload(self, ai_response):
        if not isinstance(ai_response, dict):
            return None
        response_data = ai_response.get('response')
        if isinstance(response_data, dict):
            return response_data
        return ai_response if isinstance(ai_response, dict) else None

    def _parse_time_window(self, time_window):
        if not isinstance(time_window, str) or '-' not in time_window:
            return None
        sanitized = time_window.replace('–', '-').replace('—', '-').replace(' to ', '-')
        if '-' not in sanitized:
            return None
        start_str, end_str = [part.strip() for part in sanitized.split('-', 1)]
        try:
            start = datetime.strptime(start_str, '%H:%M')
            end = datetime.strptime(end_str, '%H:%M')
        except ValueError:
            return None
        if end <= start:
            return None
        return start, end

    def _validate_and_prepare_events(self, plan_payload, planning_context=None):
        errors = []
        warnings = []
        normalized_events = []

        if not plan_payload:
            return {
                "status": "error",
                "errors": ["AI response missing structured payload."],
                "events": []
            }

        time_blocks = plan_payload.get('time_blocks', [])
        if not isinstance(time_blocks, list) or not time_blocks:
            return {
                "status": "error",
                "errors": ["AI response did not include any time_blocks."],
                "events": []
            }

        WORK_START = datetime.strptime('08:00', '%H:%M')
        WORK_END = datetime.strptime('20:00', '%H:%M')
        previous_end = WORK_START

        busy_intervals = []
        free_intervals = []
        if planning_context and isinstance(planning_context, dict):
            for busy in planning_context.get('existing_calendar_events', []):
                start_busy = busy.get('start_time')
                end_busy = busy.get('end_time')
                if not start_busy or not end_busy:
                    continue
                try:
                    start_dt_busy = datetime.strptime(start_busy, '%H:%M')
                    end_dt_busy = datetime.strptime(end_busy, '%H:%M')
                except ValueError:
                    continue
                if end_dt_busy <= start_dt_busy:
                    continue
                title_lower = (busy.get('title') or '').lower()
                busy_intervals.append((start_dt_busy, end_dt_busy, title_lower, busy.get('title', 'Busy')))

            for window in planning_context.get('free_time_windows', []):
                time_range = window.get('time')
                if not time_range:
                    continue
                parts = time_range.replace('–', '-').replace('—', '-').split('-', 1)
                if len(parts) != 2:
                    continue
                try:
                    start_free = datetime.strptime(parts[0].strip(), '%H:%M')
                    end_free = datetime.strptime(parts[1].strip(), '%H:%M')
                except ValueError:
                    continue
                if end_free <= start_free:
                    continue
                free_intervals.append((start_free, end_free))

        busy_intervals.sort(key=lambda item: item[0])
        free_intervals.sort(key=lambda item: item[0])

        for index, block in enumerate(time_blocks):
            if not isinstance(block, dict):
                errors.append(f"Time block {index + 1} is not an object.")
                continue

            window = self._parse_time_window(block.get('time'))
            if not window:
                errors.append(f"Time block {index + 1} has invalid time format: {block.get('time')}")
                continue

            start_dt, end_dt = window
            if start_dt < WORK_START or end_dt > WORK_END:
                warnings.append(
                    f"Block '{block.get('activity', 'Unnamed activity')}' falls outside 08:00-20:00 window."
                )

            latest_occupied_before = previous_end
            skip_block = False
            for busy_start, busy_end, busy_title_lower, busy_title in busy_intervals:
                if busy_end <= start_dt:
                    latest_occupied_before = max(latest_occupied_before, busy_end)
                if not (busy_end <= start_dt or busy_start >= end_dt):
                    block_title_lower = (block.get('calendar_title') or block.get('activity') or '').lower()
                    if block_title_lower and busy_title_lower and (
                        block_title_lower in busy_title_lower or busy_title_lower in block_title_lower
                    ):
                        warnings.append(
                            f"Skipped creating duplicate block '{block.get('activity', 'Unnamed activity')}' because it overlaps existing event '{busy_title}'."
                        )
                        skip_block = True
                        break
                    else:
                        errors.append(
                            f"Time block '{block.get('activity', 'Unnamed activity')}' conflicts with existing event '{busy_title}'."
                        )
            if skip_block:
                continue

            if start_dt < latest_occupied_before:
                errors.append(
                    f"Time block '{block.get('activity', 'Unnamed activity')}' overlaps with another scheduled item."
                )
                continue

            gap_minutes = (start_dt - latest_occupied_before).total_seconds() / 60
            if gap_minutes > 60:
                warnings.append(f"Gap of {int(gap_minutes)} minutes before '{block.get('activity', 'Unnamed activity')}'.")

            activity = block.get('activity') or block.get('calendar_title')
            if not activity:
                errors.append(f"Time block {index + 1} missing activity description.")
                continue

            title = block.get('calendar_title') or activity
            description_parts = [activity]
            if block.get('notes'):
                description_parts.append(block['notes'])
            if block.get('source_action_items'):
                joined_items = ", ".join(block['source_action_items'])
                description_parts.append(f"Action items: {joined_items}")

            if free_intervals:
                fits_free_window = any(start_dt >= free_start and end_dt <= free_end for free_start, free_end in free_intervals)
                if not fits_free_window:
                    errors.append(
                        f"Time block '{activity}' does not fit within any available free window."
                    )
                    continue

            normalized_events.append({
                'title': title,
                'start_time': start_dt.strftime('%H:%M'),
                'end_time': end_dt.strftime('%H:%M'),
                'description': " | ".join(description_parts),
                'source_action_items': block.get('source_action_items', [])
            })

            previous_end = end_dt

        unmatched_items = []
        if planning_context and isinstance(planning_context, dict):
            planned_text = "\n".join(
                f"{event['title']} {event.get('description', '')}" for event in normalized_events
            ).lower()
            for item in planning_context.get('action_items', []):
                title = item.get('title', '')
                if title and title.lower() not in planned_text:
                    unmatched_items.append(title)

        conflict_only = errors and all(
            ('conflicts with existing event' in err) or ('does not fit within any available free window' in err)
            for err in errors
        )

        if conflict_only and not normalized_events:
            warnings.extend(errors)
            errors = []

        if errors:
            return {
                "status": "error",
                "errors": errors,
                "warnings": warnings,
                "unmatched": unmatched_items,
                "events": []
            }

        latest_end = previous_end
        if busy_intervals:
            latest_busy_end = max(interval[1] for interval in busy_intervals)
            if latest_busy_end > latest_end:
                latest_end = latest_busy_end
        tail_gap = (WORK_END - latest_end).total_seconds() / 60
        if tail_gap > 60:
            warnings.append(f"Day ends with an unscheduled gap of {int(tail_gap)} minutes after the last commitment.")

        return {
            "status": "ok",
            "events": normalized_events,
            "warnings": warnings,
            "unmatched": unmatched_items
        }

    def list_events_for_date(self, date_str):
        """List calendar events for a specific ISO date."""
        if not self.is_available():
            return {"error": "Google Calendar not available"}

        try:
            tz = ZoneInfo(self.TIMEZONE)
        except Exception:
            tz = None

        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if tz:
            start_dt = datetime.combine(target_date, time.min, tzinfo=tz)
            end_dt = datetime.combine(target_date, time.max, tzinfo=tz)
        else:
            start_dt = datetime.combine(target_date, time.min)
            end_dt = datetime.combine(target_date, time.max)

        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = []
            for event in events_result.get('items', []):
                start = event.get('start', {})
                end = event.get('end', {})
                events.append({
                    'title': event.get('summary', 'No title'),
                    'start': start.get('dateTime') or start.get('date'),
                    'end': end.get('dateTime') or end.get('date'),
                    'id': event.get('id')
                })

            return {
                'success': True,
                'events': events
            }
        except HttpError as e:
            return {"error": f"Failed to list events: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error listing events: {e}"}

    def create_events_from_ai_response(self, ai_response, date_str=None, planning_context=None):
        """Create multiple events from AI response"""
        if not self.is_available():
            return {"error": "Google Calendar not available"}

        plan_payload = self._extract_plan_payload(ai_response)
        validation = self._validate_and_prepare_events(plan_payload, planning_context)

        if validation.get("status") != "ok":
            return {
                "error": "AI response failed validation",
                "details": validation
            }

        events_created = []
        errors = []
        calendar_events = validation["events"]

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
            "total_attempted": len(calendar_events),
            "validation_warnings": validation.get('warnings', []),
            "unscheduled_action_items": validation.get('unmatched', [])
        }
    
    def list_todays_events(self):
        """List today's calendar events"""
        if not self.is_available():
            return {"error": "Google Calendar not available"}
        today_str = datetime.now().date().isoformat()
        result = self.list_events_for_date(today_str)
        if 'error' in result:
            return result
        events = result.get('events', [])
        return {
            "success": True,
            "count": len(events),
            "events": events
        }


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
