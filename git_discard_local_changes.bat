@echo off
REM --- NexusSpace Discard Local Changes Script ---
REM Discards all unstaged changes in the current directory and subdirectories.

set /p response="WARNING: This will discard all UNSTAGED local changes. Are you sure? (y/N) "
if /i "%response%" neq "y" (
    echo Action cancelled.
    exit /b 0
)

echo --- ⚠️ Discarding Local Changes ---
REM Use git restore to safely undo file modifications
git restore .

REM Use git clean to remove untracked files
echo Cleaning untracked files...
git clean -f -d

echo --- ✅ Local Directory Cleaned ---
