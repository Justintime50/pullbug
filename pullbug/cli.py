import argparse
import logging
import os

from pullbug.github_bug import GithubBug
from pullbug.gitlab_bug import GitlabBug
from pullbug.logger import PullBugLogger

LOGGER = logging.getLogger(__name__)


class PullBugCLI:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=(
                'Get bugged via Slack or RocketChat to merge your GitHub pull requests or GitLab merge requests.'
            )
        )
        parser.add_argument(
            '-gh',
            '--github',
            required=False,
            action='store_true',
            default=False,
            help='Get bugged about pull requests from GitHub.',
        )
        parser.add_argument(
            '--github_token',
            required=False,
            type=str,
            default=None,
            help='The token to authenticate with GitHub.',
        )
        parser.add_argument(
            '-go',
            '--github_owner',
            required=False,
            type=str,
            default=None,
            help='The GitHub owner to retrieve pull requests from (can be a user or organization).',
        )
        parser.add_argument(
            '--github_state',
            required=False,
            type=str,
            default='open',
            choices=['open', 'closed', 'all'],
            help='The GitHub state to retrieve pull requests with.',
        )
        parser.add_argument(
            '-gc',
            '--github_context',
            required=False,
            type=str,
            default='orgs',
            choices=['orgs', 'users'],
            help='The GitHub context to retrieve pull requests with.',
        )
        parser.add_argument(
            '-gl',
            '--gitlab',
            required=False,
            action='store_true',
            default=False,
            help='Get bugged about merge requests from GitLab.',
        )
        parser.add_argument(
            '--gitlab_token',
            required=False,
            type=str,
            default=None,
            help='The API key to authenticate with GitLab.',
        )
        parser.add_argument(
            '-gu',
            '--gitlab_url',
            required=False,
            type=str,
            default='https://gitlab.com/api/v4',
            help='The URL of the GitLab instance to use.',
        )
        parser.add_argument(
            '--gitlab_state',
            required=False,
            type=str,
            default='opened',
            choices=['opened', 'closed', 'locked', 'merged'],
            help='The GitLab state to retrieve merge requests with.',
        )
        parser.add_argument(
            '--gitlab_scope',
            required=False,
            type=str,
            default='all',
            choices=['all', 'created_by_me', 'assigned_to_me'],
            help='The GitLab state to retrieve pull requests with.',
        )
        parser.add_argument(
            '-d',
            '--discord',
            required=False,
            action='store_true',
            default=False,
            help='Send Pullbug messages to Discord.',
        )
        parser.add_argument(
            '-du',
            '--discord_url',
            required=False,
            type=str,
            default=None,
            help='The Discord webhook URL to send messages to.',
        )
        parser.add_argument(
            '-s',
            '--slack',
            required=False,
            action='store_true',
            default=False,
            help='Send Pullbug messages to Slack.',
        )
        parser.add_argument(
            '-st',
            '--slack_token',
            required=False,
            type=str,
            default=None,
            help='The Slackbot token to authenticate with Slack.',
        )
        parser.add_argument(
            '-sc',
            '--slack_channel',
            required=False,
            type=str,
            default=None,
            help='The Slack channel to send messages to.',
        )
        parser.add_argument(
            '-rc',
            '--rocketchat',
            required=False,
            action='store_true',
            default=False,
            help='Send Pullbug messages to Rocket.Chat.',
        )
        parser.add_argument(
            '-ru',
            '--rocketchat_url',
            required=False,
            type=str,
            default=False,
            help='The Rocket.Chat URL to send messages to.',
        )
        parser.add_argument(
            '-w',
            '--wip',
            required=False,
            action='store_true',
            default=False,
            help='Include "Work in Progress" pull or merge requests.',
        )
        parser.add_argument(
            '-l',
            '--location',
            required=False,
            type=str,
            default=os.path.expanduser('~/pullbug'),
            help='The location of the Pullbug logs and files.',
        )
        parser.parse_args(namespace=self)

    def run(self):
        """Send command line args to the main run function."""
        PullBug.run(
            github=self.github,
            github_token=self.github_token,
            github_owner=self.github_owner,
            github_state=self.github_state,
            github_context=self.github_context,
            gitlab=self.gitlab,
            gitlab_token=self.gitlab_token,
            gitlab_url=self.gitlab_url,
            gitlab_state=self.gitlab_state,
            gitlab_scope=self.gitlab_scope,
            discord=self.discord,
            discord_url=self.discord_url,
            slack=self.slack,
            slack_token=self.slack_token,
            slack_channel=self.slack_channel,
            rocketchat=self.rocketchat,
            rocketchat_url=self.rocketchat_url,
            wip=self.wip,
            location=self.location,
        )


class PullBug:
    def run(
        self,
        github,
        github_token,
        github_owner,
        github_state,
        github_context,
        gitlab,
        gitlab_token,
        gitlab_url,
        gitlab_state,
        gitlab_scope,
        discord,
        discord_url,
        slack,
        slack_token,
        slack_channel,
        rocketchat,
        rocketchat_url,
        wip,
        location,
    ):
        """Run Pullbug based on the configuration."""
        PullBugLogger._setup_logging(LOGGER)
        LOGGER.info('Running Pullbug...')
        self.run_missing_checks()
        if self.github:
            github_bug = GithubBug(
                self.github_token,
                self.github_owner,
                self.github_state,
                self.github_context,
                self.wip,
                self.discord,
                self.discord_url,
                self.slack,
                self.slack_token,
                self.slack_channel,
                self.rocketchat,
                self.rocketchat_url,
            )

            github_bug.run()
        if gitlab:
            gitlab_bug = GitlabBug(
                self.gitlab_scope, self.gitlab_state, self.wip, self.discord, self.slack, self.rocketchat
            )

            gitlab_bug.run()
        LOGGER.info('Pullbug finished bugging!')

    def run_missing_checks(self):
        """Check that values are set based on configuration before proceeding."""
        if not self.github and not self.gitlab:
            message = 'Neither "github" nor "gitlab" flags were passed, one is required. Please correct and try again.'
            LOGGER.critical(message)
            raise ValueError(message)
        if self.github and not self.github_token:
            self.throw_missing_error('github_token')
        if self.gitlab and not self.gitlab_token:
            self.throw_missing_error('gitlab_token')
        if self.discord and not self.discord_url:
            self.throw_missing_error('discord_url')
        if self.slack and not self.slack_token:
            self.throw_missing_error('slack_token')
        if self.slack and not self.slack_channel:
            self.throw_missing_error('slack_channel')
        if self.rocketchat and not self.rocketchat_url:
            self.throw_missing_error('rocketchat_url')

    @staticmethod
    def throw_missing_error(missing):
        """Raise an error based on what env variables are missing."""
        message = f'No {missing} set. Please correct and try again.'
        LOGGER.critical(message)
        raise ValueError(message)


def main():
    PullBugCLI().run()


if __name__ == '__main__':
    main()
