import mock
import pytest
import requests
from pullbug.github_bug import GithubBug


@pytest.fixture
def _mock_github_token():
    return '123'


@pytest.fixture
def _mock_user():
    return 'mock-user'


@pytest.fixture
def _mock_repo():
    mock_repo = {
        'name': 'mock-repo'
    }
    return mock_repo


@pytest.fixture
def _mock_pull_request(_mock_user, _mock_repo):
    mock_pull_request = {
        'title': 'mock-pull-request',
        'description': 'Mock description',
        'assignee': {
            'login': _mock_user,
            'html_url': f'https://github.com/{_mock_user}'
        },
        'body': 'Mock body of a pull request.',
        'html_url': f'https://github.com/{_mock_user}/{_mock_repo}/pull/1'
    }
    return mock_pull_request


@mock.patch('pullbug.github_bug.GITHUB_CONTEXT', 'users')
@mock.patch('pullbug.github_bug.GITHUB_OWNER', _mock_user)
@mock.patch('pullbug.github_bug.GITHUB_TOKEN', _mock_github_token)
@mock.patch('pullbug.github_bug.GITHUB_HEADERS')
@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get')
def test_get_repos_success(mock_request, mock_logger, mock_headers):
    # TODO: Mock this request better and assert additional values
    GithubBug.get_repos()
    mock_request.assert_called_once_with(
        f'https://api.github.com/users/{_mock_user}/repos',
        headers=mock_headers
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
@mock.patch('pullbug.github_bug.GITHUB_OWNER', _mock_user)
@mock.patch('pullbug.github_bug.GITHUB_TOKEN', _mock_github_token)
@mock.patch('pullbug.github_bug.GITHUB_HEADERS')
@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get')
def test_get_pull_requests_success(mock_request, mock_logger, mock_headers, _mock_repo):
    # TODO: Mock this request better and assert additional values
    mock_repos = [_mock_repo]
    result = GithubBug.get_pull_requests(mock_repos)
    mock_request.assert_called_once_with(
        f'https://api.github.com/repos/{_mock_user}/{_mock_repo["name"]}/pulls?state=open',
        headers=mock_headers
    )
    assert mock_logger.info.call_count == 2
    assert isinstance(result, list)


@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_pull_requests_exception(mock_request, mock_logger, _mock_repo):
    mock_repos = [_mock_repo]
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_pull_requests(mock_repos)
    mock_logger.warning.assert_called_once_with(
        f'Could not retrieve GitHub pull requests for {_mock_repo["name"]}: mock-error'
    )


@mock.patch('pullbug.github_bug.IGNORE_WIP', 'false')
@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_no_wip_in_title(mock_prepare_message, _mock_pull_request):
    mock_pull_requests = [_mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests)
    mock_prepare_message.assert_called_once_with(_mock_pull_request)


@mock.patch('pullbug.github_bug.IGNORE_WIP', 'false')
@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_wip_title(mock_prepare_message, _mock_pull_request):
    _mock_pull_request['title'] = 'wip: mock-pull-request'
    mock_pull_requests = [_mock_pull_request]
    result = GithubBug.iterate_pull_requests(mock_pull_requests)
    mock_prepare_message.assert_not_called()
    assert isinstance(result, str)


@mock.patch('pullbug.github_bug.IGNORE_WIP', 'true')
@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_wip_setting_included(mock_prepare_message, _mock_pull_request):
    mock_pull_requests = [_mock_pull_request]
    result = GithubBug.iterate_pull_requests(mock_pull_requests)
    mock_prepare_message.assert_not_called()
    assert isinstance(result, str)


def test_prepare_message(_mock_pull_request, _mock_user, _mock_repo):
    result = GithubBug.prepare_message(_mock_pull_request)
    assert 'Pull Request' in result
    assert f'{_mock_pull_request["assignee"]["html_url"]}|{_mock_pull_request["assignee"]["login"]}' in result
    assert f'{_mock_pull_request["html_url"]}|{_mock_pull_request["title"]}' in result


def test_prepare_message_no_assignee(_mock_pull_request):
    _mock_pull_request['assignee'] = None
    result = GithubBug.prepare_message(_mock_pull_request)
    assert '*Waiting on:* No assignee' in result
