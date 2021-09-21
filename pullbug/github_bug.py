import logging
import os

import requests

from pullbug.logger import PullBugLogger
from pullbug.messages import Messages

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Content-Type': 'application/json; charset=utf-8',
}
LOGGER = logging.getLogger(__name__)


class GithubBug:
    @classmethod
    def run(
        cls,
        github_owner=None,
        github_state='open',
        github_context='orgs',
        wip=False,
        discord=False,
        slack=False,
        rocketchat=False,
    ):
        """Run the logic to get PR's from GitHub and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        repos = cls.get_repos(github_owner, github_context)
        pull_requests = cls.get_pull_requests(repos, github_owner, github_state)

        if pull_requests == []:
            message = 'No pull requests are available from GitHub.'
            LOGGER.info(message)

            return message

        message_preamble = '\n:bug: *The following pull requests on GitHub are still open and need your help!*\n'
        messages, discord_messages = cls.iterate_pull_requests(pull_requests, wip, discord, slack, rocketchat)
        messages.insert(0, message_preamble)
        discord_messages.insert(0, message_preamble)
        if discord:
            Messages.send_discord_message(discord_messages)
        if slack:
            Messages.send_slack_message(messages)
        if rocketchat:
            Messages.send_rocketchat_message(messages)
        LOGGER.info(messages)

    @classmethod
    def get_repos(cls, github_owner, github_context=''):
        """Get all repos of the github_owner."""
        LOGGER.info('Bugging GitHub for repos...')
        try:
            response = requests.get(
                f'https://api.github.com/{github_context}/{github_owner}/repos?per_page=100', headers=GITHUB_HEADERS
            )
            LOGGER.debug(response.text)
            LOGGER.info('GitHub repos retrieved!')
            if 'Not Found' in response.text:
                error = f'Could not retrieve GitHub repos due to bad parameter: {github_owner} | {github_context}.'
                LOGGER.error(error)
                raise ValueError(error)
        except requests.exceptions.RequestException as response_error:
            LOGGER.error(f'Could not retrieve GitHub repos: {response_error}')
            raise requests.exceptions.RequestException(response_error)

        return response.json()

    @classmethod
    def get_pull_requests(cls, repos, github_owner, github_state):
        """Grab all pull requests from each repo."""
        LOGGER.info('Bugging GitHub for pull requests...')
        pull_requests = []
        for repo in repos:
            try:
                pull_response = requests.get(
                    f'https://api.github.com/repos/{github_owner}/{repo["name"]}/pulls?state={github_state}&per_page=100',  # noqa
                    headers=GITHUB_HEADERS,
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
                    f'Could not retrieve GitHub pull requests due to bad parameter: {github_owner} | {github_state}.'
                )
                LOGGER.error(error)
                raise TypeError(error)
        LOGGER.info('Pull requests retrieved!')

        return pull_requests

    @classmethod
    def iterate_pull_requests(cls, pull_requests, wip, discord, slack, rocketchat):
        """Iterate through each pull request of a repo
        and build the message array.
        """
        message_array = []
        discord_message_array = []
        for pull_request in pull_requests:
            if not wip and 'WIP' in pull_request['title'].upper():
                continue
            else:
                message, discord_message = Messages.prepare_github_message(pull_request, discord, slack, rocketchat)
                message_array.append(message)
                discord_message_array.append(discord_message)

        return message_array, discord_message_array
