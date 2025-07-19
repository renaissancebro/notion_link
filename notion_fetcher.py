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
    print(f"DATABASE_ID: {DATABASE_ID}")
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
    for db in search_results['results']:
        print(f"  - {db['id']}: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        
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
            filter={"property": "Date", "date": {"equals": specific_date}},
        )
        return response
    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            print(f"Database not found: {DATABASE_ID}")
        else:
            print(f"API Error: {error}")
        return None


def get_page_content(page_id):
    """
    Retrieve the content/blocks of a specific Notion page.
    """
    try:
        # Get page details
        page = notion.pages.retrieve(page_id=page_id)

        # Get page content (blocks)
        blocks = notion.blocks.children.list(block_id=page_id)

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

    if not query_result or not query_result.get("results"):
        print(f"No entries found for date: {target_date or 'today'}")
        return []

    entries_with_content = []

    for page in query_result["results"]:
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
            print(f"\nEntry {i+1}:")
            print(f"  Page ID: {entry['page_id']}")
            print(f"  Properties: {list(entry['properties'].keys())}")
            if entry['content'] and entry['content']['content_blocks']:
                print(f"  Content blocks: {len(entry['content']['content_blocks']['results'])}")
            else:
                print("  No content blocks found")
