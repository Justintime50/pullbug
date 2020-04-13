"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import os
import requests
from dotenv import load_dotenv

# For Rocket Chat & GitLab

# Setup variables
load_dotenv()
AUTH = os.getenv("GITLAB_API_KEY")
SCOPE = "all"
STATE = "opened"
GITLAB_API_URL = os.getenv("GITLAB_API_URL")
ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")

# Setup endpoint
HEADERS = {'Authorization': f'Bearer {AUTH}'}
RESPONSE = requests.get(f"{GITLAB_API_URL}/merge_requests?scope={SCOPE}&state={STATE}", headers=HEADERS)

# Iterate over each merge request
DATA = RESPONSE.json()
i = 0
requests.post(ROCKET_CHAT_URL, data={'text':":bug: *The following merge requests on GitLab are still open and need your help!*\n"})
for stale_request in DATA:
    if 'wip' in DATA[i]['title'] or 'Wip' in DATA[i]['title'] or 'WIP' in DATA[i]['title']:
        i += 1
        continue
    if DATA[i]['assignee'] is None:
        user = "No assignee"
    else:
        user = f"<{DATA[i]['assignee']['web_url']}|{DATA[i]['assignee']['username']}>"

    description = (DATA[i]['description'][:100] + '...') if len(DATA[i]['description']) > 100 else DATA[i]['description']

    print(f"Merge Request: {DATA[i]['title']}\nDescription: {description}\nWaiting on: {user}\n")
    message = f"*Merge Request:* <{DATA[i]['web_url']}|{DATA[i]['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"
    # Send Rocket Chat message
    try:
        CHAT_ENDPOINT = requests.post(ROCKET_CHAT_URL, data={'text':message})
    except IndexError:
        requests.post(ROCKET_CHAT_URL, data={'text':'No merge requests stale today! Nice job.'})
    i += 1
