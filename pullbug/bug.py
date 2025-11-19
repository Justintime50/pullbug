import os
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
)

import woodchips
from github import (
    Auth,
    Github,
    Issue,
    NamedUser,
    PaginatedList,
    PullRequest,
)

from pullbug.messages import (
    prepare_issues_message,
    prepare_pulls_message,
    send_discord_message,
    send_slack_message,
)


GITHUB_STATE_CHOICES = Literal[
    "all",
    "closed",
    "open",
]
GITHUB_CONTEXT_CHOICES = Literal[
    "users",
    "orgs",
]

DEFAULT_LOG_LEVEL = "info"
LOG_LEVEL_CHOICES = Literal[
    "notset",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
]

DEFAULT_BASE_URL = "https://api.github.com"
DEFAULT_LOCATION = os.path.join("~", "pullbug")

LOGGER_NAME = "pullbug"


class Pullbug:
    def __init__(  # nosec hardcoded_password_default
        self,
        github_owner: str,
        github_token: Optional[str] = None,
        github_state: GITHUB_STATE_CHOICES = "open",
        github_context: GITHUB_CONTEXT_CHOICES = "users",
        pulls: bool = False,
        issues: bool = False,
        discord: bool = False,
        discord_url: str = "",
        slack: bool = False,
        slack_token: str = "",
        slack_channel: str = "",
        repos: str = "",
        drafts: bool = False,
        location: str = DEFAULT_LOCATION,
        base_url: str = DEFAULT_BASE_URL,
        log_level: str = DEFAULT_LOG_LEVEL,
        disable_descriptions: bool = False,
        quiet: bool = False,
    ):
        # Parameter variables
        self.github_owner = github_owner
        self.github_token = github_token
        self.github_state = github_state
        self.github_context = github_context
        self.pulls = pulls
        self.issues = issues
        self.discord = discord
        self.discord_url = discord_url
        self.slack = slack
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.repos = [repo.strip() for repo in repos.lower().split(",")] if repos else ""
        self.drafts = drafts
        self.location = os.path.expanduser(location)
        self.base_url = base_url
        self.log_level = log_level
        self.disable_descriptions = disable_descriptions
        self.quiet = quiet

        # Internal variables
        if github_token:
            self.github_instance = Github(auth=Auth.Token(github_token), base_url=self.base_url)
        else:
            self.github_instance = Github(base_url=self.base_url)

    def run(self):
        """Run the logic to get PR's from GitHub and send that data via message."""
        self.setup_logger()
        logger = woodchips.get(LOGGER_NAME)
        logger.info("Running Pullbug...")
        self._run_missing_checks()

        repos = self.get_repos()

        if self.pulls:
            pull_requests = self.get_pull_requests(repos)
            slack_pull_messages, discord_pull_messages = self.iterate_pull_requests(pull_requests)

            # Check if there are pull requests and available messages to send (eg: filtering for drafts)
            if pull_requests != [] and slack_pull_messages:
                found_pull_requests = True
                pull_message_preamble = "\n:bug: *The following GitHub pull requests still need your help!*\n"
                slack_pull_messages.insert(0, pull_message_preamble)
                discord_pull_messages.insert(0, pull_message_preamble)
            else:
                found_pull_requests = False
                slack_pull_messages = discord_pull_messages = ["\n:bug: *Pullbug found no ready pull requests!*\n"]
                logger.info(slack_pull_messages[0])

            if found_pull_requests is False and self.quiet:
                # The user doesn't want messages sent when there are no pull requests
                pass
            else:
                self.send_messages(slack_pull_messages, discord_pull_messages)

        if self.issues:
            issues = self.get_issues(repos)
            slack_issue_messages, discord_issue_messages = self.iterate_issues(issues)

            # Check if there are issues and available messages to send
            if issues != [] and slack_issue_messages:
                found_issues = True
                issue_message_preamble = "\n:bug: *The following GitHub issues still need your help!*\n"
                slack_issue_messages.insert(0, issue_message_preamble)
                discord_issue_messages.insert(0, issue_message_preamble)
            else:
                found_issues = False
                slack_issue_messages = discord_issue_messages = ["\n:bug: *Pullbug found no open issues!*\n"]
                logger.info(slack_issue_messages[0])

            if found_issues is False and self.quiet:
                # The user doesn't want messages sent when there are no issues
                pass
            else:
                self.send_messages(slack_issue_messages, discord_issue_messages)

        logger.info("Pullbug finished bugging!")

    def setup_logger(self):
        """Setup a `woodchips` logger for the project."""
        logger = woodchips.Logger(
            name=LOGGER_NAME,
            level=self.log_level,
        )
        logger.log_to_console()
        logger.log_to_file(location=os.path.join(self.location, "logs"))

    def _run_missing_checks(self):
        """Check that values are set based on configuration before proceeding."""
        if not self.pulls and not self.issues:
            self._throw_missing_error("pulls/issues")
        if self.discord and not self.discord_url:
            self._throw_missing_error("discord_url")
        if self.slack and not self.slack_token:
            self._throw_missing_error("slack_token")
        if self.slack and not self.slack_channel:
            self._throw_missing_error("slack_channel")

    @staticmethod
    def _throw_missing_error(missing_flag: str):
        """Raise an error based on what env variables are missing."""
        logger = woodchips.get(LOGGER_NAME)
        message = f"No {missing_flag} set. Please correct and try again."
        logger.critical(message)

        raise ValueError(message)

    def get_repos(self) -> PaginatedList.PaginatedList:
        """Get all repos of the `github_owner`."""
        logger = woodchips.get(LOGGER_NAME)

        logger.info("Bugging GitHub for repos...")

        repos: Any  # Fixes `mypy` type checking, repos are either a Python list or a GitHub PaginatedList

        if self.github_context == "orgs":
            repos = self.github_instance.get_organization(self.github_owner).get_repos()
        elif self.github_context == "users":
            repos = self.github_instance.get_user(self.github_owner).get_repos()

        # If the user specified a list of repos, let's filter them here
        if self.repos:
            filtered_repos = filter(lambda repo: repo.name.lower() in self.repos, repos)
            repos = list(filtered_repos)

        logger.info("GitHub repos retrieved!")

        return repos

    def get_pull_requests(self, repos: PaginatedList.PaginatedList) -> List[PullRequest.PullRequest]:
        """Grab all pull requests from each repo and return a flat list of pull requests."""
        logger = woodchips.get(LOGGER_NAME)

        logger.info("Bugging GitHub for pull requests...")
        pull_requests = []

        for repo in repos:
            repo_pull_requests = repo.get_pulls(state=self.github_state)
            if repo_pull_requests:
                pull_requests.append(repo_pull_requests)
            else:
                # Repo has no pull requests
                continue

        flat_pull_requests_list: List = [
            pull_request for pull_request in pull_requests for pull_request in pull_request
        ]

        logger.info("Pull requests retrieved!")

        return flat_pull_requests_list

    def get_pull_request_reviews(self, pull_request: PullRequest.PullRequest) -> Dict[str, List[NamedUser.NamedUser]]:
        """Grab all pull request reviews of a single pull request.

        We then break down these reviews into `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED` as the `state`.
        """
        logger = woodchips.get(LOGGER_NAME)

        logger.debug(f"Bugging GitHub for pull request reviews of {pull_request.title}...")

        pull_request_reviews_by_category: Dict[str, List[NamedUser.NamedUser]] = {
            "users_who_approved": [],
            "users_who_requested_changes": [],
            "users_who_were_dismissed": [],
        }

        pull_request_reviews = pull_request.get_reviews()

        for pull_request_review in pull_request_reviews:
            pull_request_review_user = pull_request_review.user
            if pull_request_review and pull_request_review.state == "APPROVED":
                pull_request_reviews_by_category["users_who_approved"].append(pull_request_review_user)
            elif pull_request_review and pull_request_review.state == "CHANGES_REQUESTED":
                pull_request_reviews_by_category["users_who_requested_changes"].append(pull_request_review_user)
            elif pull_request_review and pull_request_review.state == "DISMISSED":
                pull_request_reviews_by_category["users_who_were_dismissed"].append(pull_request_review_user)

        logger.debug(f"Pull request reviews retrieved for {pull_request.title}!")

        return pull_request_reviews_by_category

    def get_issues(self, repos: PaginatedList.PaginatedList) -> List[Issue.Issue]:
        """Grab all issues from each repo and return a flat list of issues."""
        logger = woodchips.get(LOGGER_NAME)

        logger.info("Bugging GitHub for issues...")
        issues = []

        for repo in repos:
            repo_issues = repo.get_issues(state=self.github_state)
            if repo_issues:
                issues.append(repo_issues)
            else:
                # Repo has no issues
                continue

        # GitHub's v3 API apparently treats pull requests as issues, filter them out here
        # Docs: https://docs.github.com/en/rest/reference/issues#list-repository-issues
        flat_issues_list = [issue for issue in issues for issue in issue if not issue.pull_request]

        logger.info("Issues retrieved!")

        return flat_issues_list

    def iterate_pull_requests(self, pull_requests: PaginatedList.PaginatedList) -> Tuple[List[str], List[str]]:
        """Iterate through each pull request of a repo and build the message array."""
        slack_message_array = []
        discord_message_array = []

        for pull_request in pull_requests:
            if pull_request.draft and not self.drafts:
                # Exclude drafts if the user doesn't want them included
                continue
            else:
                # Only reviewers requested who haven't approved, requested changes, or been dismissed will
                # be returned here.
                reviewers = pull_request.get_review_requests()
                # This is a hack to get around this bug: https://github.com/PyGithub/PyGithub/issues/2053
                # TODO: Change this from `.get_page(0) != []` to `.totalCount != 0` once `PyGithub > 1.55` is out
                user_reviewers_requested = reviewers[0] if reviewers[0].get_page(0) != [] else []
                team_reviewers_requested = reviewers[1] if reviewers[1].get_page(0) != [] else []

                reviewers_requested = []
                for user in user_reviewers_requested:
                    reviewers_requested.append(user)
                for team in team_reviewers_requested:
                    reviewers_requested.append(team)

                # We need to separately get reviewers who approved, requested changes, or got dismissed
                pull_request_reviews_by_category = self.get_pull_request_reviews(pull_request)
                users_who_approved = pull_request_reviews_by_category["users_who_approved"]
                users_who_requested_changes = pull_request_reviews_by_category["users_who_requested_changes"]
                users_who_were_dismissed = pull_request_reviews_by_category["users_who_were_dismissed"]

                message, discord_message = prepare_pulls_message(
                    pull_request=pull_request,
                    reviewers=reviewers_requested,
                    users_who_approved=users_who_approved,
                    users_who_requested_changes=users_who_requested_changes,
                    users_who_were_dismissed=users_who_were_dismissed,
                    disable_descriptions=self.disable_descriptions,
                )
                slack_message_array.append(message)
                discord_message_array.append(discord_message)

        return slack_message_array, discord_message_array

    def iterate_issues(self, issues: PaginatedList.PaginatedList) -> Tuple[List[str], List[str]]:
        """Iterate through each issue of a repo and build the message array."""
        slack_message_array = []
        discord_message_array = []

        for issue in issues:
            slack_message, discord_message = prepare_issues_message(issue, self.disable_descriptions)
            slack_message_array.append(slack_message)
            discord_message_array.append(discord_message)

        return slack_message_array, discord_message_array

    def send_messages(self, slack_messages: List[str], discord_messages: List[str]):
        """Sends a message to the messaging platforms requested (can be multiple at once)."""
        logger = woodchips.get(LOGGER_NAME)

        if self.discord:
            send_discord_message(discord_messages, self.discord_url)
        if self.slack:
            send_slack_message(slack_messages, self.slack_token, self.slack_channel)

        logger.info(slack_messages)
