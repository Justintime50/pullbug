from unittest.mock import patch

import pytest
import requests
import slack
from pullbug.messages import Messages


@patch('pullbug.messages.DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/channel_id/webhook_id')
@patch('pullbug.messages.LOGGER')
@patch('requests.post')
def test_discord_success(mock_request, mock_logger):
    message = 'mock message'
    Messages.send_discord_message([message])

    mock_request.assert_called_once_with(
        'https://discord.com/api/webhooks/channel_id/webhook_id', json={'content': message}
    )
    mock_logger.info.assert_called_once_with('Discord message sent!')


@patch('pullbug.messages.LOGGER')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_discord_exception(mock_request, mock_logger):
    message = 'mock message'
    with pytest.raises(requests.exceptions.RequestException):
        Messages.send_discord_message(message)

    mock_logger.error.assert_called_once_with('Could not send Discord message: mock-error')


@patch('pullbug.messages.ROCKET_CHAT_URL', 'http://mock-url.com')
@patch('pullbug.messages.LOGGER')
@patch('requests.post')
def test_rocket_chat_success(mock_request, mock_logger):
    message = 'mock message'
    Messages.send_rocketchat_message(message)

    mock_request.assert_called_once_with('http://mock-url.com', json={'text': message})
    mock_logger.info.assert_called_once_with('Rocket Chat message sent!')


@patch('pullbug.messages.LOGGER')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_rocket_chat_exception(mock_request, mock_logger):
    message = 'mock message'
    with pytest.raises(requests.exceptions.RequestException):
        Messages.send_rocketchat_message(message)

    mock_logger.error.assert_called_once_with('Could not send Rocket Chat message: mock-error')


@patch('pullbug.messages.SLACK_CHANNEL', 'mock-channel')
@patch('pullbug.messages.SLACK_BOT_TOKEN', '123')
@patch('pullbug.messages.LOGGER')
@patch('slack.WebClient.chat_postMessage')
def test_slack_success(mock_slack, mock_logger):
    message = 'mock message'
    Messages.send_slack_message(message)

    mock_slack.assert_called_once_with(channel='mock-channel', text=message)
    mock_logger.info.assert_called_once_with('Slack message sent!')


@patch('pullbug.messages.LOGGER')
@patch(
    'slack.WebClient.chat_postMessage',
    side_effect=slack.errors.SlackApiError(
        message='The request to the Slack API failed.', response={'ok': False, 'error': 'not_authed'}
    ),
)
def test_slack_exception(mock_slack, mock_logger):
    message = 'mock message'
    with pytest.raises(slack.errors.SlackApiError):
        Messages.send_slack_message(message)

    mock_logger.error.assert_called_once_with(
        "Could not send Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa
    )


def test_prepare_github_message(_mock_pull_request, _mock_user, _mock_repo):
    result, discord_result = Messages.prepare_github_message(_mock_pull_request, False, False, False)

    assert 'Pull Request' in result
    assert f'{_mock_pull_request["assignees"][0]["html_url"]}|{_mock_pull_request["assignees"][0]["login"]}' in result
    assert f'{_mock_pull_request["html_url"]}|{_mock_pull_request["title"]}' in result


def test_prepare_github_message_no_assignee(_mock_pull_request):
    _mock_pull_request['assignees'] = []
    result, discord_result = Messages.prepare_github_message(_mock_pull_request, False, False, False)

    assert '*Waiting on:* NA' in result


def test_prepare_gitlab_message(_mock_merge_request, _mock_url, _mock_user, _mock_repo):
    result, discord_result = Messages.prepare_gitlab_message(_mock_merge_request, False, False, False)

    assert 'Merge Request' in result
    assert (
        f'{_mock_merge_request["assignees"][0]["web_url"]}|{_mock_merge_request["assignees"][0]["username"]}' in result
    )
    assert f'{_mock_merge_request["web_url"]}|{_mock_merge_request["title"]}' in result


def test_prepare_gitlab_message_no_assignee(_mock_merge_request):
    _mock_merge_request['assignees'] = []
    result, discord_result = Messages.prepare_gitlab_message(_mock_merge_request, False, False, False)

    assert '*Waiting on:* NA' in result
