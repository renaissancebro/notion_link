"""

Notion integration grabs database and pages and returns for use in OpenAI or other ai

"""

import datetime
import requests
import json
from datetime import date
from dotenv import load_dotenv
import os
from pprint import pprint
from notion_client import APIErrorCode, APIResponseError, Client

load_dotenv()

DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

print(f"DATABASE_ID loaded: {DATABASE_ID is not None}")
print(f"NOTION_TOKEN loaded: {NOTION_TOKEN is not None}")

if DATABASE_ID:
    print(f"DATABASE_ID loaded from .env successfully")
    # Clean the database ID (remove dashes if present)
    DATABASE_ID = DATABASE_ID.replace("-", "")

notion = Client(auth=NOTION_TOKEN)

# Test basic connection
try:
    users = notion.users.list()
    print(f"Connection successful. Found {len(users['results'])} users.")

    # Try to search for databases/pages the integration has access to
    search_results = notion.search(filter={"property": "object", "value": "database"})
    print(f"Found {len(search_results['results'])} accessible databases:")
    for db in search_results["results"]:
        print(
            f"  - {db['id']}: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}"
        )

except Exception as e:
    print(f"Connection failed: {e}")


def query_database_by_date(specific_date=None):
    """
    Query the Notion database for entries on a specific date.
    If no date is provided, uses today's date.
    """
    if specific_date is None:
        specific_date = date.today().isoformat()
    elif isinstance(specific_date, date):
        specific_date = specific_date.isoformat()

    try:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "Date",  # Use the exact property name
                "date": {"equals": specific_date}  # Use lowercase 'date' for the filter type
            },
        )
        print(f"Found {len(response.get('results', []))} entries for date: {specific_date}")
        return response
    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            print(f"Database not found: {DATABASE_ID}")
        else:
            print(f"API Error: {error}")
        return None


def get_all_recent_entries():
    """
    Get all entries from the database without date filtering to see what's available.
    """
    try:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            sorts=[
                {
                    "property": "Date",
                    "direction": "descending"
                }
            ],
            page_size=10  # Get last 10 entries
        )
        print(f"Found {len(response.get('results', []))} total recent entries")
        return response
    except APIResponseError as error:
        print(f"Error getting recent entries: {error}")
        return None


def find_edited_entries():
    """
    Find all entries that have been edited (last_edited_time != created_time).
    """
    try:
        # Get more entries to check for edits
        response = notion.databases.query(
            database_id=DATABASE_ID,
            sorts=[
                {
                    "property": "Date",
                    "direction": "descending"
                }
            ],
            page_size=50  # Check last 50 entries
        )

        edited_entries = []
        if response and response.get("results"):
            for entry in response["results"]:
                created_time = entry.get("created_time")
                last_edited_time = entry.get("last_edited_time")

                # Check if the entry has been edited after creation
                if created_time != last_edited_time:
                    date_prop = entry["properties"].get("Date", {}).get("date")
                    entry_date = date_prop.get("start") if date_prop else "No date"
                    journal_prop = entry["properties"].get("Journal", {})
                    if journal_prop.get("title"):
                        title = journal_prop["title"][0].get("plain_text", "No title")
                    else:
                        title = "No title"

                    edited_entries.append({
                        "id": entry["id"],
                        "date": entry_date,
                        "title": title,
                        "created": created_time,
                        "last_edited": last_edited_time,
                        "entry": entry
                    })

        return edited_entries

    except APIResponseError as error:
        print(f"Error finding edited entries: {error}")
        return []


def debug_block_content(page_id):
    """
    Debug function to examine raw block data and look for changes.
    """
    try:
        print(f"=== DEBUGGING BLOCK CONTENT FOR {page_id} ===")
        
        # Get page details
        page = notion.pages.retrieve(page_id=page_id)
        print(f"Page created: {page.get('created_time')}")
        print(f"Page last edited: {page.get('last_edited_time')}")
        
        # Get blocks
        blocks = notion.blocks.children.list(block_id=page_id)
        print(f"\nFound {len(blocks.get('results', []))} blocks")
        
        # Examine each block for content
        for i, block in enumerate(blocks.get("results", [])):
            print(f"\n--- Block {i+1} ---")
            print(f"Type: {block.get('type')}")
            print(f"ID: {block.get('id')}")
            print(f"Created: {block.get('created_time')}")
            print(f"Last edited: {block.get('last_edited_time')}")
            
            block_type = block.get("type")
            if block_type and block_type in block:
                block_data = block[block_type]
                if "rich_text" in block_data:
                    texts = block_data["rich_text"]
                    content = "".join([t.get("plain_text", "") for t in texts])
                    print(f"Content: '{content}'")
                    if content.strip():
                        print(f"*** HAS CONTENT! ***")
                else:
                    print("No rich_text found")
            
            # Check if this block was edited after creation
            if block.get("created_time") != block.get("last_edited_time"):
                print(f"*** BLOCK WAS EDITED! ***")
        
        return blocks
        
    except APIResponseError as error:
        print(f"Error debugging block content: {error}")
        return None


