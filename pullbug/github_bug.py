import os
from typing import Any, List, Tuple

import woodchips
from github import Github, Issue, PaginatedList, PullRequest
from typing_extensions import Literal

from pullbug.messages import Messages

GITHUB_STATE_CHOICES = Literal[
    'all',
    'closed',
    'open',
]
GITHUB_CONTEXT_CHOICES = Literal[
    'users',
    'orgs',
]

LOGGER_NAME = 'pullbug'


class GithubBug:
    def __init__(
        self,
        github_owner: str,
        github_token: str = '',
        github_state: GITHUB_STATE_CHOICES = 'open',
        github_context: GITHUB_CONTEXT_CHOICES = 'users',
        pulls: bool = False,
        issues: bool = False,
        discord: bool = False,
        discord_url: str = '',
        slack: bool = False,
        slack_token: str = '',
        slack_channel: str = '',
        rocketchat: bool = False,
        rocketchat_url: str = '',
        repos: str = '',
        drafts: bool = False,
        location: str = os.path.expanduser('~/pullbug'),
    ):
        # Parameter variables
        self.github_owner = github_owner
        self.github_token = github_token
        self.github_state = github_state
        self.github_context = github_context
        self.pulls = pulls
        self.issues = issues
        self.discord = discord
        self.discord_url = discord_url
        self.slack = slack
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.rocketchat = rocketchat
        self.rocketchat_url = rocketchat_url
        self.repos = [repo.strip() for repo in repos.lower().split(',')] if repos else ''
        self.drafts = drafts
        self.location = location

        # Internal variables
        # TODO: We could eventually allow non-authenticated access
        self.github_instance = Github(self.github_token) if self.github_token else Github()

    def run(self):
        """Run the logic to get PR's from GitHub and send that data via message."""
        self.setup_logger()
        logger = woodchips.get(LOGGER_NAME)
        logger.info('Running Pullbug...')
        self.run_missing_checks()

        repos = self.get_repos()

        if self.pulls:
            pull_requests = self.get_pull_requests(repos)
            if pull_requests == []:
                message = 'No pull requests are available from GitHub.'
                logger.info(message)
                # TODO: Do we want to send this message here?
            else:
                message_preamble = (
                    '\n:bug: *The following pull requests on GitHub are still open and need your help!*\n'
                )
                messages, discord_messages = self.iterate_pull_requests(pull_requests)
                messages.insert(0, message_preamble)
                discord_messages.insert(0, message_preamble)

                self.send_messages(messages, discord_messages)

        if self.issues:
            issues = self.get_issues(repos)
            if issues == []:
                message = 'No issues are available from GitHub.'
                logger.info(message)
                # TODO: Do we want to send this message here?
            else:
                message_preamble = '\n:bug: *The following issues on GitHub are still open and need your help!*\n'
                messages, discord_messages = self.iterate_issues(issues)
                messages.insert(0, message_preamble)
                discord_messages.insert(0, message_preamble)

                self.send_messages(messages, discord_messages)

        logger.info('Pullbug finished bugging!')

    def setup_logger(self):
        """Setup a `woodchips` logger for the project."""
        logger = woodchips.Logger(
            name=LOGGER_NAME,
            level='INFO',
        )
        logger.log_to_console()
        logger.log_to_file(location=os.path.join(self.location, 'logs'))

    def run_missing_checks(self):
        """Check that values are set based on configuration before proceeding."""
        if not self.pulls and not self.issues:
            self.throw_missing_error('pulls/issues')
        if self.discord and not self.discord_url:
            self.throw_missing_error('discord_url')
        if self.slack and not self.slack_token:
            self.throw_missing_error('slack_token')
        if self.slack and not self.slack_channel:
            self.throw_missing_error('slack_channel')
        if self.rocketchat and not self.rocketchat_url:
            self.throw_missing_error('rocketchat_url')

    @staticmethod
    def throw_missing_error(missing_flag: str):
        """Raise an error based on what env variables are missing."""
        logger = woodchips.get(LOGGER_NAME)
        message = f'No {missing_flag} set. Please correct and try again.'
        logger.critical(message)

        raise ValueError(message)

    def get_repos(self) -> PaginatedList.PaginatedList:
        """Get all repos of the `github_owner`."""
        logger = woodchips.get(LOGGER_NAME)

        logger.info('Bugging GitHub for repos...')

        repos: Any  # Fixes `mypy` type checking, repos are either a Python list or a GitHub PaginatedList

        if self.github_context == 'orgs':
            repos = self.github_instance.get_organization(self.github_owner).get_repos()
        elif self.github_context == 'users':
            repos = self.github_instance.get_user(self.github_owner).get_repos()

        # If the user specified a list of repos, let's filter them here
        if self.repos:
            filtered_repos = filter(lambda repo: repo.name.lower() in self.repos, repos)
            repos = list(filtered_repos)

        logger.info('GitHub repos retrieved!')

        return repos

    def get_pull_requests(self, repos: PaginatedList.PaginatedList) -> List[PullRequest.PullRequest]:
        """Grab all pull requests from each repo and return a flat list of pull requests."""
        logger = woodchips.get(LOGGER_NAME)

        logger.info('Bugging GitHub for pull requests...')
        pull_requests = []

        for repo in repos:
            repo_pull_requests = repo.get_pulls(state=self.github_state)
            if repo_pull_requests:
                pull_requests.append(repo_pull_requests)
            else:
                # Repo has no pull requests
                continue

        flat_pull_requests_list: List = [
            pull_request for pull_request in pull_requests for pull_request in pull_request
        ]

        logger.info('Pull requests retrieved!')

        return flat_pull_requests_list

    def get_issues(self, repos: PaginatedList.PaginatedList) -> List[Issue.Issue]:
        """Grab all issues from each repo and return a flat list of issues."""
        logger = woodchips.get(LOGGER_NAME)

        logger.info('Bugging GitHub for issues...')
        issues = []

        for repo in repos:
            repo_issues = repo.get_issues(state=self.github_state)
            if repo_issues:
                issues.append(repo_issues)
            else:
                # Repo has no issues
                continue

        flat_issues_list = [issue for issue in issues for issue in issue]

        logger.info('Issues retrieved!')

        return flat_issues_list

    def iterate_pull_requests(self, pull_requests: PaginatedList.PaginatedList) -> Tuple[List[str], List[str]]:
        """Iterate through each pull request of a repo and build the message array."""
        message_array = []
        discord_message_array = []

        for pull_request in pull_requests:
            if pull_request.draft and not self.drafts:
                # Exclude drafts if the user doesn't want them included
                continue
            else:
                message, discord_message = Messages.prepare_pulls_message(pull_request)
                message_array.append(message)
                discord_message_array.append(discord_message)

        return message_array, discord_message_array

    @staticmethod
    def iterate_issues(issues: PaginatedList.PaginatedList) -> Tuple[List[str], List[str]]:
        """Iterate through each issue of a repo and build the message array."""
        message_array = []
        discord_message_array = []

        for issue in issues:
            message, discord_message = Messages.prepare_issues_message(issue)
            message_array.append(message)
            discord_message_array.append(discord_message)

        return message_array, discord_message_array

    def send_messages(self, messages: List[str], discord_messages: List[str]):
        """Sends a message to the messaging platforms requested (can be multiple at once)."""
        logger = woodchips.get(LOGGER_NAME)

        if self.discord:
            Messages.send_discord_message(discord_messages, self.discord_url)
        if self.slack:
            Messages.send_slack_message(messages, self.slack_token, self.slack_channel)
        if self.rocketchat:
            Messages.send_rocketchat_message(messages, self.rocketchat_url)

        logger.info(messages)
