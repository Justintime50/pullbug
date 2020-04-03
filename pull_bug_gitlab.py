"""Pull Bug is great at bugging you to merge or close your pull/merge requests."""
import requests
import json
import os
from dotenv import load_dotenv
import logging
import slack # pip3 install slackclient

# Setup variables
load_dotenv()
AUTH = os.getenv("GITLAB_API_KEY")
STATE = "opened"
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = slack.WebClient(SLACK_BOT_TOKEN)

# Setup endpoint
headers = {'Authorization': f'Bearer {AUTH}'}
response = requests.get(f"https://git.ncr4.com/api/v4/merge_requests?state={STATE}", headers=headers)
# TODO: Add logic on how to pull the MR/PR (eg: more than 7 days old)

# Send Slack messages via a bot
def sendMessage(slack_client, msg):
    logging.debug("Authorized Slack Client")
    logging.basicConfig(level=logging.DEBUG)
    
    # Make the POST request through the python slack client
    slack_response = slack_client.chat_postMessage(
        channel=os.getenv("SLACK_CHANNEL"),
        text=msg
    )

    # Check if the request was a success
    if slack_response['ok'] is not True:
        logging.error(response)
    else:
        logging.debug(response)

# Iterate over each merge request
data = response.json()
i = 0
print("Pull Bug - the following merge requests on GitLab are still open and need your help!\n")
for stale_request in data:
    print(f"Merge Request: {data[i]['title']}\nDescription: {data[i]['description']}\nWaiting on: {data[i]['assignee']}\n")
    message = f"Merge Request: {data[i]['title']}\nDescription: {data[i]['description']}\nWaiting on: {data[i]['assignee']}\n"
    # Send Slack message
    try:
        sendMessage(slack_client, message)
    except IndexError:
        sendMessage(slack_client, "No merge requests stale today! Nice job.")
    i += 1
