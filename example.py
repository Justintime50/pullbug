"""Example of all functions of Pull Bug"""
from pullbug import pull_bug_rocket_chat as pullbug_rc
# from pullbug import pull_bug_slack as pullbug_s

# All functions that can be run
# pullbug_s.pull_bug_gitlab() # sends messages from GitLab to Slack
# pullbug_s.pull_bug_github() # sends messages from GitHub to Slack
pullbug_rc.pull_bug_gitlab() # sends messages from GitLab to Rocket Chat
pullbug_rc.pull_bug_github() # Sends messages from GitHub to Rocket Chat
