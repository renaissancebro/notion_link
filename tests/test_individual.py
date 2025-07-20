#!/usr/bin/env python3
"""
Individual Component Testing

Quick scripts to test each component in isolation.
Use these for debugging specific parts of the pipeline.
"""

import json
from datetime import date, timedelta


def test_notion_connection():
    """Test basic Notion connection and data retrieval."""
    print("🔌 TESTING NOTION CONNECTION")
    print("=" * 50)
    
    try:
        from notion_fetcher import get_entries_for_date, get_all_recent_entries
        
        # Test today's entries
        print("1. Testing today's entries:")
        today_entries = get_entries_for_date(date.today())
        print(f"   Found {len(today_entries)} entries for today")
        
        # Test recent entries
        print("\n2. Testing recent entries:")
        recent = get_all_recent_entries()
        if recent and recent.get('results'):
            print(f"   Found {len(recent['results'])} recent entries")
            for i, entry in enumerate(recent['results'][:3]):
                date_prop = entry["properties"].get("Date", {}).get("date")
                entry_date = date_prop.get("start") if date_prop else "No date"
                print(f"     {i+1}. {entry_date} - {entry['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        return False


def test_journal_extractor_only():
    """Test only the JournalExtractor class methods."""
    print("\n📖 TESTING JOURNAL EXTRACTOR ONLY")
    print("=" * 50)
    
    try:
        from journal_extractor import JournalExtractor
        
        extractor = JournalExtractor()
        print("✓ JournalExtractor initialized")
        
        # Test getting today's entry
        print("\n1. Get today's journal:")
        today = extractor.get_journal_entry()
        print(f"   Date: {today['date']}")
        print(f"   Found: {today['found']}")
        print(f"   Has content: {today.get('has_user_content', False)}")
        
        if today['found'] and today.get('has_user_content'):
            print(f"   Content sections: {list(today['content'].keys())}")
        
        # Test getting recent entries
        print("\n2. Get recent entries (3 days):")
        recent = extractor.get_recent_entries(days=3)
        print(f"   Retrieved: {len(recent)} entries")
        
        for entry in recent:
            status = "✓ has content" if entry.get('has_user_content') else "○ no content"
            print(f"     {entry['date']}: {status}")
        
        # Test formatting for AI
        print("\n3. Format for OpenAI:")
        if recent:
            formatted = extractor.format_for_openai(recent)
            print(f"   Type: {type(formatted).__name__}")
            
            if isinstance(formatted, dict):
                if 'summary' in formatted:
                    print(f"   Summary: {formatted['summary']}")
                if 'journal_entries' in formatted:
                    print(f"   Entries: {len(formatted['journal_entries'])}")
        
        # Test calendar extraction
        print("\n4. Extract for calendar:")
        if recent:
            calendar_data = extractor.extract_for_calendar_planning(recent)
            print(f"   Type: {type(calendar_data).__name__}")
            
            if isinstance(calendar_data, dict):
                for key, value in calendar_data.items():
                    if isinstance(value, list):
                        print(f"     {key}: {len(value)} items")
        
        return extractor, recent
        
    except Exception as e:
        print(f"❌ JournalExtractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_ai_pipeline_only():
    """Test only the AIPipeline class methods."""
    print("\n🤖 TESTING AI PIPELINE ONLY")
    print("=" * 50)
    
    try:
        from ai_pipeline import AIPipeline
        
        pipeline = AIPipeline()
        print("✓ AIPipeline initialized")
        
        # Test data extraction
        print("\n1. Extract journal data:")
        journal_data = pipeline.extract_journal_data(include_recent=True)
        print(f"   Type: {type(journal_data).__name__}")
        
        if isinstance(journal_data, dict):
            if 'summary' in journal_data:
                print(f"   Summary: {journal_data['summary']}")
            else:
                print(f"   Single entry: {journal_data.get('date', 'Unknown date')}")
        
        # Test prompt generation
        print("\n2. Generate AI prompts:")
        prompt_types = ["daily_planning", "reflection", "goal_setting"]
        
        for prompt_type in prompt_types:
            try:
                prompt = pipeline.prepare_ai_prompt(journal_data, prompt_type)
                print(f"   {prompt_type}: {len(prompt)} chars")
            except Exception as e:
                print(f"   {prompt_type}: ERROR - {e}")
        
        # Test placeholder AI processing
        print("\n3. Process with OpenAI (placeholder):")
        test_prompt = pipeline.prepare_ai_prompt(journal_data, "daily_planning")
        ai_response = pipeline.process_with_openai(test_prompt)
        print(f"   Response: {ai_response.get('status', 'Unknown')}")
        print(f"   Prompt ready: {ai_response.get('prompt_ready', False)}")
        
        # Test placeholder calendar integration
        print("\n4. Calendar integration (placeholder):")
        calendar_result = pipeline.create_calendar_events(ai_response)
        print(f"   Result: {calendar_result.get('status', 'Unknown')}")
        
        return pipeline, journal_data
        
    except Exception as e:
        print(f"❌ AIPipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_convenience_functions_only():
    """Test the convenience functions."""
    print("\n⚡ TESTING CONVENIENCE FUNCTIONS")
    print("=" * 50)
    
    try:
        from journal_extractor import (
            get_today_journal_for_ai, 
            get_recent_journals_for_ai, 
            get_calendar_planning_data
        )
        
        # Test today's journal for AI
        print("1. get_today_journal_for_ai():")
        today_ai = get_today_journal_for_ai()
        print(f"   Type: {type(today_ai).__name__}")
        print(f"   Has content: {today_ai.get('has_content', False)}")
        
        # Test recent journals for AI
        print("\n2. get_recent_journals_for_ai(days=3):")
        recent_ai = get_recent_journals_for_ai(days=3)
        print(f"   Type: {type(recent_ai).__name__}")
        
        if isinstance(recent_ai, dict) and 'summary' in recent_ai:
            print(f"   Summary: {recent_ai['summary']}")
        
        # Test calendar planning data
        print("\n3. get_calendar_planning_data(days=3):")
        calendar_data = get_calendar_planning_data(days=3)
        print(f"   Type: {type(calendar_data).__name__}")
        
        if isinstance(calendar_data, dict):
            for key, value in calendar_data.items():
                if isinstance(value, list):
                    print(f"     {key}: {len(value)} items")
        
        return today_ai, recent_ai, calendar_data
        
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def test_prompt_generation():
    """Test AI prompt generation in detail."""
    print("\n📝 TESTING PROMPT GENERATION")
    print("=" * 50)
    
    try:
        from ai_pipeline import AIPipeline
        
        pipeline = AIPipeline()
        
        # Get some sample data
        journal_data = pipeline.extract_journal_data(include_recent=True)
        
        print("Testing all prompt types:")
        prompt_types = ["daily_planning", "reflection", "goal_setting", "calendar_optimization"]
        
        for prompt_type in prompt_types:
            print(f"\n{prompt_type.upper()}:")
            try:
                prompt = pipeline.prepare_ai_prompt(journal_data, prompt_type)
                print(f"   Length: {len(prompt)} characters")
                print(f"   First 200 chars: {prompt[:200]}...")
                print(f"   Contains journal data: {'journal_json' in prompt or 'JOURNAL DATA' in prompt}")
                
            except Exception as e:
                print(f"   ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt generation test failed: {e}")
        return False


def show_data_structure_examples():
    """Show examples of data structures at each stage."""
    print("\n📊 DATA STRUCTURE EXAMPLES")
    print("=" * 50)
    
    try:
        from journal_extractor import JournalExtractor
        from ai_pipeline import AIPipeline
        
        extractor = JournalExtractor()
        pipeline = AIPipeline()
        
        # Raw journal entry
        print("1. Raw journal entry structure:")
        entry = extractor.get_journal_entry()
        print(json.dumps({
            "date": entry.get("date"),
            "found": entry.get("found"),
            "has_user_content": entry.get("has_user_content"),
            "content_keys": list(entry.get("content", {}).keys())
        }, indent=2))
        
        # AI-formatted entry
        print("\n2. AI-formatted entry structure:")
        if entry['found']:
            formatted = extractor.format_for_openai(entry)
            if isinstance(formatted, dict):
                print(json.dumps({
                    "date": formatted.get("date"),
                    "has_content": formatted.get("has_content"),
                    "sections": list(formatted.get("sections", {}).keys()) if "sections" in formatted else "N/A"
                }, indent=2))
        
        # Calendar planning data
        print("\n3. Calendar planning data structure:")
        calendar_data = extractor.extract_for_calendar_planning(entry)
        if isinstance(calendar_data, dict):
            structure = {}
            for key, value in calendar_data.items():
                if isinstance(value, list):
                    structure[key] = f"list with {len(value)} items"
                else:
                    structure[key] = type(value).__name__
            print(json.dumps(structure, indent=2))
        
        # Pipeline result structure
        print("\n4. Full pipeline result structure:")
        result = pipeline.run_full_pipeline()
        if result:
            structure = {}
            for key, value in result.items():
                if isinstance(value, str):
                    structure[key] = f"string ({len(value)} chars)"
                elif isinstance(value, dict):
                    structure[key] = f"dict with keys: {list(value.keys())[:3]}..."
                else:
                    structure[key] = type(value).__name__
            print(json.dumps(structure, indent=2))
        
    except Exception as e:
        print(f"❌ Data structure examples failed: {e}")


def quick_test():
    """Quick test to verify everything is working."""
    print("⚡ QUICK SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("Notion Connection", test_notion_connection),
        ("Journal Extractor", lambda: test_journal_extractor_only()[0] is not None),
        ("AI Pipeline", lambda: test_ai_pipeline_only()[0] is not None),
        ("Convenience Functions", lambda: test_convenience_functions_only()[0] is not None)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            status = "✅ PASS" if result else "❌ FAIL"
            results.append((test_name, status))
            print(f"{test_name}: {status}")
        except Exception as e:
            results.append((test_name, f"❌ ERROR: {e}"))
            print(f"{test_name}: ❌ ERROR: {e}")
    
    print("\n📋 SUMMARY:")
    for test_name, status in results:
        print(f"  {test_name}: {status}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "notion":
            test_notion_connection()
        elif test_name == "extractor":
            test_journal_extractor_only()
        elif test_name == "pipeline":
            test_ai_pipeline_only()
        elif test_name == "convenience":
            test_convenience_functions_only()
        elif test_name == "prompts":
            test_prompt_generation()
        elif test_name == "structure":
            show_data_structure_examples()
        elif test_name == "quick":
            quick_test()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: notion, extractor, pipeline, convenience, prompts, structure, quick")
    else:
        print("🧪 INDIVIDUAL COMPONENT TESTING")
        print("=" * 50)
        print("Usage:")
        print("  python test_individual.py notion      - Test Notion connection")
        print("  python test_individual.py extractor   - Test JournalExtractor only")
        print("  python test_individual.py pipeline    - Test AIPipeline only")
        print("  python test_individual.py convenience - Test convenience functions")
        print("  python test_individual.py prompts     - Test prompt generation")
        print("  python test_individual.py structure   - Show data structures")
        print("  python test_individual.py quick       - Quick system test")
        print("")
        print("Running quick test by default...")
        quick_test()