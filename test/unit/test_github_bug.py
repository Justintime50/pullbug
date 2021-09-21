from test.conftest import MockResponse
from unittest.mock import patch

import pytest
import requests
from pullbug.github_bug import GithubBug

GITHUB_TOKEN = '123'


@patch('pullbug.cli.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.github_bug.GithubBug.get_pull_requests')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('pullbug.github_bug.LOGGER')
def test_run_success(mock_logger, mock_get_repos, mock_pull_request):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, False, False)

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_logger.info.assert_called()


@patch('pullbug.cli.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.github_bug.GithubBug.iterate_pull_requests')
@patch('pullbug.github_bug.GithubBug.get_pull_requests', return_value=[])
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('pullbug.github_bug.LOGGER')
def test_run_no_pull_requests(mock_logger, mock_get_repos, mock_pull_request, mock_iterate_pull_requests):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, False, False)

    mock_get_repos.assert_called_once()
    mock_iterate_pull_requests.assert_not_called()
    mock_logger.info.assert_called()


@patch('pullbug.cli.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.messages.Messages.send_discord_message')
@patch('pullbug.github_bug.GithubBug.get_pull_requests')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('pullbug.github_bug.LOGGER')
def test_run_with_discord(mock_logger, mock_get_repos, mock_pull_request, mock_discord):
    GithubBug.run('mock-owner', 'open', 'orgs', False, True, False, False)

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_discord.assert_called_once()
    mock_logger.info.assert_called()


@patch('pullbug.cli.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.messages.Messages.send_slack_message')
@patch('pullbug.github_bug.GithubBug.get_pull_requests')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('pullbug.github_bug.LOGGER')
def test_run_with_slack(mock_logger, mock_get_repos, mock_pull_request, mock_slack):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, True, False)

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_slack.assert_called_once()
    mock_logger.info.assert_called()


@patch('pullbug.cli.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.messages.Messages.send_rocketchat_message')
@patch('pullbug.github_bug.GithubBug.get_pull_requests')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('pullbug.github_bug.LOGGER')
def test_run_with_rocketchat(mock_logger, mock_get_repos, mock_pull_request, mock_rocketchat):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, False, True)

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_rocketchat.assert_called_once()
    mock_logger.info.assert_called()


@patch('pullbug.github_bug.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.github_bug.GITHUB_HEADERS')
@patch('pullbug.github_bug.LOGGER')
@patch('requests.get')
def test_get_repos_success(mock_request, mock_logger, mock_headers, _mock_user, _mock_github_context):
    # TODO: Mock this request better and assert additional values
    GithubBug.get_repos(_mock_user, _mock_github_context)

    mock_request.assert_called_once_with(
        f'https://api.github.com/{_mock_github_context}/{_mock_user}/repos?per_page=100', headers=mock_headers
    )
    assert mock_logger.info.call_count == 2


@patch('pullbug.github_bug.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.github_bug.GITHUB_HEADERS')
@patch('pullbug.github_bug.LOGGER')
@patch('requests.get', return_value=MockResponse(text='Not Found'))
def test_get_repos_value_exception(mock_request, mock_logger, mock_headers, _mock_user, _mock_github_context):
    with pytest.raises(ValueError):
        GithubBug.get_repos(_mock_user, _mock_github_context)

    mock_logger.error.assert_called_once_with(
        f'Could not retrieve GitHub repos due to bad parameter: {_mock_user} | {_mock_github_context}.'
    )


@patch('pullbug.github_bug.LOGGER')
@patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_repos_requests_exception(mock_request, mock_logger, _mock_user, _mock_github_context):
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_repos(_mock_user, _mock_github_context)

    mock_logger.error.assert_called_once_with('Could not retrieve GitHub repos: mock-error')


@patch('pullbug.github_bug.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.github_bug.GITHUB_HEADERS')
@patch('pullbug.github_bug.LOGGER')
@patch('requests.get')
def test_get_pull_requests_success(mock_request, mock_logger, mock_headers, _mock_repo, _mock_github_state, _mock_user):
    # TODO: Mock this request better and assert additional values
    mock_repos = [_mock_repo]
    result = GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)

    mock_request.assert_called_once_with(
        f'https://api.github.com/repos/{_mock_user}/{_mock_repo["name"]}/pulls?state={_mock_github_state}&per_page=100',
        headers=mock_headers,
    )
    assert mock_logger.info.call_count == 2
    # assert len(result) > 0  # TODO: Assert a mock value actually makes it in
    assert isinstance(result, list)


@patch('pullbug.github_bug.GITHUB_TOKEN', GITHUB_TOKEN)
@patch('pullbug.github_bug.GITHUB_HEADERS')
@patch('pullbug.github_bug.LOGGER')
@patch('requests.get', return_value=None)
def test_get_pull_requests_success_no_pull_requests(
    mock_request, mock_logger, mock_headers, _mock_repo, _mock_github_state, _mock_user
):  # noqa
    # TODO: Mock this request better and assert additional values
    mock_repos = [_mock_repo]
    result = GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)

    mock_request.assert_called_once_with(
        f'https://api.github.com/repos/{_mock_user}/{_mock_repo["name"]}/pulls?state={_mock_github_state}&per_page=100',
        headers=mock_headers,
    )
    assert isinstance(result, list)
    assert len(result) == 0


@patch('pullbug.github_bug.LOGGER')
@patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_pull_requests_request_exception(mock_request, mock_logger, _mock_repo, _mock_user, _mock_github_state):
    mock_repos = [_mock_repo]
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)

    mock_logger.error.assert_called_once_with(
        f'Could not retrieve GitHub pull requests for {_mock_repo["name"]}: mock-error'
    )


@patch('pullbug.github_bug.LOGGER')
@patch('requests.get', side_effect=TypeError('mock-error'))
def test_get_pull_requests_type_error_exception(mock_request, mock_logger, _mock_repo, _mock_user, _mock_github_state):
    mock_repos = [_mock_repo]
    with pytest.raises(TypeError):
        GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)

    mock_logger.error.assert_called_once_with(
        f'Could not retrieve GitHub pull requests due to bad parameter: {_mock_user} | {_mock_github_state}.'
    )


@patch('pullbug.github_bug.Messages.prepare_github_message', return_value=[['mock-message'], ['mock-message']])
def test_iterate_pull_requests_wip_title(mock_prepare_message, _mock_pull_request):
    _mock_pull_request['title'] = 'wip: mock-pull-request'
    mock_pull_requests = [_mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests, True, False, False, False)

    mock_prepare_message.assert_called_once()


@patch('pullbug.github_bug.Messages.prepare_github_message')
def test_iterate_pull_requests_wip_setting_absent(mock_prepare_message, _mock_pull_request):
    _mock_pull_request['title'] = 'wip: mock-pull-request'
    mock_pull_requests = [_mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests, False, False, False, False)

    mock_prepare_message.assert_not_called()
