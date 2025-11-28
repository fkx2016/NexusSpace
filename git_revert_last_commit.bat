@echo off
REM --- NexusSpace Revert Last Commit Script ---
REM Creates a new commit that safely undoes the changes of the last push.
REM Usage: git_revert_last_commit.bat "Reason for Reversion"

IF "%~1"=="" (
    echo ERROR: Please provide a reason for the reversion.
    echo Usage: git_revert_last_commit.bat "Reason for Reversion"
    exit /b 1
)

echo --- 🛡️ Starting Safe History Reversion ---

REM 1. Revert the last commit
git revert HEAD --no-edit
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Reversion failed. Resolve conflicts and try 'git revert --continue' or 'git revert --abort'.
    exit /b 1
)

REM 2. Amend the commit message with the reason and push
echo Amending commit message and pushing...
git commit --amend -m "REVERT: %~1"

git push

echo --- ✅ History Reverted and Pushed ---
