# Nango Jira Integration Demo

This is a production-grade full-stack application demonstrating how to integrate Jira using self-hosted Nango.

## 🚀 Features

- **Connect Jira**: Secure OAuth flow powered by Nango frontend SDK.
- **Projects Overview**: View all projects accessible in your Jira workspace.
- **Issue Management**: 
  - Browse issues with real-time status badges.
  - Search issues by summary.
  - Filter by project.
- **Create Tasks**: Quickly add new tasks to any project.
- **Modern UI**: Dark mode, responsive design, and glassmorphism effects.

## 🛠️ Tech Stack

- **Frontend**: React (Vite), Axios, Lucide Icons, Modern CSS.
- **Backend**: Python (FastAPI), HTTXP (Async requests), MongoDB.
- **Auth/Integration**: Nango (Self-hosted).

## 📋 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB running locally (or a connection string)
- A self-hosted Nango instance configured with a Jira integration.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure your Nango and MongoDB settings
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Nango Configuration
Ensure your Jira integration in Nango has the following scopes:
- `read:jira-work`
- `write:jira-work`
- `offline_access`

## 📂 Project Structure

- `/backend`: FastAPI application and logic.
  - `/routes`: API endpoints.
  - `/services`: Nango and Jira integration logic.
  - `models.py`: Data schemas.
- `/frontend`: React application.
  - `/src/components`: UI building blocks.
  - `/src/services`: API and Nango SDK client.
  - `App.jsx`: Main application state and flow.
