#!/bin/bash

# --- NexusSpace Discard Local Changes Script ---
# Discards all unstaged changes in the current directory and subdirectories.
# This is a safe alternative to 'git reset --hard' for local work.

read -r -p "WARNING: This will discard all UNSTAGED local changes. Are you sure? (y/N) " response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "--- ⚠️ Discarding Local Changes ---"
    # Use git restore to safely undo file modifications
    git restore .
    
    # Use git clean to remove untracked files
    echo "Cleaning untracked files..."
    git clean -f -d
    
    echo "--- ✅ Local Directory Cleaned ---"
else
    echo "Action cancelled."
fi
