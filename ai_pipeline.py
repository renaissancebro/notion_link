"""
AI Pipeline Integration

Connects journal extraction -> OpenAI processing -> Google Calendar planning
"""

import json
import os
from datetime import date, datetime, timedelta
from journal_extractor import JournalExtractor, get_today_journal_for_ai, get_calendar_planning_data
from dotenv import load_dotenv

load_dotenv()


class AIPipeline:
    """Main pipeline for processing journal data through AI and calendar integration"""
    
    def __init__(self):
        self.extractor = JournalExtractor()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️ Warning: OPENAI_API_KEY not found in .env file")
        # You'll add Google Calendar client here
    
    def extract_journal_data(self, target_date=None, include_recent=True):
        """Step 1: Extract journal data from Notion"""
        print("🔍 Extracting journal data from Notion...")
        
        if target_date:
            # Get specific date
            journal_data = self.extractor.get_journal_entry(target_date)
            formatted_data = self.extractor.format_for_openai(journal_data)
        else:
            # Get today + recent context
            today_data = self.extractor.get_journal_entry()
            
            if include_recent:
                recent_data = self.extractor.get_recent_entries(days=3)
                formatted_data = self.extractor.format_for_openai(recent_data)
            else:
                formatted_data = self.extractor.format_for_openai(today_data)
        
        print(f"✅ Extracted journal data: {formatted_data.get('summary', 'Single entry')}")
        return formatted_data
    
    def prepare_ai_prompt(self, journal_data, task_type="daily_planning"):
        """Step 2: Prepare structured prompt for OpenAI"""
        print(f"📝 Preparing AI prompt for: {task_type}")
        
        prompts = {
            "daily_planning": self._create_daily_planning_prompt(journal_data),
            "reflection": self._create_reflection_prompt(journal_data),
            "goal_setting": self._create_goal_setting_prompt(journal_data),
            "calendar_optimization": self._create_calendar_prompt(journal_data)
        }
        
        return prompts.get(task_type, prompts["daily_planning"])
    
    def _create_daily_planning_prompt(self, journal_data):
        """Create prompt for daily planning and task prioritization"""
        base_prompt = """
You are a productivity AI that helps entrepreneurs plan their day based on their journal entries.

JOURNAL DATA:
{journal_json}

TASK:
Based on this journal data, create a structured daily plan that includes:

1. **Morning Priorities** (2-3 high-impact tasks)
2. **Technical Focus** (specific tools/technologies to work on)
3. **Time Blocks** (suggested time allocation)
4. **Improvement Actions** (based on yesterday's reflections)
5. **Calendar Events** (specific meetings/blocks to schedule)

FORMAT YOUR RESPONSE AS JSON:
{{
  "morning_priorities": ["task1", "task2", "task3"],
  "technical_focus": "specific technology or tool",
  "time_blocks": [
    {{"time": "9:00-11:00", "activity": "Deep work on X", "calendar_title": "Deep Work: X"}},
    {{"time": "11:00-12:00", "activity": "Y", "calendar_title": "Y"}}
  ],
  "improvement_actions": ["action1", "action2"],
  "calendar_events": [
    {{"title": "Event Title", "start_time": "09:00", "duration_minutes": 120, "description": "Event description"}}
  ],
  "reasoning": "Brief explanation of planning decisions"
}}
"""
        return base_prompt.format(journal_json=json.dumps(journal_data, indent=2))
    
    def _create_reflection_prompt(self, journal_data):
        """Create prompt for reflection and insights"""
        return f"""
Analyze this entrepreneur's journal entries and provide insights on:
1. Progress patterns
2. Recurring challenges  
3. Growth opportunities
4. Productivity recommendations

JOURNAL DATA:
{json.dumps(journal_data, indent=2)}

Provide actionable insights in structured format.
"""
    
    def _create_goal_setting_prompt(self, journal_data):
        """Create prompt for goal setting and strategic planning"""
        return f"""
Based on this journal data, suggest:
1. Weekly goals
2. Monthly objectives
3. Skill development priorities
4. Strategic focus areas

JOURNAL DATA:
{json.dumps(journal_data, indent=2)}

Format as actionable goals with timelines.
"""
    
    def _create_calendar_prompt(self, journal_data):
        """Create prompt specifically for calendar event generation"""
        calendar_data = self.extractor.extract_for_calendar_planning(journal_data)
        
        return f"""
Create specific calendar events based on this planning data:

PLANNING DATA:
{json.dumps(calendar_data, indent=2)}

Return a JSON array of calendar events:
[
  {{
    "title": "Event Title",
    "start_time": "09:00",
    "end_time": "10:30", 
    "date": "2025-07-20",
    "description": "Detailed description",
    "event_type": "focus_time|meeting|review|planning"
  }}
]

Focus on creating actionable, time-bounded events that align with the user's priorities.
"""
    
    def process_with_openai(self, prompt):
        """Step 3: Send to OpenAI (placeholder - you'll implement this)"""
        print("🤖 Processing with OpenAI...")
        
        # This is where you'll add your OpenAI API call
        # Example structure:
        """
        import openai
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a productivity AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
        """
        
        # For now, return a placeholder
        return {
            "status": "placeholder",
            "message": "OpenAI integration not yet implemented",
            "prompt_ready": True,
            "prompt_length": len(prompt)
        }
    
    def create_calendar_events(self, ai_response):
        """Step 4: Create Google Calendar events (placeholder)"""
        print("📅 Creating Google Calendar events...")
        
        # This is where you'll add Google Calendar integration
        # Example structure:
        """
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        service = build('calendar', 'v3', credentials=creds)
        
        for event_data in ai_response['calendar_events']:
            event = {
                'summary': event_data['title'],
                'start': {'dateTime': f"2025-07-20T{event_data['start_time']}:00"},
                'end': {'dateTime': f"2025-07-20T{event_data['end_time']}:00"},
                'description': event_data['description']
            }
            
            service.events().insert(calendarId='primary', body=event).execute()
        """
        
        return {
            "status": "placeholder", 
            "message": "Google Calendar integration not yet implemented",
            "events_ready": True
        }
    
    def run_full_pipeline(self, target_date=None, task_type="daily_planning"):
        """Run the complete pipeline"""
        print("🚀 Starting AI Pipeline...")
        print("="*50)
        
        # Step 1: Extract journal data
        journal_data = self.extract_journal_data(target_date)
        
        # Step 2: Prepare AI prompt
        ai_prompt = self.prepare_ai_prompt(journal_data, task_type)
        
        # Step 3: Process with OpenAI
        ai_response = self.process_with_openai(ai_prompt)
        
        # Step 4: Create calendar events
        calendar_result = self.create_calendar_events(ai_response)
        
        print("="*50)
        print("✅ Pipeline complete!")
        
        return {
            "journal_data": journal_data,
            "ai_prompt": ai_prompt,
            "ai_response": ai_response,
            "calendar_result": calendar_result,
            "timestamp": datetime.now().isoformat()
        }


def quick_pipeline_test():
    """Quick test of the pipeline with current data"""
    pipeline = AIPipeline()
    return pipeline.run_full_pipeline()


if __name__ == "__main__":
    # Test the pipeline
    print("Testing AI Pipeline...")
    result = quick_pipeline_test()
    
    print("\n=== PIPELINE RESULT ===")
    print(json.dumps(result, indent=2, default=str))