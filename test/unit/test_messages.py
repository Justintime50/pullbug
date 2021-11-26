from unittest.mock import patch

import pytest
import requests
import slack

from pullbug.messages import Messages


@patch('logging.Logger.info')
@patch('requests.post')
def test_discord_success(mock_request, mock_logger, mock_url, mock_messages):
    Messages.send_discord_message(mock_messages, mock_url)

    mock_request.assert_called_once_with(mock_url, json={'content': mock_messages[0]})
    mock_logger.assert_called_once_with('Discord message sent!')


@patch('logging.Logger.error')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_discord_exception(mock_request, mock_logger, mock_url, mock_messages):
    with pytest.raises(requests.exceptions.RequestException):
        Messages.send_discord_message(mock_messages, mock_url)

    mock_logger.assert_called_once_with('Could not send Discord message: mock-error')


@patch('logging.Logger.info')
@patch('requests.post')
def test_rocket_chat_success(mock_request, mock_logger, mock_url, mock_messages):
    Messages.send_rocketchat_message(mock_messages, mock_url)

    mock_request.assert_called_once_with(mock_url, json={'text': mock_messages[0]})
    mock_logger.assert_called_once_with('Rocket Chat message sent!')


@patch('logging.Logger.error')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_rocket_chat_exception(mock_request, mock_logger, mock_url, mock_messages):
    with pytest.raises(requests.exceptions.RequestException):
        Messages.send_rocketchat_message(mock_messages, mock_url)

    mock_logger.assert_called_once_with('Could not send Rocket Chat message: mock-error')


@patch('logging.Logger.info')
@patch('slack.WebClient.chat_postMessage')
def test_slack_success(mock_slack, mock_logger, mock_messages, mock_token, mock_channel):
    Messages.send_slack_message(mock_messages, mock_token, mock_channel)

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
        Messages.send_slack_message(mock_messages, mock_token, mock_channel)

    mock_logger.assert_called_once_with(
        "Could not send Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa
    )


def test_prepare_pulls_message(mock_pull_request, mock_user, mock_repo):
    result, discord_result = Messages.prepare_pulls_message(mock_pull_request)

    # Message
    assert 'Pull Request' in result
    assert f'{mock_pull_request.assignees[0].html_url}|{mock_pull_request.assignees[0].login}' in result
    assert f'{mock_pull_request.html_url}|{mock_pull_request.title}' in result

    # Discord message
    assert 'Pull Request' in discord_result
    assert f'{mock_pull_request.assignees[0].login} (<{mock_pull_request.assignees[0].html_url}>)' in discord_result
    assert f'{mock_pull_request.title} (<{mock_pull_request.html_url}>)' in discord_result


def test_prepare_pulls_message_no_assignee(mock_pull_request):
    mock_pull_request.assignees = []
    result, discord_result = Messages.prepare_pulls_message(mock_pull_request)

    assert '*Waiting on:* NA' in result


def test_prepare_issues_message(mock_issue, mock_user, mock_repo):
    result, discord_result = Messages.prepare_issues_message(mock_issue)

    # Message
    assert 'Issue' in result
    assert f'{mock_issue.assignees[0].html_url}|{mock_issue.assignees[0].login}' in result
    assert f'{mock_issue.html_url}|{mock_issue.title}' in result

    # Discord message
    assert 'Issue' in discord_result
    assert f'{mock_issue.assignees[0].login} (<{mock_issue.assignees[0].html_url}>)' in discord_result
    assert f'{mock_issue.title} (<{mock_issue.html_url}>)' in discord_result


def test_prepare_issues_message_no_assignee(mock_issue):
    mock_issue.assignees = []
    result, discord_result = Messages.prepare_issues_message(mock_issue)

    assert '*Assigned to:* NA' in result
