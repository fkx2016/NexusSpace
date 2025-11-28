# --- STAGE 1: Build the Frontend (Node Environment) ---
FROM node:20-alpine AS frontend-builder

# Set working directory for the frontend
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source code and build the production assets
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html .
COPY frontend/vite.config.js .
# Run the build command defined in package.json
RUN npm run build


# --- STAGE 2: Build the Backend (Python Environment) ---
FROM python:3.11-slim AS final-backend

# Install system dependencies needed for Git cloning (for RemoteFetcher)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory for the final application
WORKDIR /app

# Copy Python requirements and install dependencies
COPY pyproject.toml .
RUN pip install .

# Copy the entire backend and the root configuration files
COPY backend /app/backend
COPY .env.example .
COPY git_safe_commit.sh .
COPY git_discard_local_changes.sh .
COPY git_revert_last_commit.sh .

# Copy the built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the configured default port (8001)
EXPOSE 8001

# Run the application using the programmatic entry point
# This ensures SERVER_PORT and other settings from the environment are used,
# fulfilling the 12-Factor principle.
CMD ["python", "-m", "backend.main"]
