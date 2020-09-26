import mock
import pytest
import requests
from pullbug.github_bug import GithubBug


@mock.patch('pullbug.github_bug.GITHUB_CONTEXT', 'users')
@mock.patch('pullbug.github_bug.GITHUB_OWNER', 'mock-user')
@mock.patch('pullbug.github_bug.GITHUB_TOKEN', '123')
@mock.patch('pullbug.github_bug.HEADERS', {'mock-headers': True})
@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get')
def test_get_repos_success(mock_request, mock_logger):
    # TODO: Mock this request better and assert additional values
    GithubBug.get_repos()
    mock_request.assert_called_once_with(
        'https://api.github.com/users/mock-user/repos',
        headers={'mock-headers': True}
    )
    assert mock_logger.info.call_count == 2


@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_repos_exception(mock_request, mock_logger):
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_repos()
    mock_logger.warning.assert_called_once_with(
        'Could not retrieve GitHub repos: mock-error'
    )


@mock.patch('pullbug.github_bug.GITHUB_STATE', 'open')
@mock.patch('pullbug.github_bug.GITHUB_OWNER', 'mock-user')
@mock.patch('pullbug.github_bug.GITHUB_TOKEN', '123')
@mock.patch('pullbug.github_bug.HEADERS', {'mock-headers': True})
@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get')
def test_get_pull_requests_success(mock_request, mock_logger):
    # TODO: Mock this request better and assert additional values
    mock_repo = {'name': 'mock-repo'}
    mock_repos = [mock_repo]
    GithubBug.get_pull_requests(mock_repos)
    mock_request.assert_called_once_with(
        f'https://api.github.com/repos/mock-user/{mock_repo["name"]}/pulls?state=open',
        headers={'mock-headers': True}
    )
    assert mock_logger.info.call_count == 2


@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_pull_requests_exception(mock_request, mock_logger):
    mock_repo = {'name': 'mock-repo'}
    mock_repos = [mock_repo]
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_pull_requests(mock_repos)
    mock_logger.warning.assert_called_once_with(
        f'Could not retrieve GitHub pull requests for {mock_repo["name"]}: mock-error'
    )


@mock.patch('pullbug.github_bug.IGNORE_WIP', 'false')
@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_no_wip(mock_prepare_message):
    mock_pull_request = {'title': 'mock-pull-request'}
    mock_pull_requests = [mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests)
    mock_prepare_message.assert_called_once_with(mock_pull_request)


@mock.patch('pullbug.github_bug.IGNORE_WIP', 'false')
@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_wip_title(mock_prepare_message):
    mock_pull_request = {'title': 'wip: mock-pull-request'}
    mock_pull_requests = [mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests)
    mock_prepare_message.assert_not_called()


@mock.patch('pullbug.github_bug.IGNORE_WIP', 'true')
@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_wip_included(mock_prepare_message):
    mock_pull_request = {'title': 'mock-pull-request'}
    mock_pull_requests = [mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests)
    mock_prepare_message.assert_not_called()
