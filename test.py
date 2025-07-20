from notion_fetcher import get_all_recent_entries, get_entry_by_id, get_page_content, find_edited_entries
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


get_page_content = notion.pages.retrieve

find_edited_entries() 
