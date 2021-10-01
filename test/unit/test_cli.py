from unittest.mock import patch

import pytest
from pullbug.cli import PullBugCli


@patch('pullbug.cli.LOGGER')
def test_throw_missing_error(mock_logger):
    with pytest.raises(ValueError):
        PullBugCli.throw_missing_error('GITHUB_TOKEN')

    mock_logger.critical.assert_called_once_with('No GITHUB_TOKEN set. Please correct and try again.')


@patch('pullbug.cli.GITHUB_TOKEN', '123')
@patch('pullbug.cli.PullBugCli.run_missing_checks')
@patch('pullbug.github_bug.GithubBug.run')
@patch('pullbug.cli.LOGGER')
def test_run_with_github_arg(mock_logger, mock_github, mock_missing_checks):
    PullBugCli.run(True, False, False, False, False, False, 'mock-owner', 'open', 'orgs', 'opened', 'all')

    mock_missing_checks.assert_called_once_with(True, False, False, False, False)
    mock_github.assert_called_once()
    mock_logger.info.assert_called()


@patch('pullbug.cli.GITHUB_TOKEN', '123')
@patch('pullbug.cli.LOGGER')
def test_run_missing_checks_no_discord_webhook_url(mock_logger):
    message = 'No DISCORD_WEBHOOK_URL set. Please correct and try again.'
    with pytest.raises(ValueError):
        PullBugCli.run_missing_checks(True, False, True, False, False)

    mock_logger.critical.assert_called_once_with(message)


@patch('pullbug.cli.LOGGER')
def test_run_missing_checks_no_github_token(mock_logger):
    message = 'No GITHUB_TOKEN set. Please correct and try again.'
    with pytest.raises(ValueError):
        PullBugCli.run_missing_checks(True, False, False, False, False)

    mock_logger.critical.assert_called_once_with(message)


@patch('pullbug.cli.GITHUB_TOKEN', '123')
@patch('pullbug.cli.LOGGER')
def test_run_missing_checks_no_slack_bot_token(mock_logger):
    message = 'No SLACK_BOT_TOKEN set. Please correct and try again.'
    with pytest.raises(ValueError):
        PullBugCli.run_missing_checks(True, False, False, True, False)

    mock_logger.critical.assert_called_once_with(message)


@patch('pullbug.cli.SLACK_BOT_TOKEN', '123')
@patch('pullbug.cli.GITHUB_TOKEN', '123')
@patch('pullbug.cli.LOGGER')
def test_run_missing_checks_no_slack_channel(mock_logger):
    message = 'No SLACK_CHANNEL set. Please correct and try again.'
    with pytest.raises(ValueError):
        PullBugCli.run_missing_checks(True, False, False, True, False)

    mock_logger.critical.assert_called_once_with(message)


@patch('pullbug.cli.GITHUB_TOKEN', '123')
@patch('pullbug.cli.LOGGER')
def test_run_missing_checks_no_rocket_chat_url(mock_logger):
    message = 'No ROCKET_CHAT_URL set. Please correct and try again.'
    with pytest.raises(ValueError):
        PullBugCli.run_missing_checks(True, False, False, False, True)

    mock_logger.critical.assert_called_once_with(message)


@patch('pullbug.cli.ROCKET_CHAT_URL', 'http://mock-url.com')
@patch('pullbug.cli.SLACK_CHANNEL', 'mock-channel')
@patch('pullbug.cli.SLACK_BOT_TOKEN', '123')
@patch('pullbug.cli.GITHUB_TOKEN', '123')
@patch('pullbug.cli.LOGGER')
def test_run_missing_checks_no_errors(mock_logger):
    PullBugCli.run_missing_checks(True, False, False, False, True)

    mock_logger.critical.assert_not_called()
