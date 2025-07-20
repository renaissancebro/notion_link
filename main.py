import datetime
import sys
from notion_fetcher import (
    query_database_by_date,
    get_entries_for_date,
    get_page_content,
    get_all_recent_entries,
    get_entry_by_id,
    find_edited_entries,
)
from datetime import date


def display_entry(entry):
    """Helper function to display a journal entry"""
    print(f"Page ID: {entry['page_id']}")

    # Show when the page was last edited
    if entry["content"] and entry["content"]["page_details"]:
        last_edited = entry["content"]["page_details"].get("last_edited_time")
        print(f"Last edited: {last_edited}")

    # Print Journal property content (handle both title and rich_text types)
    journal_prop = entry["properties"].get("Journal")
    if journal_prop:
        if journal_prop["type"] == "title" and journal_prop["title"]:
            journal_text = "".join(
                [
                    t["plain_text"]
                    for t in journal_prop["title"]
                    if "plain_text" in t
                ]
            )
            print("Journal Title:")
            print(journal_text)
        elif journal_prop["type"] == "rich_text" and journal_prop["rich_text"]:
            journal_text = "".join(
                [
                    t["plain_text"]
                    for t in journal_prop["rich_text"]
                    if "plain_text" in t
                ]
            )
            print("Journal Content:")
            print(journal_text)

    # Print full content from blocks (this contains the actual journal content)
    if entry["content"] and entry["content"]["content_blocks"]:
        blocks = entry["content"]["content_blocks"]["results"]
        print("\nFull Journal Content:")
        print("=" * 50)

        for block in blocks:
            block_type = block.get("type")

            # Handle different block types
            if block_type == "paragraph" and block.get("paragraph", {}).get(
                "rich_text"
            ):
                texts = block["paragraph"]["rich_text"]
                paragraph_text = "".join(
                    [t.get("plain_text", "") for t in texts]
                )
                if paragraph_text.strip():
                    print(paragraph_text)

            elif block_type == "heading_1" and block.get("heading_1", {}).get(
                "rich_text"
            ):
                texts = block["heading_1"]["rich_text"]
                heading_text = "".join([t.get("plain_text", "") for t in texts])
                if heading_text.strip():
                    print(f"\n# {heading_text}")

            elif block_type == "heading_2" and block.get("heading_2", {}).get(
                "rich_text"
            ):
                texts = block["heading_2"]["rich_text"]
                heading_text = "".join([t.get("plain_text", "") for t in texts])
                if heading_text.strip():
                    print(f"\n## {heading_text}")

            elif block_type == "heading_3" and block.get("heading_3", {}).get(
                "rich_text"
            ):
                texts = block["heading_3"]["rich_text"]
                heading_text = "".join([t.get("plain_text", "") for t in texts])
                if heading_text.strip():
                    print(f"\n### {heading_text}")

            elif block_type == "bulleted_list_item" and block.get(
                "bulleted_list_item", {}
            ).get("rich_text"):
                texts = block["bulleted_list_item"]["rich_text"]
                list_text = "".join([t.get("plain_text", "") for t in texts])
                if list_text.strip():
                    print(f"• {list_text}")

            elif block_type == "numbered_list_item" and block.get(
                "numbered_list_item", {}
            ).get("rich_text"):
                texts = block["numbered_list_item"]["rich_text"]
                list_text = "".join([t.get("plain_text", "") for t in texts])
                if list_text.strip():
                    print(f"1. {list_text}")

            elif block_type == "to_do" and block.get("to_do", {}).get(
                "rich_text"
            ):
                texts = block["to_do"]["rich_text"]
                todo_text = "".join([t.get("plain_text", "") for t in texts])
                checked = block["to_do"].get("checked", False)
                checkbox = "☑" if checked else "☐"
                if todo_text.strip():
                    print(f"{checkbox} {todo_text}")

            elif block_type == "quote" and block.get("quote", {}).get(
                "rich_text"
            ):
                texts = block["quote"]["rich_text"]
                quote_text = "".join([t.get("plain_text", "") for t in texts])
                if quote_text.strip():
                    print(f"> {quote_text}")

            elif block_type == "code" and block.get("code", {}).get(
                "rich_text"
            ):
                texts = block["code"]["rich_text"]
                code_text = "".join([t.get("plain_text", "") for t in texts])
                language = block["code"].get("language", "")
                if code_text.strip():
                    print(f"```{language}")
                    print(code_text)
                    print("```")

        print("=" * 50)


