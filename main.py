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
            
            # Print Journal property content (handle both title and rich_text types)
            journal_prop = entry["properties"].get("Journal")
            if journal_prop:
                if journal_prop["type"] == "title" and journal_prop["title"]:
                    journal_text = "".join([t["plain_text"] for t in journal_prop["title"] if "plain_text" in t])
                    print("Journal Title:")
                    print(journal_text)
                elif journal_prop["type"] == "rich_text" and journal_prop["rich_text"]:
                    journal_text = "".join([t["plain_text"] for t in journal_prop["rich_text"] if "plain_text" in t])
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
                    if block_type == "paragraph" and block.get("paragraph", {}).get("rich_text"):
                        texts = block["paragraph"]["rich_text"]
                        paragraph_text = "".join([t.get("plain_text", "") for t in texts])
                        if paragraph_text.strip():
                            print(paragraph_text)
                    
                    elif block_type == "heading_1" and block.get("heading_1", {}).get("rich_text"):
                        texts = block["heading_1"]["rich_text"]
                        heading_text = "".join([t.get("plain_text", "") for t in texts])
                        if heading_text.strip():
                            print(f"\n# {heading_text}")
                    
                    elif block_type == "heading_2" and block.get("heading_2", {}).get("rich_text"):
                        texts = block["heading_2"]["rich_text"]
                        heading_text = "".join([t.get("plain_text", "") for t in texts])
                        if heading_text.strip():
                            print(f"\n## {heading_text}")
                    
                    elif block_type == "heading_3" and block.get("heading_3", {}).get("rich_text"):
                        texts = block["heading_3"]["rich_text"]
                        heading_text = "".join([t.get("plain_text", "") for t in texts])
                        if heading_text.strip():
                            print(f"\n### {heading_text}")
                    
                    elif block_type == "bulleted_list_item" and block.get("bulleted_list_item", {}).get("rich_text"):
                        texts = block["bulleted_list_item"]["rich_text"]
                        list_text = "".join([t.get("plain_text", "") for t in texts])
                        if list_text.strip():
                            print(f"• {list_text}")
                    
                    elif block_type == "numbered_list_item" and block.get("numbered_list_item", {}).get("rich_text"):
                        texts = block["numbered_list_item"]["rich_text"]
                        list_text = "".join([t.get("plain_text", "") for t in texts])
                        if list_text.strip():
                            print(f"1. {list_text}")
                    
                    elif block_type == "to_do" and block.get("to_do", {}).get("rich_text"):
                        texts = block["to_do"]["rich_text"]
                        todo_text = "".join([t.get("plain_text", "") for t in texts])
                        checked = block["to_do"].get("checked", False)
                        checkbox = "☑" if checked else "☐"
                        if todo_text.strip():
                            print(f"{checkbox} {todo_text}")
                    
                    elif block_type == "quote" and block.get("quote", {}).get("rich_text"):
                        texts = block["quote"]["rich_text"]
                        quote_text = "".join([t.get("plain_text", "") for t in texts])
                        if quote_text.strip():
                            print(f"> {quote_text}")
                    
                    elif block_type == "code" and block.get("code", {}).get("rich_text"):
                        texts = block["code"]["rich_text"]
                        code_text = "".join([t.get("plain_text", "") for t in texts])
                        language = block["code"].get("language", "")
                        if code_text.strip():
                            print(f"```{language}")
                            print(code_text)
                            print("```")
                
                print("=" * 50)
            
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
                
                # Print Journal property content (handle both title and rich_text types)
                journal_prop = entry["properties"].get("Journal")
                if journal_prop:
                    if journal_prop["type"] == "title" and journal_prop["title"]:
                        journal_text = "".join([t["plain_text"] for t in journal_prop["title"] if "plain_text" in t])
                        print("Journal Title:")
                        print(journal_text)
                    elif journal_prop["type"] == "rich_text" and journal_prop["rich_text"]:
                        journal_text = "".join([t["plain_text"] for t in journal_prop["rich_text"] if "plain_text" in t])
                        print("Journal Content:")
                        print(journal_text)
                
                # Print full content from blocks
                if entry["content"] and entry["content"]["content_blocks"]:
                    blocks = entry["content"]["content_blocks"]["results"]
                    print("\nFull Journal Content:")
                    print("=" * 50)
                    
                    for block in blocks:
                        block_type = block.get("type")
                        
                        if block_type == "paragraph" and block.get("paragraph", {}).get("rich_text"):
                            texts = block["paragraph"]["rich_text"]
                            paragraph_text = "".join([t.get("plain_text", "") for t in texts])
                            if paragraph_text.strip():
                                print(paragraph_text)
                        
                        elif block_type in ["heading_1", "heading_2", "heading_3"] and block.get(block_type, {}).get("rich_text"):
                            texts = block[block_type]["rich_text"]
                            heading_text = "".join([t.get("plain_text", "") for t in texts])
                            if heading_text.strip():
                                level = block_type.split("_")[-1]
                                print(f"\n{'#' * int(level)} {heading_text}")
                        
                        elif block_type == "bulleted_list_item" and block.get("bulleted_list_item", {}).get("rich_text"):
                            texts = block["bulleted_list_item"]["rich_text"]
                            list_text = "".join([t.get("plain_text", "") for t in texts])
                            if list_text.strip():
                                print(f"• {list_text}")
                    
                    print("=" * 50)
                    
                print("-" * 40)
        else:
            print("No entries found for yesterday either.")
