<div align="center">

# Pullbug 🐛

Get bugged via Discord or Slack to merge your GitHub pull requests or close open issues.

[![Build Status](https://github.com/Justintime50/pullbug/workflows/build/badge.svg)](https://github.com/Justintime50/pullbug/actions)
[![Coverage Status](https://img.shields.io/codecov/c/github/justintime50/pullbug)](https://app.codecov.io/github/Justintime50/pullbug)
[![PyPi](https://img.shields.io/pypi/v/pullbug)](https://pypi.org/project/pullbug)
[![Licence](https://img.shields.io/github/license/justintime50/pullbug)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/pullbug/showcase.png" alt="Showcase">

</div>

Pullbug can notify you on Discord or Slack of all open pull requests from GitHub. This tool ensures requests never go unnoticed as it can be setup on a schedule to constantly bug you to merge your work. This is perfect for finding old or stale requests and helps you to stay current on new ones. Pass in a few environment variables, setup a [Slackbot](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) or [Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) webhook and you're all set to be bugged by Pullbug.

**NOTE:** Pullbug works best if you have link unfurling turned off for GitHub on Discord and Slack.

## Install

```bash
# Homebrew install
brew tap justintime50/formulas
brew install pullbug

# Pip install
pip3 install pullbug

# Install locally
just install
```

## Usage

Pullbug works best when run on a schedule. Run one-off reports or setup Pullbug to notify you at whatever interval you'd like to be bugged via Discord or Slack about pull requests.

Pullbug is highly customizable allowing you to choose which messaging service and what kinds of pull requests or issues you'd like.

```text
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
  -gs {all,open,closed}, --github_state {all,open,closed}
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
  -r REPOS, --repos REPOS
                        A comma-separated list of repos to run Pullbug against.
  -dr, --drafts         Include draft pull requests.
  -l LOCATION, --location LOCATION
                        The location of the Pullbug logs and files.
  --base_url BASE_URL   The base URL of your GitHub instance (useful for enterprise users with custom hostnames).
  --log_level {warning,debug,info,notset,error,critical}
                        The log level used for the tool.
  --disable_descriptions
                        Disables descriptions in messages.
  --quiet               Does not output when there is nothing to bug about.
  --version             show program's version number and exit
```

## Development

```bash
# Get a comprehensive list of development tools
just --list

# Run the tool locally
venv/bin/python pullbug/cli.py --help
```

## Trusted By

The following companies use `Pullbug`:

* [EasyPost](https://easypost.com)
