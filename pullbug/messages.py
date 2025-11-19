import math
from typing import (
    List,
    Tuple,
    Union,
)

import requests
import slack_sdk
import woodchips
from github import (
    Issue,
    NamedUser,
    PullRequest,
    Team,
)


LOGGER_NAME = "pullbug"
DESCRIPTION_CONTINUATION = "..."
DESCRIPTION_MAX_LENGTH = 120
TIMEOUT = 30


def send_discord_message(messages: List[str], discord_url: str):
    """Send a Discord message.

    Discord has a hard limit of 2000 characters per
    As such, we break up the messages into batches, allow for
    breathing room, and send each batch of messages separately.
    """
    logger = woodchips.get(LOGGER_NAME)

    num_of_messages = len(messages)
    # The message size of ~300 characters means we can send 6 messages per request plus some buffer room
    max_messages_per_batch = 6
    i = 1
    new_cutoff = max_messages_per_batch
    old_cutoff = 0

    while i <= math.ceil(num_of_messages / max_messages_per_batch):
        i += 1
        batch_message = "".join(messages[old_cutoff:new_cutoff])
        new_cutoff += max_messages_per_batch
        old_cutoff += max_messages_per_batch
        try:
            requests.post(
                discord_url,
                json={"content": batch_message},
                timeout=TIMEOUT,
            )
            logger.info("Discord message sent!")
        except requests.exceptions.RequestException as discord_error:
            logger.error(f"Could not send Discord message: {discord_error}")
            raise requests.exceptions.RequestException(discord_error)


def send_slack_message(messages: List[str], slack_token: str, slack_channel: str):
    """Send Slack messages via a bot.

    Slack truncates messages after 40,000 characters so
    we truncate there before sending the request.
    """
    logger = woodchips.get(LOGGER_NAME)

    message_max_length = 40000
    slack_message = "".join(messages)[:message_max_length]
    slack_client = slack_sdk.WebClient(slack_token)

    try:
        slack_client.chat_postMessage(
            channel=slack_channel,
            text=slack_message,
        )
        logger.info("Slack message sent!")
    except slack_sdk.errors.SlackApiError as slack_error:
        logger.error(f"Could not send Slack message: {slack_error}")
        raise slack_sdk.errors.SlackApiError(slack_error.response["ok"], slack_error.response["error"])


def prepare_pulls_message(
    pull_request: PullRequest.PullRequest,
    reviewers: List[Union[NamedUser.NamedUser, Team.Team]],
    users_who_approved: List[NamedUser.NamedUser],
    users_who_requested_changes: List[NamedUser.NamedUser],
    users_who_were_dismissed: List[NamedUser.NamedUser],
    disable_descriptions: bool = False,
) -> Tuple[str, str]:
    """Prepares a GitHub pull request message with a single pull request's data.
    This will then be appended to an array of messages.

    Slack and Discord each have slightly different formatting required, both messages are returned here.
    """
    pull_request_body = pull_request.body if pull_request.body else ""
    description_message_element = ""

    if disable_descriptions is False:
        description = (
            pull_request_body[:DESCRIPTION_MAX_LENGTH] + DESCRIPTION_CONTINUATION
            if len(pull_request_body) > DESCRIPTION_MAX_LENGTH
            else pull_request_body
        )
        description_message_element = f"\n*Description:* {description}"

    slack_reviewers_string = ""
    discord_reviewers_string = ""

    if users_who_approved:
        slack_users_who_approved = []
        discord_users_who_approved = []

        for user in users_who_approved:
            slack_users_who_approved.append(_create_slack_user_link(user))
            discord_users_who_approved.append(_create_discord_user_link(user))

        if slack_users_who_approved:
            slack_reviewers_string += f"  :white_check_mark: {', '.join(set(slack_users_who_approved))};"
            discord_reviewers_string += f"  :white_check_mark: {', '.join(set(discord_users_who_approved))};"

    if users_who_requested_changes:
        slack_users_who_requested_changes = []
        discord_users_who_requested_changes = []

        for user in users_who_requested_changes:
            if user not in users_who_approved:
                slack_users_who_requested_changes.append(_create_slack_user_link(user))
                discord_users_who_requested_changes.append(_create_discord_user_link(user))

        if slack_users_who_requested_changes:
            slack_reviewers_string += f"  :no_entry: {', '.join(set(slack_users_who_requested_changes))};"
            discord_reviewers_string += f"  :no_entry: {', '.join(set(discord_users_who_requested_changes))};"

    if users_who_were_dismissed:
        slack_users_who_were_dismissed = []
        discord_users_who_were_dismissed = []

        for user in users_who_were_dismissed:
            if user not in users_who_approved:
                slack_users_who_were_dismissed.append(_create_slack_user_link(user))
                discord_users_who_were_dismissed.append(_create_discord_user_link(user))

        if slack_users_who_were_dismissed:
            slack_reviewers_string += f"  :eyes: {', '.join(set(slack_users_who_were_dismissed))};"
            discord_reviewers_string += f"  :eyes: {', '.join(set(discord_users_who_were_dismissed))};"

    if reviewers:
        slack_reviewers = []
        discord_reviewers = []

        for reviewer in reviewers:
            if isinstance(reviewer, NamedUser.NamedUser):
                slack_reviewers.append(_create_slack_user_link(reviewer))
                discord_reviewers.append(_create_discord_user_link(reviewer))
            elif isinstance(reviewer, Team.Team):
                slack_reviewers.append(_create_slack_team_link(reviewer))
                discord_reviewers.append(_create_discord_team_link(reviewer))

        if slack_reviewers:
            slack_reviewers_string += f"  :timer_clock: {', '.join(set(slack_reviewers))};"
            discord_reviewers_string += f"  :timer: {', '.join(set(discord_reviewers))};"

    slack_message = (
        f"\n:arrow_heading_up: *Pull Request:* {_create_slack_object_link(pull_request)}"
        f"\n*Repo:* <{pull_request.base.repo.html_url}|{pull_request.base.repo.name}>"
        f"\n*Author:* <{pull_request.user.html_url}|{pull_request.user.login}>"
        f"{description_message_element}"
        f"\n*Reviewers:*{slack_reviewers_string if slack_reviewers_string else ' NA'}\n"
    )

    discord_message = (
        f"\n:arrow_heading_up: **Pull Request:** {_create_discord_object_link(pull_request)}"
        f"\n**Repo:** [{pull_request.base.repo.name}]({pull_request.base.repo.html_url})"
        f"\n**Author:** [{pull_request.user.login}]({pull_request.user.html_url})"
        f"{description_message_element}"
        f"\n*Reviewers:*{discord_reviewers_string if discord_reviewers_string else ' NA'}\n"
    )

    return slack_message, discord_message


