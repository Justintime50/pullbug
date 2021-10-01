from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_github_token():
    mock_github_token = '123'

    return mock_github_token


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
    mock_pull_request.assignees = MagicMock()
    mock_pull_request.assignees = [
        {
            'login': mock_user,
            'html_url': f'https://github.com/{mock_user}',
        }
    ]
    mock_pull_request.body = 'Mock body of a pull request.'
    mock_pull_request.html_url = f'https://github.com/{mock_user}/{mock_repo}/pull/1'
    mock_pull_request.base.repo.name = 'mock-repo'
    mock_pull_request.base.repo.html_url = f'https://github.com/{mock_user}/{mock_repo}'

    return mock_pull_request


@pytest.fixture
def mock_url():
    mock_url = 'http://mock-url.com'

    return mock_url


class MockResponse:
    def __init__(self, json=None, text=None):
        self.json = json
        self.text = text
