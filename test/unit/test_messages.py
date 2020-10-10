import mock
import pytest
import requests
import slack
from pullbug.messages import Messages


@mock.patch('pullbug.messages.ROCKET_CHAT_URL', 'http://mock-url.com')
@mock.patch('pullbug.messages.LOGGER')
@mock.patch('requests.post')
def test_rocket_chat_success(mock_request, mock_logger):
    message = 'mock message'
    Messages.rocketchat(message)
    mock_request.assert_called_once_with(
        'http://mock-url.com', data={'text': message}
    )
    mock_logger.info.assert_called_once_with('Rocket Chat message sent!')


@mock.patch('pullbug.messages.LOGGER')
@mock.patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
def test_rocket_chat_exception(mock_request, mock_logger):
    message = 'mock message'
    with pytest.raises(requests.exceptions.RequestException):
        Messages.rocketchat(message)
    mock_logger.error.assert_called_once_with(
        'Could not send Rocket Chat message: mock-error'
    )


@mock.patch('pullbug.messages.SLACK_CHANNEL', 'mock-channel')
@mock.patch('pullbug.messages.SLACK_BOT_TOKEN', '123')
@mock.patch('pullbug.messages.LOGGER')
@mock.patch('slack.WebClient.chat_postMessage')
def test_slack_success(mock_slack, mock_logger):
    message = 'mock message'
    Messages.slack(message)
    mock_slack.assert_called_once_with(channel='mock-channel', text=message)
    mock_logger.info.assert_called_once_with('Slack message sent!')


@mock.patch('pullbug.messages.LOGGER')
@mock.patch('slack.WebClient.chat_postMessage',
            side_effect=slack.errors.SlackApiError(
                message='The request to the Slack API failed.',
                response={'ok': False, 'error': 'not_authed'}
            ))
def test_slack_exception(mock_slack, mock_logger):
    message = 'mock message'
    with pytest.raises(slack.errors.SlackApiError):
        Messages.slack(message)
    mock_logger.error.assert_called_once_with(
        "Could not send Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa
    )
