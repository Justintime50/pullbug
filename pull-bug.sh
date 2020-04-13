#!/bin/sh

# This script is intended to be used inside of Docker to run both GitLab and GitHub scripts

echo "Running scripts..."
python ./pull_bug_gitlab.py
python ./pull_bug_github.py
echo "Scripts complete!"
