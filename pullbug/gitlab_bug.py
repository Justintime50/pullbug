import os
import requests
import logging
from pullbug.logger import PullBugLogger
from pullbug.messages import Messages


GITLAB_API_KEY = os.getenv('GITLAB_API_KEY')
GITLAB_API_URL = os.getenv('GITLAB_API_URL', 'https://gitlab.com/api/v4')
IGNORE_WIP = os.getenv('IGNORE_WIP')
GITLAB_HEADERS = {
    'authorization': f'Bearer {GITLAB_API_KEY}'
}
LOGGER = logging.getLogger(__name__)


class GitlabBug():
    @classmethod
    def run(cls, gitlab_scope, gitlab_state, wip, slack, rocketchat):
        """Run the logic to get MR's from GitLab and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        merge_requests = cls.get_merge_requests(gitlab_scope, gitlab_state)
        message_preamble = ''
        if merge_requests == []:
            message = 'No merge requests are available from GitLab.'
            LOGGER.info(message)
            return message
        message_preamble = '\n:bug: *The following merge requests on GitLab ar still open and need your help!*\n'
        merge_request_messages = cls.iterate_merge_requests(merge_requests, wip)
        final_message = message_preamble + merge_request_messages
        if slack:
            Messages.slack(final_message)
        if rocketchat:
            Messages.rocketchat(final_message)
        LOGGER.info(final_message)

    @classmethod
    def get_merge_requests(cls, gitlab_scope, gitlab_state):
        """Get all repos of the GITLAB_API_URL.
        """
        LOGGER.info('Bugging GitLab for merge requests...')
        try:
            response = requests.get(
                f"{GITLAB_API_URL}/merge_requests?scope={gitlab_scope}&state={gitlab_state}&per_page=100",
                headers=GITLAB_HEADERS
            )
            print(response.json())
            LOGGER.info('GitLab merge requests retrieved!')
            if 'does not have a valid value' in response.text:
                error = f'Could not retrieve GitLab merge requests due to bad parameter: {gitlab_scope} | {gitlab_state}.'  # noqa
                LOGGER.warning(error)
                raise ValueError(error)
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
            # TODO: There is a "work_in_progress" key in the response
            # that could be used? https://docs.gitlab.com/ee/api/merge_requests.html
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
        try:
            if merge_request['assignees'][0]['username']:
                users = ''
                for assignee in merge_request['assignees']:
                    user = f"<{assignee['web_url']}|{assignee['username']}>"
                    users += user + ' '
            else:
                users = 'No assignee'
        except IndexError:
            users = 'No assignee'

        # Truncate description after 120 characters
        description = (merge_request['description'][:120] +
                       '...') if len(merge_request['description']) > 120 else merge_request['description']
        message = f"\n:arrow_heading_up: *Merge Request:* <{merge_request['web_url']}|" + \
            f"{merge_request['title']}>\n*Description:* {description}\n*Waiting on:* {users}\n"

        return message
