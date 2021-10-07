import argparse
import os

from pullbug.github_bug import GithubBug


class PullBugCli:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Get bugged via Slack or RocketChat to merge your GitHub pull requests.'
        )
        parser.add_argument(
            '-p',
            '--pulls',
            required=False,
            action='store_true',
            default=False,
            help='Bug GitHub for Pull Requests.',
        )
        parser.add_argument(
            '-i',
            '--issues',
            required=False,
            action='store_true',
            default=False,
            help='Bug GitHub for Issues.',
        )
        parser.add_argument(
            '-gt',
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
            help='The GitHub owner to retrieve pull requests or issues for (can be a user or organization).',
        )
        parser.add_argument(
            '-gs',
            '--github_state',
            required=False,
            type=str,
            default='open',
            choices=['open', 'closed', 'all'],
            help='The GitHub state to retrieve pull requests or issues for.',
        )
        parser.add_argument(
            '-gc',
            '--github_context',
            required=True,
            type=str,
            default=None,
            choices=['orgs', 'users'],
            help='The GitHub context to retrieve pull requests or issues for.',
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
            '-r',
            '--repos',
            required=False,
            type=str,
            default=None,
            help='A comma-separated list of repos to run Pullbug against.',
        )
        parser.add_argument(
            '-dr',
            '--drafts',
            required=False,
            action='store_true',
            default=False,
            help='Include draft pull requests.',
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
        github_bug = GithubBug(
            self.pulls,
            self.issues,
            self.github_token,
            self.github_owner,
            self.github_state,
            self.github_context,
            self.discord,
            self.discord_url,
            self.slack,
            self.slack_token,
            self.slack_channel,
            self.rocketchat,
            self.rocketchat_url,
            self.repos,
            self.drafts,
            self.location,
        )
        github_bug.run()


def main():
    PullBugCli().run()


if __name__ == '__main__':
    main()
