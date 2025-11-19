import argparse
from typing import get_args

from pullbug._version import __version__
from pullbug.bug import (
    DEFAULT_BASE_URL,
    DEFAULT_LOCATION,
    DEFAULT_LOG_LEVEL,
    GITHUB_CONTEXT_CHOICES,
    GITHUB_STATE_CHOICES,
    LOG_LEVEL_CHOICES,
    Pullbug,
)


class PullBugCli:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Get bugged via Discord or Slack to merge your GitHub pull requests."
        )
        parser.add_argument(
            "-p",
            "--pulls",
            required=False,
            action="store_true",
            default=False,
            help="Bug GitHub for Pull Requests.",
        )
        parser.add_argument(
            "-i",
            "--issues",
            required=False,
            action="store_true",
            default=False,
            help="Bug GitHub for Issues.",
        )
        parser.add_argument(
            "-gt",
            "--github_token",
            required=False,
            type=str,
            default=None,
            help="The token to authenticate with GitHub.",
        )
        parser.add_argument(
            "-go",
            "--github_owner",
            required=False,
            type=str,
            default="",
            help="The GitHub owner to retrieve pull requests or issues for (can be a user or organization).",
        )
        parser.add_argument(
            "-gs",
            "--github_state",
            required=False,
            type=str,
            default="open",
            choices=set(get_args(GITHUB_STATE_CHOICES)),
            help="The GitHub state to retrieve pull requests or issues for.",
        )
        parser.add_argument(
            "-gc",
            "--github_context",
            required=False,
            type=str,
            default="users",
            choices=set(get_args(GITHUB_CONTEXT_CHOICES)),
            help="The GitHub context to retrieve pull requests or issues for.",
        )
        parser.add_argument(
            "-d",
            "--discord",
            required=False,
            action="store_true",
            default=False,
            help="Send Pullbug messages to Discord.",
        )
        parser.add_argument(
            "-du",
            "--discord_url",
            required=False,
            type=str,
            default="",
            help="The Discord webhook URL to send messages to.",
        )
        parser.add_argument(
            "-s",
            "--slack",
            required=False,
            action="store_true",
            default=False,
            help="Send Pullbug messages to Slack.",
        )
        parser.add_argument(
            "-st",
            "--slack_token",
            required=False,
            type=str,
            default="",
            help="The Slackbot token to authenticate with Slack.",
        )
        parser.add_argument(
            "-sc",
            "--slack_channel",
            required=False,
            type=str,
            default="",
            help="The Slack channel to send messages to.",
        )
        parser.add_argument(
            "-r",
            "--repos",
            required=False,
            type=str,
            default="",
            help="A comma-separated list of repos to run Pullbug against.",
        )
        parser.add_argument(
            "-dr",
            "--drafts",
            required=False,
            action="store_true",
            default=False,
            help="Include draft pull requests.",
        )
        parser.add_argument(
            "-l",
            "--location",
            required=False,
            type=str,
            default=DEFAULT_LOCATION,
            help="The location of the Pullbug logs and files.",
        )
        parser.add_argument(
            "--base_url",
            required=False,
            type=str,
            default=DEFAULT_BASE_URL,
            help="The base URL of your GitHub instance (useful for enterprise users with custom hostnames).",
        )
        parser.add_argument(
            "--log_level",
            type=str,
            required=False,
            default=DEFAULT_LOG_LEVEL,
            choices=set(get_args(LOG_LEVEL_CHOICES)),
            help="The log level used for the tool.",
        )
        parser.add_argument(
            "--disable_descriptions",
            required=False,
            action="store_true",
            default=False,
            help="Disables descriptions in messages.",
        )
        parser.add_argument(
            "--quiet",
            required=False,
            action="store_true",
            default=False,
            help="Does not output when there is nothing to bug about.",
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
        )
        parser.parse_args(namespace=self)

    def run(self):
        bug = Pullbug(
            self.github_owner,
            self.github_token,
            self.github_state,
            self.github_context,
            self.pulls,
            self.issues,
            self.discord,
            self.discord_url,
            self.slack,
            self.slack_token,
            self.slack_channel,
            self.repos,
            self.drafts,
            self.location,
            self.base_url,
            self.log_level,
            self.disable_descriptions,
            self.quiet,
        )
        bug.run()


def main():
    PullBugCli().run()


if __name__ == "__main__":
    main()
