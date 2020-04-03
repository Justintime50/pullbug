"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import os
import logging
import requests
from dotenv import load_dotenv
import slack

# Setup variables
load_dotenv()
AUTH = os.getenv("GITLAB_API_KEY")
STATE = "opened"
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CLIENT = slack.WebClient(SLACK_BOT_TOKEN)

# Setup endpoint
HEADERS = {'Authorization': f'Bearer {AUTH}'}
RESPONSE = requests.get(f"https://git.ncr4.com/api/v4/merge_requests?state={STATE}", headers=HEADERS)
# TODO: Add logic on how to pull the MR/PR (eg: more than 7 days old)

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
send_message(SLACK_CLIENT, "*Pull Bug - the following merge requests on GitLab are still open and need your help!*\n")
for stale_request in DATA:
    print(f"Merge Request: {DATA[i]['title']}\nDescription: {DATA[i]['description']}\nWaiting on: {DATA[i]['assignee']}\n")
    message = f"*Merge Request:* <{DATA[i]['web_url']}|{DATA[i]['title']}>\n*Description:* {DATA[i]['description']}\n*Waiting on:* {DATA[i]['assignee']}\n"
    # Send Slack message
    try:
        send_message(SLACK_CLIENT, message)
    except IndexError:
        send_message(SLACK_CLIENT, "No merge requests stale today! Nice job.")
    i += 1
