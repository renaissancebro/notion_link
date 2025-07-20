"""
Main Pipeline

Orchestrates the complete flow: Notion → AI → Calendar
"""

import json
from datetime import date, datetime

from notion.extractor import JournalExtractor
from ai.processor import AIProcessor, PromptGenerator
from calendar_api.integration import GoogleCalendarIntegration


class JournalAIPipeline:
    """Main pipeline for processing journal data through AI and calendar integration"""
    
    def __init__(self):
        self.notion = JournalExtractor()
        self.ai = AIProcessor()
        self.calendar = GoogleCalendarIntegration()
        
        # Check component availability
        if not self.ai.is_available():
            print("⚠️ Warning: OpenAI integration not available")
        if not self.calendar.is_available():
            print("⚠️ Warning: Google Calendar integration not available")
    
    def extract_journal_data(self, target_date=None, include_recent=True):
        """Step 1: Extract journal data from Notion"""
        print("🔍 Extracting journal data from Notion...")
        
        if target_date:
            # Get specific date
            journal_data = self.notion.get_journal_entry(target_date)
            formatted_data = self.notion.format_for_openai(journal_data)
        else:
            # Get today + recent context
            today_data = self.notion.get_journal_entry()
            
            if include_recent:
                recent_data = self.notion.get_recent_entries(days=3)
                formatted_data = self.notion.format_for_openai(recent_data)
            else:
                formatted_data = self.notion.format_for_openai(today_data)
        
        print(f"✅ Extracted journal data: {formatted_data.get('summary', 'Single entry')}")
        return formatted_data
    
    def prepare_ai_prompt(self, journal_data, task_type="daily_planning"):
        """Step 2: Prepare structured prompt for OpenAI"""
        print(f"📝 Preparing AI prompt for: {task_type}")
        
        prompts = {
            "daily_planning": PromptGenerator.create_daily_planning_prompt(journal_data),
            "reflection": PromptGenerator.create_reflection_prompt(journal_data),
            "goal_setting": PromptGenerator.create_goal_setting_prompt(journal_data),
            "calendar_optimization": PromptGenerator.create_calendar_prompt(journal_data)
        }
        
        return prompts.get(task_type, prompts["daily_planning"])
    
    def process_with_ai(self, prompt):
        """Step 3: Process with OpenAI"""
        return self.ai.process_with_openai(prompt)
    
    def create_calendar_events(self, ai_response, target_date=None):
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
        result = self.calendar.create_events_from_ai_response(ai_response, date_str)
        
        if 'error' in result:
            return {
                "status": "error",
                "message": result['error'],
                "events_created": 0
            }
        
        return {
            "status": "success",
            "events_created": result['events_created'],
            "events": result['events'],
            "errors": result['errors'],
            "total_attempted": result['total_attempted'],
            "date": date_str
        }
    
    def run_full_pipeline(self, target_date=None, task_type="daily_planning"):
        """Run the complete pipeline"""
        print("🚀 Starting AI Pipeline...")
        print("="*50)
        
        try:
            # Step 1: Extract journal data
            journal_data = self.extract_journal_data(target_date)
            
            # Step 2: Prepare AI prompt
            ai_prompt = self.prepare_ai_prompt(journal_data, task_type)
            
            # Step 3: Process with OpenAI
            ai_response = self.process_with_ai(ai_prompt)
            
            # Step 4: Create calendar events
            calendar_result = self.create_calendar_events(ai_response, target_date)
            
            print("="*50)
            print("✅ Pipeline complete!")
            
            return {
                "journal_data": journal_data,
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