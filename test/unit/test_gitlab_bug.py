import mock
import pytest
import requests
from pullbug.gitlab_bug import GitlabBug


@pytest.fixture
def _mock_user():
    mock_user = {
        'name': 'mock-user'
    }
    return mock_user


@pytest.fixture
def _mock_repo():
    mock_repo = {
        'name': 'mock-repo'
    }
    return mock_repo


@pytest.fixture
def _mock_url():
    return 'http://mock-url.com'


@pytest.fixture
def _mock_merge_request(_mock_user, _mock_repo, _mock_url):
    mock_merge_request = {
        'title': 'mock-pull-request',
        'description': 'Mock description',
        'assignee': {
            'username': _mock_user,
            'web_url': f'https://github.com/{_mock_user}'
        },
        'body': 'Mock body of a pull request.',
        'web_url': f'{_mock_url}/{_mock_user}/{_mock_repo}/pull/1'
    }
    return mock_merge_request


@mock.patch('pullbug.gitlab_bug.GITLAB_API_KEY', '123')
@mock.patch('pullbug.gitlab_bug.GITLAB_API_URL', _mock_url)
@mock.patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@mock.patch('pullbug.gitlab_bug.LOGGER')
@mock.patch('requests.get')
def test_get_merge_requests_success(mock_request, mock_logger, mock_headers):
    # TODO: Mock this request better and assert additional values
    GitlabBug.get_merge_requests()
    mock_request.assert_called_once_with(
        f'{_mock_url}/merge_requests?scope=all&state=opened',
        headers=mock_headers
    )
    assert mock_logger.info.call_count == 2


@mock.patch('pullbug.gitlab_bug.LOGGER')
@mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_repos_exception(mock_request, mock_logger):
    with pytest.raises(requests.exceptions.RequestException):
        GitlabBug.get_merge_requests()
    mock_logger.warning.assert_called_once_with(
        'Could not retrieve GitLab merge requests: mock-error'
    )


@mock.patch('pullbug.gitlab_bug.IGNORE_WIP', 'false')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
def test_iterate_merge_requests_no_wip_in_title(mock_prepare_message, _mock_merge_request):
    mock_merge_requests = [_mock_merge_request]
    GitlabBug.iterate_merge_requests(mock_merge_requests)
    mock_prepare_message.assert_called_once_with(_mock_merge_request)


@mock.patch('pullbug.gitlab_bug.IGNORE_WIP', 'false')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
def test_iterate_merge_requests_wip_title(mock_prepare_message, _mock_merge_request):
    _mock_merge_request['title'] = 'wip: mock-merge-request'
    mock_merge_requests = [_mock_merge_request]
    result = GitlabBug.iterate_merge_requests(mock_merge_requests)
    mock_prepare_message.assert_not_called()
    assert isinstance(result, str)


@mock.patch('pullbug.gitlab_bug.IGNORE_WIP', 'true')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
def test_iterate_merge_requests_wip_setting_included(mock_prepare_message, _mock_merge_request):
    mock_merge_requests = [_mock_merge_request]
    result = GitlabBug.iterate_merge_requests(mock_merge_requests)
    mock_prepare_message.assert_not_called()
    assert isinstance(result, str)


def test_prepare_message(_mock_merge_request, _mock_url, _mock_user, _mock_repo):
    result = GitlabBug.prepare_message(_mock_merge_request)
    assert 'Merge Request' in result
    assert f'{_mock_merge_request["assignee"]["web_url"]}|{_mock_merge_request["assignee"]["username"]}' in result
    assert f'{_mock_merge_request["web_url"]}|{_mock_merge_request["title"]}' in result


def test_prepare_message_no_assignee(_mock_merge_request):
    _mock_merge_request['assignee'] = None
    result = GitlabBug.prepare_message(_mock_merge_request)
    assert '*Waiting on:* No assignee' in result
