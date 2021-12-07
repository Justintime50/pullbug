import math
from typing import List, Tuple

import github
import requests
import slack
import woodchips
from github.Issue import Issue

LOGGER_NAME = 'pullbug'

DESCRIPTION_CONTINUATION = '...'
DESCRIPTION_MAX_LENGTH = 120


class Messages:
    @staticmethod
    def send_discord_message(messages: List[str], discord_url: str):
        """Send a Discord message.

        Discord has a hard limit of 2000 characters per message,
        as such, we break up the messages into batches, allow for
        breathing room, and send each batch of messages separately.
        """
        logger = woodchips.get(LOGGER_NAME)

        num_of_messages = len(messages)
        max_messages_per_batch = 6
        i = 1
        new_cutoff = max_messages_per_batch
        old_cutoff = 0

        while i <= math.ceil(num_of_messages / max_messages_per_batch):
            i += 1
            batch_message = ''.join(messages[old_cutoff:new_cutoff])
            new_cutoff += max_messages_per_batch
            old_cutoff += max_messages_per_batch
            try:
                requests.post(discord_url, json={'content': batch_message})
                logger.info('Discord message sent!')
            except requests.exceptions.RequestException as discord_error:
                logger.error(f'Could not send Discord message: {discord_error}')
                raise requests.exceptions.RequestException(discord_error)

    @staticmethod
    def send_rocketchat_message(messages: List[str], rocketchat_url: str):
        """Send a Rocket Chat message.

        We truncate the message at 40,000 characters to match Slack
        and improve performance. RC doesn't specify a char limit.
        """
        logger = woodchips.get(LOGGER_NAME)

        rocketchat_message = ''.join(messages)[:40000]

        try:
            requests.post(rocketchat_url, json={'text': rocketchat_message})
            logger.info('Rocket Chat message sent!')
        except requests.exceptions.RequestException as rc_error:
            logger.error(f'Could not send Rocket Chat message: {rc_error}')
            raise requests.exceptions.RequestException(rc_error)

    @staticmethod
    def send_slack_message(messages: List[str], slack_token: str, slack_channel: str):
        """Send Slack messages via a bot.

        Slack truncates messages after 40,000 characters so
        we truncate there before sending the request.
        """
        logger = woodchips.get(LOGGER_NAME)

        slack_message = ''.join(messages)[:40000]
        slack_client = slack.WebClient(slack_token)

        try:
            slack_client.chat_postMessage(
                channel=slack_channel,
                text=slack_message,
            )
            logger.info('Slack message sent!')
        except slack.errors.SlackApiError as slack_error:
            logger.error(f'Could not send Slack message: {slack_error}')
            raise slack.errors.SlackApiError(slack_error.response["ok"], slack_error.response['error'])

    @staticmethod
    def prepare_pulls_message(pull_request: github.PullRequest.PullRequest) -> Tuple[str, str]:
        """Prepares a GitHub pull request message with a single pull request's data.
        This will then be appended to an array of messages.

        Slack & RocketChat can use the same format while Discord requires
        some tweaking.
        """
        # TODO: Check requested_reviewers array also
        if pull_request.assignees:
            users = discord_users = ''
            for assignee in pull_request.assignees:
                user = f"<{assignee.html_url}|{assignee.login}>"
                users += user + ' '
                discord_user = f"{assignee.login} (<{assignee.html_url}>)"
                discord_users += discord_user + ' '
        else:
            users = discord_users = 'NA'

        pull_request_body = pull_request.body if pull_request.body else ''
        description = (
            pull_request_body[:DESCRIPTION_MAX_LENGTH] + DESCRIPTION_CONTINUATION
            if len(pull_request_body) > DESCRIPTION_MAX_LENGTH
            else pull_request_body
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
    def prepare_issues_message(issue: Issue) -> Tuple[str, str]:
        """Prepares a GitHub issue message with a single issue's data.
        This will then be appended to an array of messages.

        Slack & RocketChat can use the same format while Discord requires
        some tweaking.
        """
        if issue.assignees:
            users = discord_users = ''
            for assignee in issue.assignees:
                user = f"<{assignee.html_url}|{assignee.login}>"
                users += user + ' '
                discord_user = f"{assignee.login} (<{assignee.html_url}>)"
                discord_users += discord_user + ' '
        else:
            users = discord_users = 'NA'

        issue_body = issue.body if issue.body else ''
        description = (
            issue_body[:DESCRIPTION_MAX_LENGTH] + DESCRIPTION_CONTINUATION
            if len(issue_body) > DESCRIPTION_MAX_LENGTH
            else issue_body
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
