from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_token():
    mock_token = '123'

    return mock_token


@pytest.fixture
def mock_user():
    mock_user = 'mock-user'

    return mock_user


@pytest.fixture
def mock_github_context():
    mock_github_context = 'users'

    return mock_github_context


@pytest.fixture
def mock_github_state():
    mock_github_state = 'open'

    return mock_github_state


@pytest.fixture
def mock_repo():
    mock_repo = 'mock-repo'

    return mock_repo


@pytest.fixture
def mock_pull_request(mock_user, mock_repo):
    mock_pull_request = MagicMock()
    mock_pull_request.title = 'mock-pull-request'
    mock_pull_request.description = 'Mock description'
    mock_pull_request.body = 'Mock body of a pull request.'
    mock_pull_request.html_url = f'https://github.com/{mock_user}/{mock_repo}/pull/1'
    mock_pull_request.base.repo.name = 'mock-repo'
    mock_pull_request.base.repo.html_url = f'https://github.com/{mock_user}/{mock_repo}'

    return mock_pull_request


@pytest.fixture
def mock_issue(mock_user, mock_repo):
    mock_issue = MagicMock()
    mock_issue.title = 'mock-issue'
    mock_issue.description = 'Mock description'
    assignee = MagicMock()
    assignee.login = mock_user
    assignee.html_url = f'https://github.com/{mock_user}'
    mock_issue.assignees = [assignee]
    mock_issue.body = 'Mock body of an issue.'
    mock_issue.html_url = f'https://github.com/{mock_user}/{mock_repo}/issue/1'
    mock_issue.repository.name = 'mock-repo'
    mock_issue.repository.html_url = f'https://github.com/{mock_user}/{mock_repo}'

    return mock_issue


@pytest.fixture
def mock_url():
    mock_url = 'http://mock-url.com'

    return mock_url


@pytest.fixture
def mock_messages():
    mock_messages = ['mock message']

    return mock_messages


@pytest.fixture
def mock_channel():
    mock_channel = 'mock-channel'

    return mock_channel
