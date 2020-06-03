"""Pull Bug Sending Messages Logic"""
import os
import sys
import requests
from dotenv import load_dotenv
import slack


class Messages():
    """All sending message logic lives here"""
    # Setup variables
    load_dotenv()
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    ROCKET_CHAT_URL = os.getenv('ROCKET_CHAT_URL')

    @classmethod
    def rocket_chat(cls, message):
        """Send a Rocket Chat message"""
        try:
            requests.post(Messages.ROCKET_CHAT_URL, data={'text': message})
            print("Rocket Chat message sent!")
        except requests.exceptions.RequestException as rc_error:
            sys.exit(rc_error)

    @classmethod
    def slack(cls, message):
        """Send Slack messages via a bot"""
        slack_client = slack.WebClient(Messages.SLACK_BOT_TOKEN)
        try:
            slack_client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text=message
            )
            print("Slack message sent!")
        except slack.errors.SlackApiError as slack_error:
            sys.exit(slack_error)