def prepare_issues_message(issue: Issue.Issue, disable_descriptions: bool = False) -> Tuple[str, str]:
    """Prepares a GitHub issue message with a single issue's data.
    This will then be appended to an array of messages.

    Slack and Discord each have slightly different formatting required, both messages are returned here.
    """
    issue_body = issue.body if issue.body else ""
    description_message_element = ""

    if disable_descriptions is False:
        description = (
            issue_body[:DESCRIPTION_MAX_LENGTH] + DESCRIPTION_CONTINUATION
            if len(issue_body) > DESCRIPTION_MAX_LENGTH
            else issue_body
        )
        description_message_element = f"\n*Description:* {description}"

    if issue.assignees:
        slack_users = []
        discord_users = []
        for assignee in issue.assignees:
            slack_users.append(_create_slack_user_link(assignee))
            discord_users.append(_create_discord_user_link(assignee))
    else:
        slack_users = ["NA"]
        discord_users = ["NA"]

    slack_message = (
        f"\n:exclamation: *Issue:* {_create_slack_object_link(issue)}"
        f"\n*Repo:* <{issue.repository.html_url}|{issue.repository.name}>"
        f"{description_message_element}"
        f"\n*Assigned to:* {', '.join(slack_users)}\n"
    )

    discord_message = (
        f"\n:exclamation: **Issue:** {_create_discord_object_link(issue)}"
        f"\n**Repo:** [{issue.repository.name}]({issue.repository.html_url})"
        f"{description_message_element}"
        f"\n**Assigned to:** {', '.join(discord_users)}\n"
    )

    return slack_message, discord_message


def _create_slack_user_link(user: NamedUser.NamedUser) -> str:
    """Creates a Slack user name/url combo to be used in messages."""
    return f"<{user.html_url}|{user.login}>"


def _create_discord_user_link(user: NamedUser.NamedUser) -> str:
    """Creates a Discord user name/url combo to be used in messages."""
    return f"[{user.login}]({user.html_url})"


def _create_slack_object_link(object: Union[PullRequest.PullRequest, Issue.Issue]) -> str:
    """Creates a Slack object name/url combo to be used in messages."""
    return f"<{object.html_url}|{object.title}>"


def _create_discord_object_link(object: Union[PullRequest.PullRequest, Issue.Issue]) -> str:
    """Creates a Discord object name/url combo to be used in messages."""
    return f"[{object.title}]({object.html_url})"


def _create_slack_team_link(team: Team.Team) -> str:
    """Creates a Slack team name/url combo to be used in messages."""
    # TODO: The URL is not populating currently from PyGithub
    return team.name


def _create_discord_team_link(team: Team.Team) -> str:
    """Creates a Discord team name/url combo to be used in messages."""
    # TODO: The URL is not populating currently from PyGithub
    return team.name
