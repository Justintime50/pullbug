<div align="center">

# Pull Bug 🐛 

Get bugged via Slack or RocketChat to merge your GitHub pull requests or GitLab merge requests.

[![Build Status](https://travis-ci.com/Justintime50/pull-bug.svg?branch=master)](https://travis-ci.com/Justintime50/pull-bug)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/pull-bug/badge.svg?branch=master)](https://coveralls.io/github/Justintime50/pull-bug?branch=master)
[![PyPi](https://img.shields.io/pypi/v/pull-bug)](https://pypi.org/project/pull-bug)
[![Licence](https://img.shields.io/github/license/justintime50/pull-bug)](LICENSE)

<img src="assets/showcase.png">

</div>

Pull Bug is a script that can be run on a cron to notify you on Slack or Rocket.Chat of all open pull and merge requests from GitHub or GitLab. This tool ensures requests never go unnoticed as it constantly bugs you to merge or close your work. This is perfect for finding old stale requests and staying on top of current ones. Pass in a few environment variables, setup a [Slackbot](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) or [Rocket.Chat integration](https://rocket.chat/docs/developer-guides/rest-api/integration/create/) and you're all set to be bugged by Pull Bug.

**NOTE:** Pull Bug works best if you have link unfurling turned off for GitHub and GitLab on Slack or Rocket.Chat.
**GitLab Users:** Pull Bug assumes you are self hosting your organization's GitLab instance (all merge requests will be checked for by default). If you are not hosting your own and are instead using gitlab.com, it's recommended to change the scope to "owner" and provide an owner who has access to all your organizations merge requests.

## Install

```bash
# Install Pull Bug
pip3 install pullbug

# Copy and fill out the .env file
cp .env.example .env
```

## Usage

Pull Bug is intended to be run on a cron, launch agent, or via Docker at whatever interval you'd like to be notified via Slack or Rocket.Chat.

Pick and choose for your needs. Build only GitLab/GitHub messages, combine them into one. Send to Slack or Rocket.Chat - maybe both!

```python
import pullbug

# Build messages
github_message = pullbug.Git.github()
gitlab_message = pullbug.Git.gitlab()
message = github_message + gitlab_message

# Send messages
pullbug.Messages.rocketchat(message)
pullbug.Messages.slack(message)
```

### Commands

```bash
# Run our examples
python3 examples/slack_message.py

# Run the following for Docker (environment variables must be set in docker-compose.yml)
docker-compose up -d
```

## Development

```bash
# Install dev dependencies
pip3 install -e ."[dev]"

# Run linting
pylint pullbug/*.py
```


## TODO

Document all env variables
- GITHUB_CONTEXT: 'users', 'orgs'
- GITLAB_SCOPE: created_by_me, assigned_to_me or all. Defaults to created_by_me
- GITLAB_STATE: opened, closed, locked, or merged
- CHANGE IGNORE_WIP to default to not include WIP

- VALIDATE ARGS FROM ARGPARSE! Only allow input from a list for those that only accept from a list of criteria
- Handle pagination of results that exceed more than 100 for GitHub
