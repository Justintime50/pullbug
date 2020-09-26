import os
import json
import sys
import requests
from dotenv import load_dotenv

GITLAB_API_KEY = os.getenv('GITLAB_API_KEY')
GITLAB_API_URL = os.getenv('GITLAB_API_URL')
GITLAB_SCOPE = os.getenv('GITLAB_SCOPE')
GITLAB_STATE = os.getenv('GITLAB_STATE')
IGNORE_WIP = os.getenv('IGNORE_WIP')


class GitlabBug():
    @classmethod
    def run(cls):
        """Query your GitLab instance for Merge Requests
        """
        load_dotenv()
        print('Bugging GitLab...')
        # Grab all repos
        if not GITLAB_API_KEY:
            sys.exit('Not GitLab token set. Please correct and try again.')
        headers = {
            'authorization': f'Bearer {GITLAB_API_KEY}'
        }
        try:
            response = requests.get(
                f"{GITLAB_API_URL}/merge_requests?scope={GITLAB_SCOPE}" +
                f"&state={GITLAB_STATE}",
                headers=headers)
            merge_requests = response.json()
        except requests.exceptions.RequestException as response_error:
            sys.exit(response_error)

        # Iterate over each merge request
        message = '\n:bug: *The following merge requests on GitLab are' + \
            'still open and need your help!*\n'
        pulled = False
        for merge_request in merge_requests:
            # If MR is a WIP and this setting is enabled, ignore it
            if IGNORE_WIP == 'true':
                if 'wip' in merge_request['title'] or 'Wip' in merge_request['title'] \
                        or 'WIP' in merge_request['title']:
                    continue
            pulled = True

            # Craft the message
            if merge_request['assignee'] is None:
                user = "No assignee"
            else:
                user = f"<{merge_request['assignee']['web_url']}|" + \
                    f"{merge_request['assignee']['username']}>"
            # Truncate description after 100 characters
            description = (merge_request['description'][:100] + '...') if len(
                merge_request['description']) > 100 else merge_request['description']
            message += f"\n:arrow_heading_up: *Merge Request:* <{merge_request['web_url']}|" + \
                f"{merge_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

        if pulled is False:
            message = '\n:bug: Pull Bug has nothing to pull from GitLab!\n'

        return message
