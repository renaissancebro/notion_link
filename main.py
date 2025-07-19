import datetime
from notion_fetcher import (
    query_database_by_date,
    get_entries_for_date,
    get_page_content,
)
from datetime import date


today = date.today()
today_entries = get_entries_for_date(today)


if __name__ == "__main__":
    print(f"Fetching journal entries for today: {today}")
    
    if today_entries:
        for i, entry in enumerate(today_entries):
            print(f"\n=== Entry {i + 1} ===")
            print(f"Page ID: {entry['page_id']}")
            
            # Print Journal property content
            journal_prop = entry["properties"].get("Journal")
            if journal_prop and "rich_text" in journal_prop and journal_prop["rich_text"]:
                journal_text = "".join([t["plain_text"] for t in journal_prop["rich_text"] if "plain_text" in t])
                print("Journal Content:")
                print(journal_text)
            
            # Print content from blocks if available
            if entry["content"] and entry["content"]["content_blocks"]:
                blocks = entry["content"]["content_blocks"]["results"]
                block_text = []
                for block in blocks:
                    block_type = block.get("type")
                    if block_type and "text" in block.get(block_type, {}):
                        texts = block[block_type]["text"]
                        for t in texts:
                            if "plain_text" in t:
                                block_text.append(t["plain_text"])
                
                if block_text:
                    print("Additional Content from Blocks:")
                    print("\n".join(block_text))
            
            print("-" * 40)
    else:
        print("No journal entries found for today.")
        print("Trying yesterday's entries...")
        
        yesterday = date.today() - datetime.timedelta(days=1)
        yesterday_entries = get_entries_for_date(yesterday)
        
        if yesterday_entries:
            print(f"\nFound {len(yesterday_entries)} entries for yesterday ({yesterday}):")
            for i, entry in enumerate(yesterday_entries):
                print(f"\n=== Yesterday's Entry {i + 1} ===")
                
                journal_prop = entry["properties"].get("Journal")
                if journal_prop and "rich_text" in journal_prop and journal_prop["rich_text"]:
                    journal_text = "".join([t["plain_text"] for t in journal_prop["rich_text"] if "plain_text" in t])
                    print("Journal Content:")
                    print(journal_text)
                    
                print("-" * 40)
        else:
            print("No entries found for yesterday either.")
