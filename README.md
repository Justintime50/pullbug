<div align="center">

# Pullbug 🐛 

Get bugged via Discord, Slack, or RocketChat to merge your GitHub pull requests.

[![Build Status](https://github.com/Justintime50/pullbug/workflows/build/badge.svg)](https://github.com/Justintime50/pullbug/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/pullbug/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/pullbug?branch=main)
[![PyPi](https://img.shields.io/pypi/v/pullbug)](https://pypi.org/project/pullbug)
[![Licence](https://img.shields.io/github/license/justintime50/pullbug)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/pullbug/showcase.png" alt="Showcase">

</div>

Pullbug can notify you on Discord, Slack, or Rocket.Chat of all open pull requests from GitHub. This tool ensures requests never go unnoticed as it can be setup on a schedule to constantly bug you to merge your work. This is perfect for finding old or stale requests and helps you to stay current on new ones. Pass in a few environment variables, setup a [Slackbot](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) or [Rocket.Chat](https://rocket.chat/docs/developer-guides/rest-api/integration/create/) integration and you're all set to be bugged by Pullbug.

**NOTE:** Pullbug works best if you have link unfurling turned off for GitHub on Discord, Slack, or Rocket.Chat.

## Install

```bash
# Install tool
pip3 install pullbug

# Install locally
make install

# Get Makefile help
make help
```

## Usage

Pullbug works best when run on a schedule. Run one-off reports or setup Pullbug to notify you at whatever interval you'd like to be bugged via Discord, Slack, or Rocket.Chat about pull requests.

Pullbug is highly customizable allowing you to mix and match version control software along with messaging platforms to get the right fit. Additionally choose which kinds of pull requests to retrieve.

```
Usage:
    pullbug --github_token 123... --github_owner justintime50 --github_context users

Options:
    -h, --help            show this help message and exit
    -p, --pulls           Bug GitHub for Pull Requests.
    -i, --issues          Bug GitHub for Issues.
    -gt GITHUB_TOKEN, --github_token GITHUB_TOKEN
                            The token to authenticate with GitHub.
    -go GITHUB_OWNER, --github_owner GITHUB_OWNER
                            The GitHub owner to retrieve pull requests or issues for (can be a user or organization).
    -gs {open,closed,all}, --github_state {open,closed,all}
                            The GitHub state to retrieve pull requests or issues for.
    -gc {orgs,users}, --github_context {orgs,users}
                            The GitHub context to retrieve pull requests or issues for.
    -d, --discord         Send Pullbug messages to Discord.
    -du DISCORD_URL, --discord_url DISCORD_URL
                            The Discord webhook URL to send messages to.
    -s, --slack           Send Pullbug messages to Slack.
    -st SLACK_TOKEN, --slack_token SLACK_TOKEN
                            The Slackbot token to authenticate with Slack.
    -sc SLACK_CHANNEL, --slack_channel SLACK_CHANNEL
                            The Slack channel to send messages to.
    -rc, --rocketchat     Send Pullbug messages to Rocket.Chat.
    -ru ROCKETCHAT_URL, --rocketchat_url ROCKETCHAT_URL
                            The Rocket.Chat URL to send messages to.
    -r REPOS, --repos REPOS
                            A comma-separated list of repos to run Pullbug against.
    -dr, --drafts         Include draft pull requests.
    -l LOCATION, --location LOCATION
                            The location of the Pullbug logs and files.
```

## Development

```bash
# Lint the project
make lint

# Run tests
make test

# Run test coverage
make coverage

# Run the tool locally
venv/bin/python pullbug/cli.py --help
```