def find_recent_entries_by_creation():
    """
    Find entries by creation time instead of date property (for late entries).
    """
    try:
        # Get entries sorted by creation time instead of date property
        response = notion.databases.query(
            database_id=DATABASE_ID,
            sorts=[
                {
                    "timestamp": "created_time",
                    "direction": "descending"
                }
            ],
            page_size=20
        )
        
        recent_entries = []
        if response and response.get("results"):
            for entry in response["results"]:
                date_prop = entry["properties"].get("Date", {}).get("date")
                entry_date = date_prop.get("start") if date_prop else "No date"
                journal_prop = entry["properties"].get("Journal", {})
                if journal_prop.get("title"):
                    title = journal_prop["title"][0].get("plain_text", "No title")
                else:
                    title = "No title"
                
                recent_entries.append({
                    "id": entry["id"],
                    "date_property": entry_date,
                    "title": title,
                    "created": entry.get("created_time"),
                    "last_edited": entry.get("last_edited_time"),
                    "entry": entry
                })
        
        return recent_entries
        
    except APIResponseError as error:
        print(f"Error finding recent entries by creation: {error}")
        return []


def search_for_entries_with_content():
    """
    Search through ALL entries to find any that have actual user content (not just template text).
    """
    try:
        print("Searching through ALL entries for actual user content...")
        
        # Get ALL entries, not just recent ones
        response = notion.databases.query(
            database_id=DATABASE_ID,
            sorts=[
                {
                    "timestamp": "created_time", 
                    "direction": "descending"
                }
            ],
            page_size=100  # Get up to 100 entries
        )
        
        entries_with_content = []
        template_keywords = [
            "Notion Template", "Daily Founder Frame", "Entrepreneur Identity Tracker",
            "Entrepreneurial Creed", "Time to Ship", "What Did I Build Today",
            "technical rep", "Name your enemy", "Dangerous Entrepreneur"
        ]
        
        if response and response.get("results"):
            print(f"Checking {len(response['results'])} total entries...")
            
            for i, entry in enumerate(response["results"]):
                print(f"Checking entry {i+1}/{len(response['results'])}: {entry['id']}")
                
                # Get the blocks for this entry
                try:
                    blocks = notion.blocks.children.list(block_id=entry["id"])
                    
                    has_user_content = False
                    user_content_blocks = []
                    
                    for block in blocks.get("results", []):
                        block_type = block.get("type")
                        if block_type and block_type in block:
                            block_data = block[block_type]
                            if "rich_text" in block_data:
                                texts = block_data["rich_text"]
                                content = "".join([t.get("plain_text", "") for t in texts])
                                
                                # Check if this content is user-generated (not template)
                                if content.strip():
                                    is_template = any(keyword.lower() in content.lower() for keyword in template_keywords)
                                    if not is_template and len(content.strip()) > 5:
                                        has_user_content = True
                                        user_content_blocks.append({
                                            "type": block_type,
                                            "content": content.strip(),
                                            "created": block.get("created_time"),
                                            "last_edited": block.get("last_edited_time")
                                        })
                    
                    if has_user_content:
                        date_prop = entry["properties"].get("Date", {}).get("date")
                        entry_date = date_prop.get("start") if date_prop else "No date"
                        journal_prop = entry["properties"].get("Journal", {})
                        if journal_prop.get("title"):
                            title = journal_prop["title"][0].get("plain_text", "No title")
                        else:
                            title = "No title"
                        
                        entries_with_content.append({
                            "id": entry["id"],
                            "date": entry_date,
                            "title": title,
                            "created": entry.get("created_time"),
                            "last_edited": entry.get("last_edited_time"),
                            "user_content_blocks": user_content_blocks,
                            "entry": entry
                        })
                        print(f"*** FOUND ENTRY WITH USER CONTENT! {entry['id']} ***")
                    
                except Exception as block_error:
                    print(f"Error checking blocks for entry {entry['id']}: {block_error}")
                    continue
        
        return entries_with_content
        
    except APIResponseError as error:
        print(f"Error searching for entries with content: {error}")
        return []


