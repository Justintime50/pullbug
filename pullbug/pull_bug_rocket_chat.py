"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import os
import logging
import json
import requests
from dotenv import load_dotenv

# Setup variables
load_dotenv()
GITLAB_API_KEY = os.getenv("GITLAB_API_KEY")
GITLAB_API_URL = os.getenv("GITLAB_API_URL")
GITLAB_SCOPE = os.getenv("GITLAB_SCOPE")
GITLAB_STATE = os.getenv("GITLAB_STATE")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_STATE = os.getenv("GITHUB_STATE")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")
IGNORE_WIP = os.getenv("IGNORE_WIP")

def send_message(slack_client, msg):
    """Send Slack messages via a bot"""
    logging.debug("authorized Slack Client")
    logging.basicConfig(level=logging.DEBUG)

    # Make the POST request through the python slack client
    slack_response = slack_client.chat_postMessage(
        channel=os.getenv("SLACK_CHANNEL"),
        text=msg
    )

    # Check if the request was a success
    if slack_response['ok'] is not True:
        logging.error(slack_response)
    else:
        logging.debug(slack_response)

def pull_bug_gitlab():
    """Send a message from GitLab to Slack for Merge Requests"""

    # Setup endpoint & Slack client
    headers = {'authorization': f'Bearer {GITLAB_API_KEY}'}
    response = requests.get(f"{GITLAB_API_URL}/merge_requests?scope={GITLAB_SCOPE}&state={GITLAB_STATE}", headers=headers)

    # Iterate over each merge request
    data = response.json()
    i = 0
    message = ":bug: *The following merge requests on GitLab are still open and need your help!*\n"
    for stale_request in data:
        # If MR is a WIP, ignore it
        if IGNORE_WIP == 'true':
            if 'wip' in stale_request['title'] or 'Wip' in stale_request['title'] or 'WIP' in stale_request['title']:
                i += 1
                continue

        # Setup assignee
        if stale_request['assignee'] is None:
            user = "No assignee"
        else:
            user = f"<{stale_request['assignee']['web_url']}|{stale_request['assignee']['username']}>"

        # Craft message
        description = (stale_request['description'][:100] + '...') if len(stale_request['description']) > 100 else stale_request['description']
        message += f"\n:arrow_heading_up: *Merge Request:* <{stale_request['web_url']}|{stale_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"
        i += 1

    # Send Rocket Chat message
    try:
        requests.post(ROCKET_CHAT_URL, data={'text': message})
        print("Pull Bug GitLab Message Sent!")
    except IndexError:
        requests.post(ROCKET_CHAT_URL, data={'text': 'No merge requests stale today! Nice job.'})
        print("No MR's today!")

def pull_bug_github():
    """Send a message from GitHub to Slack for Pull Requests"""

    # Grab all repos of the owner
    headers = {
        "Authorization": f"token {GITHUB_API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }
    repos_response = requests.get(f"https://api.github.com/orgs/{GITHUB_OWNER}/repos", headers=headers).text
    repos = json.loads(repos_response)

    # Grab all pull requests of each repo and send the data
    message = ":bug: *The following pull requests on GitHub are still open and need your help!*\n"
    for repo in repos:
        pull_response = requests.get(f"https://api.github.com/repos/{GITHUB_OWNER}/{repo['name']}/pulls?state={GITHUB_STATE}", headers=headers).text
        pull_requests = json.loads(pull_response)
        for pull_request in pull_requests:
            # TODO: Check assignee array instead of a single record # pylint: disable=fixme
            # TODO: Check requested_reviewers array also # pylint: disable=fixme
            # If PR is a WIP, ignore it
            if IGNORE_WIP == 'true':
                if 'wip' in pull_request['title'] or 'Wip' in pull_request['title'] or 'WIP' in pull_request['title']:
                    continue
            if pull_request['assignee'] is None:
                user = "No assignee"
            else:
                user = f"<{pull_request['assignee']['html_url']}|{pull_request['assignee']['login']}>"

            description = (pull_request['body'][:100] + '...') if len(pull_request['body']) > 100 else pull_request['body']
            message += f"\n:arrow_heading_up: *Pull Request:* <{pull_request['html_url']}|{pull_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

    # Send Rocket Chat message
    try:
        requests.post(ROCKET_CHAT_URL, data={'text': message})
        print("Pull Bug GitHub Message Sent!")
    except IndexError:
        requests.post(ROCKET_CHAT_URL, data={'text': 'No pull requests stale today! Nice job.'})
        print("No PR's today!")
