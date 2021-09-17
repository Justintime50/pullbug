<div align="center">

# Pullbug 🐛 

Get bugged via Discord, Slack, or RocketChat to merge your GitHub pull requests or GitLab merge requests.

[![Build Status](https://github.com/Justintime50/pullbug/workflows/build/badge.svg)](https://github.com/Justintime50/pullbug/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/pullbug/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/pullbug?branch=main)
[![PyPi](https://img.shields.io/pypi/v/pullbug)](https://pypi.org/project/pullbug)
[![Licence](https://img.shields.io/github/license/justintime50/pullbug)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/pullbug/showcase.png" alt="Showcase">

</div>

Pullbug can notify you on Discord, Slack, or Rocket.Chat of all open pull and merge requests from GitHub or GitLab. This tool ensures requests never go unnoticed as it can be setup on a schedule to constantly bug you to merge your work. This is perfect for finding old or stale requests and helps you to stay current on new ones. Pass in a few environment variables, setup a [Slackbot](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) or [Rocket.Chat](https://rocket.chat/docs/developer-guides/rest-api/integration/create/) integration and you're all set to be bugged by Pullbug.

**NOTE:** Pullbug works best if you have link unfurling turned off for GitHub and GitLab on Discord, Slack, or Rocket.Chat.

**GitLab Users:** If you are not hosting your own GitLab instance and are instead using `gitlab.com`, it's recommended to change the scope to `owner` and provide an owner who has access to all your organizations merge requests.

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

Pullbug works best when run on a schedule. Run one-off reports or setup Pullbug to notify you at whatever interval you'd like to be bugged via Discord, Slack, or Rocket.Chat about pull or merge requests.

Pullbug is highly customizable allowing you to mix and match version control software along with messaging platforms to get the right fit. Additionally choose which kinds of pull or merge requests to retrieve.

```
Usage:
    GITHUB_TOKEN=123... SLACK_BOT_TOKEN=123... SLACK_CHANNEL=my-channel pullbug --github --github_owner my_org --slack

Options:
    -h, --help            show this help message and exit
    -gh, --github         Get bugged about pull requests from GitHub.
    -gl, --gitlab         Get bugged about merge requests from GitLab.
    -d, --discord         Send Pullbug messages to Discord.
    -s, --slack           Send Pullbug messages to Slack.
    -rc, --rocketchat     Send Pullbug messages to Rocket.Chat.
    -w, --wip             Include "Work in Progress" pull or merge requests.
    -gho GITHUB_OWNER, --github_owner GITHUB_OWNER
                            The GitHub owner to retrieve pull requests from (can be a user or organization).
    -ghs {open,closed,all}, --github_state {open,closed,all}
                            The GitHub state to retrieve pull requests with.
    -ghc {orgs,users}, --github_context {orgs,users}
                            The GitHub context to retrieve pull requests with.
    -glst {opened,closed,locked,merged}, --gitlab_state {opened,closed,locked,merged}
                            The GitLab state to retrieve merge requests with.
    -glsc {all,created_by_me,assigned_to_me}, --gitlab_scope {all,created_by_me,assigned_to_me}
                            The GitLab state to retrieve pull requests with.

Environment Variables:
    GITHUB_TOKEN        The GitHub Token used to authenticate with the GitHub API.
    GITLAB_API_KEY      The GitLab API Key used to authenticate with the GitLab API.
    GITLAB_API_URL      The GitLab API url for your GitLab instance. Default: https://gitlab.com/api/v4.
    DISCORD_WEBHOOK_URL The Discord webhook url to send a message to. Will look like: https://discord.com/api/webhooks/channel_id/webhook_id
    SLACK_BOT_TOKEN     The Slackbot Token used to authenticate with Slack.
    SLACK_CHANNEL       The Slack channel to post a message to.
    ROCKET_CHAT_URL     The Rocket.Chat url of the room to post a message to.
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
