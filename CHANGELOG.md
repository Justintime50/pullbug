# CHANGELOG

## v6.0.0 (2025-11-18)

- Drops support for Python 3.8 and 3.9
- Flattens `messages.py` since the `Message` class is not necessary
- Bumps deps

## v5.1.3 (2024-07-16)

- Fixes Discord message links to appear correctly (previously the wrong syntax was used or has since changed on the Discord side and inline links weren't getting wrapped properly)

## v5.1.2 (2023-10-25)

- Swaps the deprecated `slackclient` for the new `slack_sdk`, no user impact expected

## v5.1.1 (2023-08-27)

- Expand paths for user-supplied `--location` strings. This now allows for spaces in paths and proper expansion of home directories (eg: `~`)

## v5.1.0 (2023-08-24)

- Adds `--version` CLI flag
- Bumps dependencies

## v5.0.1 (2023-06-29)

- Pins the correct version of `PyGithub` to properly use the new `Auth` object

## v5.0.0 (2023-06-26)

- Drops support for Python 3.7
- Adds a new `--quiet` flag which will not send messages if no PRs or issues can be found

## v4.5.0 (2022-10-25)

- Adds `--disable_descriptions` flag which will not populate the description in messages

## v4.4.0 (2022-08-08)

- Adds support for team reviewers to populate in messages

## v4.3.0 (2022-05-16)

- Adds `log_level` flag allowing the user to specify a log level of their choice (defaults to `INFO`)

## v4.2.1 (2021-02-21)

- Filters out pull requests from the returned issues. Apparently GitHub's v3 API returns pull requests in the response of a list of issues, see <https://docs.github.com/en/rest/reference/issues#list-repository-issues> for details

## v4.2.0 (2022-02-21)

- Messages now include dismissed reviewers under the `Reviewers` section
- Reviewers are now a set to avoid duplicates (such as multiple "changes requested" or "dismissed" reviews)

## v4.1.0 (2022-02-10)

- Adds reviewers to messages who have approved or requested changes. Previously, only reviewers that had been requested but had not reviewed would show in messages. Depending on the status of the review, an appropriate emoji will show in the message to signify what the user did for their review
- Various other small improvements to message building

## v4.0.3 (2022-02-09)

- Fixes a bug where the "no pull requests" message wouldn't be used properly when draft pull requests were present but not requested as the check for pull requests happened before the filtering occured

## v4.0.2 (2022-02-08)

- Fixes a bug where if both pull request and issue flags were used at the same time that pull request data would bleed into the issue messages due to reassignment of variables (variables have since been distinguished from one another)
- Bumps dev deps

## v4.0.1 (2022-01-31)

- Fix the index error on retrieving requested reviewers

## v4.0.0 (2022-01-30)

- Added the `author` to the messages
- Switched from `assignees` to `requested reviewers` for the `waiting on` portion of the message
- Added `base_url` paremeter to specify an enterprise GitHub instance if necessary
- Reworked the `github_token` logic to allow for better unauthenticated usage when no GitHub token is passed
- Removed support to send messages to `Rocket.Chat`
- Renamed all occurances of `GithubBug` to `Pullbug` as Gitlab was removed previously and the distinction between platforms was no longer needed. Also renamed the `github_bug` module to `bug` and made various functions used only for the tool private. Also corrects the `Messages` class name to the singular `Message`

## v3.2.1 (2022-01-26)

- Moved `typed_extensions` to the list of requirements from dev requirements since we import the package in code, fixes `module not found` error

## v3.2.0 (2021-12-07)

- `github_owner` is now required, was previously optional by mistake
- `github_context` now has a default of `users` restoring previously changed default behavior
- Fixes a bug where iterating over issues may have not worked due to a syntax error
- Adds `mypy` type checking
  - Fixes some typing errors around default values when no parameter is passed (changes strings from `None` to an empty string to better represent the type across the whole app.)

## v3.1.0 (2021-11-25)

- Use `woodchips` for logging
- Adds missing `__all__` variable for importing
- Adds Python type hinting, stronger tests
- Small bug fixes

## v3.0.0 (2021-10-06)

### Breaking Changes

- Completely removes `GitLab` support as I no longer use the platform and can't reliably test its functionality nor have a desire to maintain that piece. For those looking to still use Pullbug's GitLab feature, you can use any version of Pullbug prior to `v3.0.0`
- Replaces all env variables with CLI args for a more uniform experience, various shortcodes for flags were changed or removed as a part of this process (closes #24)
- Replaces the `--wip` flag with `--drafts` to use the newer GitHub draft boolean to determine if a pull request is a draft or not (closes #28)
- Now requires the `--github_context` flag for explicit logic routing
- Now requires the `--pulls` or `--issues` flag for explicit logic routing

### Other Changes

- Added new `--repos` flag to filter repos you want pull requests for (closes #23)
- Added new `--issues` flag to bug GitHub for issues instead of pull requests. No includes `--pulls` flag to help differentiate (closes #19)
- Switched from raw API calls to `PyGithub` which allows us to properly handle pagination (closes #14)
- Replace all `classmethods` with instance or static methods
- Various bug fixes and code refactor

## v2.4.0 (2021-09-20)

- Drops support for Python 3.6
- Swaps `mock` library for builtin `unittest.mock` library
- Formats entire project with `Black`

## v2.3.0 (2021-05-31)

- Pin dependencies
- Fix typos in classmethod decorators

## v2.2.0 (2021-04-27)

- Command line arguments are now validated at runtime and their defaults have been set in code (closes #22)
- If there is no assignee to a pull request, we will now populate the `waiting on` message with `NA` instead of leaving it blank
- Small code refactor and improved test coverage

## v2.1.0 (2020-12-03)

- Adds Discord support. Now you can send Pullbug messages to a Discord webhook (closes #17)
- Completely rewrote the message module. Messages are now an array of messages built from PR/MR data. This allows messages to be broken up easily into batches for chat services such as Discord which may require multiple batches of messages due to character limit
- The repo name is now included in each message with a link to the repo (closes #16)
- Reworked tests to be more clean and uniform
- Various bug fixes and code refactor for better performance and maintainability

## v2.0.6 (2020-10-10)

- Fixing typo in gitlab message

## v2.0.5 (2020-10-10)

- Fixed bug where arguments weren't being passed properly to the `run_missing_checks` function.
- Beefed up tests to ensure args were being passed to this function

## v2.0.4 (2020-10-10)

- Adding missing `main` entrypoint function that was accidentally deleted during code refactor for v2.0.0

## v2.0.3 (2020-10-10)

- Replaced `logger.warning` with `logger.error` as they were used incorrectly (closes #15)

## v2.0.2 (2020-10-10)

- Correcting references of "Pull Bug" to "Pullbug"

## v2.0.1 (2020-09-30)

- Instead of raising an error when no pull or merge requests can be found, we return that message. This is helpful when a user wanted to use both GitHub and GitLab in a single invocation. The previous implementation would exit the script without running the other.

## v2.0.0 (2020-09-29)

- Added context for GitHub, you can now get personal pull requests in addition to orgs
- Added logging both to console and to a file. Logs will rollover when their size gets too big
- Added various error handling that was missing
- Added unit tests and code coverage
- Bumped character count from 100 to 120 for descriptions on messages
- Assignees are now checked against the assignee array instead of a single assignee if there are multiple
- Bumped pagination from 20 to 100 items
- Updated documentation
- Various settings now have default values
- Introduced various new settings that can be altered
- Various bug fixes

## v1.3.0 (2020-06-01)

- Removed requirements.txt and added dependencies to setup.py
- Added error handling for requests and Slack messaging
- Added error handling surrounding missing API Keys
- Fixed line-too-long linting errors
- Added helpful information to `.env.example`
- Closed #8 - added a custom message when there is nothing to pull
- Added additional output during script execution to show progress

## v1.2.0 (2020-04-14)

- Published to PyPI
- Reworked the entire project into a Python package with proper class and function naming
- Consolidated code once again allowing for now code requests
- Bug fixes
- Better documentation

## v1.1.0 (2020-04-13)

- Added GitHub and Slack as options
- Cleaned up code and added testing
- Consolidated multiple scripts into fewer items
- Allowed WIP requests to be ignored
- Added more customization with additional environment variables
- Messages are now a single message instead of individual ones

## v1.0.0 (2020-04-02)

- Initial release
- Added ability to send messages from GitLab to Rocket Chat
