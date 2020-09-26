import mock
from pullbug import PullBugLogger


@mock.patch('pullbug.logger.LOG_PATH', 'test/mock-dir')
@mock.patch('pullbug.logger.LOG_FILE', './test/test.log')
@mock.patch('os.makedirs')
@mock.patch('pullbug.github_bug.LOGGER')
def test_setup_logger(mock_logger, mock_make_dirs):
    with mock.patch('builtins.open', mock.mock_open()):
        PullBugLogger.setup_logging(mock_logger)
    mock_make_dirs.assert_called_once()
    mock_logger.setLevel.assert_called()
    mock_logger.addHandler.assert_called()
