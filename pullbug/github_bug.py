import logging

import requests

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
        wip=False,
        discord=False,
        discord_url=None,
        slack=False,
        slack_token=None,
        slack_channel=None,
        rocketchat=False,
        rocketchat_url=None,
    ):
        # Parameter variables
        self.github_token = github_token
        self.github_owner = github_owner
        self.github_state = github_state
        self.github_context = github_context
        self.wip = wip
        self.discord = discord
        self.discord_url = discord_url
        self.slack = slack
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.rocketchat = rocketchat
        self.rocketchat_url = rocketchat_url

        # Internal variables
        self.github_headers = {
            'Authorization': f'token {self.github_token}',
            'Content-Type': 'application/json; charset=utf-8',
        }

    def run(self):
        """Run the logic to get PR's from GitHub and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        repos = self.get_repos()
        pull_requests = self.get_pull_requests(repos)

        if pull_requests == []:
            message = 'No pull requests are available from GitHub.'
            LOGGER.info(message)

            return message  # TODO: Don't return early here, handle this better

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
        try:
            response = requests.get(
                f'https://api.github.com/{self.github_context}/{self.github_owner}/repos?per_page=100',
                headers=self.github_headers,
            )
            LOGGER.debug(response.text)
            LOGGER.info('GitHub repos retrieved!')
            if 'Not Found' in response.text:
                error = (
                    f'Could not retrieve GitHub repos due to bad parameter: {self.github_owner} |'
                    f' {self.github_context}.'
                )
                LOGGER.error(error)
                raise ValueError(error)
        except requests.exceptions.RequestException as response_error:
            LOGGER.error(f'Could not retrieve GitHub repos: {response_error}')
            raise requests.exceptions.RequestException(response_error)

        return response.json()

    def get_pull_requests(self, repos):
        """Grab all pull requests from each repo."""
        LOGGER.info('Bugging GitHub for pull requests...')
        pull_requests = []
        for repo in repos:
            try:
                pull_response = requests.get(
                    f'https://api.github.com/repos/{self.github_owner}/{repo["name"]}/pulls?state={self.github_state}&per_page=100',  # noqa
                    headers=self.github_headers,
                )
                if pull_response and pull_response.json():
                    LOGGER.debug(pull_response.text)
                    for single_pull_request in pull_response.json():
                        pull_requests.append(single_pull_request)
                else:
                    # Repo has no pull requests
                    continue
            except requests.exceptions.RequestException as response_error:
                LOGGER.error(f'Could not retrieve GitHub pull requests for {repo["name"]}: {response_error}')
                raise requests.exceptions.RequestException(response_error)
            except TypeError:
                error = (
                    f'Could not retrieve GitHub pull requests due to bad parameter: {self.github_owner} |'
                    f' {self.github_state}.'
                )
                LOGGER.error(error)
                raise TypeError(error)
        LOGGER.info('Pull requests retrieved!')

        return pull_requests

    def iterate_pull_requests(self, pull_requests):
        """Iterate through each pull request of a repo
        and build the message array.
        """
        message_array = []
        discord_message_array = []
        for pull_request in pull_requests:
            if not self.wip and 'WIP' in pull_request['title'].upper():
                continue
            else:
                message, discord_message = Messages.prepare_github_message(
                    pull_request, self.discord, self.slack, self.rocketchat
                )
                message_array.append(message)
                discord_message_array.append(discord_message)

        return message_array, discord_message_array
