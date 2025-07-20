#!/usr/bin/env python3
"""
Test script: Extract yesterday's journal and create calendar events for tomorrow
"""

import sys
import os
from datetime import date, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import JournalAIPipeline

def main():
    """Test the full pipeline: yesterday's journal → tomorrow's calendar"""
    
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    print("🧪 Testing: Yesterday's Journal → Tomorrow's Calendar")
    print("=" * 60)
    print(f"📖 Source: Journal from {yesterday}")
    print(f"📅 Target: Calendar events for {tomorrow}")
    print()
    
    # Initialize pipeline
    pipeline = JournalAIPipeline()
    
    try:
        # Step 1: Extract yesterday's journal data
        print("🔍 Step 1: Extracting yesterday's journal...")
        journal_data = pipeline.extract_journal_data(yesterday, include_recent=False)
        print(f"✅ Extracted: {journal_data.get('summary', 'Single entry')}")
        
        # Step 2: Prepare AI prompt for daily planning
        print("\n📝 Step 2: Preparing AI prompt...")
        ai_prompt = pipeline.prepare_ai_prompt(journal_data, "daily_planning")
        print("✅ Prompt prepared for daily planning")
        
        # Step 3: Process with OpenAI
        print("\n🤖 Step 3: Processing with AI...")
        ai_response = pipeline.process_with_ai(ai_prompt)
        
        if ai_response.get('status') == 'success':
            print(f"✅ AI processing successful")
            print(f"📊 Response preview: {str(ai_response.get('response', {}))[0:100]}...")
        else:
            print(f"❌ AI processing failed: {ai_response.get('message')}")
            return
        
        # Step 4: Create calendar events for TOMORROW
        print(f"\n📅 Step 4: Creating calendar events for {tomorrow}...")
        calendar_result = pipeline.create_calendar_events(ai_response, tomorrow)
        
        # Show results
        print("\n" + "=" * 60)
        print("📊 RESULTS:")
        print("=" * 60)
        
        if calendar_result.get('status') == 'success':
            events_created = calendar_result.get('events_created', 0)
            total_attempted = calendar_result.get('total_attempted', 0)
            
            print(f"✅ Successfully created {events_created} calendar events for {tomorrow}")
            print(f"📋 Total attempted: {total_attempted}")
            
            # Show created events
            for i, event in enumerate(calendar_result.get('events', []), 1):
                print(f"\n📅 Event {i}:")
                print(f"   📌 Title: {event.get('title', 'N/A')}")
                print(f"   🕐 Time: {event.get('start', 'N/A')} - {event.get('end', 'N/A')}")
                if event.get('event_link'):
                    print(f"   🔗 Link: {event['event_link']}")
            
            # Show any errors
            errors = calendar_result.get('errors', [])
            if errors:
                print(f"\n⚠️ Errors encountered:")
                for error in errors:
                    print(f"   • {error}")
        
        else:
            print(f"❌ Calendar creation failed: {calendar_result.get('message')}")
        
        print(f"\n✅ Test complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()