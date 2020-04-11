"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import os
import logging
import requests
from dotenv import load_dotenv
import slack

# For Slack & GitLab

# Setup variables
load_dotenv()
AUTH = os.getenv("GITLAB_API_KEY")
SCOPE = "all"
STATE = "opened"
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CLIENT = slack.WebClient(SLACK_BOT_TOKEN)
GITLAB_API_URL = os.getenv("GITLAB_API_URL")

# Setup endpoint
HEADERS = {'Authorization': f'Bearer {AUTH}'}
RESPONSE = requests.get(f"{GITLAB_API_URL}/merge_requests?scope={SCOPE}&state={STATE}", headers=HEADERS)

# Setup Slack client
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

# Iterate over each merge request
DATA = RESPONSE.json()
i = 0
send_message(SLACK_CLIENT, ":bug: *The following merge requests on GitLab are still open and need your help!*\n")
for stale_request in DATA:
    if DATA[i]['assignee'] is None:
        user = "No assignee"
    else:
        user = f"<{DATA[i]['assignee']['web_url']}|{DATA[i]['assignee']['username']}>"

    description = (DATA[i]['description'][:100] + '...') if len(DATA[i]['description']) > 100 else DATA[i]['description']

    print(f"Merge Request: {description}\nDescription: {description}\nWaiting on: {user}\n")
    message = f"*Merge Request:* <{DATA[i]['web_url']}|{DATA[i]['title']}>\n*Description:* {DATA[i]['description']}\n*Waiting on:* {user}\n"
    # Send Slack message
    try:
        send_message(SLACK_CLIENT, message)
    except IndexError:
        send_message(SLACK_CLIENT, "No merge requests stale today! Nice job.")
    i += 1
