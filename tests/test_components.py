#!/usr/bin/env python3
"""
Component Testing Suite for Journal AI Pipeline

Test each component individually to ensure everything works correctly.
Run with: python test_components.py
"""

import json
from datetime import date, timedelta
from journal_extractor import JournalExtractor, get_today_journal_for_ai, get_calendar_planning_data
from ai_pipeline import AIPipeline


def test_journal_extractor():
    """Test the JournalExtractor class methods individually."""
    print("🧪 TESTING JOURNAL EXTRACTOR")
    print("=" * 60)
    
    extractor = JournalExtractor()
    
    # Test 1: Get today's journal entry
    print("\n1. Testing get_journal_entry() for today:")
    today_entry = extractor.get_journal_entry()
    print(f"   ✓ Found entry: {today_entry['found']}")
    print(f"   ✓ Has user content: {today_entry.get('has_user_content', False)}")
    print(f"   ✓ Date: {today_entry['date']}")
    
    # Test 2: Get recent entries
    print("\n2. Testing get_recent_entries(days=3):")
    recent_entries = extractor.get_recent_entries(days=3)
    print(f"   ✓ Retrieved {len(recent_entries)} entries")
    for entry in recent_entries:
        print(f"     - {entry['date']}: content={entry.get('has_user_content', False)}")
    
    # Test 3: Format for OpenAI
    print("\n3. Testing format_for_openai():")
    if recent_entries:
        formatted = extractor.format_for_openai(recent_entries)
        print(f"   ✓ Formatted data type: {type(formatted).__name__}")
        if isinstance(formatted, dict) and 'summary' in formatted:
            print(f"   ✓ Summary: {formatted['summary']}")
            print(f"   ✓ Journal entries count: {len(formatted.get('journal_entries', []))}")
    
    # Test 4: Extract for calendar planning
    print("\n4. Testing extract_for_calendar_planning():")
    if recent_entries:
        calendar_data = extractor.extract_for_calendar_planning(recent_entries)
        print(f"   ✓ Planning data type: {type(calendar_data).__name__}")
        print(f"   ✓ Keys: {list(calendar_data.keys()) if isinstance(calendar_data, dict) else 'Not a dict'}")
    
    return extractor, recent_entries


def test_ai_pipeline_stages():
    """Test each stage of the AI pipeline individually."""
    print("\n\n🧪 TESTING AI PIPELINE STAGES")
    print("=" * 60)
    
    pipeline = AIPipeline()
    
    # Test 1: Extract journal data
    print("\n1. Testing extract_journal_data():")
    journal_data = pipeline.extract_journal_data(include_recent=True)
    print(f"   ✓ Data type: {type(journal_data).__name__}")
    if isinstance(journal_data, dict):
        print(f"   ✓ Keys: {list(journal_data.keys())}")
        if 'summary' in journal_data:
            print(f"   ✓ Summary: {journal_data['summary']}")
    
    # Test 2: Prepare AI prompts for different task types
    print("\n2. Testing prepare_ai_prompt() for different task types:")
    task_types = ["daily_planning", "reflection", "goal_setting", "calendar_optimization"]
    
    for task_type in task_types:
        try:
            prompt = pipeline.prepare_ai_prompt(journal_data, task_type=task_type)
            print(f"   ✓ {task_type}: {len(prompt)} characters")
        except Exception as e:
            print(f"   ✗ {task_type}: ERROR - {e}")
    
    # Test 3: Process with OpenAI (placeholder)
    print("\n3. Testing process_with_openai():")
    test_prompt = pipeline.prepare_ai_prompt(journal_data, "daily_planning")
    ai_response = pipeline.process_with_openai(test_prompt)
    print(f"   ✓ Response type: {type(ai_response).__name__}")
    print(f"   ✓ Status: {ai_response.get('status', 'Unknown')}")
    
    # Test 4: Create calendar events (placeholder)
    print("\n4. Testing create_calendar_events():")
    calendar_result = pipeline.create_calendar_events(ai_response)
    print(f"   ✓ Result type: {type(calendar_result).__name__}")
    print(f"   ✓ Status: {calendar_result.get('status', 'Unknown')}")
    
    return pipeline, journal_data, test_prompt


def test_convenience_functions():
    """Test the convenience functions from journal_extractor."""
    print("\n\n🧪 TESTING CONVENIENCE FUNCTIONS")
    print("=" * 60)
    
    # Test 1: get_today_journal_for_ai()
    print("\n1. Testing get_today_journal_for_ai():")
    try:
        today_ai_data = get_today_journal_for_ai()
        print(f"   ✓ Data type: {type(today_ai_data).__name__}")
        if isinstance(today_ai_data, dict):
            print(f"   ✓ Has content: {today_ai_data.get('has_content', False)}")
            print(f"   ✓ Date: {today_ai_data.get('date', 'Unknown')}")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
    
    # Test 2: get_calendar_planning_data()
    print("\n2. Testing get_calendar_planning_data(days=3):")
    try:
        planning_data = get_calendar_planning_data(days=3)
        print(f"   ✓ Data type: {type(planning_data).__name__}")
        if isinstance(planning_data, dict):
            print(f"   ✓ Keys: {list(planning_data.keys())}")
            for key, value in planning_data.items():
                if isinstance(value, list):
                    print(f"     - {key}: {len(value)} items")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")


