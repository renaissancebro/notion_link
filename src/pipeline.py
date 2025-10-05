"""
Main Pipeline

Orchestrates the complete flow: Notion → AI → Calendar
"""

import json
from datetime import date, datetime
from zoneinfo import ZoneInfo

from notion.extractor import JournalExtractor
from ai.processor import AIProcessor, PromptGenerator
from calendar_api.integration import GoogleCalendarIntegration


class JournalAIPipeline:
    """Main pipeline for processing journal data through AI and calendar integration"""
    
    def __init__(self):
        self.notion = JournalExtractor()
        self.ai = AIProcessor()
        self.calendar = GoogleCalendarIntegration()
        self._latest_planning_source = None
        
        # Check component availability
        if not self.ai.is_available():
            print("⚠️ Warning: OpenAI integration not available")
        if not self.calendar.is_available():
            print("⚠️ Warning: Google Calendar integration not available")
    
    def extract_journal_data(self, target_date=None, include_recent=True):
        """Step 1: Extract journal data from Notion"""
        print("🔍 Extracting journal data from Notion...")
        planning_source = None

        if target_date:
            # Get specific date
            journal_data = self.notion.get_journal_entry(target_date)
            formatted_data = self.notion.format_for_openai(journal_data)
            planning_source = journal_data
        else:
            # Get today + recent context
            today_data = self.notion.get_journal_entry()
            
            if include_recent:
                recent_data = self.notion.get_recent_entries(days=3)
                planning_source = recent_data if recent_data else today_data
                formatted_data = self.notion.format_for_openai(recent_data)
            else:
                formatted_data = self.notion.format_for_openai(today_data)
                planning_source = today_data

        print(f"✅ Extracted journal data: {formatted_data.get('summary', 'Single entry')}")
        self._latest_planning_source = planning_source
        return formatted_data

    def build_planning_context(self, planning_source=None, plan_date=None):
        """Construct structured planning context with existing calendar events."""
        source = planning_source or self._latest_planning_source
        if not source:
            return {}

        context = self.notion.extract_for_calendar_planning(source)

        plan_date_str = None
        if plan_date:
            if isinstance(plan_date, str):
                plan_date_str = plan_date
            else:
                plan_date_str = plan_date.isoformat()
        elif isinstance(source, dict) and source.get('date'):
            plan_date_str = source['date']
        elif isinstance(source, list) and source:
            first = source[0]
            if isinstance(first, dict) and first.get('date'):
                plan_date_str = first['date']

        tz = ZoneInfo(getattr(self.calendar, 'TIMEZONE', 'America/Chicago')) if self.calendar else None

        if plan_date_str and self.calendar and self.calendar.is_available():
            existing = self.calendar.list_events_for_date(plan_date_str)
            if 'events' in existing:
                normalized = []
                busy_minutes = []
                for event in existing['events']:
                    start_raw = event.get('start')
                    end_raw = event.get('end')
                    start_time = self._extract_local_time(start_raw, tz)
                    end_time = self._extract_local_time(end_raw, tz)
                    normalized.append({
                        'title': event.get('title', event.get('summary', 'Busy')), 
                        'start_time': start_time,
                        'end_time': end_time
                    })
                    if start_time and end_time:
                        busy_minutes.append((self._time_to_minutes(start_time), self._time_to_minutes(end_time)))
                context['existing_calendar_events'] = normalized

                free_windows = self._compute_free_windows(busy_minutes)
                if free_windows:
                    context['free_time_windows'] = free_windows

        return context

    def _extract_local_time(self, raw_value, tz):
        if not raw_value or len(raw_value) <= 10:
            return None
        sanitized = raw_value.replace('Z', '+00:00')
        try:
            dt = datetime.fromisoformat(sanitized)
        except ValueError:
            return None
        if dt.tzinfo and tz:
            dt = dt.astimezone(tz)
        elif tz and not dt.tzinfo:
            dt = dt.replace(tzinfo=tz)
        return dt.strftime('%H:%M')

    def _time_to_minutes(self, time_str):
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def _minutes_to_time(self, minutes):
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def _compute_free_windows(self, busy_minutes):
        WORK_START = 8 * 60
        WORK_END = 20 * 60
        if not busy_minutes:
            return [{
                'time': f"{self._minutes_to_time(WORK_START)}-{self._minutes_to_time(WORK_END)}",
                'duration_minutes': WORK_END - WORK_START
            }]

        merged = []
        for start, end in sorted(busy_minutes):
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        free_windows = []
        cursor = WORK_START
        for start, end in merged:
            if start > cursor:
                free_windows.append({
                    'time': f"{self._minutes_to_time(cursor)}-{self._minutes_to_time(min(start, WORK_END))}",
                    'duration_minutes': max(0, min(start, WORK_END) - cursor)
                })
            cursor = max(cursor, end)
        if cursor < WORK_END:
            free_windows.append({
                'time': f"{self._minutes_to_time(cursor)}-{self._minutes_to_time(WORK_END)}",
                'duration_minutes': WORK_END - cursor
            })

        return [window for window in free_windows if window['duration_minutes'] > 0]

    def prepare_ai_prompt(self, journal_data, task_type="daily_planning", planning_context=None, explicit_plan=None):
        """Step 2: Prepare structured prompt for OpenAI"""
        print(f"📝 Preparing AI prompt for: {task_type}")

        if planning_context is None and task_type == "daily_planning":
            planning_context = self.build_planning_context()

        # If we have an explicit plan, use that instead of AI inference
        if explicit_plan and len(explicit_plan) > 0:
            print("✅ Using explicit plan from journal")
            return PromptGenerator.create_explicit_plan_prompt(explicit_plan, planning_context)

        prompts = {
            "daily_planning": PromptGenerator.create_daily_planning_prompt(journal_data, planning_context),
            "reflection": PromptGenerator.create_reflection_prompt(journal_data),
            "goal_setting": PromptGenerator.create_goal_setting_prompt(journal_data),
            "calendar_optimization": PromptGenerator.create_calendar_prompt(journal_data)
        }

        return prompts.get(task_type, prompts["daily_planning"])
    
    def process_with_ai(self, prompt):
        """Step 3: Process with OpenAI"""
        return self.ai.process_with_openai(prompt)
    
    def create_calendar_events(self, ai_response, target_date=None, planning_context=None):
        """Step 4: Create Google Calendar events"""
        print("📅 Creating Google Calendar events...")
        
        if not self.calendar.is_available():
            return {
                "status": "error",
                "message": "Google Calendar integration not available",
                "events_created": 0
            }
        
        # Determine target date
        if target_date:
            if isinstance(target_date, str):
                date_str = target_date
            else:
                date_str = target_date.isoformat()
        else:
            date_str = date.today().isoformat()
        
        # Create events from AI response
        result = self.calendar.create_events_from_ai_response(ai_response, date_str, planning_context)

        if 'error' in result:
            return {
                "status": "error",
                "message": result['error'],
                "events_created": 0,
                "details": result.get('details')
            }

        return {
            "status": "success",
            "events_created": result['events_created'],
            "events": result['events'],
            "errors": result['errors'],
            "total_attempted": result['total_attempted'],
            "validation_warnings": result.get('validation_warnings', []),
            "unscheduled_action_items": result.get('unscheduled_action_items', []),
            "date": date_str
        }
    
    def run_full_pipeline(self, target_date=None, task_type="daily_planning"):
        """Run the complete pipeline"""
        print("🚀 Starting AI Pipeline...")
        print("="*50)

        try:
            # Step 1: Extract journal data
            journal_data = self.extract_journal_data(target_date)

            # Step 1.5: Determine the plan date (always TOMORROW relative to journal date)
            from datetime import timedelta
            if target_date:
                journal_date = datetime.strptime(target_date, '%Y-%m-%d').date() if isinstance(target_date, str) else target_date
            else:
                journal_date = date.today()

            # Schedule for the NEXT day
            plan_date = (journal_date + timedelta(days=1)).isoformat()
            print(f"📅 Journal date: {journal_date.isoformat()} → Scheduling for: {plan_date}")

            planning_context = self.build_planning_context(plan_date=plan_date)

            # Check if we have an explicit plan from the journal
            explicit_plan = None
            if self._latest_planning_source:
                if isinstance(self._latest_planning_source, list):
                    # Check most recent entry for explicit plan
                    for entry in self._latest_planning_source:
                        if entry.get("has_explicit_plan"):
                            explicit_plan = entry.get("explicit_plan")
                            print(f"📋 Found explicit plan with {len(explicit_plan)} items")
                            break
                elif isinstance(self._latest_planning_source, dict):
                    if self._latest_planning_source.get("has_explicit_plan"):
                        explicit_plan = self._latest_planning_source.get("explicit_plan")
                        print(f"📋 Found explicit plan with {len(explicit_plan)} items")

            # Step 2: Prepare AI prompt (uses explicit plan if available)
            ai_prompt = self.prepare_ai_prompt(journal_data, task_type, planning_context, explicit_plan)

            # Step 3: Process with OpenAI
            ai_response = self.process_with_ai(ai_prompt)

            # Step 4: Create calendar events
            calendar_result = self.create_calendar_events(ai_response, target_date, planning_context)

            print("="*50)
            print("✅ Pipeline complete!")

            return {
                "journal_data": journal_data,
                "planning_context": planning_context,
                "explicit_plan": explicit_plan,
                "ai_prompt": ai_prompt,
                "ai_response": ai_response,
                "calendar_result": calendar_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }


def quick_test():
    """Quick test of the complete pipeline"""
    pipeline = JournalAIPipeline()
    return pipeline.run_full_pipeline()


if __name__ == "__main__":
    # Test the pipeline
    print("Testing Complete AI Pipeline...")
    result = quick_test()
    
    print("\n=== PIPELINE RESULT ===")
    print(json.dumps(result, indent=2, default=str))
