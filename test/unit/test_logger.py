from unittest.mock import mock_open, patch

from pullbug import PullBugLogger


@patch('pullbug.logger.LOG_PATH', 'test/mock-dir')
@patch('pullbug.logger.LOG_FILE', './test/test.log')
@patch('os.makedirs')
@patch('pullbug.github_bug.LOGGER')
def test_setup_logging(mock_logger, mock_make_dirs):
    with patch('builtins.open', mock_open()):
        PullBugLogger._setup_logging(mock_logger)

    mock_make_dirs.assert_called_once()
    mock_logger.setLevel.assert_called()
    mock_logger.addHandler.assert_called()


@patch('os.makedirs')
@patch('pullbug.github_bug.LOGGER')
def test_setup_logging_dir_exists(mock_logger, mock_make_dirs):
    with patch('builtins.open', mock_open()):
        PullBugLogger._setup_logging(mock_logger)

    mock_make_dirs.assert_not_called()
    mock_logger.setLevel.assert_called()
    mock_logger.addHandler.assert_called()
