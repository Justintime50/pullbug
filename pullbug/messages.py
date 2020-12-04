import os
import logging
import requests
import slack


DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
ROCKET_CHAT_URL = os.getenv('ROCKET_CHAT_URL')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
LOGGER = logging.getLogger(__name__)


class Messages():
    @classmethod
    def discord(cls, message):
        """Send a Discord message
        """
        try:
            # TODO: Discord has a hard limit of 2000 characters per message
            # break up long messages and send separately if necessary
            # TODO: Discord has sad formatting, fix links on messages
            requests.post(DISCORD_WEBHOOK_URL, json={'content': message[:2000]})
            LOGGER.info('Discord message sent!')
        except requests.exceptions.RequestException as discord_error:
            LOGGER.error(f'Could not send Discord message: {discord_error}')
            raise requests.exceptions.RequestException(discord_error)

    @classmethod
    def rocketchat(cls, message):
        """Send a Rocket Chat message
        """
        try:
            requests.post(ROCKET_CHAT_URL, json={'text': message})
            LOGGER.info('Rocket Chat message sent!')
        except requests.exceptions.RequestException as rc_error:
            LOGGER.error(f'Could not send Rocket Chat message: {rc_error}')
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
            LOGGER.error(f'Could not send Slack message: {slack_error}')
            raise slack.errors.SlackApiError(
                slack_error.response["ok"], slack_error.response['error']
            )
