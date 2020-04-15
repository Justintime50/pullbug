<div align="center">

# Pull Bug

Pull Bug is great at bugging you to merge or close your pull/merge requests.

[![Build Status](https://travis-ci.org/Justintime50/pull-bug.svg?branch=master)](https://travis-ci.org/Justintime50/pull-bug)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)

<img src="assets/showcase.png">

</div>

Pull Bug is a script that can be run on a cron to notify you on Slack or Rocket Chat of all open pull and merge requests from GitHub or GitLab. This tool ensures requests never go unnoticed as it constantly bugs you to merge or close your work. This is perfect for finding old stale requests and staying on top of current ones. Pass in a few environment variables, setup a [Slackbot](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) or [Rocket Chat integration](https://rocket.chat/docs/developer-guides/rest-api/integration/create/) and you're all set to be bugged by Pull Bug.

**NOTE:** Pull Bug works best if you have link unfurling turned off for GitHub and GitLab on Slack or Rocket Chat.

## Install

```bash
# Copy and fill out the .env file
cp .env.example .env

# Install Python packages
pip3 install -r requirements.txt
```

## Usage

Pull Bug is intended to be run on a cron, launch agent, or via Docker at whatever interval you'd like to be notified via Slack or Rocket Chat.

Pick and choose for your needs. Build only GitLab/GitHub messages, combine them into one. Send to Slack or Rocket Chat - maybe both!

```bash
# Build messages
github_message = pullbug.Requests.github()
gitlab_message = pullbug.Requests.gitlab()
message = github_message + gitlab_message

# Send messages
pullbug.Messages.rocket_chat(message)
pullbug.Messages.slack(message)
```

### Commands

```bash
# Run our example
python3 example.py

# Run the following for Docker (environment variables must be set in docker-compose.yml)
docker-compose up -d
```

## Development

```bash
# Install dev dependencies
pip3 install -r requirements.txt

# Run linting
pylint pullbug/*.py
```
