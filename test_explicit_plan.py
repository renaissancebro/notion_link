#!/usr/bin/env python3
"""
Test script for explicit plan parsing and scheduling.

This demonstrates how the system now handles explicit user-written plans
instead of AI inference.
"""

import sys
sys.path.insert(0, 'src')

from notion.extractor import JournalExtractor

def test_time_parsing():
    """Test the time parsing regex patterns"""
    extractor = JournalExtractor()

    test_cases = [
        "9:00-10:30: Deep work on feature X",
        "2pm-4pm: Customer calls",
        "14:00: Review PRs (1 hour)",
        "8:30-9:00 Morning standup",
        "3pm: Team sync (30 minutes)",
    ]

    print("Testing time entry parsing:")
    print("="*60)

    for test_text in test_cases:
        result = extractor._parse_time_entry(test_text)
        if result:
            print(f"✅ '{test_text}'")
            print(f"   → {result['start_time']} to {result['end_time']}: {result['task']}")
        else:
            print(f"❌ Failed to parse: '{test_text}'")
        print()

def test_explicit_plan_extraction():
    """Test extracting explicit plans from a mock journal entry"""

    # Mock blocks structure similar to what Notion returns
    mock_blocks = {
        "results": [
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "Plan for Tomorrow"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "9:00-10:30: Deep work on accounting system"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "11:00-12:00: Internship applications"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "2pm-3:30pm: Customer discovery calls"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "4:00: Code review (1 hour)"}]
                }
            }
        ]
    }

    extractor = JournalExtractor()
    explicit_plan = extractor.extract_explicit_plan(mock_blocks)

    print("\nExtracting explicit plan from mock journal:")
    print("="*60)

    if explicit_plan:
        print(f"✅ Found {len(explicit_plan)} planned items:\n")
        for i, item in enumerate(explicit_plan, 1):
            print(f"{i}. {item['start_time']}-{item['end_time']}: {item['task']}")
    else:
        print("❌ No explicit plan found")

if __name__ == "__main__":
    print("\n🧪 EXPLICIT PLAN PARSER TEST\n")

    test_time_parsing()
    test_explicit_plan_extraction()

    print("\n" + "="*60)
    print("\n💡 How to use in your journal:")
    print("   1. At end of each day, add a section header like 'Plan for Tomorrow'")
    print("   2. List your tasks with times:")
    print("      - 9:00-10:30: Task description")
    print("      - 2pm-4pm: Another task")
    print("      - 14:00: Quick task (1 hour)")
    print("   3. Run the pipeline - it will use your exact plan!")
    print()
