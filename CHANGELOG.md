# CHANGELOG

## v1.3.0 (2020-06-01)

* Removed requirements.txt and added dependencies to setup.py
* Added error handling for requests and Slack messaging
* Added error handling surrounding missing API Keys
* Fixed line-too-long linting errors
* Added helpful information to `.env.example`
* Closed #8 - added a custom message when there is nothing to pull

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
