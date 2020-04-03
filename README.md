<div align="center">

# Pull Bug

Pull Bug is great at bugging you to merge or close your pull/merge requests.

[![Build Status](https://travis-ci.org/Justintime50/pull-bug.svg?branch=master)](https://travis-ci.org/Justintime50/pull-bug)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)

<img src="assets/showcase.png">

</div>

Pull Bug can be run on a cron to notify you on Slack of all open pull and merge requests from GitHub or GitLab. This tool ensures requests never go stale as it constantly bugs you to merge or close your work. This is perfect for finding old stale requests and staying on top of current ones.

## Install

```bash
# Copy and fill out the .env file
cp .env.example .env

# Install Python packages
pip3 install -r requirements.txt
```

## Usage

Pull Bug is intended to be run on a cron or launch agent at whatever interval you'd like to notify you via Slack.

```bash
# Run the following for GitLab
python3 pull_bug_gitlab.py

# Run the following for GitHub
python3 pull_bug_github.py
```

**NOTE:** Pull Bug works best if you have link unfurling turned off for GitHub and GitLab on Slack.
