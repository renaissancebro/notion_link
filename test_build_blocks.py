#!/usr/bin/env python3
"""
Test Build Blocks format parsing
"""

import sys
sys.path.insert(0, 'src')

from notion.extractor import JournalExtractor

def test_build_blocks_parsing():
    """Test parsing Build Blocks format from your actual journal"""

    # Your actual format
    mock_blocks = {
        "results": [
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "📅 Build Blocks (Tomorrow's System)"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "*(Estimate time + set anchor order)*"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "Task — X min"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "Meet with Chris 2 hours"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "accounting homework 1 hour"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "python homework 1 hour"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "internship applications 1 hour + SEO 30 min"}]
                }
            }
        ]
    }

    extractor = JournalExtractor()
    explicit_plan = extractor.extract_explicit_plan(mock_blocks)

    print("\n🧪 BUILD BLOCKS FORMAT TEST\n")
    print("="*60)
    print("Parsing your Build Blocks format:\n")

    if explicit_plan:
        print(f"✅ Found {len(explicit_plan)} scheduled tasks:\n")
        for i, item in enumerate(explicit_plan, 1):
            print(f"{i}. {item['start_time']}-{item['end_time']}: {item['task']}")

        print("\n" + "="*60)
        print("\n📅 Ready to schedule to Google Calendar!")
    else:
        print("❌ No tasks parsed")

def test_duration_patterns():
    """Test various duration format patterns"""

    test_cases = [
        "Meet with Chris 2 hours",
        "accounting homework 1 hour",
        "python homework — 1 hour",
        "internship applications 1 hour + SEO 30 min",
        "Deep work session — 90 min",
        "Quick task 30 minutes"
    ]

    extractor = JournalExtractor()

    print("\n\n🧪 DURATION PATTERN TESTS\n")
    print("="*60)

    for test_text in test_cases:
        result = extractor._parse_time_entry(test_text)
        if result:
            if 'duration_minutes' in result:
                print(f"✅ '{test_text}'")
                print(f"   → {result['task']} ({result['duration_minutes']} minutes)")
            else:
                print(f"✅ '{test_text}'")
                print(f"   → {result.get('start_time', '?')}-{result.get('end_time', '?')}: {result['task']}")
        else:
            print(f"❌ Failed to parse: '{test_text}'")
        print()

if __name__ == "__main__":
    test_duration_patterns()
    test_build_blocks_parsing()
