"""Pull Bug Version Control Requests Logic"""
import os
import json
import sys
import requests
from dotenv import load_dotenv


class Git():
    """All version control functions are housed here"""
    # Setup variables
    load_dotenv()
    GITLAB_API_KEY = os.getenv('GITLAB_API_KEY')
    GITLAB_API_URL = os.getenv('GITLAB_API_URL')
    GITLAB_SCOPE = os.getenv('GITLAB_SCOPE')
    GITLAB_STATE = os.getenv('GITLAB_STATE')
    GITHUB_API_KEY = os.getenv('GITHUB_API_KEY')
    GITHUB_OWNER = os.getenv('GITHUB_OWNER')
    GITHUB_STATE = os.getenv('GITHUB_STATE')
    IGNORE_WIP = os.getenv('IGNORE_WIP')

    @classmethod
    def github(cls):
        """Query your GitHub instance for Pull Requests"""
        # Grab all repos of the GITHUB_OWNER
        print('Bugging GitHub...')
        if not Git.GITHUB_API_KEY:
            sys.exit('No GitHub token set. Please correct and try again.')
        headers = {
            'Authorization': f'token {Git.GITHUB_API_KEY}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        try:
            repos_response = requests.get(
                f'https://api.github.com/orgs/{Git.GITHUB_OWNER}/repos', headers=headers).text
            repos = json.loads(repos_response)
        except requests.exceptions.RequestException as response_error:
            sys.exit(response_error)

        # Grab all pull requests from each repo
        message = '\n:bug: *The following pull requests on GitHub are still open and' + \
            'need your help!*\n'
        pulled = False
        for repo in repos:
            try:
                pull_response = requests.get(
                    f"https://api.github.com/repos/{Git.GITHUB_OWNER}/{repo['name']}/" +
                    f"pulls?state={Git.GITHUB_STATE}", headers=headers).text
                pull_requests = json.loads(pull_response)
                print(f"{repo['name']} bugged!")
            except requests.exceptions.RequestException as response_error:
                sys.exit(response_error)

            for pull_request in pull_requests:
                # TODO: Check assignee array instead of a single record # pylint: disable=fixme
                # TODO: Check requested_reviewers array also # pylint: disable=fixme
                # If PR is a WIP and this setting is enabled, ignore it
                if Git.IGNORE_WIP == 'true':
                    if 'wip' in pull_request['title'] or 'Wip' in pull_request['title'] \
                            or 'WIP' in pull_request['title']:
                        continue
                pulled = True

                # Craft the message
                if pull_request['assignee'] is None:
                    user = "No assignee"
                else:
                    user = f"<{pull_request['assignee']['html_url']}|" \
                        f"{pull_request['assignee']['login']}>"
                # Truncate description after 100 characters
                description = (pull_request['body'][:100] + '...') if len(
                    pull_request['body']) > 100 else pull_request['body']
                message += f"\n:arrow_heading_up: *Pull Request:* <{pull_request['html_url']}|" + \
                    f"{pull_request['title']}>\n*Description:* {description}\n" + \
                    f"*Waiting on:* {user}\n"

        if pulled is False:
            message = '\n:bug: Pull Bug has nothing to pull from GitHub!\n'

        return message

    @classmethod
    def gitlab(cls):
        """Query your GitLab instance for Merge Requests"""
        print('Bugging GitLab...')
        # Grab all repos
        if not Git.GITLAB_API_KEY:
            sys.exit('Not GitLab token set. Please correct and try again.')
        headers = {
            'authorization': f'Bearer {Git.GITLAB_API_KEY}'
        }
        try:
            response = requests.get(
                f"{Git.GITLAB_API_URL}/merge_requests?scope={Git.GITLAB_SCOPE}" +
                f"&state={Git.GITLAB_STATE}",
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
            if Git.IGNORE_WIP == 'true':
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
