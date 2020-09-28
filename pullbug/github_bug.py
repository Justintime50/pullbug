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
        if pull_requests:
            message_preamble = '\n:bug: *The following pull requests on GitHub are still open and need your help!*\n'
        pull_request_messages = cls.iterate_pull_requests(pull_requests, wip)
        final_message = message_preamble + pull_request_messages
        if slack:
            Messages.slack(final_message)
        elif rocketchat:
            Messages.rocketchat(final_message)
        LOGGER.info(final_message)

    @classmethod
    def get_repos(cls, github_owner, github_context):
        """Get all repos of the GITHUB_OWNER.
        """
        LOGGER.info('Bugging GitHub for repos...')
        try:
            repos_response = requests.get(
                f'https://api.github.com/{github_context}/{github_owner}/repos?per_page=100',
                headers=GITHUB_HEADERS
            )
            # LOGGER.debug(repos_response.text)
            LOGGER.info('GitHub repos retrieved!')
        except requests.exceptions.RequestException as response_error:
            LOGGER.warning(
                f'Could not retrieve GitHub repos: {response_error}'
            )
            raise requests.exceptions.RequestException(response_error)
        return repos_response.json()

    @ classmethod
    def get_pull_requests(cls, repos, github_owner, github_state):
        """Grab all pull requests from each repo.
        """
        LOGGER.info('Bugging GitHub for pull requests...')
        pull_requests = []
        for repo in repos:
            try:
                # TODO: Catch invalid github owners as a bad owner here will throw `TypeError` for the repo name index
                pull_response = requests.get(
                    f'https://api.github.com/repos/{github_owner}/{repo["name"]}/pulls?state={github_state}?per_page=100',  # noqa
                    headers=GITHUB_HEADERS
                )
                # TODO: This does not break out multiple pull requests from the same
                # repo and will only pull the first, iterate over each
                LOGGER.debug(pull_response.text)
                if pull_response.json():
                    pull_requests.append(pull_response.json())
                else:
                    continue
            except requests.exceptions.RequestException as response_error:
                LOGGER.warning(
                    f'Could not retrieve GitHub pull requests for {repo["name"]}: {response_error}'
                )
                raise requests.exceptions.RequestException(response_error)
        LOGGER.info('Pull requests retrieved!')
        # print(pull_requests)
        return pull_requests

    @ classmethod
    def iterate_pull_requests(cls, pull_requests, wip):
        """Iterate through each pull request of a repo
        and send a message to Slack if a PR exists.
        """
        final_message = ''
        for pull_request in pull_requests:
            # TODO: Check assignee array instead of a single record  # noqa
            # TODO: Check requested_reviewers array also  # noqa
            if not wip and 'WIP' in pull_request[0]['title'].upper():
                continue
            else:
                message = cls.prepare_message(pull_request)
                final_message += message
        return final_message

    @ classmethod
    def prepare_message(cls, pull_request):
        """Prepare the message with pull request data.
        """
        if pull_request[0]['assignee'] is None:
            user = "No assignee"
        else:
            user = f"<{pull_request[0]['assignee']['html_url']}|{pull_request[0]['assignee']['login']}>"

        # Truncate description after 100 characters
        description = (pull_request[0]['body'][:100] + '...') if len(pull_request[0]
                                                                     ['body']) > 100 else pull_request[0]['body']
        message = f"\n:arrow_heading_up: *Pull Request:* <{pull_request[0]['html_url']}|" + \
            f"{pull_request[0]['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

        return message
