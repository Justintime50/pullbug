import os
import logging
import requests
import slack


SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
ROCKET_CHAT_URL = os.getenv('ROCKET_CHAT_URL')
LOGGER = logging.getLogger(__name__)


class Messages():
    @classmethod
    def rocketchat(cls, message):
        """Send a Rocket Chat message
        """
        try:
            requests.post(ROCKET_CHAT_URL, data={'text': message})
            LOGGER.info('Rocket Chat message sent!')
        except requests.exceptions.RequestException as rc_error:
            LOGGER.warning(f'Could not send Rocket Chat message: {rc_error}')
            raise requests.exceptions.RequestException(rc_error)

    @classmethod
    def slack(cls, message):
        """Send Slack messages via a bot
        """
        slack_client = slack.WebClient(SLACK_BOT_TOKEN)
        try:
            slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message
            )
            LOGGER.info('Slack message sent!')
        except slack.errors.SlackApiError as slack_error:
            LOGGER.warning(f'Could not send Slack message: {slack_error}')
            raise slack.errors.SlackApiError(
                slack_error.response["ok"], slack_error.response['error']
            )
