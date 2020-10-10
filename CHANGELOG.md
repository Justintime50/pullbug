# CHANGELOG

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
