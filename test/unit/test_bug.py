from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from pullbug.bug import Pullbug


@patch("pullbug.bug.Pullbug.send_messages")
@patch("pullbug.bug.Pullbug.get_pull_requests")
@patch("pullbug.bug.Pullbug.get_repos")
@patch("logging.Logger.info")
def test_run_pull_requests(mock_logger, mock_get_repos, mock_pull_request, mock_send_messages):
    Pullbug(
        github_owner="justintime50",
        github_token="123",
        github_context="users",
        pulls=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_logger.assert_called()
    mock_send_messages.assert_called_once()


@patch("pullbug.bug.Pullbug.get_pull_requests", return_value=[])
@patch("pullbug.bug.Pullbug.get_repos")
@patch("logging.Logger.info")
def test_run_no_pull_requests(mock_logger, mock_get_repos, mock_pull_request):
    Pullbug(
        github_owner="justintime50",
        github_token="123",
        github_context="users",
        pulls=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    assert mock_logger.call_count == 4


@patch("pullbug.bug.Pullbug.send_messages")
@patch("pullbug.bug.Pullbug.get_issues")
@patch("pullbug.bug.Pullbug.get_repos")
@patch("logging.Logger.info")
def test_run_issues(mock_logger, mock_get_repos, mock_issues, mock_send_messages):
    Pullbug(
        github_owner="justintime50",
        github_token="123",
        github_context="users",
        issues=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_issues.assert_called_once()
    mock_logger.assert_called()
    mock_send_messages.assert_called_once()


@patch("pullbug.bug.Pullbug.get_issues", return_value=[])
@patch("pullbug.bug.Pullbug.get_repos")
@patch("logging.Logger.info")
def test_run_no_issues(mock_logger, mock_get_repos, mock_issues):
    Pullbug(
        github_owner="justintime50",
        github_token="123",
        github_context="users",
        issues=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_issues.assert_called_once()
    assert mock_logger.call_count == 4


@patch("woodchips.Logger")
def test_setup_logger(mock_logger):
    Pullbug(
        github_owner="justintime50",
    ).setup_logger()

    mock_logger.assert_called_once()


@pytest.mark.parametrize(
    "pulls, issues, github_token, discord, discord_url, slack, slack_token, slack_channel",
    [
        # No pulls (side-effect of testing no github_token)
        (False, False, None, False, False, False, False, False),
        # Discord but no url
        (True, False, "123", True, False, False, False, False),
        # Slack but no token
        (True, False, "123", False, False, True, False, False),
        # Slack, token, but no channel
        (True, False, "123", False, False, True, "123", False),
    ],
)
@patch("pullbug.bug.Pullbug.get_issues")
@patch("pullbug.bug.Pullbug.get_repos")
@patch("logging.Logger.critical")
def test_run_missing_required_cli_params(
    mock_logger,
    mock_get_repos,
    mock_issues,
    pulls,
    issues,
    github_token,
    discord,
    discord_url,
    slack,
    slack_token,
    slack_channel,
):
    with pytest.raises(ValueError):
        Pullbug(
            github_owner="justintime50",
            github_token=github_token,
            pulls=pulls,
            issues=issues,
            discord=discord,
            discord_url=discord_url,
            slack=slack,
            slack_token=slack_token,
            slack_channel=slack_channel,
        ).run()

    # throw_missing_error should get called which logs a critical error
    mock_logger.assert_called_once()


@patch("pullbug.bug.Github")
@patch("pullbug.bug.Github.get_repos")
@patch("pullbug.bug.Github.get_user")
@patch("logging.Logger.info")
def test_get_repos_users(mock_logger, mock_get_user, mock_get_repos, mock_github_instance):
    bug = Pullbug(
        github_owner="justintime50",
        github_context="users",
        repos="justintime50",
    )
    repos = bug.get_repos()

    mock_logger.call_count == 2
    assert isinstance(repos, list)
    # TODO: Assert the get_repos and get_user/org gets called


@patch("pullbug.bug.Github")
@patch("pullbug.bug.Github.get_repos")
@patch("pullbug.bug.Github.get_organization")
@patch("logging.Logger.info")
def test_get_repos_orgs(mock_logger, mock_get_org, mock_get_repos, mock_github_instance):
    bug = Pullbug(
        github_owner="justintime50",
        github_context="orgs",
        repos="justintime50",
    )
    repos = bug.get_repos()

    mock_logger.call_count == 2
    assert isinstance(repos, list)
    # TODO: Assert the get_repos and get_user/org gets called


@patch("logging.Logger.info")
def test_get_pull_requests(mock_logger):
    pull_requests = Pullbug(
        github_owner="justintime50",
    ).get_pull_requests(repos=[MagicMock()])

    assert isinstance(pull_requests, list)
    mock_logger.call_count == 2
    # TODO: Assert and mock that `get_pulls` gets called


@patch("logging.Logger.info")
def test_get_issues(mock_logger):
    issues = Pullbug(
        github_owner="justintime50",
    ).get_issues(repos=[MagicMock()])

    assert isinstance(issues, list)
    mock_logger.call_count == 2
    # TODO: Assert and mock that `get_pulls` gets called


@patch("pullbug.bug.prepare_pulls_message", return_value=([], []))
def test_iterate_pull_requests(mock_prepare_pulls_message):
    slack_messages, discord_messages = Pullbug(
        github_owner="justintime50",
        drafts=True,  # Lazy approach but keeps us from needing to build the MagicMock object below
    ).iterate_pull_requests(pull_requests=[MagicMock()])

    assert isinstance(slack_messages, list)
    assert isinstance(discord_messages, list)
    mock_prepare_pulls_message.assert_called_once()


@patch("pullbug.bug.prepare_issues_message", return_value=([], []))
def test_iterate_issues(mock_prepare_issues_message):
    slack_messages, discord_messages = Pullbug(
        github_owner="justintime50",
    ).iterate_issues(issues=[MagicMock()])

    assert isinstance(slack_messages, list)
    assert isinstance(discord_messages, list)
    mock_prepare_issues_message.assert_called_once()


@patch("pullbug.bug.send_discord_message")
def test_send_messages_discord(mock_send_discord_message, mock_url):
    slack_messages = discord_messages = []

    Pullbug(
        github_owner="justintime50",
        discord=True,
        discord_url=mock_url,
    ).send_messages(slack_messages, discord_messages)

    mock_send_discord_message.assert_called_once_with(slack_messages, mock_url)


@patch("pullbug.bug.send_slack_message")
def test_send_messages_slack(mock_send_slack_message, mock_token, mock_channel):
    slack_messages = discord_messages = []

    Pullbug(
        github_owner="justintime50",
        slack=True,
        slack_token=mock_token,
        slack_channel=mock_channel,
    ).send_messages(slack_messages, discord_messages)

    mock_send_slack_message.assert_called_once_with(slack_messages, mock_token, mock_channel)


@patch("pullbug.bug.Pullbug.send_messages")
@patch("pullbug.bug.Pullbug.get_pull_requests")
@patch("pullbug.bug.Pullbug.get_repos")
@patch("logging.Logger.info")
def test_no_messages_when_quiet(mock_logger, mock_get_repos, mock_pull_request, mock_send_messages):
    """Tests that we do not send messages when the user passes the `quiet` flag."""
    Pullbug(
        github_owner="justintime50",
        github_token="123",
        github_context="users",
        pulls=True,
        issues=True,
        quiet=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_logger.assert_called()
    mock_send_messages.assert_not_called()
