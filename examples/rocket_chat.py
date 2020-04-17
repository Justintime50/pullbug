"""Example of all functions of Pull Bug"""
import pullbug

# Pick and choose for your needs. Build only GitLab/GitHub messages, combine them into one. Send to Slack or Rocket Chat - maybe both!

# Build messages
github_message = pullbug.Requests.github()
gitlab_message = pullbug.Requests.gitlab()
message = github_message + gitlab_message

# Send message
pullbug.Messages.rocket_chat(message)
