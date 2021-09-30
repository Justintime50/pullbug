import pytest


@pytest.fixture
def _mock_github_token(scope='module'):
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
    return {'name': 'mock-repo'}


@pytest.fixture
def _mock_pull_request(_mock_user, _mock_repo):
    return {
        'title': 'mock-pull-request',
        'description': 'Mock description',
        'assignees': [
            {'login': _mock_user, 'html_url': f'https://github.com/{_mock_user}'},
        ],
        'body': 'Mock body of a pull request.',
        'html_url': f'https://github.com/{_mock_user}/{_mock_repo}/pull/1',
        'base': {'repo': {'name': 'mock-repo', 'html_url': f'https://github.com/{_mock_user}/{_mock_repo}'}},
    }


@pytest.fixture
def _mock_url():
    return 'http://mock-url.com'


class MockResponse:
    def __init__(self, json=None, text=None):
        self.json = json
        self.text = text
