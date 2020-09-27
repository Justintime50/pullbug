import os
import requests
import logging
from pullbug.logger import PullBugLogger


GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_OWNER = os.getenv('GITHUB_OWNER')
GITHUB_STATE = os.getenv('GITHUB_STATE', 'open')
GITHUB_CONTEXT = os.getenv('GITHUB_CONTEXT', 'orgs')
IGNORE_WIP = os.getenv('IGNORE_WIP')
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Content-Type': 'application/json; charset=utf-8'
}
LOGGER = logging.getLogger(__name__)


class GithubBug():
    @classmethod
    def run(cls):
        """Run the logic to get PR's from GitHub and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        repos = cls.get_repos()
        pull_requests = cls.get_pull_requests(repos)
        # TODO: Fix the message (re-introduce the pulled = True variable)

        if pull_requests:
            message = '\n:bug: *The following pull requests on GitHub are still open and need your help!*\n'
        cls.iterate_pull_requests(pull_requests)
        # TODO: Send message

    @classmethod
    def get_repos(cls):
        """Get all repos of the GITHUB_OWNER.
        """
        LOGGER.info('Bugging GitHub for repos...')
        try:
            repos_response = requests.get(
                f'https://api.github.com/{GITHUB_CONTEXT}/{GITHUB_OWNER}/repos',
                headers=GITHUB_HEADERS
            )
            LOGGER.info('GitHub repos retrieved!')
        except requests.exceptions.RequestException as response_error:
            LOGGER.warning(
                f'Could not retrieve GitHub repos: {response_error}'
            )
            raise requests.exceptions.RequestException(response_error)
        return repos_response.json()

    @classmethod
    def get_pull_requests(cls, repos):
        """Grab all pull requests from each repo.
        """
        LOGGER.info('Bugging GitHub for pull requests...')
        pull_requests = []
        for repo in repos:
            try:
                pull_response = requests.get(
                    f"https://api.github.com/repos/{GITHUB_OWNER}/{repo['name']}/pulls?state={GITHUB_STATE}",
                    headers=GITHUB_HEADERS
                )
                LOGGER.info(f"{repo['name']} bugged!")
                pull_requests.append(pull_response)
            except requests.exceptions.RequestException as response_error:
                LOGGER.warning(
                    f'Could not retrieve GitHub pull requests for {repo["name"]}: {response_error}'
                )
                raise requests.exceptions.RequestException(response_error)
        return pull_requests

    @classmethod
    def iterate_pull_requests(cls, pull_requests):
        """Iterate through each pull request of a repo
        and send a message to Slack if a PR exists.
        """
        final_message = ''
        for pull_request in pull_requests:
            # TODO: Check assignee array instead of a single record  # noqa
            # TODO: Check requested_reviewers array also  # noqa
            if IGNORE_WIP != 'true' and 'WIP' not in pull_request['title'].upper():
                message = cls.prepare_message(pull_request)
                final_message += message
        return final_message

    @classmethod
    def prepare_message(cls, pull_request):
        """Prepare the message with pull request data.
        """
        if pull_request['assignee'] is None:
            user = "No assignee"
        else:
            user = f"<{pull_request['assignee']['html_url']}|{pull_request['assignee']['login']}>"

        # Truncate description after 100 characters
        description = (pull_request['body'][:100] + '...') if len(pull_request['body']) > 100 else pull_request['body']
        message = f"\n:arrow_heading_up: *Pull Request:* <{pull_request['html_url']}|" + \
            f"{pull_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

        return message
