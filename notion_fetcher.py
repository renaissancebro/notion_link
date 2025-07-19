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
