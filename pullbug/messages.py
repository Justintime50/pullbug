import logging
import math
import os
import re

import requests
import slack

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
ROCKET_CHAT_URL = os.getenv('ROCKET_CHAT_URL')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
GITLAB_API_URL = os.getenv('GITLAB_API_URL', 'https://gitlab.com/api/v4')
LOGGER = logging.getLogger(__name__)


class Messages:
    @classmethod
    def send_discord_message(cls, message):
        """Send a Discord message.

        Discord has a hard limit of 2000 characters per message,
        as such, we break up the messages into batches, allow for
        breathing room, and send each batch of messages separately.
        """
        num_of_messages = len(message)
        max_per_batch = 6
        i = 1
        new_cutoff = max_per_batch
        old_cutoff = 0
        while i <= math.ceil(num_of_messages / max_per_batch):
            i += 1
            batch_message = ''.join(message[old_cutoff:new_cutoff])
            new_cutoff += max_per_batch
            old_cutoff += max_per_batch
            try:
                requests.post(DISCORD_WEBHOOK_URL, json={'content': batch_message})
                LOGGER.info('Discord message sent!')
            except requests.exceptions.RequestException as discord_error:
                LOGGER.error(f'Could not send Discord message: {discord_error}')
                raise requests.exceptions.RequestException(discord_error)

    @classmethod
    def send_rocketchat_message(cls, message):
        """Send a Rocket Chat message

        We truncate the message at 40,000 characters to match Slack
        and improve performance. RC doesn't specify a char limit.
        """
        rocketchat_message = ''.join(message)[:40000]
        try:
            requests.post(ROCKET_CHAT_URL, json={'text': rocketchat_message})
            LOGGER.info('Rocket Chat message sent!')
        except requests.exceptions.RequestException as rc_error:
            LOGGER.error(f'Could not send Rocket Chat message: {rc_error}')
            raise requests.exceptions.RequestException(rc_error)

    @classmethod
    def send_slack_message(cls, message):
        """Send Slack messages via a bot.

        Slack truncates messages after 40,000 characters so
        we truncate there before sending the request.
        """
        slack_message = ''.join(message)[:40000]
        slack_client = slack.WebClient(SLACK_BOT_TOKEN)
        try:
            slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=slack_message,
            )
            LOGGER.info('Slack message sent!')
        except slack.errors.SlackApiError as slack_error:
            LOGGER.error(f'Could not send Slack message: {slack_error}')
            raise slack.errors.SlackApiError(slack_error.response["ok"], slack_error.response['error'])

    @classmethod
    def prepare_github_message(cls, pull_request, discord, slack, rocketchat):
        """Prepares a GitHub message with a single pull request's data.
        This will then be appended to an array of messages.

        Slack & RocketChat can use the same format while Discord requires
        some tweaking.
        """
        # TODO: Check requested_reviewers array also
        description_max_length = 120
        users = ''
        discord_users = ''
        if pull_request.get('assignees'):
            for assignee in pull_request['assignees']:
                discord_user = f"{assignee['login']} (<{assignee['html_url']}>)"
                user = f"<{assignee['html_url']}|{assignee['login']}>"
                users += user + ' '
                discord_users += discord_user + ' '
        else:
            users = 'NA'

        description = (
            (pull_request.get('body')[:description_max_length] + '...')
            if len(pull_request['body']) > description_max_length
            else pull_request.get('body')
        )
        message = (
            f"\n:arrow_heading_up: *Pull Request:* <{pull_request['html_url']}|{pull_request['title']}>"
            f"\n*Repo:* <{pull_request['base']['repo']['html_url']}|{pull_request['base']['repo']['name']}>"
            f"\n*Description:* {description}\n*Waiting on:* {users}\n"
        )
        discord_message = (
            f"\n:arrow_heading_up: **Pull Request:** {pull_request['title']} (<{pull_request['html_url']}>)"
            f"\n**Repo:** {pull_request['base']['repo']['name']} (<{pull_request['base']['repo']['html_url']}>)"
            f"\n**Description:** {description}\n**Waiting on:** {discord_users}\n"
        )

        return message, discord_message

    @classmethod
    def prepare_gitlab_message(cls, merge_request, discord, slack, rocketchat):
        """Prepare a GitLab message with a single merge request's data.
        This will then be appended to an array of messages.

        Slack & RocketChat can use the same format while Discord requires
        some tweaking.
        """
        description_max_length = 120
        users = ''
        discord_users = ''
        re_repo_name = re.compile('(?P<group_name>[\\w-]+)/(?P<repo_name>[\\w-]+)!(?P<merge_request_num>\\d+)')
        re_match = re_repo_name.search(merge_request['references']['full'])
        if merge_request.get('assignees'):
            for assignee in merge_request['assignees']:
                user = f"<{assignee['web_url']}|{assignee['username']}>"
                discord_user = f"{assignee['username']} (<{assignee['web_url']}>)"
                users += user + ' '
                discord_users += discord_user + ' '
        else:
            users = 'NA'

        description = (
            (merge_request.get('description')[:description_max_length] + '...')
            if len(merge_request['description']) > description_max_length
            else merge_request.get('description')
        )
        message = (
            f"\n:arrow_heading_up: *Merge Request:* <{merge_request['web_url']}|{merge_request['title']}>"
            f"\n*Repo:* <{GITLAB_API_URL}/{re_match['group_name']}/{re_match['repo_name']}|{re_match['repo_name']}>"
            f"\n*Description:* {description}\n*Waiting on:* {users}\n"
        )
        discord_message = (
            f"\n:arrow_heading_up: **Pull Request:** {merge_request['title']} (<{merge_request['web_url']}>)"
            f"\n**Repo:** {re_match['repo_name']} (<{GITLAB_API_URL}/{re_match['group_name']}/{re_match['repo_name']}>)"
            f"\n**Description:** {description}\n**Waiting on:** {discord_users}\n"
        )

        return message, discord_message
