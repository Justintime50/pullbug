import logging
import os

from github import Github

from pullbug.logger import PullBugLogger
from pullbug.messages import Messages

LOGGER = logging.getLogger(__name__)


class GithubBug:
    def __init__(
        self,
        github_token=None,
        github_owner=None,
        github_state='open',
        github_context='orgs',
        discord=False,
        discord_url=None,
        slack=False,
        slack_token=None,
        slack_channel=None,
        rocketchat=False,
        rocketchat_url=None,
        repos=None,
        drafts=False,
        location=os.path.expanduser('~/pullbug'),
    ):
        # Parameter variables
        self.github_token = github_token
        self.github_owner = github_owner
        self.github_state = github_state
        self.github_context = github_context
        self.discord = discord
        self.discord_url = discord_url
        self.slack = slack
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.rocketchat = rocketchat
        self.rocketchat_url = rocketchat_url
        self.repos = repos.lower().split(',') if repos else ''
        self.drafts = drafts
        self.location = location

        # Internal variables
        # TODO: We could eventually allow non-authenticated access
        self.github_instance = Github(self.github_token) if self.github_token else Github()

    def run(self):
        """Run the logic to get PR's from GitHub and send that data via message."""
        PullBugLogger._setup_logging(LOGGER, self.location)
        repos = self.get_repos()

        # if self.pulls:
        #     pull_requests = self.get_pull_requests(repos)
        # elif self.issues:
        issues = self.get_issues(repos)
        print(issues)  # TODO: REMOVE ME ONCE WE HAVE MESSAGES SETUP

        if pull_requests == []:
            message = 'No pull requests are available from GitHub.'
            LOGGER.info(message)
            # TODO: Do we want to send this message here?
        else:
            message_preamble = '\n:bug: *The following pull requests on GitHub are still open and need your help!*\n'
            messages, discord_messages = self.iterate_pull_requests(pull_requests)
            messages.insert(0, message_preamble)
            discord_messages.insert(0, message_preamble)

            if self.discord:
                Messages.send_discord_message(discord_messages)
            if self.slack:
                Messages.send_slack_message(messages)
            if self.rocketchat:
                Messages.send_rocketchat_message(messages)
            LOGGER.info(messages)

    def get_repos(self):
        """Get all repos of the github_owner."""
        LOGGER.info('Bugging GitHub for repos...')
        if self.github_context == 'orgs':
            repos = self.github_instance.get_organization(self.github_owner).get_repos()
        elif self.github_context == 'users':
            repos = self.github_instance.get_user(self.github_owner).get_repos()
        else:
            # Can't determine github_context
            pass
        LOGGER.info('GitHub repos retrieved!')

        if self.repos:
            formatted_repos_list = [repo.strip() for repo in self.repos]
            repos = [repo for repo in repos if repo.name.lower() in formatted_repos_list]

        return repos

    def get_pull_requests(self, repos):
        """Grab all pull requests from each repo and return a flat list of pull requests."""
        LOGGER.info('Bugging GitHub for pull requests...')
        pull_requests = []
        for repo in repos:
            repo_pull_requests = repo.get_pulls(state=self.github_state)
            if repo_pull_requests:
                pull_requests.append(repo_pull_requests)
            else:
                # Repo has no pull requests
                continue
        LOGGER.info('Pull requests retrieved!')

        flat_pull_requests_list = [pull_request for pull_request in pull_requests for pull_request in pull_request]

        return flat_pull_requests_list

    def get_issues(self, repos):
        """Grab all issues from each repo and return a flat list of issues."""
        LOGGER.info('Bugging GitHub for issues...')
        issues = []
        for repo in repos:
            repo_issues = repo.get_issues(state=self.github_state)
            if repo_issues:
                issues.append(repo_issues)
            else:
                # Repo has no issues
                continue
        LOGGER.info('Issues retrieved!')

        flat_issues_list = [issue for issue in issues for issue in issue]

        return flat_issues_list

    def iterate_pull_requests(self, pull_requests):
        """Iterate through each pull request of a repo and build the message array."""
        message_array = []
        discord_message_array = []
        for pull_request in pull_requests:
            if pull_request.draft and not self.drafts:
                # Exclude drafts if the user doesn't want them included
                continue
            else:
                message, discord_message = Messages.prepare_github_message(pull_request)
                message_array.append(message)
                discord_message_array.append(discord_message)

        return message_array, discord_message_array
