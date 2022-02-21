from unittest.mock import MagicMock, patch

import pytest
import requests
import slack

from pullbug.messages import Message


@patch('logging.Logger.info')
@patch('requests.post')
def test_discord_success(mock_request, mock_logger, mock_url, mock_messages):
    Message.send_discord_message(mock_messages, mock_url)

    mock_request.assert_called_once_with(mock_url, json={'content': mock_messages[0]})
    mock_logger.assert_called_once_with('Discord message sent!')


@patch('logging.Logger.error')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_discord_exception(mock_request, mock_logger, mock_url, mock_messages):
    with pytest.raises(requests.exceptions.RequestException):
        Message.send_discord_message(mock_messages, mock_url)

    mock_logger.assert_called_once_with('Could not send Discord message: mock-error')


@patch('logging.Logger.info')
@patch('slack.WebClient.chat_postMessage')
def test_slack_success(mock_slack, mock_logger, mock_messages, mock_token, mock_channel):
    Message.send_slack_message(mock_messages, mock_token, mock_channel)

    mock_slack.assert_called_once_with(channel='mock-channel', text=mock_messages[0])
    mock_logger.assert_called_once_with('Slack message sent!')


@patch('logging.Logger.error')
@patch(
    'slack.WebClient.chat_postMessage',
    side_effect=slack.errors.SlackApiError(
        message='The request to the Slack API failed.', response={'ok': False, 'error': 'not_authed'}
    ),
)
def test_slack_exception(mock_slack, mock_logger, mock_messages, mock_token, mock_channel):
    with pytest.raises(slack.errors.SlackApiError):
        Message.send_slack_message(mock_messages, mock_token, mock_channel)

    mock_logger.assert_called_once_with(
        "Could not send Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa
    )


def test_prepare_pulls_message(mock_pull_request, mock_user, mock_repo):
    """Tests that we build user strings and messages correctly when present."""
    reviewer = MagicMock()
    reviewer.login = 'reviewer'
    reviewer.html_url = f'https://github.com/{mock_user}'
    reviewers = [reviewer]

    approved_reviewer = MagicMock()
    approved_reviewer.login = 'approved_reviewer'
    approved_reviewer.html_url = f'https://github.com/{mock_user}'
    approved_reviewers = [approved_reviewer]

    requested_changes_reviewer = MagicMock()
    requested_changes_reviewer.login = 'requested_changes_reviewer'
    requested_changes_reviewer.html_url = f'https://github.com/{mock_user}'
    requested_changes_reviewers = [requested_changes_reviewer]

    dismissed_reviewer = MagicMock()
    dismissed_reviewer.login = 'dismissed_reviewer'
    dismissed_reviewer.html_url = f'https://github.com/{mock_user}'
    dismissed_reviewers = [dismissed_reviewer]

    slack_message, discord_message = Message.prepare_pulls_message(
        mock_pull_request, reviewers, approved_reviewers, requested_changes_reviewers, dismissed_reviewers
    )

    # Slack message
    assert 'Pull Request' in slack_message
    assert f'{reviewer.html_url}|{reviewer.login}' in slack_message
    assert f'{mock_pull_request.html_url}|{mock_pull_request.title}' in slack_message

    # Discord message
    assert 'Pull Request' in discord_message
    assert f'{reviewer.login} (<{reviewer.html_url}>)' in discord_message
    assert f'{mock_pull_request.title} (<{mock_pull_request.html_url}>)' in discord_message


def test_prepare_pulls_message_same_reviewer(mock_pull_request, mock_user, mock_repo):
    """Ensures that when a user has requested changes, been dismissed, then approved, we filter those correctly."""
    reviewer = MagicMock()
    reviewer.login = 'reviewer'
    reviewer.html_url = f'https://github.com/{mock_user}'
    reviewers = [reviewer]

    slack_message, discord_message = Message.prepare_pulls_message(
        mock_pull_request, reviewers, reviewers, reviewers, reviewers
    )

    # Slack message
    assert 'Pull Request' in slack_message
    assert f'{reviewer.html_url}|{reviewer.login}' in slack_message
    assert f'{mock_pull_request.html_url}|{mock_pull_request.title}' in slack_message

    # Discord message
    assert 'Pull Request' in discord_message
    assert f'{reviewer.login} (<{reviewer.html_url}>)' in discord_message
    assert f'{mock_pull_request.title} (<{mock_pull_request.html_url}>)' in discord_message


def test_prepare_pulls_message_no_reviewers(mock_pull_request):
    """Tests that no user strings are generated when there are no reviewers."""
    mock_pull_request.requested_reviewers = []
    slack_message, discord_message = Message.prepare_pulls_message(mock_pull_request, [], [], [], [])

    assert '*Reviewers:* NA' in slack_message
    assert '*Reviewers:* NA' in discord_message


def test_prepare_issues_message(mock_issue, mock_user, mock_repo):
    slack_message, discord_message = Message.prepare_issues_message(mock_issue)

    # Slack message
    assert 'Issue' in slack_message
    assert f'{mock_issue.assignees[0].html_url}|{mock_issue.assignees[0].login}' in slack_message
    assert f'{mock_issue.html_url}|{mock_issue.title}' in slack_message

    # Discord message
    assert 'Issue' in discord_message
    assert f'{mock_issue.assignees[0].login} (<{mock_issue.assignees[0].html_url}>)' in discord_message
    assert f'{mock_issue.title} (<{mock_issue.html_url}>)' in discord_message


def test_prepare_issues_message_no_assignee(mock_issue):
    mock_issue.assignees = []
    slack_message, _ = Message.prepare_issues_message(mock_issue)

    assert '*Assigned to:* NA' in slack_message
