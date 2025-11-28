#!/bin/bash

# --- NexusSpace Safe Commit/Push Script ---
# Usage: ./git_safe_commit.sh "Descriptive Commit Message"

# Check if a commit message was provided
if [ -z "$1" ]; then
    echo "ERROR: Please provide a commit message."
    echo "Usage: ./git_safe_commit.sh \"Your message here\""
    exit 1
fi

echo "--- 🛡️ Starting Safe Commit and Push ---"

# 1. Stage all tracked, modified, and deleted files (-A flag is comprehensive)
git add -A

# 2. Commit the staged changes with the provided message
echo "Committing changes..."
git commit -m "$1"

# Check if the commit succeeded (returns non-zero if no changes were committed)
if [ $? -eq 0 ]; then
    # 3. Push the new commit
    echo "Pushing commit to remote..."
    git push

    # 4. Push any new tags (like V2.0.0 tags)
    echo "Pushing new tags..."
    git push --tags
    
    echo "--- ✅ Git Workflow Complete ---"
else
    echo "--- ⚠️ Nothing to Commit (Working tree clean) ---"
fi
