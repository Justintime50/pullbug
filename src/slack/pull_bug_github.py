"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import json
import os
import logging
import sys
import requests
from dotenv import load_dotenv
import slack

# For Rocket Chat & GitHub

# Setup variables
load_dotenv()
AUTH = os.getenv("GITHUB_API_KEY")
OWNER = os.getenv("GITHUB_OWNER")
STATE = os.getenv("GITHUB_STATE")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")
if AUTH is None or OWNER is None or STATE is None or SLACK_BOT_TOKEN is None or ROCKET_CHAT_URL is None:
    print("You are missing required environment variables, please correct this and run the script again.")
    sys.exit()

# Setup Slack client
SLACK_CLIENT = slack.WebClient(SLACK_BOT_TOKEN)
def send_message(slack_client, msg):
    """Send Slack messages via a bot"""
    logging.debug("Authorized Slack Client")
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


# Grab all repos of the owner
HEADERS = {
    "Authorization": f"token {AUTH}",
    "Content-Type": "application/json; charset=utf-8"
}
REPOS_RESPONSE = requests.get(f"https://api.github.com/orgs/{OWNER}/repos", headers=HEADERS).text
REPOS = json.loads(REPOS_RESPONSE)

# Grab all pull requests of each repo and send the data
send_message(SLACK_CLIENT, ":bug: *The following pull requests on GitHub are still open and need your help!*\n")
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
        # Send Slack message
        try:
            send_message(SLACK_CLIENT, message)
        except IndexError:
            send_message(SLACK_CLIENT, "No pull requests stale today! Nice job.")
