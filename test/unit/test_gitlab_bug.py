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
def _mock_gitlab_scope():
    return 'all'


@pytest.fixture
def _mock_gitlab_state():
    return 'opened'


@pytest.fixture
def _mock_merge_request(_mock_user, _mock_repo, _mock_url):
    mock_merge_request = {
        'title': 'mock-pull-request',
        'description': 'Mock description',
        'assignees': [
            {
                'username': _mock_user,
                'web_url': f'https://github.com/{_mock_user}'
            }
        ],
        'body': 'Mock body of a pull request.',
        'web_url': f'{_mock_url}/{_mock_user}/{_mock_repo}/pull/1'
    }
    return mock_merge_request


@mock.patch('pullbug.gitlab_bug.GITLAB_API_KEY', '123')
@mock.patch('pullbug.gitlab_bug.GITLAB_API_URL', _mock_url)
@mock.patch('pullbug.messages.Messages.rocketchat')
@mock.patch('pullbug.messages.Messages.slack')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
@mock.patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests')
@mock.patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@mock.patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@mock.patch('pullbug.gitlab_bug.LOGGER')
@mock.patch('requests.get')
def test_run_no_slack_or_rocketchat_messages(mock_request, mock_logger, mock_headers,
                                             mock_get_merge_requests, mock_iterate_merge_requests,
                                             mock_prepare_message, mock_slack, mock_rocketchat):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, False)
    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_slack.assert_not_called()
    mock_rocketchat.assert_not_called()


@mock.patch('pullbug.gitlab_bug.GITLAB_API_KEY', '123')
@mock.patch('pullbug.gitlab_bug.GITLAB_API_URL', _mock_url)
@mock.patch('pullbug.messages.Messages.rocketchat')
@mock.patch('pullbug.messages.Messages.slack')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
@mock.patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests')
@mock.patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@mock.patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@mock.patch('pullbug.gitlab_bug.LOGGER')
@mock.patch('requests.get')
def test_run_slack_message(mock_request, mock_logger, mock_headers,
                           mock_get_merge_requests, mock_iterate_merge_requests,
                           mock_prepare_message, mock_slack, mock_rocketchat):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, True, False)
    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_slack.assert_called_once()
    mock_rocketchat.assert_not_called()


@mock.patch('pullbug.gitlab_bug.GITLAB_API_KEY', '123')
@mock.patch('pullbug.gitlab_bug.GITLAB_API_URL', _mock_url)
@mock.patch('pullbug.messages.Messages.rocketchat')
@mock.patch('pullbug.messages.Messages.slack')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
@mock.patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests')
@mock.patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests')
@mock.patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@mock.patch('pullbug.gitlab_bug.LOGGER')
@mock.patch('requests.get')
def test_run_rocketchat_message(mock_request, mock_logger, mock_headers,
                                mock_get_merge_requests, mock_iterate_merge_requests,
                                mock_prepare_message, mock_slack, mock_rocketchat):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, True)
    mock_logger.info.assert_called()
    mock_get_merge_requests.assert_called_once()
    mock_iterate_merge_requests.assert_called()
    mock_slack.assert_not_called()
    mock_rocketchat.assert_called_once()


@mock.patch('pullbug.gitlab_bug.GITLAB_API_KEY', '123')
@mock.patch('pullbug.gitlab_bug.GITLAB_API_URL', _mock_url)
@mock.patch('pullbug.messages.Messages.rocketchat')
@mock.patch('pullbug.messages.Messages.slack')
@mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
@mock.patch('pullbug.gitlab_bug.GitlabBug.iterate_merge_requests')
@mock.patch('pullbug.gitlab_bug.GitlabBug.get_merge_requests', return_value=[])
@mock.patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@mock.patch('pullbug.gitlab_bug.LOGGER')
@mock.patch('requests.get')
def test_run_no_returned_merge_requests(mock_request, mock_logger, mock_headers,
                                        mock_get_merge_requests, mock_iterate_merge_requests,
                                        mock_prepare_message, mock_slack, mock_rocketchat):
    GitlabBug.run(_mock_gitlab_scope, _mock_gitlab_state, False, False, False)
    mock_logger.info.assert_called_with('No merge requests are available from GitLab.')
    mock_iterate_merge_requests.assert_not_called()
    mock_slack.assert_not_called()
    mock_rocketchat.assert_not_called()


@ mock.patch('pullbug.gitlab_bug.GITLAB_API_KEY', '123')
@ mock.patch('pullbug.gitlab_bug.GITLAB_API_URL', _mock_url)
@ mock.patch('pullbug.gitlab_bug.GITLAB_HEADERS')
@ mock.patch('pullbug.gitlab_bug.LOGGER')
@ mock.patch('requests.get')
def test_get_merge_requests_success(mock_request, mock_logger, mock_headers):
    # TODO: Mock this request better and assert additional values
    GitlabBug.get_merge_requests(_mock_gitlab_scope, _mock_gitlab_state)
    mock_request.assert_called_once_with(
        f'{_mock_url}/merge_requests?scope={_mock_gitlab_scope}&state={_mock_gitlab_state}&per_page=100',
        headers=mock_headers
    )
    assert mock_logger.info.call_count == 2


@ mock.patch('pullbug.gitlab_bug.LOGGER')
@ mock.patch('requests.get', side_effect=requests.exceptions.RequestException('mock-error'))
def test_get_repos_exception(mock_request, mock_logger):
    with pytest.raises(requests.exceptions.RequestException):
        GitlabBug.get_merge_requests(_mock_gitlab_scope, _mock_gitlab_state)
    mock_logger.warning.assert_called_once_with(
        'Could not retrieve GitLab merge requests: mock-error'
    )


@ mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
def test_iterate_merge_requests_wip_title(mock_prepare_message, _mock_merge_request):
    _mock_merge_request['title'] = 'wip: mock-merge-request'
    mock_merge_requests = [_mock_merge_request]
    GitlabBug.iterate_merge_requests(mock_merge_requests, True)
    mock_prepare_message.assert_called_once()


@ mock.patch('pullbug.gitlab_bug.GitlabBug.prepare_message')
def test_iterate_merge_requests_wip_setting_absent(mock_prepare_message, _mock_merge_request):
    _mock_merge_request['title'] = 'wip: mock-merge-request'
    mock_merge_requests = [_mock_merge_request]
    GitlabBug.iterate_merge_requests(mock_merge_requests, False)
    mock_prepare_message.assert_not_called()


def test_prepare_message(_mock_merge_request, _mock_url, _mock_user, _mock_repo):
    result = GitlabBug.prepare_message(_mock_merge_request)
    assert 'Merge Request' in result
    assert f'{_mock_merge_request["assignees"][0]["web_url"]}|{_mock_merge_request["assignees"][0]["username"]}' in result  # noqa
    assert f'{_mock_merge_request["web_url"]}|{_mock_merge_request["title"]}' in result


def test_prepare_message_no_assignees_data(_mock_merge_request):
    _mock_merge_request['assignees'][0]['username'] = None
    result = GitlabBug.prepare_message(_mock_merge_request)
    assert '*Waiting on:* No assignee' in result


def test_prepare_message_no_assignee(_mock_merge_request):
    _mock_merge_request['assignees'] = []
    result = GitlabBug.prepare_message(_mock_merge_request)
    assert '*Waiting on:* No assignee' in result
