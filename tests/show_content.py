#!/usr/bin/env python3
"""
Show Actual Content Being Extracted

This script will display the exact content being extracted from your Notion entries
so you can verify it's grabbing your actual edits, not just template text.
"""

import json
from datetime import date, timedelta
from journal_extractor import JournalExtractor


def show_raw_content():
    """Show the raw content being extracted."""
    print("🔍 SHOWING ACTUAL CONTENT BEING EXTRACTED")
    print("=" * 60)
    
    extractor = JournalExtractor()
    
    # Get today's entry
    print("\n📅 TODAY'S ENTRY CONTENT:")
    print("-" * 40)
    today_entry = extractor.get_journal_entry()
    
    if today_entry['found'] and today_entry.get('has_user_content'):
        print(f"Date: {today_entry['date']}")
        print(f"Page ID: {today_entry['page_id']}")
        print(f"Last edited: {today_entry['last_edited']}")
        print("\n📝 USER CONTENT BY SECTION:")
        
        for section_name, content_blocks in today_entry['content'].items():
            print(f"\n🔸 {section_name.upper().replace('_', ' ')}:")
            for i, block in enumerate(content_blocks):
                print(f"   {i+1}. [{block['type']}] {block['content']}")
                if block.get('last_edited'):
                    print(f"      ⏰ Edited: {block['last_edited']}")
    else:
        print("❌ No user content found for today")
    
    # Get recent entries
    print(f"\n\n📅 RECENT ENTRIES (Last 3 days):")
    print("-" * 40)
    recent_entries = extractor.get_recent_entries(days=3)
    
    for entry in recent_entries:
        print(f"\n📆 {entry['date']}:")
        if entry.get('has_user_content'):
            print(f"   ✅ Has user content - {len(entry['content'])} sections")
            for section_name, content_blocks in entry['content'].items():
                if content_blocks:  # Only show sections with content
                    print(f"   🔸 {section_name.replace('_', ' ').title()}:")
                    for block in content_blocks[:2]:  # Show first 2 blocks per section
                        preview = block['content'][:100] + "..." if len(block['content']) > 100 else block['content']
                        print(f"      • {preview}")
        else:
            print("   ❌ No user content found")


def show_formatted_content():
    """Show how the content looks when formatted for AI."""
    print("\n\n🤖 FORMATTED FOR AI:")
    print("=" * 60)
    
    extractor = JournalExtractor()
    recent_entries = extractor.get_recent_entries(days=3)
    
    if recent_entries:
        formatted = extractor.format_for_openai(recent_entries)
        
        print(f"📊 Summary: {formatted.get('summary', 'N/A')}")
        
        print(f"\n📝 JOURNAL ENTRIES ({len(formatted.get('journal_entries', []))}):")
        for i, entry in enumerate(formatted.get('journal_entries', [])):
            print(f"\n{i+1}. {entry['date']}:")
            if entry.get('has_content'):
                print(f"   ✅ Content found - Last updated: {entry.get('last_updated', 'Unknown')}")
                sections = entry.get('sections', {})
                for section_name, content_list in sections.items():
                    if content_list:
                        print(f"   🔸 {section_name}:")
                        for content in content_list[:2]:  # Show first 2 items
                            preview = content[:80] + "..." if len(content) > 80 else content
                            print(f"      • {preview}")
            else:
                print(f"   ❌ {entry.get('message', 'No content')}")


def show_calendar_data():
    """Show what data is extracted for calendar planning."""
    print("\n\n📅 CALENDAR PLANNING DATA:")
    print("=" * 60)
    
    extractor = JournalExtractor()
    recent_entries = extractor.get_recent_entries(days=3)
    
    if recent_entries:
        calendar_data = extractor.extract_for_calendar_planning(recent_entries)
        
        print("🎯 EXTRACTED FOR CALENDAR INTEGRATION:")
        for category, items in calendar_data.items():
            print(f"\n🔸 {category.replace('_', ' ').title()} ({len(items)} items):")
            for item in items[:3]:  # Show first 3 items
                print(f"   • {item}")
            if len(items) > 3:
                print(f"   ... and {len(items) - 3} more")


def check_template_vs_user_content():
    """Show the difference between template text and user content."""
    print("\n\n🔍 TEMPLATE VS USER CONTENT CHECK:")
    print("=" * 60)
    
    extractor = JournalExtractor()
    
    print("🚫 TEMPLATE KEYWORDS BEING FILTERED OUT:")
    for i, keyword in enumerate(extractor.template_keywords):
        print(f"   {i+1}. '{keyword}'")
    
    print(f"\n✅ CONTENT THAT PASSES THE FILTER:")
    print("   - Not containing any template keywords")
    print("   - More than 5 characters long") 
    print("   - Has actual text content")
    
    # Show example from today
    today_entry = extractor.get_journal_entry()
    if today_entry['found'] and today_entry.get('has_user_content'):
        print(f"\n📝 EXAMPLE USER CONTENT FROM TODAY:")
        content = today_entry['content']
        for section, blocks in content.items():
            if blocks:
                print(f"   🔸 {section}: {len(blocks)} user-written blocks")
                break


def show_edit_detection():
    """Show which entries have been edited vs created."""
    print("\n\n⏱ EDIT DETECTION:")
    print("=" * 60)
    
    extractor = JournalExtractor()
    recent_entries = extractor.get_recent_entries(days=3)
    
    print("📝 CHECKING FOR EDITED CONTENT:")
    for entry in recent_entries:
        created = entry.get('created', 'Unknown')
        last_edited = entry.get('last_edited', 'Unknown')
        
        print(f"\n📆 {entry['date']}:")
        print(f"   Created: {created}")
        print(f"   Last edited: {last_edited}")
        
        if created != last_edited:
            print("   ✅ ENTRY WAS EDITED AFTER CREATION")
        else:
            print("   ℹ️  Entry not edited after creation")
        
        if entry.get('has_user_content'):
            print(f"   📝 User content sections: {list(entry['content'].keys())}")
        else:
            print("   ❌ No user content detected")


def main():
    """Run all content verification checks."""
    show_raw_content()
    show_formatted_content()
    show_calendar_data()
    check_template_vs_user_content()
    show_edit_detection()
    
    print(f"\n\n✅ VERIFICATION COMPLETE")
    print("=" * 60)
    print("If you see your actual content above, the system is working correctly!")
    print("If you only see template text, check that you've saved your edits in Notion.")


if __name__ == "__main__":
    main()