from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
import requests
import slack_sdk
from github import (
    NamedUser,
    Team,
)

from pullbug.messages import (
    prepare_issues_message,
    prepare_pulls_message,
    send_discord_message,
    send_slack_message,
)


@patch("logging.Logger.info")
@patch("requests.post")
def test_discord_success(mock_request, mock_logger, mock_url, mock_messages):
    """Tests that we can send a Discord message."""
    send_discord_message(mock_messages, mock_url)

    mock_request.assert_called_once_with(mock_url, json={"content": mock_messages[0]}, timeout=30)
    mock_logger.assert_called_once_with("Discord message sent!")


@patch("logging.Logger.error")
@patch("requests.post", side_effect=requests.exceptions.RequestException("mock-error"))
def test_discord_exception(mock_request, mock_logger, mock_url, mock_messages):
    """Tests that we log errors when sending Discord messages."""
    with pytest.raises(requests.exceptions.RequestException):
        send_discord_message(mock_messages, mock_url)

    mock_logger.assert_called_once_with("Could not send Discord message: mock-error")


@patch("logging.Logger.info")
@patch("slack_sdk.WebClient.chat_postMessage")
def test_slack_success(mock_slack, mock_logger, mock_messages, mock_token, mock_channel):
    """Tests that we can send a Slack message."""
    send_slack_message(mock_messages, mock_token, mock_channel)

    mock_slack.assert_called_once_with(channel="mock-channel", text=mock_messages[0])
    mock_logger.assert_called_once_with("Slack message sent!")


@patch("logging.Logger.error")
@patch(
    "slack_sdk.WebClient.chat_postMessage",
    side_effect=slack_sdk.errors.SlackApiError(
        message="The request to the Slack API failed.", response={"ok": False, "error": "not_authed"}
    ),
)
def test_slack_exception(mock_slack, mock_logger, mock_messages, mock_token, mock_channel):
    """Tests that we log errors when sending Slack messages."""
    with pytest.raises(slack_sdk.errors.SlackApiError):
        send_slack_message(mock_messages, mock_token, mock_channel)

    mock_logger.assert_called_once_with(
        "Could not send Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa
    )


def test_prepare_pulls_message(mock_pull_request, mock_user, mock_repo):
    """Tests that we build all user strings and messages correctly when present."""
    reviewer = MagicMock(spec=NamedUser.NamedUser)
    reviewer.login = "reviewer"
    reviewer.html_url = f"https://github.com/{mock_user}"

    team = MagicMock(spec=Team.Team)
    team.name = "team"

    reviewers = [reviewer, team]

    approved_reviewer = MagicMock(spec=NamedUser.NamedUser)
    approved_reviewer.login = "approved_reviewer"
    approved_reviewer.html_url = f"https://github.com/{mock_user}"
    approved_reviewers = [approved_reviewer]

    requested_changes_reviewer = MagicMock(spec=NamedUser.NamedUser)
    requested_changes_reviewer.login = "requested_changes_reviewer"
    requested_changes_reviewer.html_url = f"https://github.com/{mock_user}"
    requested_changes_reviewers = [requested_changes_reviewer]

    dismissed_reviewer = MagicMock(spec=NamedUser.NamedUser)
    dismissed_reviewer.login = "dismissed_reviewer"
    dismissed_reviewer.html_url = f"https://github.com/{mock_user}"
    dismissed_reviewers = [dismissed_reviewer]

    slack_message, discord_message = prepare_pulls_message(
        pull_request=mock_pull_request,
        reviewers=reviewers,
        users_who_approved=approved_reviewers,
        users_who_requested_changes=requested_changes_reviewers,
        users_who_were_dismissed=dismissed_reviewers,
    )

    # Slack message
    assert "Pull Request" in slack_message
    assert "Description" in slack_message
    assert f"{reviewer.html_url}|{reviewer.login}" in slack_message
    assert team.name in slack_message
    assert f"{approved_reviewer.html_url}|{approved_reviewer.login}" in slack_message
    assert f"{requested_changes_reviewer.html_url}|{requested_changes_reviewer.login}" in slack_message
    assert f"{dismissed_reviewer.html_url}|{dismissed_reviewer.login}" in slack_message
    assert f"{mock_pull_request.html_url}|{mock_pull_request.title}" in slack_message

    # Discord message
    assert "Pull Request" in discord_message
    assert "Description" in discord_message
    assert f"[{reviewer.login}]({reviewer.html_url})" in discord_message
    assert team.name in discord_message
    assert f"[{approved_reviewer.login}]({approved_reviewer.html_url})" in discord_message
    assert f"[{requested_changes_reviewer.login}]({requested_changes_reviewer.html_url})" in discord_message
    assert f"[{dismissed_reviewer.login}]({dismissed_reviewer.html_url})" in discord_message
    assert f"[{mock_pull_request.title}]({mock_pull_request.html_url})" in discord_message


def test_prepare_pulls_message_same_reviewer(mock_pull_request, mock_user, mock_repo):
    """Ensures that when a user has requested changes, been dismissed, then approved, we filter those correctly."""
    reviewer = MagicMock(spec=NamedUser.NamedUser)
    reviewer.login = "reviewer"
    reviewer.html_url = f"https://github.com/{mock_user}"
    reviewers = [reviewer]

    slack_message, discord_message = prepare_pulls_message(
        pull_request=mock_pull_request,
        reviewers=reviewers,
        users_who_approved=reviewers,
        users_who_requested_changes=reviewers,
        users_who_were_dismissed=reviewers,
    )

    # Slack message
    assert "Pull Request" in slack_message
    assert f"{reviewer.html_url}|{reviewer.login}" in slack_message
    assert f"{mock_pull_request.html_url}|{mock_pull_request.title}" in slack_message

    # Discord message
    assert "Pull Request" in discord_message
    assert f"[{reviewer.login}]({reviewer.html_url})" in discord_message
    assert f"[{mock_pull_request.title}]({mock_pull_request.html_url})" in discord_message