today = date.today()
today_entries = get_entries_for_date(today)


if __name__ == "__main__":
    # Check if a specific page ID or date was provided as command line argument
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Check for special commands
        if arg.lower() in ['edited', '--edited', '-e']:
            print("Scanning for edited entries...")
            print("="*60)

            edited_entries = find_edited_entries()
            if edited_entries:
                print(f"Found {len(edited_entries)} edited entries:")
                for entry in edited_entries:
                    print(f"\nDate: {entry['date']}")
                    print(f"Title: {entry['title']}")
                    print(f"ID: {entry['id']}")
                    print(f"Created: {entry['created']}")
                    print(f"Last edited: {entry['last_edited']}")
                    print("-" * 40)

                # Show the most recently edited entry in detail
                if edited_entries:
                    most_recent = edited_entries[0]  # They should be sorted by date
                    print(f"\n{'='*60}")
                    print(f"MOST RECENTLY EDITED ENTRY:")
                    print(f"{'='*60}")

                    # Get full entry details
                    full_entry = get_entry_by_id(most_recent['id'])
                    if full_entry:
                        display_entry(full_entry)
            else:
                print("No edited entries found. All entries have the same created and last_edited times.")
                print("This means either:")
                print("1. No entries have been edited after creation")
                print("2. Edits were made to the title/properties only")
                print("3. Edits haven't been saved properly in Notion")
            sys.exit(0)

        # Check if it's a date (YYYY-MM-DD format) or page ID
        elif len(arg) == 10 and arg.count('-') == 2:
            # It's a date
            try:
                target_date = datetime.datetime.strptime(arg, '%Y-%m-%d').date()
                print(f"Fetching entries for date: {target_date}")
                print("="*60)

                date_entries = get_entries_for_date(target_date)
                if date_entries:
                    for i, entry in enumerate(date_entries):
                        print(f"\n=== Entry {i + 1} for {target_date} ===")
                        display_entry(entry)
                        print("-" * 40)
                else:
                    print(f"No entries found for {target_date}")
            except ValueError:
                print(f"Invalid date format: {arg}. Use YYYY-MM-DD format.")
        else:
            # It's a page ID
            page_id = arg
            print(f"Fetching specific entry with ID: {page_id}")
            print("="*60)

            entry = get_entry_by_id(page_id)
            if entry:
                print(f"\n=== Entry Details ===")
                display_entry(entry)
                print("-" * 40)
            else:
                print("Entry not found or error occurred.")

    else:
        print(f"Fetching journal entries for today: {today}")
        print("Usage:")
        print("  python main.py                    - Show all recent entries + today's entries")
        print("  python main.py edited             - Find and show all edited entries")
        print("  python main.py YYYY-MM-DD         - Show entries for specific date")
        print("  python main.py [page_id]          - Show specific entry by ID")

        # First, let's see what entries are available in the database
        print("\n" + "="*60)
        print("CHECKING ALL RECENT ENTRIES IN DATABASE:")
        print("="*60)
        recent_entries = get_all_recent_entries()
        if recent_entries and recent_entries.get("results"):
            for i, entry in enumerate(recent_entries["results"]):
                date_prop = entry["properties"].get("Date", {}).get("date")
                entry_date = date_prop.get("start") if date_prop else "No date"
                journal_prop = entry["properties"].get("Journal", {})
                if journal_prop.get("title"):
                    title = journal_prop["title"][0].get("plain_text", "No title")
                else:
                    title = "No title"
                print(f"{i+1}. Date: {entry_date} | Title: {title} | ID: {entry['id']}")

        print("\n" + "="*60)
        print(f"NOW LOOKING FOR TODAY'S ENTRIES ({today}):")
        print("="*60)

        if today_entries:
            for i, entry in enumerate(today_entries):
                print(f"\n=== Entry {i + 1} ===")
                display_entry(entry)
                print("-" * 40)
        else:
            print("No journal entries found for today.")
            print("Trying yesterday's entries...")

            yesterday = date.today() - datetime.timedelta(days=1)
            yesterday_entries = get_entries_for_date(yesterday)

            if yesterday_entries:
                print(
                    f"\nFound {len(yesterday_entries)} entries for yesterday ({yesterday}):"
                )
                for i, entry in enumerate(yesterday_entries):
                    print(f"\n=== Yesterday's Entry {i + 1} ===")
                    display_entry(entry)
                    print("-" * 40)
            else:
                print("No entries found for yesterday either.")
