import os
import requests
import logging
from pullbug.logger import PullBugLogger


GITLAB_API_KEY = os.getenv('GITLAB_API_KEY')
GITLAB_API_URL = os.getenv('GITLAB_API_URL', 'https://gitlab.com/api/v4')
IGNORE_WIP = os.getenv('IGNORE_WIP')
GITLAB_HEADERS = {
    'authorization': f'Bearer {GITLAB_API_KEY}'
}
LOGGER = logging.getLogger(__name__)


class GitlabBug():
    @classmethod
    def run(cls, gitlab_scope, gitlab_state, wip):
        """Run the logic to get MR's from GitLab and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        merge_requests = cls.get_repos(gitlab_scope, gitlab_state)
        cls.iterate_merge_requests(merge_requests, wip)
        # TODO: Fix message
        message = '\n:bug: *The following merge requests on GitLab ar still open and need your help!*\n'
        # TODO: Send message

    @classmethod
    def get_merge_requests(cls, gitlab_scope, gitlab_state):
        """Get all repos of the GITLAB_API_URL.
        """
        LOGGER.info('Bugging GitLab for merge requests...')
        try:
            response = requests.get(
                f"{GITLAB_API_URL}/merge_requests?scope={gitlab_scope}&state={gitlab_state}",
                headers=GITLAB_HEADERS
            )
            LOGGER.info('GitLab merge requests retrieved!')
        except requests.exceptions.RequestException as response_error:
            LOGGER.warning(
                f'Could not retrieve GitLab merge requests: {response_error}'
            )
            raise requests.exceptions.RequestException(response_error)
        return response.json()

    @classmethod
    def iterate_merge_requests(cls, merge_requests, wip):
        """Iterate through each merge request and send
        a message to Slack if a PR exists.
        """
        final_message = ''
        for merge_request in merge_requests:
            if not wip and 'WIP' in merge_request['title'].upper():
                continue
            else:
                message = cls.prepare_message(merge_request)
                final_message += message
        return final_message

    @classmethod
    def prepare_message(cls, merge_request):
        """Prepare the message with merge request data.
        """
        if merge_request['assignee'] is None:
            user = "No assignee"
        else:
            user = f"<{merge_request['assignee']['web_url']}|{merge_request['assignee']['username']}>"

        # Truncate description after 100 characters
        description = (merge_request['description'][:100] +
                       '...') if len(merge_request['description']) > 100 else merge_request['description']
        message = f"\n:arrow_heading_up: *Merge Request:* <{merge_request['web_url']}|" + \
            f"{merge_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

        return message