def test_prepare_pulls_message_no_reviewers(mock_pull_request):
    """Tests that no user strings are generated when there are no reviewers."""
    mock_pull_request.requested_reviewers = []
    slack_message, discord_message = prepare_pulls_message(
        pull_request=mock_pull_request,
        reviewers=[],
        users_who_approved=[],
        users_who_requested_changes=[],
        users_who_were_dismissed=[],
    )

    assert "*Reviewers:* NA" in slack_message
    assert "*Reviewers:* NA" in discord_message


def test_prepare_pulls_message_disabled_description(mock_pull_request, mock_user, mock_repo):
    """Tests that we build all user strings and messages correctly when descriptions are disabled."""
    reviewer = MagicMock(spec=NamedUser.NamedUser)
    reviewer.login = "reviewer"
    reviewer.html_url = f"https://github.com/{mock_user}"

    team = MagicMock(spec=Team.Team)
    team.name = "team"

    reviewers = [reviewer, team]

    approved_reviewer = MagicMock(spec=NamedUser.NamedUser)
    approved_reviewer.login = "approved_reviewer"
    approved_reviewer.html_url = f"https://github.com/{mock_user}"
    approved_reviewers = [approved_reviewer]

    requested_changes_reviewer = MagicMock(spec=NamedUser.NamedUser)
    requested_changes_reviewer.login = "requested_changes_reviewer"
    requested_changes_reviewer.html_url = f"https://github.com/{mock_user}"
    requested_changes_reviewers = [requested_changes_reviewer]

    dismissed_reviewer = MagicMock(spec=NamedUser.NamedUser)
    dismissed_reviewer.login = "dismissed_reviewer"
    dismissed_reviewer.html_url = f"https://github.com/{mock_user}"
    dismissed_reviewers = [dismissed_reviewer]

    slack_message, discord_message = prepare_pulls_message(
        pull_request=mock_pull_request,
        reviewers=reviewers,
        users_who_approved=approved_reviewers,
        users_who_requested_changes=requested_changes_reviewers,
        users_who_were_dismissed=dismissed_reviewers,
        disable_descriptions=True,
    )

    # Slack message
    assert "Pull Request" in slack_message
    assert "Description" not in slack_message
    assert f"{reviewer.html_url}|{reviewer.login}" in slack_message
    assert team.name in slack_message
    assert f"{approved_reviewer.html_url}|{approved_reviewer.login}" in slack_message
    assert f"{requested_changes_reviewer.html_url}|{requested_changes_reviewer.login}" in slack_message
    assert f"{dismissed_reviewer.html_url}|{dismissed_reviewer.login}" in slack_message
    assert f"{mock_pull_request.html_url}|{mock_pull_request.title}" in slack_message

    # Discord message
    assert "Pull Request" in discord_message
    assert "Description" not in discord_message
    assert f"[{reviewer.login}]({reviewer.html_url})" in discord_message
    assert team.name in discord_message
    assert f"[{approved_reviewer.login}]({approved_reviewer.html_url})" in discord_message
    assert f"[{requested_changes_reviewer.login}]({requested_changes_reviewer.html_url})" in discord_message
    assert f"[{dismissed_reviewer.login}]({dismissed_reviewer.html_url})" in discord_message
    assert f"[{mock_pull_request.title}]({mock_pull_request.html_url})" in discord_message


def test_prepare_issues_message(mock_issue, mock_user, mock_repo):
    """Tests that we build the issue message strings correctly when there is an assignee."""
    slack_message, discord_message = prepare_issues_message(mock_issue)

    # Slack message
    assert "Issue" in slack_message
    assert "Description" in slack_message
    assert f"{mock_issue.assignees[0].html_url}|{mock_issue.assignees[0].login}" in slack_message
    assert f"{mock_issue.html_url}|{mock_issue.title}" in slack_message

    # Discord message
    assert "Issue" in discord_message
    assert "Description" in discord_message
    assert f"[{mock_issue.assignees[0].login}]({mock_issue.assignees[0].html_url})" in discord_message
    assert f"[{mock_issue.title}]({mock_issue.html_url})" in discord_message


def test_prepare_issues_message_no_assignee(mock_issue):
    """Tests that we build the issue message string correctly when there is no assignee."""
    mock_issue.assignees = []
    slack_message, _ = prepare_issues_message(mock_issue)

    assert "*Assigned to:* NA" in slack_message


def test_prepare_issues_message_disable_descriptions(mock_issue, mock_user, mock_repo):
    """Tests that we build the issue message strings correctly when descriptions are disabled."""
    slack_message, discord_message = prepare_issues_message(issue=mock_issue, disable_descriptions=True)

    # Slack message
    assert "Issue" in slack_message
    assert "Description" not in slack_message
    assert f"{mock_issue.assignees[0].html_url}|{mock_issue.assignees[0].login}" in slack_message
    assert f"{mock_issue.html_url}|{mock_issue.title}" in slack_message

    # Discord message
    assert "Issue" in discord_message
    assert "Description" not in discord_message
    assert f"[{mock_issue.assignees[0].login}]({mock_issue.assignees[0].html_url})" in discord_message
    assert f"[{mock_issue.title}]({mock_issue.html_url})" in discord_message
