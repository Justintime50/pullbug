import argparse
import logging
import os

from dotenv import load_dotenv

from pullbug.github_bug import GithubBug
from pullbug.gitlab_bug import GitlabBug
from pullbug.logger import PullBugLogger

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITLAB_API_KEY = os.getenv('GITLAB_API_KEY')
GITLAB_API_URL = os.getenv('GITLAB_API_URL', 'https://gitlab.com/api/v4')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
ROCKET_CHAT_URL = os.getenv('ROCKET_CHAT_URL')
LOGGER = logging.getLogger(__name__)


class PullBugCLI:
    def __init__(self):
        """Initiate CLI args."""
        parser = argparse.ArgumentParser(
            description='Get bugged via Slack or RocketChat to merge your GitHub pull requests or GitLab merge requests.'  # noqa
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
            '-gl',
            '--gitlab',
            required=False,
            action='store_true',
            default=False,
            help='Get bugged about merge requests from GitLab.',
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
            '-s',
            '--slack',
            required=False,
            action='store_true',
            default=False,
            help='Send Pullbug messages to Slack.',
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
            '-w',
            '--wip',
            required=False,
            action='store_true',
            default=False,
            help='Include "Work in Progress" pull or merge requests.',
        )
        parser.add_argument(
            '-gho',
            '--github_owner',
            required=False,
            type=str,
            default=None,
            help='The GitHub owner to retrieve pull requests from (can be a user or organization).',
        )
        parser.add_argument(
            '-ghs',
            '--github_state',
            required=False,
            type=str,
            default='open',
            choices=['open', 'closed', 'all'],
            help='The GitHub state to retrieve pull requests with.',
        )
        parser.add_argument(
            '-ghc',
            '--github_context',
            required=False,
            type=str,
            default='orgs',
            choices=['orgs', 'users'],
            help='The GitHub context to retrieve pull requests with.',
        )
        parser.add_argument(
            '-glst',
            '--gitlab_state',
            required=False,
            type=str,
            default='opened',
            choices=['opened', 'closed', 'locked', 'merged'],
            help='The GitLab state to retrieve merge requests with.',
        )
        parser.add_argument(
            '-glsc',
            '--gitlab_scope',
            required=False,
            type=str,
            default='all',
            choices=['all', 'created_by_me', 'assigned_to_me'],
            help='The GitLab state to retrieve pull requests with.',
        )
        parser.parse_args(namespace=self)

    def run(self):
        """Send command line args to the main run function."""
        PullBug.run(
            github=self.github,
            gitlab=self.gitlab,
            discord=self.discord,
            slack=self.slack,
            rocketchat=self.rocketchat,
            wip=self.wip,
            github_owner=self.github_owner,
            github_state=self.github_state,
            github_context=self.github_context,
            gitlab_state=self.gitlab_state,
            gitlab_scope=self.gitlab_scope,
        )


class PullBug:
    @classmethod
    def run(
        cls,
        github,
        gitlab,
        discord,
        slack,
        rocketchat,
        wip,
        github_owner,
        github_state,
        github_context,
        gitlab_state,
        gitlab_scope,
    ):
        """Run Pullbug based on the configuration."""
        PullBugLogger._setup_logging(LOGGER)
        LOGGER.info('Running Pullbug...')
        load_dotenv()
        cls.run_missing_checks(github, gitlab, discord, slack, rocketchat)
        if github:
            GithubBug.run(github_owner, github_state, github_context, wip, discord, slack, rocketchat)
        if gitlab:
            GitlabBug.run(gitlab_scope, gitlab_state, wip, discord, slack, rocketchat)
        LOGGER.info('Pullbug finished bugging!')

    @classmethod
    def run_missing_checks(cls, github, gitlab, discord, slack, rocketchat):
        """Check that values are set based on
        configuration before proceeding.
        """
        if not github and not gitlab:
            message = 'Neither "github" nor "gitlab" flags were passed, one is required. Please correct and try again.'
            LOGGER.critical(message)
            raise ValueError(message)
        if github and not GITHUB_TOKEN:
            cls.throw_missing_error('GITHUB_TOKEN')
        if gitlab and not GITLAB_API_KEY:
            cls.throw_missing_error('GITLAB_API_KEY')
        if discord and not DISCORD_WEBHOOK_URL:
            cls.throw_missing_error('DISCORD_WEBHOOK_URL')
        if slack and not SLACK_BOT_TOKEN:
            cls.throw_missing_error('SLACK_BOT_TOKEN')
        if slack and not SLACK_CHANNEL:
            cls.throw_missing_error('SLACK_CHANNEL')
        if rocketchat and not ROCKET_CHAT_URL:
            cls.throw_missing_error('ROCKET_CHAT_URL')

    @classmethod
    def throw_missing_error(cls, missing):
        """Raise an error based on what env variables
        are missing.
        """
        message = f'No {missing} set. Please correct and try again.'
        LOGGER.critical(message)
        raise ValueError(message)


def main():
    PullBugCLI().run()


if __name__ == '__main__':
    main()
