#!/usr/bin/env python3
"""
Clean Content Printer

Shows only the user-written content from your journal entries,
without debug output or JSON data.
"""

import sys
from datetime import date, timedelta
from journal_extractor import JournalExtractor


def print_clean_content(target_date=None):
    """Print clean user content for a specific date."""
    extractor = JournalExtractor()
    
    if target_date:
        entry = extractor.get_journal_entry(target_date)
        entries = [entry] if entry['found'] else []
    else:
        # Get recent entries
        entries = extractor.get_recent_entries(days=5)
    
    if not entries:
        print("❌ No entries found")
        return
    
    print("📝 USER CONTENT EXTRACTED FROM NOTION")
    print("=" * 60)
    
    for entry in entries:
        print(f"\n📅 DATE: {entry['date']}")
        print(f"🔗 PAGE ID: {entry['page_id']}")
        print(f"⏰ LAST EDITED: {entry.get('last_edited', 'Unknown')}")
        
        if not entry.get('has_user_content'):
            print("❌ No user content found (only template text)")
            continue
        
        print(f"✅ USER CONTENT FOUND - {len(entry['content'])} sections")
        print("-" * 40)
        
        for section_name, content_blocks in entry['content'].items():
            if content_blocks:  # Only show sections with content
                section_title = section_name.replace('_', ' ').title()
                print(f"\n🔸 {section_title}:")
                
                for i, block in enumerate(content_blocks):
                    content = block['content']
                    block_type = block['type']
                    
                    # Clean up the content display
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    print(f"   {i+1}. [{block_type}] {content}")
        
        print("\n" + "=" * 60)


def show_formatted_for_ai(target_date=None):
    """Show how the content looks when formatted for AI."""
    extractor = JournalExtractor()
    
    if target_date:
        entry = extractor.get_journal_entry(target_date)
        formatted = extractor.format_for_openai(entry)
    else:
        recent_entries = extractor.get_recent_entries(days=3)
        formatted = extractor.format_for_openai(recent_entries)
    
    print("\n🤖 FORMATTED FOR AI:")
    print("=" * 60)
    
    if isinstance(formatted, dict):
        if 'summary' in formatted:
            print(f"📊 Summary: {formatted['summary']}")
            print(f"\n📝 ENTRIES ({len(formatted.get('journal_entries', []))}):")
            
            for i, entry in enumerate(formatted.get('journal_entries', [])):
                print(f"\n{i+1}. {entry['date']}:")
                if entry.get('has_content'):
                    sections = entry.get('sections', {})
                    for section_name, content_list in sections.items():
                        if content_list:
                            print(f"   🔸 {section_name}:")
                            for content in content_list[:2]:  # Show first 2 items
                                preview = content[:100] + "..." if len(content) > 100 else content
                                print(f"      • {preview}")
                else:
                    print(f"   ❌ {entry.get('message', 'No content')}")
        else:
            # Single entry
            if formatted.get('has_content'):
                print(f"📅 Date: {formatted['date']}")
                print(f"⏰ Last updated: {formatted.get('last_updated', 'Unknown')}")
                sections = formatted.get('sections', {})
                for section_name, content_list in sections.items():
                    if content_list:
                        print(f"\n🔸 {section_name}:")
                        for content in content_list:
                            preview = content[:100] + "..." if len(content) > 100 else content
                            print(f"   • {preview}")
            else:
                print(f"❌ No content for {formatted.get('date', 'Unknown date')}")


def main():
    """Main function to handle command line arguments."""
    target_date = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "today":
            target_date = date.today()
        elif arg == "yesterday":
            target_date = date.today() - timedelta(days=1)
        elif len(arg) == 10 and arg.count('-') == 2:
            # Date format YYYY-MM-DD
            try:
                from datetime import datetime
                target_date = datetime.strptime(arg, '%Y-%m-%d').date()
            except ValueError:
                print(f"Invalid date format: {arg}. Use YYYY-MM-DD")
                return
        else:
            print("Usage:")
            print("  python print_content.py              - Show last 5 days")
            print("  python print_content.py today        - Show today only")
            print("  python print_content.py yesterday    - Show yesterday only")
            print("  python print_content.py 2025-07-19   - Show specific date")
            return
    
    # Print the actual content
    print_clean_content(target_date)
    
    # Show how it looks formatted for AI
    show_formatted_for_ai(target_date)


if __name__ == "__main__":
    main()