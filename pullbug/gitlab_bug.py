import logging
import os

import requests

from pullbug.logger import PullBugLogger
from pullbug.messages import Messages

GITLAB_API_KEY = os.getenv('GITLAB_API_KEY')
GITLAB_API_URL = os.getenv('GITLAB_API_URL', 'https://gitlab.com/api/v4')
IGNORE_WIP = os.getenv('IGNORE_WIP')
GITLAB_HEADERS = {
    'authorization': f'Bearer {GITLAB_API_KEY}',
}
LOGGER = logging.getLogger(__name__)


class GitlabBug:
    @classmethod
    def run(cls, gitlab_scope='all', gitlab_state='opened', wip=False, discord=False, slack=False, rocketchat=False):
        """Run the logic to get MR's from GitLab and
        send that data via message.
        """
        PullBugLogger._setup_logging(LOGGER)
        merge_requests = cls.get_merge_requests(gitlab_scope, gitlab_state)

        if merge_requests == []:
            message = 'No merge requests are available from GitLab.'
            LOGGER.info(message)
            return message

        message_preamble = '\n:bug: *The following merge requests on GitLab are still open and need your help!*\n'
        messages, discord_messages = cls.iterate_merge_requests(merge_requests, wip, discord, slack, rocketchat)
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
    def get_merge_requests(cls, gitlab_scope, gitlab_state):
        """Get all repos of the GITLAB_API_URL."""
        LOGGER.info('Bugging GitLab for merge requests...')
        try:
            response = requests.get(
                f"{GITLAB_API_URL}/merge_requests?scope={gitlab_scope}&state={gitlab_state}&per_page=100",
                headers=GITLAB_HEADERS,
            )
            LOGGER.debug(response.text)
            LOGGER.info('GitLab merge requests retrieved!')
            if 'does not have a valid value' in response.text:
                error = (
                    f'Could not retrieve GitLab merge requests due to bad parameter: {gitlab_scope} | {gitlab_state}.'
                )
                LOGGER.error(error)
                raise ValueError(error)
        except requests.exceptions.RequestException as response_error:
            LOGGER.error(f'Could not retrieve GitLab merge requests: {response_error}')
            raise requests.exceptions.RequestException(response_error)

        return response.json()

    @classmethod
    def iterate_merge_requests(cls, merge_requests, wip, discord, slack, rocketchat):
        """Iterate through each merge request of a repo
        and build the message array.
        """
        message_array = []
        discord_message_array = []
        for merge_request in merge_requests:
            # TODO: There is a "work_in_progress" key in the response
            # that could be used? https://docs.gitlab.com/ee/api/merge_requests.html
            if not wip and 'WIP' in merge_request['title'].upper():
                continue
            else:
                message, discord_message = Messages.prepare_gitlab_message(merge_request, discord, slack, rocketchat)
                message_array.append(message)
                discord_message_array.append(discord_message)

        return message_array, discord_message_array
