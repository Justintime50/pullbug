from unittest.mock import patch

import pytest
import requests
import slack
from pullbug.messages import Messages

MOCK_URL = 'http://mock-url.com'
MOCK_MESSAGES = ['mock message']
MOCK_TOKEN = '123'
MOCK_CHANNEL = 'mock-channel'


@patch('pullbug.messages.LOGGER')
@patch('requests.post')
def test_discord_success(mock_request, mock_logger):
    Messages.send_discord_message(MOCK_MESSAGES, MOCK_URL)

    mock_request.assert_called_once_with(MOCK_URL, json={'content': MOCK_MESSAGES[0]})
    mock_logger.info.assert_called_once_with('Discord message sent!')


@patch('pullbug.messages.LOGGER')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_discord_exception(mock_request, mock_logger):
    with pytest.raises(requests.exceptions.RequestException):
        Messages.send_discord_message(MOCK_MESSAGES, MOCK_URL)

    mock_logger.error.assert_called_once_with('Could not send Discord message: mock-error')


@patch('pullbug.messages.LOGGER')
@patch('requests.post')
def test_rocket_chat_success(mock_request, mock_logger):
    Messages.send_rocketchat_message(MOCK_MESSAGES, MOCK_URL)

    mock_request.assert_called_once_with(MOCK_URL, json={'text': MOCK_MESSAGES[0]})
    mock_logger.info.assert_called_once_with('Rocket Chat message sent!')


@patch('pullbug.messages.LOGGER')
@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_rocket_chat_exception(mock_request, mock_logger):
    with pytest.raises(requests.exceptions.RequestException):
        Messages.send_rocketchat_message(MOCK_MESSAGES, MOCK_URL)

    mock_logger.error.assert_called_once_with('Could not send Rocket Chat message: mock-error')


@patch('pullbug.messages.LOGGER')
@patch('slack.WebClient.chat_postMessage')
def test_slack_success(mock_slack, mock_logger):
    Messages.send_slack_message(MOCK_MESSAGES, MOCK_TOKEN, MOCK_CHANNEL)

    mock_slack.assert_called_once_with(channel='mock-channel', text=MOCK_MESSAGES[0])
    mock_logger.info.assert_called_once_with('Slack message sent!')


@patch('pullbug.messages.LOGGER')
@patch(
    'slack.WebClient.chat_postMessage',
    side_effect=slack.errors.SlackApiError(
        message='The request to the Slack API failed.', response={'ok': False, 'error': 'not_authed'}
    ),
)
def test_slack_exception(mock_slack, mock_logger):
    with pytest.raises(slack.errors.SlackApiError):
        Messages.send_slack_message(MOCK_MESSAGES, MOCK_TOKEN, MOCK_CHANNEL)

    mock_logger.error.assert_called_once_with(
        "Could not send Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa
    )


def test_prepare_pulls_message(mock_pull_request, mock_user, mock_repo):
    result, discord_result = Messages.prepare_pulls_message(mock_pull_request)

    # Message
    assert 'Pull Request' in result
    assert f'{mock_pull_request.assignees[0]["html_url"]}|{mock_pull_request.assignees[0]["login"]}' in result
    assert f'{mock_pull_request.html_url}|{mock_pull_request.title}' in result

    # Discord message
    # assert 'Pull Request' in discord_result
    # assert f'{mock_pull_request.assignees[0].html_url} (<{mock_pull_request.assignees[0].login}>)' in discord_result
    # assert f'{mock_pull_request.html_url} (<{mock_pull_request.title}>)' in discord_result


# def test_prepare_github_message_no_assignee(mock_pull_request):
#     mock_pull_request['assignees'] = []
#     result, discord_result = Messages.prepare_github_message(mock_pull_request, False, False, False)

#     assert '*Waiting on:* NA' in result
