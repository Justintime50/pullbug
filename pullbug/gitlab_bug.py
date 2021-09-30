import logging

import requests

from pullbug.logger import PullBugLogger
from pullbug.messages import Messages

LOGGER = logging.getLogger(__name__)


class GitlabBug:
    def __init__(
        self,
        gitlab_token=None,
        gitlab_url='https://gitlab.com/api/v4',
        gitlab_state='opened',
        gitlab_scope='all',
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
        self.gitlab_token = gitlab_token
        self.gitlab_url = gitlab_url
        self.gitlab_state = gitlab_state
        self.gitlab_scope = gitlab_scope
        self.wip = wip
        self.discord = discord
        self.discord_url = discord_url
        self.slack = slack
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.rocketchat = rocketchat
        self.rocketchat_url = rocketchat_url

    @staticmethod
    def run(self):
        """Run the logic to get MR's from GitLab and send that data via message."""
        PullBugLogger._setup_logging(LOGGER)
        merge_requests = self.get_merge_requests(self.gitlab_scope, self.gitlab_state)

        if merge_requests == []:
            message = 'No merge requests are available from GitLab.'
            LOGGER.info(message)
            return message

        message_preamble = '\n:bug: *The following merge requests on GitLab are still open and need your help!*\n'
        messages, discord_messages = self.iterate_merge_requests(
            merge_requests, self.wip, self.discord, self.slack, self.rocketchat
        )
        messages.insert(0, message_preamble)
        discord_messages.insert(0, message_preamble)
        if self.discord:
            Messages.send_discord_message(discord_messages)
        if self.slack:
            Messages.send_slack_message(messages)
        if self.rocketchat:
            Messages.send_rocketchat_message(messages)
        LOGGER.info(messages)

    @staticmethod
    def get_merge_requests(self):
        """Get all repos of the GITLAB_API_URL."""
        LOGGER.info('Bugging GitLab for merge requests...')
        try:
            response = requests.get(
                f"{self.gitlab_url}/merge_requests?scope={self.gitlab_scope}&state={self.gitlab_state}&per_page=100",
                headers={
                    'authorization': f'Bearer {self.gitlab_token}',
                },
            )
            LOGGER.debug(response.text)
            LOGGER.info('GitLab merge requests retrieved!')
            if 'does not have a valid value' in response.text:
                error = (
                    f'Could not retrieve GitLab merge requests due to bad parameter: {self.gitlab_scope} |'
                    f' {self.gitlab_state}.'
                )
                LOGGER.error(error)
                raise ValueError(error)
        except requests.exceptions.RequestException as response_error:
            LOGGER.error(f'Could not retrieve GitLab merge requests: {response_error}')
            raise requests.exceptions.RequestException(response_error)

        return response.json()

    @staticmethod
    def iterate_merge_requests(self, merge_requests):
        """Iterate through each merge request of a repo and build the message array."""
        message_array = []
        discord_message_array = []
        for merge_request in merge_requests:
            # TODO: There is a "work_in_progress" key in the response
            # that could be used? https://docs.gitlab.com/ee/api/merge_requests.html
            if not self.wip and 'WIP' in merge_request['title'].upper():
                continue
            else:
                message, discord_message = Messages.prepare_gitlab_message(
                    merge_request, self.discord, self.slack, self.rocketchat
                )
                message_array.append(message)
                discord_message_array.append(discord_message)

        return message_array, discord_message_array
