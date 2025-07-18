"""

Notion integration grabs database and pages and returns for use in OpenAI or other ai

"""

import requests
import json
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

# Keys
NOTION_KEY = os.getenv("INTERNAL_INTEGRATION_SECRET")
OPENAI_KEy = os.getenv("OPENAI_API_KEY")
