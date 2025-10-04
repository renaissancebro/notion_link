#!/usr/bin/env python3
"""
Journal AI Pipeline - Main Runner

Clean interface to run the complete journal processing pipeline.
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import JournalAIPipeline


def main():
    """Main entry point for the Journal AI Pipeline"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['help', '--help', '-h']:
            show_help()
            return
        
        elif command == 'test':
            test_pipeline()
            return
        
        elif command == 'run':
            # Full pipeline run
            target_date = sys.argv[2] if len(sys.argv) > 2 else None
            task_type = sys.argv[3] if len(sys.argv) > 3 else "daily_planning"
            
            run_pipeline(target_date, task_type)
            return
        
        elif command == 'extract':
            # Just extract and show data
            target_date = sys.argv[2] if len(sys.argv) > 2 else None
            extract_only(target_date)
            return
    
    # Default: run the pipeline
    print("🚀 Running Journal AI Pipeline...")
    run_pipeline()


def show_help():
    """Show usage help"""
    print("""
📋 Journal AI Pipeline - Usage

COMMANDS:
  python run.py                    - Run full pipeline for today
  python run.py run [date] [type]  - Run pipeline for specific date/type  
  python run.py extract [date]     - Extract journal data only
  python run.py test              - Test all components
  python run.py help              - Show this help

EXAMPLES:
  python run.py                           # Process today's journal
  python run.py run 2025-07-19           # Process specific date
  python run.py run today reflection     # Today with reflection prompt
  python run.py extract 2025-07-19       # Just show extracted data

TASK TYPES:
  daily_planning     - Create daily schedule (default)
  reflection         - Analyze patterns and insights  
  goal_setting       - Generate goals and objectives
  calendar_optimization - Focus on calendar events

SETUP:
  1. Copy .env.sample to .env and add your API keys
  2. Follow GOOGLE_CALENDAR_SETUP.md for calendar setup
  3. Run: pip install -r requirements.txt
""")


def test_pipeline():
    """Test all components"""
    print("🧪 Testing Journal AI Pipeline Components")
    print("=" * 60)
    
    pipeline = JournalAIPipeline()
    
    # Test Notion extraction
    print("\n1. Testing Notion extraction:")
    try:
        journal_data = pipeline.extract_journal_data()
        print(f"   ✅ Extracted: {journal_data.get('summary', 'Single entry')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test AI processing  
    print("\n2. Testing AI processing:")
    if pipeline.ai.is_available():
        print("   ✅ OpenAI API key configured")
    else:
        print("   ❌ OpenAI API key missing")
    
    # Test Calendar integration
    print("\n3. Testing Calendar integration:")
    if pipeline.calendar.is_available():
        print("   ✅ Google Calendar available")
    else:
        print("   ❌ Google Calendar not configured")
    
    print("\n✅ Component test complete!")


def extract_only(target_date=None):
    """Extract and display journal data only"""
    print("📖 Extracting Journal Data")
    print("=" * 40)
    
    pipeline = JournalAIPipeline()
    
    # Parse date
    if target_date and target_date.lower() == 'today':
        target_date = None
    elif target_date and target_date.lower() == 'yesterday':
        target_date = (date.today() - timedelta(days=1)).isoformat()
    
    try:
        journal_data = pipeline.extract_journal_data(target_date, include_recent=False)
        
        print(f"\n📅 Date: {journal_data.get('date', target_date or 'today')}")
        
        if isinstance(journal_data, dict) and journal_data.get('has_content'):
            sections = journal_data.get('sections', {})
            print(f"✅ Found content in {len(sections)} sections:")
            
            for section_name, content_list in sections.items():
                if content_list:
                    print(f"\n🔸 {section_name}:")
                    for item in content_list[:3]:  # Show first 3 items
                        preview = item[:100] + "..." if len(item) > 100 else item
                        print(f"   • {preview}")
                    if len(content_list) > 3:
                        print(f"   ... and {len(content_list) - 3} more items")
        else:
            print("❌ No user content found for this date")
    
    except Exception as e:
        print(f"❌ Error extracting data: {e}")


def run_pipeline(target_date=None, task_type="daily_planning"):
    """Run the complete pipeline"""
    print("🚀 Starting Complete Journal AI Pipeline")
    print("=" * 60)
    
    # Parse date
    if target_date and target_date.lower() == 'today':
        target_date = None
    elif target_date and target_date.lower() == 'yesterday':
        target_date = (date.today() - timedelta(days=1)).isoformat()
    
    pipeline = JournalAIPipeline()
    
    try:
        result = pipeline.run_full_pipeline(target_date, task_type)
        
        # Show results summary
        print("\n📊 PIPELINE RESULTS:")
        print("=" * 40)
        
        if result.get('status') == 'error':
            print(f"❌ Pipeline failed: {result.get('message')}")
            return
        
        # AI Results
        ai_response = result.get('ai_response', {})
        if ai_response.get('status') == 'success':
            tokens = ai_response.get('tokens_used', 0)
            print(f"✅ AI Processing: Success ({tokens} tokens used)")
        else:
            print(f"❌ AI Processing: {ai_response.get('message', 'Failed')}")
        
        # Calendar Results  
        calendar_result = result.get('calendar_result', {})
        if calendar_result.get('status') == 'success':
            events_created = calendar_result.get('events_created', 0)
            print(f"✅ Calendar Events: {events_created} events created")
            
            # Show created events
            for event in calendar_result.get('events', [])[:3]:
                print(f"   📅 {event.get('title')} at {event.get('start', '')}")
                
        else:
            print(f"❌ Calendar Events: {calendar_result.get('message', 'Failed')}")
            if calendar_result.get('details'):
                print(f"   Details: {calendar_result['details']}")

        print(f"\n🕒 Completed at: {result.get('timestamp')}")
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")


if __name__ == "__main__":
    main()
