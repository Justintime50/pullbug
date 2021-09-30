import logging
import math

import requests
import slack

LOGGER = logging.getLogger(__name__)


class Messages:
    def send_discord_message(self, message):
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
                requests.post(self.discord_url, json={'content': batch_message})
                LOGGER.info('Discord message sent!')
            except requests.exceptions.RequestException as discord_error:
                LOGGER.error(f'Could not send Discord message: {discord_error}')
                raise requests.exceptions.RequestException(discord_error)

    def send_rocketchat_message(self, message):
        """Send a Rocket Chat message.

        We truncate the message at 40,000 characters to match Slack
        and improve performance. RC doesn't specify a char limit.
        """
        rocketchat_message = ''.join(message)[:40000]
        try:
            requests.post(self.rocketchat_url, json={'text': rocketchat_message})
            LOGGER.info('Rocket Chat message sent!')
        except requests.exceptions.RequestException as rc_error:
            LOGGER.error(f'Could not send Rocket Chat message: {rc_error}')
            raise requests.exceptions.RequestException(rc_error)

    def send_slack_message(self, message):
        """Send Slack messages via a bot.

        Slack truncates messages after 40,000 characters so
        we truncate there before sending the request.
        """
        slack_message = ''.join(message)[:40000]
        slack_client = slack.WebClient(self.slack_token)
        try:
            slack_client.chat_postMessage(
                channel=self.slack_channel,
                text=slack_message,
            )
            LOGGER.info('Slack message sent!')
        except slack.errors.SlackApiError as slack_error:
            LOGGER.error(f'Could not send Slack message: {slack_error}')
            raise slack.errors.SlackApiError(slack_error.response["ok"], slack_error.response['error'])

    @staticmethod
    def prepare_pulls_message(pull_request):
        """Prepares a GitHub pull request message with a single pull request's data.
        This will then be appended to an array of messages.

        Slack & RocketChat can use the same format while Discord requires
        some tweaking.
        """
        # TODO: Check requested_reviewers array also
        description_max_length = 120
        users = ''
        discord_users = ''

        if pull_request.assignees:
            for assignee in pull_request.assignees:
                discord_user = f"{assignee.login} (<{assignee.html_url}>)"
                user = f"<{assignee.html_url}|{assignee.login}>"
                users += user + ' '
                discord_users += discord_user + ' '
        else:
            users = 'NA'

        description = (
            pull_request.body[:description_max_length] + '...'
            if len(pull_request.body) > description_max_length
            else pull_request.body
        )
        message = (
            f"\n:arrow_heading_up: *Pull Request:* <{pull_request.html_url}|{pull_request.title}>"
            f"\n*Repo:* <{pull_request.base.repo.html_url}|{pull_request.base.repo.name}>"
            f"\n*Description:* {description}\n*Waiting on:* {users}\n"
        )
        discord_message = (
            f"\n:arrow_heading_up: **Pull Request:** {pull_request.title} (<{pull_request.html_url}>)"
            f"\n**Repo:** {pull_request.base.repo.name} (<{pull_request.base.repo.html_url}>)"
            f"\n**Description:** {description}\n**Waiting on:** {discord_users}\n"
        )

        return message, discord_message

    @staticmethod
    def prepare_issues_message(issue):
        """Prepares a GitHub issue message with a single issue's data.
        This will then be appended to an array of messages.

        Slack & RocketChat can use the same format while Discord requires
        some tweaking.
        """
        description_max_length = 120
        users = ''
        discord_users = ''

        if issue.assignees:
            for assignee in issue.assignees:
                discord_user = f"{assignee.login} (<{assignee.html_url}>)"
                user = f"<{assignee.html_url}|{assignee.login}>"
                users += user + ' '
                discord_users += discord_user + ' '
        else:
            users = 'NA'

        description = (
            issue.body[:description_max_length] + '...' if len(issue.body) > description_max_length else issue.body
        )
        message = (
            f"\n:exclamation: *Issue:* <{issue.html_url}|{issue.title}>"
            f"\n*Repo:* <{issue.repository.html_url}|{issue.repository.name}>"
            f"\n*Description:* {description}\n*Assigned to:* {users}\n"
        )
        discord_message = (
            f"\n:exclamation: **Issue:** {issue.title} (<{issue.html_url}>)"
            f"\n**Repo:** {issue.repository.name} (<{issue.repository.html_url}>)"
            f"\n**Description:** {description}\n**Assigned to:** {discord_users}\n"
        )

        return message, discord_message
