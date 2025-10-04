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
            from openai import OpenAI
            
            # Initialize OpenAI client
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
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
    def create_explicit_plan_prompt(explicit_plan, planning_context=None):
        """Create prompt for scheduling explicit user-provided plan.

        This bypasses AI inference and just validates/schedules the user's explicit plan.
        """
        planning_context = planning_context or {}
        plan_json = json.dumps(explicit_plan, indent=2)
        existing_events = planning_context.get('existing_calendar_events', [])
        existing_events_json = json.dumps(existing_events, indent=2)

        prompt = f"""
You are a scheduling assistant. The user has provided an explicit daily plan with specific times.
Your job is to validate it and format it for calendar creation.

USER'S EXPLICIT PLAN:
{plan_json}

EXISTING CALENDAR EVENTS (to check for conflicts):
{existing_events_json}

Return a JSON response with this structure:
{{
  "calendar_events": [
    {{
      "title": "Task from user's plan",
      "start_time": "09:00",
      "end_time": "10:30",
      "description": "Task details"
    }}
  ],
  "conflicts": [
    {{
      "plan_item": "User's task that conflicts",
      "conflict_with": "Existing calendar event",
      "suggestion": "How to resolve"
    }}
  ],
  "validation_notes": "Any warnings or suggestions"
}}

RULES:
1. Use the exact times and tasks from the user's plan
2. Flag any conflicts with existing calendar events
3. If a task doesn't have an end time, use reasonable defaults (1 hour for most tasks)
4. Keep task titles clear and actionable
5. Do NOT modify the user's intent - just format it for the calendar
"""
        return prompt

    @staticmethod
    def create_daily_planning_prompt(journal_data, planning_context=None):
        """Create prompt for daily planning and task prioritization"""
        planning_context = planning_context or {}
        journal_json = json.dumps(journal_data, indent=2)
        planning_json = json.dumps(planning_context, indent=2)
        existing_events = planning_context.get('existing_calendar_events', [])
        existing_events_json = json.dumps(existing_events, indent=2)
        free_windows = planning_context.get('free_time_windows', [])
        free_windows_json = json.dumps(free_windows, indent=2)
        example_schema = {
            "overview": "High-level goals for the day",
            "time_blocks": [
                {
                    "time": "08:00-09:30",
                    "activity": "Internship application sprint",
                    "calendar_title": "Apply: Target Internships",
                    "source_action_items": ["Internship outreach emails"],
                    "notes": "Customize resumes for top roles"
                }
            ],
            "calendar_events": [
                {
                    "title": "Apply: Target Internships",
                    "start_time": "08:00",
                    "end_time": "09:30",
                    "description": "Internship outreach emails"
                }
            ],
            "unassigned_action_items": [],
            "reasoning": "Explain prioritization, how the schedule avoids conflicts, and how gaps are used"
        }
        schema_json = json.dumps(example_schema, indent=2)

        prompt = f"""
You are a focused productivity strategist. Build a concrete, time-blocked plan for the next workday using the journal context and actionable items below. Prioritize meaningful work streams such as internship applications, accounting study, and customer discovery outreach while preserving momentum from recent accomplishments.

WORKING HOURS TO PLAN: 08:00-20:00 Central Time. Ensure the schedule is sequential, has no overlaps, and leaves no gaps longer than 60 minutes. Include purposeful breaks (e.g., lunch) and focused deep-work blocks.

JOURNAL DATA (verbatim, do not repeat back verbatim):
{journal_json}

ACTIONABLE INPUTS FOR SCHEDULING (includes extracted tasks with suggested durations):
{planning_json}

EXISTING CALENDAR EVENTS (busy blocks you must respect; schedule around these and do not edit them):
{existing_events_json}

AVAILABLE FREE WINDOWS (use these gaps for new work blocks):
{free_windows_json}

PLANNING DIRECTIVES:
1. Every action item with an "estimated_minutes" value must appear across enough time blocks to cover that estimate; break intensive work (over ~60 minutes) into multiple focused sessions.
2. Only schedule new work inside the free windows above; do not overlap the busy events. If a free window is longer than needed, you may split it across multiple purposeful blocks (deep work, outreach, recovery).
3. Prioritize high-leverage tasks (internship applications, accounting study, customer discovery) early in the day before generic admin tasks.
4. Use the provided estimates as guidance, but you may adjust by ±15 minutes to fit the available windows. Ensure the sum of blocks for a task is realistic and fits the free windows.
5. Keep block descriptions specific and actionable so they can be placed directly onto the calendar.
6. If any action item cannot be scheduled, list it in "unassigned_action_items" with a brief reason and a suggested next opportunity.

Respond with valid JSON only using this structure (fill every field):
{schema_json}
"""
        return prompt
    
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
