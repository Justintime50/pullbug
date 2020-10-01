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
def _mock_github_context():
    return 'users'


@pytest.fixture
def _mock_github_state():
    return 'open'


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
        'assignees': [
            {
                'login': _mock_user,
                'html_url': f'https://github.com/{_mock_user}'
            },
        ],
        'body': 'Mock body of a pull request.',
        'html_url': f'https://github.com/{_mock_user}/{_mock_repo}/pull/1'
    }
    return mock_pull_request


@mock.patch('pullbug.cli.GITHUB_TOKEN', '123')
@mock.patch('pullbug.github_bug.GithubBug.get_pull_requests')
@mock.patch('pullbug.github_bug.GithubBug.get_repos')
@mock.patch('pullbug.github_bug.LOGGER')
def test_run_success(mock_logger, mock_get_repos, mock_pull_request):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, False)
    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_logger.info.assert_called()


@mock.patch('pullbug.cli.GITHUB_TOKEN', '123')
@mock.patch('pullbug.github_bug.GithubBug.iterate_pull_requests')
@mock.patch('pullbug.github_bug.GithubBug.get_pull_requests', return_value=[])
@mock.patch('pullbug.github_bug.GithubBug.get_repos')
@mock.patch('pullbug.github_bug.LOGGER')
def test_run_no_pull_requests(mock_logger, mock_get_repos, mock_pull_request, mock_iterate_pull_requests):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, False)
    mock_get_repos.assert_called_once()
    mock_iterate_pull_requests.assert_not_called()
    mock_logger.info.assert_called()


@mock.patch('pullbug.cli.GITHUB_TOKEN', '123')
@mock.patch('pullbug.messages.Messages.slack')
@mock.patch('pullbug.github_bug.GithubBug.get_pull_requests')
@mock.patch('pullbug.github_bug.GithubBug.get_repos')
@mock.patch('pullbug.github_bug.LOGGER')
def test_run_with_slack(mock_logger, mock_get_repos, mock_pull_request, mock_slack):
    GithubBug.run('mock-owner', 'open', 'orgs', False, True, False)
    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_slack.assert_called_once()
    mock_logger.info.assert_called()


@mock.patch('pullbug.cli.GITHUB_TOKEN', '123')
@mock.patch('pullbug.messages.Messages.rocketchat')
@mock.patch('pullbug.github_bug.GithubBug.get_pull_requests')
@mock.patch('pullbug.github_bug.GithubBug.get_repos')
@mock.patch('pullbug.github_bug.LOGGER')
def test_run_with_rocketchat(mock_logger, mock_get_repos, mock_pull_request, mock_rocketchat):
    GithubBug.run('mock-owner', 'open', 'orgs', False, False, True)
    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_rocketchat.assert_called_once()
    mock_logger.info.assert_called()


@mock.patch('pullbug.github_bug.GITHUB_TOKEN', _mock_github_token)
@mock.patch('pullbug.github_bug.GITHUB_HEADERS')
@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get')
def test_get_repos_success(mock_request, mock_logger, mock_headers, _mock_user, _mock_github_context):
    # TODO: Mock this request better and assert additional values
    GithubBug.get_repos(_mock_user, _mock_github_context)
    mock_request.assert_called_once_with(
        f'https://api.github.com/{_mock_github_context}/{_mock_user}/repos?per_page=100',
        headers=mock_headers
    )
    assert mock_logger.info.call_count == 2


@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_repos_exception(mock_request, mock_logger, _mock_user, _mock_github_context):
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_repos(_mock_user, _mock_github_context)
    mock_logger.warning.assert_called_once_with(
        'Could not retrieve GitHub repos: mock-error'
    )


@mock.patch('pullbug.github_bug.GITHUB_TOKEN', _mock_github_token)
@mock.patch('pullbug.github_bug.GITHUB_HEADERS')
@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get')
def test_get_pull_requests_success(mock_request, mock_logger, mock_headers, _mock_repo, _mock_github_state):
    # TODO: Mock this request better and assert additional values
    mock_repos = [_mock_repo]
    result = GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)
    mock_request.assert_called_once_with(
        f'https://api.github.com/repos/{_mock_user}/{_mock_repo["name"]}/pulls?state={_mock_github_state}&per_page=100',
        headers=mock_headers
    )
    assert mock_logger.info.call_count == 2
    assert isinstance(result, list)


@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_pull_requests_request_exception(mock_request, mock_logger, _mock_repo):
    mock_repos = [_mock_repo]
    with pytest.raises(requests.exceptions.RequestException):
        GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)
    mock_logger.warning.assert_called_once_with(
        f'Could not retrieve GitHub pull requests for {_mock_repo["name"]}: mock-error'
    )


@mock.patch('pullbug.github_bug.LOGGER')
@mock.patch('requests.get', side_effect=TypeError('mock-error'))
def test_get_pull_requests_type_error_exception(mock_request, mock_logger, _mock_repo):
    mock_repos = [_mock_repo]
    with pytest.raises(TypeError):
        GithubBug.get_pull_requests(mock_repos, _mock_user, _mock_github_state)
    mock_logger.warning.assert_called_once_with(
        f'Could not retrieve GitHub pull requests due to bad parameter: {_mock_user} | {_mock_github_state}.'
    )


@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_wip_title(mock_prepare_message, _mock_pull_request):
    _mock_pull_request['title'] = 'wip: mock-pull-request'
    mock_pull_requests = [_mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests, True)
    mock_prepare_message.assert_called_once()


@mock.patch('pullbug.github_bug.GithubBug.prepare_message')
def test_iterate_pull_requests_wip_setting_absent(mock_prepare_message, _mock_pull_request):
    _mock_pull_request['title'] = 'wip: mock-pull-request'
    mock_pull_requests = [_mock_pull_request]
    GithubBug.iterate_pull_requests(mock_pull_requests, False)
    mock_prepare_message.assert_not_called()


def test_prepare_message(_mock_pull_request, _mock_user, _mock_repo):
    result = GithubBug.prepare_message(_mock_pull_request)
    assert 'Pull Request' in result
    assert f'{_mock_pull_request["assignees"][0]["html_url"]}|{_mock_pull_request["assignees"][0]["login"]}' in result
    assert f'{_mock_pull_request["html_url"]}|{_mock_pull_request["title"]}' in result


def test_prepare_message_no_assignees_data(_mock_pull_request):
    _mock_pull_request['assignees'][0]['login'] = None
    result = GithubBug.prepare_message(_mock_pull_request)
    assert '*Waiting on:* No assignee' in result


def test_prepare_message_no_assignee(_mock_pull_request):
    _mock_pull_request['assignees'] = []
    result = GithubBug.prepare_message(_mock_pull_request)
    assert '*Waiting on:* No assignee' in result
