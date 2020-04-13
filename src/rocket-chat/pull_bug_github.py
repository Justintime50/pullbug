"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import json
import os
import requests
from dotenv import load_dotenv

# For Rocket Chat & GitHub

# Setup variables
load_dotenv()
AUTH = os.getenv("GITHUB_API_KEY")
OWNER = os.getenv("GITHUB_OWNER")
STATE = "open"
ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")

# Grab all repos of the owner
HEADERS = {
    "Authorization": f"token {AUTH}",
    "Content-Type": "application/json; charset=utf-8"
}
REPOS_RESPONSE = requests.get(f"https://api.github.com/orgs/{OWNER}/repos", headers=HEADERS).text
REPOS = json.loads(REPOS_RESPONSE)

# Grab all pull requests of each repo and send the data
requests.post(ROCKET_CHAT_URL, data={'text':":bug: *The following pull requests on GitHub are still open and need your help!*\n"})
for repo in REPOS:
    PULL_RESPONSE = requests.get(f"https://api.github.com/repos/{OWNER}/{repo['name']}/pulls?state={STATE}", headers=HEADERS).text
    PULL_REQUESTS = json.loads(PULL_RESPONSE)
    for pull_request in PULL_REQUESTS:
        # TODO: Check assignee array instead of a single record # pylint: disable=fixme
        # TODO: Check requested_reviewers array also # pylint: disable=fixme
        if 'wip' in pull_request['title'] or 'Wip' in pull_request['title'] or 'WIP' in pull_request['title']:
            continue
        if pull_request['assignee'] is None:
            user = "No assignee"
        else:
            user = f"<{pull_request['assignee']['html_url']}|{pull_request['assignee']['login']}>"

        description = (pull_request['body'][:100] + '...') if len(pull_request['body']) > 100 else pull_request['body']

        print(f"Pull Request: {pull_request['title']}\nDescription: {description}\nWaiting on: {user}\n")
        message = f"*Pull Request:* <{pull_request['html_url']}|{pull_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"
        # Send Rocket Chat message
        try:
            CHAT_ENDPOINT = requests.post(ROCKET_CHAT_URL, data={'text':message})
        except IndexError:
            requests.post(ROCKET_CHAT_URL, data={'text':'No pull requests stale today! Nice job.'})
