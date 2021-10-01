# CHANGELOG

## NEXT RELEASE

### Breaking Changes

* Completely removes `GitLab` support as I no longer use the platform and can't reliably test its functionality nor have a desire to maintain that piece. For those looking to still use Pullbug's GitLab feature, you can use any version of Pullbug prior to `v3.0.0`
* Replaces all env variables with CLI args for a more uniform experience, various shortcodes for flags were changed or removed as a part of this process (closes #24)
* Replaces the `--wip` flag with `--drafts` to use the newer GitHub draft boolean to determine if a pull request is a draft or not (closes #28)
* Now requires the `--github_context` flag for explicit logic routing
* Now requires the `--pulls` or `--issues` flag for explicit logic routing

### Other Changes

* Added new `--repos` flag to filter repos you want pull requests for (closes #23)
* Added new `--issues` flag to bug GitHub for issues instead of pull requests. No includes `--pulls` flag to help differentiate (closes #19)
* Switched from raw API calls to PyGithub which allows us to properly handle pagination (closes #14)
* Replace all `classmethods` with instance or static methods
* Various bug fixes and code refactor

## v2.4.0 (2021-09-20)

* Drops support for Python 3.6
* Swaps `mock` library for builtin `unittest.mock` library
* Formats entire project with `Black`

## v2.3.0 (2021-05-31)

* Pin dependencies
* Fix typos in classmethod decorators

## v2.2.0 (2021-04-27)

* Command line arguments are now validated at runtime and their defaults have been set in code (closes #22)
* If there is no assignee to a pull request, we will now populate the `waiting on` message with `NA` instead of leaving it blank
* Small code refactor and improved test coverage

## v2.1.0 (2020-12-03)

* Adds Discord support. Now you can send Pullbug messages to a Discord webhook (closes #17)
* Completely rewrote the message module. Messages are now an array of messages built from PR/MR data. This allows messages to be broken up easily into batches for chat services such as Discord which may require multiple batches of messages due to character limit
* The repo name is now included in each message with a link to the repo (closes #16)
* Reworked tests to be more clean and uniform
* Various bug fixes and code refactor for better performance and maintainability

## v2.0.6 (2020-10-10)

* Fixing typo in gitlab message

## v2.0.5 (2020-10-10)

* Fixed bug where arguments weren't being passed properly to the `run_missing_checks` function.
* Beefed up tests to ensure args were being passed to this function

## v2.0.4 (2020-10-10)

* Adding missing `main` entrypoint function that was accidentally deleted during code refactor for v2.0.0

## v2.0.3 (2020-10-10)

* Replaced `logger.warning` with `logger.error` as they were used incorrectly (closes #15)

## v2.0.2 (2020-10-10)

* Correcting references of "Pull Bug" to "Pullbug"

## v2.0.1 (2020-09-30)

* Instead of raising an error when no pull or merge requests can be found, we return that message. This is helpful when a user wanted to use both GitHub and GitLab in a single invocation. The previous implementation would exit the script without running the other.

## v2.0.0 (2020-09-29)

* Added context for GitHub, you can now get personal pull requests in addition to orgs
* Added logging both to console and to a file. Logs will rollover when their size gets too big
* Added various error handling that was missing
* Added unit tests and code coverage
* Bumped character count from 100 to 120 for descriptions on messages
* Assignees are now checked against the assignee array instead of a single assignee if there are multiple
* Bumped pagination from 20 to 100 items
* Updated documentation
* Various settings now have default values
* Introduced various new settings that can be altered
* Various bug fixes

## v1.3.0 (2020-06-01)

* Removed requirements.txt and added dependencies to setup.py
* Added error handling for requests and Slack messaging
* Added error handling surrounding missing API Keys
* Fixed line-too-long linting errors
* Added helpful information to `.env.example`
* Closed #8 - added a custom message when there is nothing to pull
* Added additional output during script execution to show progress

## v1.2.0 (2020-04-14)

* Published to PyPI
* Reworked the entire project into a Python package with proper class and function naming
* Consolidated code once again allowing for now code requests
* Bug fixes
* Better documentation

## v1.1.0 (2020-04-13)

* Added GitHub and Slack as options
* Cleaned up code and added testing
* Consolidated multiple scripts into fewer items
* Allowed WIP requests to be ignored
* Added more customization with additional environment variables
* Messages are now a single message instead of individual ones

## v1.0.0 (2020-04-02)

* Initial release
* Added ability to send messages from GitLab to Rocket Chat
