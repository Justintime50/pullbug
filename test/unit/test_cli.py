import pytest
import mock
from pullbug.cli import PullBug, PullBugCLI   # noqa


@mock.patch('pullbug.cli.LOGGER')
def test_throw_missing_error(mock_logger):
    with pytest.raises(ValueError):
        PullBug.throw_missing_error('GITHUB_TOKEN')
    mock_logger.critical.assert_called_once_with(
        'No GITHUB_TOKEN set. Please correct and try again.'
    )
