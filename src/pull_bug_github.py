"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import json
import os
import requests
from dotenv import load_dotenv

# Setup variables
load_dotenv()
AUTH = os.getenv("GITHUB_API_KEY")
OWNER = os.getenv("GITHUB_OWNER")
STATE = "open"

# Setup endpoint
HEADERS = {"Authorization": f"token {AUTH}"}
RESPONSE = requests.get(f"https://api.github.com/repos/{OWNER}/REPO/pulls?state={STATE}", headers=HEADERS)

def jprint(obj):
    """Setup pretty printing for JSON"""
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
jprint(RESPONSE.json())
