@echo off
REM --- NexusSpace Safe Commit/Push Script ---
REM Usage: git_safe_commit.bat "Descriptive Commit Message"

IF "%~1"=="" (
    echo ERROR: Please provide a commit message.
    echo Usage: git_safe_commit.bat "Your message here"
    exit /b 1
)

echo --- 🛡️ Starting Safe Commit and Push ---

REM 1. Stage all tracked, modified, and deleted files
git add -A

REM 2. Commit the staged changes
echo Committing changes...
git commit -m "%~1"

REM Check if commit succeeded (git commit returns 0 on success, 1 on empty/error)
IF %ERRORLEVEL% EQU 0 (
    REM 3. Push the new commit
    echo Pushing commit to remote...
    git push

    REM 4. Push any new tags
    echo Pushing new tags...
    git push --tags
    
    echo --- ✅ Git Workflow Complete ---
) ELSE (
    echo --- ⚠️ Nothing to Commit (Working tree clean) or Error ---
)