def get_entry_by_id(page_id):
    """
    Get a specific entry by its page ID.
    """
    try:
        print(f"Fetching entry with ID: {page_id}")

        # Get page details
        page = notion.pages.retrieve(page_id=page_id)
        print(f"Page last edited: {page.get('last_edited_time')}")

        # Get page content
        page_content = get_page_content(page_id)

        if page_content:
            return {
                "page_id": page_id,
                "properties": page.get("properties", {}),
                "content": page_content,
            }
        return None

    except APIResponseError as error:
        print(f"Error retrieving entry by ID: {error}")
        return None


def get_page_content(page_id):
    """
    Retrieve the content/blocks of a specific Notion page.
    """
    try:
        print(f"Fetching fresh content for page: {page_id}")

        # Get page details (this will show last_edited_time)
        page = notion.pages.retrieve(page_id=page_id)
        print(f"Page last edited: {page.get('last_edited_time')}")

        # Get page content (blocks) - this should always fetch fresh content
        blocks = notion.blocks.children.list(block_id=page_id)
        print(f"Retrieved {len(blocks.get('results', []))} content blocks")

        return {"page_details": page, "content_blocks": blocks}
    except APIResponseError as error:
        print(f"Error retrieving page content: {error}")
        return None


def get_entries_for_date(target_date=None):
    """
    Get all entries for a specific date and their page content.
    """
    # Query database for entries on the target date
    query_result = query_database_by_date(target_date)

    # After query_result = query_database_by_date(target_date)
    print(json.dumps(query_result, indent=2))

    if not query_result or not query_result.get("results"):
        print(f"No entries found for date: {target_date or 'today'}")
        return []

    entries_with_content = []

    for page in query_result["results"]:
        print(page["properties"])
        page_id = page["id"]
        page_content = get_page_content(page_id)

        entries_with_content.append(
            {
                "page_id": page_id,
                "properties": page["properties"],
                "content": page_content,
            }
        )

    return entries_with_content


# Example usage
if __name__ == "__main__":
    # Test the functions
    print("Testing Notion fetcher...")

    # Get entries for yesterday
    yesterday = (date.today() - datetime.timedelta(days=1)).isoformat()
    print(f"Looking for entries on: {yesterday}")

    yesterday_entries = get_entries_for_date(yesterday)
    print(f"Found {len(yesterday_entries)} entries for yesterday")

    # Print details if entries found



    if yesterday_entries:
        for i, entry in enumerate(yesterday_entries):
            print(f"\nEntry {i + 1}:")
            print(f"  Page ID: {entry['page_id']}")
            print(f"  Properties: {list(entry['properties'].keys())}")

            # Print Journal property if it exists
            journal_prop = entry["properties"].get("Journal")
            if journal_prop and "rich_text" in journal_prop and journal_prop["rich_text"]:
                journal_text = "".join([t["plain_text"] for t in journal_prop["rich_text"] if "plain_text" in t])
                print("  Journal property content:")
                print(journal_text)
            else:
                print("  No Journal property content found.")

            if entry["content"] and entry["content"]["content_blocks"]:
                blocks = entry["content"]["content_blocks"]["results"]
                print(f"  Content blocks: {len(blocks)}")
                # Extract and print text from each block
                block_text = []
                for block in blocks:
                    block_type = block.get("type")
                    if block_type and "text" in block.get(block_type, {}):
                        texts = block[block_type]["text"]
                        for t in texts:
                            if "plain_text" in t:
                                block_text.append(t["plain_text"])
                print("  Journal content from blocks:")
                print("\n".join(block_text) if block_text else "    (No text found)")
            else:
                print("  No content blocks found")
            # Print the Journal property directly
            if "Journal" in entry["properties"]:
                journal_property = entry["properties"]["Journal"]
                if journal_property["type"] == "rich_text" and journal_property["rich_text"]:
                    # Access the plain_text of the first rich_text element
                    journal_text = journal_property["rich_text"][0]["plain_text"]
                    print(f"  Journal property text: {journal_text}")
                else:
                    print("  Journal property is empty or not of type 'rich_text'")
            else:
                print("  Journal property not found in entry properties")
