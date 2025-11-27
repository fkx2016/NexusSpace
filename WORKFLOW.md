# NexusSpace Development Workflow

This document outlines the standard operating procedures for developing and running the NexusSpace multi-agent code analysis system.

## Prerequisites

Before you begin, ensure you have the following tools installed:

- **Python 3.11+**: Required for the backend FastAPI server
- **uv**: Python package manager for dependency management
- **Node.js 18+**: Required for the frontend React application
- **npm**: Node package manager (comes with Node.js)
- **Git**: Version control system

### Verify Installation

```bash
python --version
uv --version
node --version
npm --version
git --version
```

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd llm-council
```

### 2. Backend Setup

```bash
# Install Python dependencies using uv
uv sync
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

### 4. Environment Configuration

Ensure you have the necessary API keys configured:

- **OpenRouter API Key**: Required for LLM access
- Set environment variables or configure in `backend/config.py`

## One-Click Startup

### Using the Startup Script (Recommended)

Simply double-click `start_nexus.bat` in the project root directory, or run it from the command line:

```bash
start_nexus.bat
```

This will:
1. Open a new terminal window running the backend server on `http://localhost:8001`
2. Open a second terminal window running the frontend dev server (typically on `http://localhost:5173`)
3. Display startup confirmation messages
4. Close the launcher window after 5 seconds

### Manual Startup

If you prefer to start the servers manually:

#### Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --port 8001
```

The backend API will be available at `http://localhost:8001`

#### Frontend Server

Open a new terminal window:

```bash
cd frontend
npm run dev
```

The frontend will typically be available at `http://localhost:5173` (check terminal output for exact URL)

## Using NexusSpace

1. Open your browser and navigate to the frontend URL (e.g., `http://localhost:5173`)
2. The application will automatically analyze the configured project directory
3. View the multi-agent analysis results in the dashboard
4. Explore individual agent reports and the chairman's synthesis

## Development Workflow

### Making Code Changes

- **Backend changes**: The uvicorn server will auto-reload when you save Python files
- **Frontend changes**: The Vite dev server will hot-reload when you save React files
- **Configuration changes**: May require manual server restart

### Testing Changes

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

### Committing Changes

```bash
git add .
git commit -m "Description of changes"
git push
```

## Shutdown Procedure

### Stopping the Servers

1. **Locate the terminal windows** titled "NexusSpace Backend" and "NexusSpace Frontend"
2. **In each window**, press `Ctrl+C` to stop the server
3. **Close the terminal windows** or type `exit` and press Enter

### Safe Shutdown Checklist

- [ ] Stop backend server (Ctrl+C in backend terminal)
- [ ] Stop frontend server (Ctrl+C in frontend terminal)
- [ ] Close browser tabs with the application
- [ ] Commit any unsaved work to Git

## Troubleshooting

### Port Already in Use

If you see an error about port 8001 or 5173 already being in use:

```bash
# Windows: Find and kill process using the port
netstat -ano | findstr :8001
taskkill /PID <process-id> /F
```

### Dependencies Out of Sync

```bash
# Backend
uv sync

# Frontend
cd frontend
npm install
```

### Server Not Responding

1. Stop all running servers (Ctrl+C)
2. Close all terminal windows
3. Restart using `start_nexus.bat`

## Project Structure

```
llm-council/
├── backend/           # FastAPI backend server
│   ├── main.py       # Main application entry point
│   ├── config.py     # Configuration settings
│   └── services/     # Business logic services
├── frontend/         # React frontend application
│   ├── src/          # Source code
│   └── package.json  # Node dependencies
├── start_nexus.bat   # One-click startup script
├── WORKFLOW.md       # This file
└── README.md         # Project documentation
```

## Additional Resources

- **API Documentation**: `http://localhost:8001/docs` (when backend is running)
- **Project README**: See `README.md` for project overview and architecture
- **Git Repository**: Refer to commit history for change tracking

---

**Last Updated**: 2025-11-27  
**Maintained By**: NexusSpace Development Team
