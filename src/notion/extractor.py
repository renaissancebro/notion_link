"""
Journal Content Extractor for AI Pipeline

Extracts structured journal data from Notion and formats it for OpenAI processing
and Google Calendar integration.
"""

import datetime
import json
from datetime import date, timedelta
from notion_fetcher import (
    get_entries_for_date,
    find_edited_entries,
    search_for_entries_with_content,
    get_entry_by_id
)


class JournalExtractor:
    """Extract and format journal content for AI pipeline"""
    
    def __init__(self):
        self.template_keywords = [
            "Notion Template", "Daily Founder Frame", "Entrepreneur Identity Tracker",
            "Entrepreneurial Creed", "Time to Ship", "What Did I Build Today",
            "technical rep", "Name your enemy", "Dangerous Entrepreneur", 
            "Call it out", "Train your mind", "Estimate total time"
        ]
    
    def extract_user_content_from_blocks(self, blocks):
        """Extract only user-generated content, filtering out template text"""
        user_content = {}
        current_section = "general"
        
        for block in blocks.get("results", []):
            block_type = block.get("type")
            if not block_type or block_type not in block:
                continue
                
            block_data = block[block_type]
            if "rich_text" not in block_data:
                continue
                
            texts = block_data["rich_text"]
            content = "".join([t.get("plain_text", "") for t in texts]).strip()
            
            if not content:
                continue
            
            # Skip template content
            is_template = any(keyword.lower() in content.lower() for keyword in self.template_keywords)
            if is_template:
                # Update current section based on headings
                if block_type.startswith("heading"):
                    if "What Did I Build Today" in content:
                        current_section = "built_today"
                    elif "technical rep" in content:
                        current_section = "emotional_work"
                    elif "module, snippet, or flow" in content:
                        current_section = "shipped_code"
                    elif "Dangerous Entrepreneur" in content:
                        current_section = "ideal_self"
                    elif "Scar Faced" in content:
                        current_section = "challenges"
                    elif "part of the stack" in content:
                        current_section = "tech_progress"
                    elif "3 ways better" in content:
                        current_section = "improvements"
                    elif "one thing to do tomorrow" in content:
                        current_section = "tomorrow_priority"
                    elif "tool am I rep" in content:
                        current_section = "tomorrow_tool"
                continue
            
            # This is user content - categorize it
            if current_section not in user_content:
                user_content[current_section] = []
            
            user_content[current_section].append({
                "type": block_type,
                "content": content,
                "created": block.get("created_time"),
                "last_edited": block.get("last_edited_time")
            })
        
        return user_content
    
    def get_journal_entry(self, target_date=None):
        """Get structured journal entry for a specific date"""
        if target_date is None:
            target_date = date.today()
        elif isinstance(target_date, str):
            target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date()
        
        entries = get_entries_for_date(target_date)
        
        if not entries:
            return {
                "date": target_date.isoformat(),
                "found": False,
                "content": {},
                "raw_data": None
            }
        
        entry = entries[0]  # Take first entry for the date
        
        # Extract user content
        if entry["content"] and entry["content"]["content_blocks"]:
            user_content = self.extract_user_content_from_blocks(entry["content"]["content_blocks"])
        else:
            user_content = {}
        
        return {
            "date": target_date.isoformat(),
            "found": True,
            "page_id": entry["page_id"],
            "created": entry["content"]["page_details"].get("created_time") if entry["content"] else None,
            "last_edited": entry["content"]["page_details"].get("last_edited_time") if entry["content"] else None,
            "content": user_content,
            "has_user_content": len(user_content) > 0,
            "raw_data": entry
        }
    
    def get_recent_entries(self, days=7):
        """Get journal entries for the last N days"""
        entries = []
        today = date.today()
        
        for i in range(days):
            target_date = today - timedelta(days=i)
            entry = self.get_journal_entry(target_date)
            if entry["found"]:
                entries.append(entry)
        
        return entries
    
    def format_for_openai(self, journal_data):
        """Format journal data for OpenAI consumption"""
        if isinstance(journal_data, list):
            # Multiple entries
            formatted = {
                "journal_entries": [],
                "summary": {
                    "total_entries": len(journal_data),
                    "date_range": f"{journal_data[-1]['date']} to {journal_data[0]['date']}" if journal_data else None,
                    "entries_with_content": sum(1 for entry in journal_data if entry["has_user_content"])
                }
            }
            
            for entry in journal_data:
                formatted["journal_entries"].append(self._format_single_entry(entry))
            
            return formatted
        else:
            # Single entry
            return self._format_single_entry(journal_data)
    
    def _format_single_entry(self, entry):
        """Format a single journal entry for AI processing"""
        if not entry["found"] or not entry["has_user_content"]:
            return {
                "date": entry["date"],
                "has_content": False,
                "message": "No user content found for this date"
            }
        
        formatted = {
            "date": entry["date"],
            "has_content": True,
            "last_updated": entry["last_edited"],
            "sections": {}
        }
        
        # Map our sections to readable names for AI
        section_mapping = {
            "built_today": "What I Built Today",
            "emotional_work": "Emotional/Technical Work Done", 
            "shipped_code": "Code/Features Shipped",
            "ideal_self": "What My Ideal Self Would Do",
            "challenges": "Challenges Faced",
            "tech_progress": "Technical Stack Progress",
            "improvements": "Daily Improvements",
            "tomorrow_priority": "Tomorrow's Priority",
            "tomorrow_tool": "Tomorrow's Tool Focus",
            "general": "General Notes"
        }
        
        for section_key, content_list in entry["content"].items():
            section_name = section_mapping.get(section_key, section_key)
            formatted["sections"][section_name] = [item["content"] for item in content_list]
        
        return formatted
    
    def extract_for_calendar_planning(self, journal_data):
        """Extract specific data useful for calendar/task planning"""
        if isinstance(journal_data, list):
            # Multiple entries - extract patterns and upcoming tasks
            planning_data = {
                "recent_accomplishments": [],
                "recurring_challenges": [],
                "tomorrow_priorities": [],
                "technical_focus_areas": [],
                "improvement_patterns": []
            }
            
            for entry in journal_data:
                if not entry["has_user_content"]:
                    continue
                
                content = entry["content"]
                
                # Extract accomplishments
                if "built_today" in content:
                    planning_data["recent_accomplishments"].extend([
                        f"{entry['date']}: {item['content']}" for item in content["built_today"]
                    ])
                
                # Extract tomorrow priorities
                if "tomorrow_priority" in content:
                    planning_data["tomorrow_priorities"].extend([
                        item["content"] for item in content["tomorrow_priority"]
                    ])
                
                # Extract technical focus
                if "tomorrow_tool" in content:
                    planning_data["technical_focus_areas"].extend([
                        item["content"] for item in content["tomorrow_tool"]
                    ])
                
                # Extract improvements for pattern recognition
                if "improvements" in content:
                    planning_data["improvement_patterns"].extend([
                        f"{entry['date']}: {item['content']}" for item in content["improvements"]
                    ])
            
            return planning_data
        else:
            # Single entry
            return self._extract_single_entry_for_calendar(journal_data)
    
    def _extract_single_entry_for_calendar(self, entry):
        """Extract calendar-relevant data from a single entry"""
        if not entry.get("has_user_content", False):
            return {"has_planning_data": False}
        
        content = entry["content"]
        
        return {
            "has_planning_data": True,
            "date": entry["date"],
            "completed_today": content.get("built_today", []),
            "tomorrow_priority": content.get("tomorrow_priority", []),
            "tomorrow_tool": content.get("tomorrow_tool", []),
            "challenges_to_address": content.get("challenges", []),
            "improvement_areas": content.get("improvements", [])
        }


# Convenience functions for easy import
def get_today_journal_for_ai():
    """Quick function to get today's journal formatted for OpenAI"""
    extractor = JournalExtractor()
    today_data = extractor.get_journal_entry()
    return extractor.format_for_openai(today_data)


def get_recent_journals_for_ai(days=7):
    """Quick function to get recent journals formatted for OpenAI"""
    extractor = JournalExtractor()
    recent_data = extractor.get_recent_entries(days)
    return extractor.format_for_openai(recent_data)


def get_calendar_planning_data(days=3):
    """Quick function to get calendar planning data"""
    extractor = JournalExtractor()
    recent_data = extractor.get_recent_entries(days)
    return extractor.extract_for_calendar_planning(recent_data)


if __name__ == "__main__":
    # Example usage
    print("=== TODAY'S JOURNAL FOR AI ===")
    today_ai_data = get_today_journal_for_ai()
    print(json.dumps(today_ai_data, indent=2))
    
    print("\n=== CALENDAR PLANNING DATA ===")
    calendar_data = get_calendar_planning_data()
    print(json.dumps(calendar_data, indent=2))