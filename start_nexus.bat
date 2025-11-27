@echo off
REM NexusSpace Development Environment Startup Script
REM This script launches both backend and frontend servers in separate windows

echo ========================================
echo   NexusSpace Development Environment
echo ========================================
echo.
echo Starting servers...
echo.

REM Start Backend Server (uvicorn on port 8001)
start "NexusSpace Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --port 8001"

REM Wait a moment before starting frontend
timeout /t 2 /nobreak >nul

REM Start Frontend Server (Vite dev server)
start "NexusSpace Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ✓ Backend server starting on http://localhost:8001
echo ✓ Frontend server starting (check terminal for URL)
echo.
echo Both servers are now running in separate windows.
echo Close those windows or press Ctrl+C in them to stop the servers.
echo.

REM Wait 5 seconds then close this window
timeout /t 5
exit
