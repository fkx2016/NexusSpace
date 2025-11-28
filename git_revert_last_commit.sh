#!/bin/bash

# --- NexusSpace Revert Last Commit Script ---
# Creates a new commit that safely undoes the changes of the last push.
# Usage: ./git_revert_last_commit.sh "Reason for Reversion"

# Check if a reason was provided
if [ -z "$1" ]; then
    echo "ERROR: Please provide a reason for the reversion."
    echo "Usage: ./git_revert_last_commit.sh \"Reason for Reversion\""
    exit 1
fi

echo "--- 🛡️ Starting Safe History Reversion ---"

# 1. Revert the last commit
git revert HEAD --no-edit
if [ $? -ne 0 ]; then
    echo "ERROR: Reversion failed. Resolve conflicts and try 'git revert --continue' or 'git revert --abort'."
    exit 1
fi

# 2. Amend the commit message with the reason and push
echo "Amending commit message and pushing..."
git commit --amend -m "REVERT: $1"

git push

echo "--- ✅ History Reverted and Pushed ---"
