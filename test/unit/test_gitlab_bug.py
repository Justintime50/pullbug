from test.conftest import MockResponse
from unittest.mock import patch

import pytest
import requests
from pullbug.gitlab_bug import GitlabBug

GITLAB_API_KEY = '123'
MOCK_URL = 'http://mock-url.com'


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.messages.Messages.send_rocketchat_message')
@patch('pullbug.messages.Messages.send_slack_message')
@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message')
@patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests', return_value=[['mock-message'], ['mock-message']])
@patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get')
def test_run_no_slack_or_rocketchat_messages(
    mock_request,
    mock_logger,
    mock_headers,
    mock_get_merge_requests,
    mock_iterate_merge_requests,
    mock_prepare_message,
    mock_slack,
    mock_rocketchat,
    _mock_gitlab_scope,
    _mock_gitlab_state,
):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, False, False)

    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_slack.assert_not_called()
    mock_rocketchat.assert_not_called()


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.messages.Messages.send_discord_message')
@patch('pullbug.messages.Messages.send_slack_message')
@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message')
@patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests', return_value=[['mock-message'], ['mock-message']])
@patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get')
def test_run_discord_message(
    mock_request,
    mock_logger,
    mock_headers,
    mock_get_merge_requests,
    mock_iterate_merge_requests,
    mock_prepare_message,
    mock_slack,
    mock_discord,
    _mock_gitlab_scope,
    _mock_gitlab_state,
):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, True, False, False)

    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_discord.assert_called_once()


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.messages.Messages.send_rocketchat_message')
@patch('pullbug.messages.Messages.send_slack_message')
@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message')
@patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests', return_value=[['mock-message'], ['mock-message']])
@patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get')
def test_run_slack_message(
    mock_request,
    mock_logger,
    mock_headers,
    mock_get_merge_requests,
    mock_iterate_merge_requests,
    mock_prepare_message,
    mock_slack,
    mock_rocketchat,
    _mock_gitlab_scope,
    _mock_gitlab_state,
):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, True, False)

    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_slack.assert_called_once()


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.messages.Messages.send_rocketchat_message')
@patch('pullbug.messages.Messages.send_slack_message')
@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message')
@patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests', return_value=[['mock-message'], ['mock-message']])
@patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get')
def test_run_rocketchat_message(
    mock_request,
    mock_logger,
    mock_headers,
    mock_get_merge_requests,
    mock_iterate_merge_requests,
    mock_prepare_message,
    mock_slack,
    mock_rocketchat,
    _mock_gitlab_scope,
    _mock_gitlab_state,
):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, False, True)

    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_slack.assert_not_called()


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.messages.Messages.send_rocketchat_message')
@patch('pullbug.messages.Messages.send_slack_message')
@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message')
@patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests', return_value=[['mock-message'], ['mock-message']])
@patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests', return_value=[])
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get')
def test_run_no_returned_merge_requests(
    mock_request,
    mock_logger,
    mock_headers,
    mock_get_merge_requests,
    mock_iterate_merge_requests,
    mock_prepare_message,
    mock_slack,
    mock_rocketchat,
    _mock_gitlab_scope,
    _mock_gitlab_state,
):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, False, False)

    mock_logger.info.assert_called_with('No merge requests are available from GitLab.')
    mock_iterate_merge_requests.assert_not_called()
    mock_slack.assert_not_called()
    mock_rocketchat.assert_not_called()


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get')
def test_get_merge_requests_success(
    mock_request, mock_logger, mock_headers, _mock_gitlab_scope, _mock_gitlab_state, _mock_url
):
    # TODO: Mock this request better and assert additional values
    GitlabBug.get_merge_requests(_mock_gitlab_scope, _mock_gitlab_state)

    mock_request.assert_called_once_with(
        f'{_mock_url}/merge_requests?scope={_mock_gitlab_scope}&state={_mock_gitlab_state}&per_page=100',
        headers=mock_headers,
    )
    assert mock_logger.info.call_count == 2


@patch('pullbug.gitlab_bug.GITLAB_API_KEY', GITLAB_API_KEY)
@patch('pullbug.gitlab_bug.GITLAB_API_URL', MOCK_URL)
@patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get', return_value=MockResponse(text='does not have a valid value'))
def test_get_merge_value_exception(
    mock_request, mock_logger, mock_headers, _mock_gitlab_scope, _mock_gitlab_state, _mock_url
):
    with pytest.raises(ValueError):
        GitlabBug.get_merge_requests(_mock_gitlab_scope, _mock_gitlab_state)

    mock_logger.error.assert_called_once_with(
        f'Could not retrieve GitLab merge requests due to bad parameter: {_mock_gitlab_scope} | {_mock_gitlab_state}.'
    )


@patch('pullbug.gitlab_bug.LOGGER')
@patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_repos_exception(mock_request, mock_logger, _mock_gitlab_scope, _mock_gitlab_state):
    with pytest.raises(requests.exceptions.RequestException):
        GitlabBug.get_merge_requests(_mock_gitlab_scope, _mock_gitlab_state)

    mock_logger.error.assert_called_once_with('Could not retrieve GitLab merge requests: mock-error')


@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message', return_value=[['mock-message'], ['mock-message']])
def test_iterate_merge_requests_wip_title(mock_prepare_message, _mock_merge_request):
    _mock_merge_request['title'] = 'wip: mock-merge-request'
    mock_merge_requests = [_mock_merge_request]
    GitlabBug.iterate_merge_requests(mock_merge_requests, True, False, False, False)

    mock_prepare_message.assert_called_once()


@patch('pullbug.gitlab_bug.Messages.prepare_gitlab_message')
def test_iterate_merge_requests_wip_setting_absent(mock_prepare_message, _mock_merge_request):
    _mock_merge_request['title'] = 'wip: mock-merge-request'
    mock_merge_requests = [_mock_merge_request]
    GitlabBug.iterate_merge_requests(mock_merge_requests, False, False, False, False)

    mock_prepare_message.assert_not_called()
