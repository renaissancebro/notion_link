"""
AI Processing Module

Handles OpenAI integration and prompt generation for journal analysis.
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()


class AIProcessor:
    """Handles OpenAI API calls and response processing"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️ Warning: OPENAI_API_KEY not found in .env file")
    
    def is_available(self):
        """Check if AI processing is available"""
        return self.api_key is not None
    
    def process_with_openai(self, prompt):
        """Send prompt to OpenAI and return structured response"""
        print("🤖 Processing with OpenAI...")
        
        if not self.is_available():
            return {
                "status": "error",
                "message": "OpenAI API key not configured",
                "prompt_ready": True,
                "prompt_length": len(prompt)
            }
        
        try:
            import openai
            
            # Set the API key
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a productivity AI assistant helping entrepreneurs plan their day based on journal entries. Always respond with structured, actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON response if the prompt requested JSON
            try:
                parsed_response = json.loads(ai_response)
                return {
                    "status": "success",
                    "response": parsed_response,
                    "raw_response": ai_response,
                    "prompt_length": len(prompt),
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                # Return as text if not valid JSON
                return {
                    "status": "success",
                    "response": ai_response,
                    "prompt_length": len(prompt),
                    "tokens_used": response.usage.total_tokens
                }
                
        except ImportError:
            return {
                "status": "error",
                "message": "OpenAI library not installed. Run: pip install openai",
                "prompt_ready": True,
                "prompt_length": len(prompt)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"OpenAI API error: {str(e)}",
                "prompt_ready": True,
                "prompt_length": len(prompt)
            }


class PromptGenerator:
    """Generates structured prompts for different AI tasks"""
    
    @staticmethod
    def create_daily_planning_prompt(journal_data):
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
    
    @staticmethod
    def create_reflection_prompt(journal_data):
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
    
    @staticmethod
    def create_goal_setting_prompt(journal_data):
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
    
    @staticmethod
    def create_calendar_prompt(journal_data):
        """Create prompt specifically for calendar event generation"""
        return f"""
Create specific calendar events based on this planning data:

PLANNING DATA:
{json.dumps(journal_data, indent=2)}

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