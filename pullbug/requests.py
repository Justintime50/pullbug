"""Pull Bug Version Control Requests Logic"""
import os
import json
import requests
from dotenv import load_dotenv

# Setup variables
load_dotenv()
GITLAB_API_KEY = os.getenv("GITLAB_API_KEY")
GITLAB_API_URL = os.getenv("GITLAB_API_URL")
GITLAB_SCOPE = os.getenv("GITLAB_SCOPE")
GITLAB_STATE = os.getenv("GITLAB_STATE")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_STATE = os.getenv("GITHUB_STATE")
IGNORE_WIP = os.getenv("IGNORE_WIP")

class Requests():
    """All version control functions are housed here"""
    @classmethod
    def github(cls):
        """Query your GitHub instance for Pull Requests"""
        # Grab all repos of the GITHUB_OWNER
        headers = {
            "Authorization": f"token {GITHUB_API_KEY}",
            "Content-Type": "application/json; charset=utf-8"
        }
        repos_response = requests.get(f"https://api.github.com/orgs/{GITHUB_OWNER}/repos", headers=headers).text
        repos = json.loads(repos_response)

        # Grab all pull requests from each repo
        message = "\n:bug: *The following pull requests on GitHub are still open and need your help!*\n"
        for repo in repos:
            pull_response = requests.get(f"https://api.github.com/repos/{GITHUB_OWNER}/{repo['name']}/pulls?state={GITHUB_STATE}", headers=headers).text
            pull_requests = json.loads(pull_response)

            for pull_request in pull_requests:
                # TODO: Check assignee array instead of a single record # pylint: disable=fixme
                # TODO: Check requested_reviewers array also # pylint: disable=fixme
                # If PR is a WIP, ignore it
                if IGNORE_WIP == 'true':
                    if 'wip' in pull_request['title'] or 'Wip' in pull_request['title'] or 'WIP' in pull_request['title']:
                        continue

                # Craft the message
                if pull_request['assignee'] is None:
                    user = "No assignee"
                else:
                    user = f"<{pull_request['assignee']['html_url']}|{pull_request['assignee']['login']}>"
                description = (pull_request['body'][:100] + '...') if len(pull_request['body']) > 100 else pull_request['body']
                message += f"\n:arrow_heading_up: *Pull Request:* <{pull_request['html_url']}|{pull_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

        return message

    @classmethod
    def gitlab(cls):
        """Query your GitLab instance for Merge Requests"""
        # Grab all repos
        headers = {
            "authorization": f"Bearer {GITLAB_API_KEY}"
        }
        response = requests.get(f"{GITLAB_API_URL}/merge_requests?scope={GITLAB_SCOPE}&state={GITLAB_STATE}", headers=headers)
        merge_requests = response.json()

        # Iterate over each merge request
        message = "\n:bug: *The following merge requests on GitLab are still open and need your help!*\n"
        for merge_request in merge_requests:
            # If MR is a WIP, ignore it
            if IGNORE_WIP == 'true':
                if 'wip' in merge_request['title'] or 'Wip' in merge_request['title'] or 'WIP' in merge_request['title']:
                    continue

            # Craft the message
            if merge_request['assignee'] is None:
                user = "No assignee"
            else:
                user = f"<{merge_request['assignee']['web_url']}|{merge_request['assignee']['username']}>"
            description = (merge_request['description'][:100] + '...') if len(merge_request['description']) > 100 else merge_request['description']
            message += f"\n:arrow_heading_up: *Merge Request:* <{merge_request['web_url']}|{merge_request['title']}>\n*Description:* {description}\n*Waiting on:* {user}\n"

        return message
