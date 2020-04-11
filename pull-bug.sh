#!/bin/bash

# This script is intended to be used inside of Docker to run both GitLab and GitHub scripts

echo "Running scripts..."
python ./pull_bug_gitlab_rc.py
python ./pull_bug_github_rc.py
echo "Scripts complete!"
