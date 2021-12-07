from unittest.mock import patch

import pytest

from pullbug.github_bug import GithubBug


@patch('pullbug.github_bug.GithubBug.get_pull_requests')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('logging.Logger.info')
def test_run_pull_requests(mock_logger, mock_get_repos, mock_pull_request):
    GithubBug(
        github_owner='justintime50',
        github_token='123',
        github_context='users',
        pulls=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    mock_logger.assert_called()


@patch('pullbug.github_bug.GithubBug.get_pull_requests', return_value=[])
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('logging.Logger.info')
def test_run_no_pull_requests(mock_logger, mock_get_repos, mock_pull_request):
    GithubBug(
        github_owner='justintime50',
        github_token='123',
        github_context='users',
        pulls=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_pull_request.assert_called_once()
    assert mock_logger.call_count == 3


@patch('pullbug.github_bug.GithubBug.get_issues')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('logging.Logger.info')
def test_run_issues(mock_logger, mock_get_repos, mock_issues):
    GithubBug(
        github_owner='justintime50',
        github_token='123',
        github_context='users',
        issues=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_issues.assert_called_once()
    mock_logger.assert_called()


@patch('pullbug.github_bug.GithubBug.get_issues', return_value=[])
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('logging.Logger.info')
def test_run_no_issues(mock_logger, mock_get_repos, mock_issues):
    GithubBug(
        github_owner='justintime50',
        github_token='123',
        github_context='users',
        issues=True,
    ).run()

    mock_get_repos.assert_called_once()
    mock_issues.assert_called_once()
    assert mock_logger.call_count == 3


@patch('woodchips.Logger')
def test_setup_logger(mock_logger):
    GithubBug(
        github_owner='justintime50',
    ).setup_logger()

    mock_logger.assert_called_once()


@pytest.mark.parametrize(
    'pulls, issues, github_token, discord, discord_url, slack, slack_token, slack_channel, rocketchat, rocketchat_url',
    [
        # no pulls
        (False, False, False, False, False, False, False, False, False, False),
        # discord but no url
        (True, False, '123', True, False, False, False, False, False, False),
        # slack but no token
        (True, False, '123', False, False, True, False, False, False, False),
        # slack, token, but no channel
        (True, False, '123', False, False, True, '123', False, False, False),
        # rocketchat but no url
        (True, False, '123', False, False, False, False, False, True, False),
    ],
)
@patch('pullbug.github_bug.GithubBug.get_issues')
@patch('pullbug.github_bug.GithubBug.get_repos')
@patch('logging.Logger.critical')
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
    rocketchat,
    rocketchat_url,
):
    with pytest.raises(ValueError):
        GithubBug(
            github_owner='justintime50',
            github_token=github_token,
            pulls=pulls,
            issues=issues,
            discord=discord,
            discord_url=discord_url,
            slack=slack,
            slack_token=slack_token,
            slack_channel=slack_channel,
            rocketchat=rocketchat,
            rocketchat_url=rocketchat_url,
        ).run()

    # throw_missing_error should get called which logs a critical error
    mock_logger.assert_called_once()


@patch('pullbug.github_bug.Github')
@patch('pullbug.github_bug.Github.get_repos')
@patch('pullbug.github_bug.Github.get_user')
@patch('logging.Logger.info')
def test_get_repos_users(mock_logger, mock_get_user, mock_get_repos, mock_github_instance):
    github_bug = GithubBug(
        github_owner='justintime50',
        github_context='users',
        repos='justintime50',
    )
    repos = github_bug.get_repos()

    mock_logger.call_count == 2
    assert type(repos) == list
    # TODO: Assert the get_repos and get_user/org gets called


@patch('pullbug.github_bug.Github')
@patch('pullbug.github_bug.Github.get_repos')
@patch('pullbug.github_bug.Github.get_organization')
@patch('logging.Logger.info')
def test_get_repos_orgs(mock_logger, mock_get_org, mock_get_repos, mock_github_instance):
    github_bug = GithubBug(
        github_owner='justintime50',
        github_context='orgs',
        repos='justintime50',
    )
    repos = github_bug.get_repos()

    mock_logger.call_count == 2
    assert type(repos) == list
    # TODO: Assert the get_repos and get_user/org gets called


@patch('logging.Logger.info')
def test_get_pull_requests(mock_logger):
    pull_requests = GithubBug(
        github_owner='justintime50',
    ).get_pull_requests(repos=[])

    assert pull_requests == []
    mock_logger.call_count == 2
    # TODO: Assert and mock that `get_pulls` gets called


@patch('logging.Logger.info')
def test_get_issues(mock_logger):
    issues = GithubBug(
        github_owner='justintime50',
    ).get_issues(repos=[])

    assert issues == []
    mock_logger.call_count == 2
    # TODO: Assert and mock that `get_pulls` gets called


def test_iterate_pull_requests():
    messages, discord_messages = GithubBug(
        github_owner='justintime50',
    ).iterate_pull_requests(pull_requests=[])

    assert messages == []
    assert discord_messages == []
    # TODO: Assert the message building functions get called


def test_iterate_issues():
    messages, discord_messages = GithubBug(
        github_owner='justintime50',
    ).iterate_issues(issues=[])

    assert messages == []
    assert discord_messages == []
    # TODO: Assert the message building functions get called


@patch('pullbug.github_bug.Messages.send_discord_message')
def test_send_messages_discord(mock_send_discord_message, mock_url):
    messages = discord_messages = []

    GithubBug(
        github_owner='justintime50',
        discord=True,
        discord_url=mock_url,
    ).send_messages(messages, discord_messages)

    mock_send_discord_message.assert_called_once_with(messages, mock_url)


@patch('pullbug.github_bug.Messages.send_slack_message')
def test_send_messages_slack(mock_send_slack_message, mock_token, mock_channel):
    messages = discord_messages = []

    GithubBug(
        github_owner='justintime50',
        slack=True,
        slack_token=mock_token,
        slack_channel=mock_channel,
    ).send_messages(messages, discord_messages)

    mock_send_slack_message.assert_called_once_with(messages, mock_token, mock_channel)


@patch('pullbug.github_bug.Messages.send_rocketchat_message')
def test_send_messages_rocketchat(mock_send_rocketchat_message, mock_url):
    messages = discord_messages = []

    GithubBug(
        github_owner='justintime50',
        rocketchat=True,
        rocketchat_url=mock_url,
    ).send_messages(messages, discord_messages)

    mock_send_rocketchat_message.assert_called_once_with(messages, mock_url)
