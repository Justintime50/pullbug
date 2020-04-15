"""Pull Bug Sending Messages Logic"""
import os
import requests
from dotenv import load_dotenv
import slack

# Setup variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
ROCKET_CHAT_URL = os.getenv("ROCKET_CHAT_URL")

class Messages():
    """All sending message logic lives here"""
    @classmethod
    def rocket_chat(cls, message):
        """Send a Rocket Chat message"""
        try:
            requests.post(ROCKET_CHAT_URL, data={'text': message})
            print("Message Sent!")
        except IndexError:
            requests.post(ROCKET_CHAT_URL, data={'text': 'No requests to pull!'})
            print("No requests!")

    @classmethod
    def slack(cls, message):
        """Send Slack messages via a bot"""
        # Make the POST request through the python slack client
        slack_client = slack.WebClient(SLACK_BOT_TOKEN)
        try:
            slack_client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text=message
            )
            print("Message Sent!")
        except IndexError:
            slack_client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text="No MR's"
            )
            print("No requests!")