def test_full_pipeline():
    """Test the complete pipeline end-to-end."""
    print("\n\n🧪 TESTING FULL PIPELINE")
    print("=" * 60)
    
    pipeline = AIPipeline()
    
    print("\n1. Running full pipeline with default settings:")
    try:
        result = pipeline.run_full_pipeline()
        print(f"   ✓ Pipeline completed successfully")
        print(f"   ✓ Result keys: {list(result.keys())}")
        print(f"   ✓ Timestamp: {result.get('timestamp', 'Unknown')}")
        
        # Check each component
        if 'journal_data' in result:
            journal_data = result['journal_data']
            if isinstance(journal_data, dict) and 'summary' in journal_data:
                print(f"   ✓ Journal data: {journal_data['summary']}")
            else:
                print(f"   ✓ Journal data: Single entry for {journal_data.get('date', 'Unknown')}")
        
        if 'ai_prompt' in result:
            prompt_length = len(result['ai_prompt'])
            print(f"   ✓ AI prompt: {prompt_length} characters ready")
        
        if 'ai_response' in result:
            ai_status = result['ai_response'].get('status', 'Unknown')
            print(f"   ✓ AI response: {ai_status}")
        
        if 'calendar_result' in result:
            cal_status = result['calendar_result'].get('status', 'Unknown')
            print(f"   ✓ Calendar result: {cal_status}")
            
        return result
        
    except Exception as e:
        print(f"   ✗ Pipeline failed: {e}")
        return None


def test_specific_date():
    """Test pipeline with a specific date."""
    print("\n\n🧪 TESTING SPECIFIC DATE")
    print("=" * 60)
    
    # Test with yesterday's date
    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    
    print(f"\n1. Testing pipeline for specific date: {yesterday_str}")
    
    pipeline = AIPipeline()
    extractor = JournalExtractor()
    
    # Test journal extraction for specific date
    try:
        entry = extractor.get_journal_entry(yesterday)
        print(f"   ✓ Entry found: {entry['found']}")
        print(f"   ✓ Has content: {entry.get('has_user_content', False)}")
        
        if entry['found']:
            # Test pipeline for this specific date
            result = pipeline.run_full_pipeline(target_date=yesterday_str)
            print(f"   ✓ Pipeline completed for {yesterday_str}")
            return result
        else:
            print(f"   ! No entry found for {yesterday_str}, skipping pipeline test")
            
    except Exception as e:
        print(f"   ✗ Error testing specific date: {e}")
        return None


def show_sample_outputs():
    """Show sample outputs for understanding data structure."""
    print("\n\n📋 SAMPLE DATA STRUCTURES")
    print("=" * 60)
    
    extractor = JournalExtractor()
    
    print("\n1. Sample journal entry structure:")
    entry = extractor.get_journal_entry()
    sample_entry = {
        "date": entry.get("date", "2025-07-20"),
        "found": entry.get("found", True),
        "has_user_content": entry.get("has_user_content", False),
        "content": "{ ... user content organized by sections ... }"
    }
    print(json.dumps(sample_entry, indent=2))
    
    print("\n2. Sample AI-formatted data structure:")
    if entry['found']:
        formatted = extractor.format_for_openai(entry)
        # Show structure without overwhelming content
        if isinstance(formatted, dict) and 'sections' in formatted:
            sample_formatted = {
                "date": formatted.get("date"),
                "has_content": formatted.get("has_content"),
                "sections": "{ ... organized content sections ... }"
            }
        else:
            sample_formatted = formatted
        print(json.dumps(sample_formatted, indent=2))
    
    print("\n3. Sample calendar planning data structure:")
    planning_data = extractor.extract_for_calendar_planning(entry)
    if isinstance(planning_data, dict):
        sample_planning = {key: f"[{len(value)} items]" if isinstance(value, list) else value 
                          for key, value in planning_data.items()}
        print(json.dumps(sample_planning, indent=2))


def main():
    """Run all tests."""
    print("🚀 JOURNAL AI PIPELINE - COMPONENT TEST SUITE")
    print("=" * 80)
    
    # Run all tests
    try:
        # Test individual components
        extractor, recent_entries = test_journal_extractor()
        pipeline, journal_data, test_prompt = test_ai_pipeline_stages()
        test_convenience_functions()
        
        # Test full pipeline
        full_result = test_full_pipeline()
        
        # Test specific date
        date_result = test_specific_date()
        
        # Show sample outputs
        show_sample_outputs()
        
        # Summary
        print("\n\n✅ TEST SUMMARY")
        print("=" * 60)
        print("✓ Journal Extractor: All methods tested")
        print("✓ AI Pipeline Stages: All stages tested") 
        print("✓ Convenience Functions: Tested")
        print("✓ Full Pipeline: Tested")
        print("✓ Specific Date: Tested")
        print("✓ Sample Outputs: Displayed")
        
        print("\n📝 NEXT STEPS:")
        print("1. Add OpenAI API integration to ai_pipeline.py")
        print("2. Add Google Calendar API integration to ai_pipeline.py")
        print("3. Replace placeholder responses with real API calls")
        
        print("\n🛠 USAGE EXAMPLES:")
        print("# Test individual components:")
        print("python test_components.py")
        print("")
        print("# Test journal extraction only:")
        print("from journal_extractor import JournalExtractor")
        print("extractor = JournalExtractor()")
        print("today = extractor.get_journal_entry()")
        print("")
        print("# Test full pipeline:")
        print("from ai_pipeline import AIPipeline")
        print("pipeline = AIPipeline()")
        print("result = pipeline.run_full_pipeline()")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()