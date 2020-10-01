import os
import requests
import logging
from pullbug.logger import PullBugLogger
from pullbug.messages import Messages

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_OWNER = os.getenv('GITHUB_OWNER')
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Content-Type': 'application/json; charset=utf-8'
}
LOGGER = logging.getLogger(__name__)


class GithubBug():
    @classmethod
    def run(cls, github_owner, github_state, github_context, wip, slack, rocketchat):
        """Run the logic to get PR's from GitHub and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        repos = cls.get_repos(github_owner, github_context)
        pull_requests = cls.get_pull_requests(repos, github_owner, github_state)
        message_preamble = ''
        if pull_requests == []:
            message = 'No pull requests are available from GitHub.'
            LOGGER.info(message)
            return message
        message_preamble = '\n:bug: *The following pull requests on GitHub are still open and need your help!*\n'
        pull_request_messages = cls.iterate_pull_requests(pull_requests, wip)
        final_message = message_preamble + pull_request_messages
        if slack:
            Messages.slack(final_message)
        if rocketchat:
            Messages.rocketchat(final_message)
        LOGGER.info(final_message)

    @classmethod
    def get_repos(cls, github_owner, github_context=''):
        """Get all repos of the GITHUB_OWNER.
        """
        LOGGER.info('Bugging GitHub for repos...')
        try:
            repos_response = requests.get(
                f'https://api.github.com/{github_context}/{github_owner}/repos?per_page=100',
                headers=GITHUB_HEADERS
            )
            LOGGER.debug(repos_response.text)
            if 'Not Found' in repos_response.text:
                error = f'Could not retrieve GitHub repos due to bad parameter: {github_owner} | {github_context}.'
                LOGGER.warning(error)
                raise ValueError(error)
            LOGGER.info('GitHub repos retrieved!')
        except requests.exceptions.RequestException as response_error:
            LOGGER.warning(
                f'Could not retrieve GitHub repos: {response_error}'
            )
            raise requests.exceptions.RequestException(response_error)
        return repos_response.json()

    @classmethod
    def get_pull_requests(cls, repos, github_owner, github_state):
        """Grab all pull requests from each repo.
        """
        LOGGER.info('Bugging GitHub for pull requests...')
        pull_requests = []
        for repo in repos:
            try:
                pull_response = requests.get(
                    f'https://api.github.com/repos/{github_owner}/{repo["name"]}/pulls?state={github_state}&per_page=100',  # noqa
                    headers=GITHUB_HEADERS
                )
                LOGGER.debug(pull_response.text)
                if pull_response.json():
                    for single_pull_request in pull_response.json():
                        pull_requests.append(single_pull_request)
                else:
                    continue
            except requests.exceptions.RequestException as response_error:
                LOGGER.warning(
                    f'Could not retrieve GitHub pull requests for {repo["name"]}: {response_error}'
                )
                raise requests.exceptions.RequestException(response_error)
            except TypeError:
                error = f'Could not retrieve GitHub pull requests due to bad parameter: {github_owner} | {github_state}.'  # noqa
                LOGGER.warning(error)
                raise TypeError(error)
        LOGGER.info('Pull requests retrieved!')
        return pull_requests

    @classmethod
    def iterate_pull_requests(cls, pull_requests, wip):
        """Iterate through each pull request of a repo
        and send a message to Slack if a PR exists.
        """
        final_message = ''
        for pull_request in pull_requests:
            if not wip and 'WIP' in pull_request['title'].upper():
                continue
            else:
                message = cls.prepare_message(pull_request)
                final_message += message
        return final_message

    @classmethod
    def prepare_message(cls, pull_request):
        """Prepare the message with pull request data.
        """
        # TODO: Check requested_reviewers array also
        try:
            if pull_request['assignees'][0]['login']:
                users = ''
                for assignee in pull_request['assignees']:
                    user = f"<{assignee['html_url']}|{assignee['login']}>"
                    users += user + ' '
            else:
                users = 'No assignee'
        except IndexError:
            users = 'No assignee'

        # Truncate description after 120 characters
        description = (pull_request['body'][:120] + '...') if len(pull_request
                                                                  ['body']) > 120 else pull_request['body']
        message = f"\n:arrow_heading_up: *Pull Request:* <{pull_request['html_url']}|" + \
            f"{pull_request['title']}>\n*Description:* {description}\n*Waiting on:* {users}\n"

        return message
