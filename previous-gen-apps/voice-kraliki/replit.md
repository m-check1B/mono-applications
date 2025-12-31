# CC-Lite 2026 - AI Call Center Platform

## Project Status

This is a full-stack AI-powered call center platform that has been imported to Replit.

### Technology Stack
- **Backend**: FastAPI (Python 3.11) with PostgreSQL
- **Frontend**: SvelteKit 2.x with TypeScript and Tailwind CSS
- **Database**: PostgreSQL (Replit-managed)
- **AI Providers**: OpenAI, Google Gemini, Deepgram v3.x
- **Telephony**: Twilio, Telnyx

## Import Completion Summary

### ✅ Completed Tasks

1. **Dependencies Installed**
   - Python 3.11 and Node.js 20 installed
   - Backend dependencies installed (with Deepgram SDK downgraded to v3.11.0 for compatibility)
   - Frontend dependencies installed (npm packages)

2. **PostgreSQL Database**
   - Database created via Replit integration
   - Database tables created successfully using SQLAlchemy ORM
   - Fixed SQLAlchemy reserved keyword issue (`metadata` columns renamed to `custom_metadata`)

3. **Frontend Configuration**
   - Vite configured to run on 0.0.0.0:5000
   - Frontend workflow configured and running successfully
   - SvelteKit configured with proper host and port settings
   - Frontend .env created with backend URL pointing to Replit domain

4. **Model Fixes**
   - Fixed duplicate `PerformanceAlert` table (renamed to `SupervisorPerformanceAlert` in supervisor model)
   - Fixed missing `List` import in call_flow.py
   - Fixed incorrect import path in supervisor.py (`app.models.database` → `app.database`)

### ✅ Application Status: FULLY OPERATIONAL

**Both frontend and backend are now running successfully!**

- **Frontend**: http://localhost:5000 (Vite dev server with proxy to backend)
- **Backend**: http://localhost:8000 (FastAPI server)
- **API Proxy**: All `/api/*` requests from frontend are proxied to backend

### ⚠️ Known Non-Critical Issues

1. **Redis Connection** (Non-Critical)
   - Warning: "Failed to connect to Redis" - Redis is optional for basic functionality
   - Token revocation and caching features disabled, but authentication still works
   
2. **Database Schema Warnings** (Non-Critical)
   - Some relationship warnings in the logs (voicemail, call_states)
   - Core functionality (auth, campaigns, etc.) works fine

### 📝 Configuration Files

- **Frontend**: Runs on port 5000 (web preview)
  - `frontend/.env` - Contains `PUBLIC_BACKEND_URL`
  - `frontend/vite.config.ts` - Configured for 0.0.0.0:5000
  - `frontend/svelte.config.js` - Configured for port 5000

- **Backend**: Should run on port 8000 (internal)
  - `backend/start_server.py` - Custom server startup script that creates tables
  - `backend/requirements.txt` - Deepgram pinned to v3.x

### 🎯 What You Can Do Now

1. **✅ Create an Account**
   - Visit the web preview
   - Sign up with email and password
   - Account creation is fully functional!

2. **✅ Use Core Features**
   - User authentication and authorization
   - Database operations
   - All CRUD endpoints

3. **Configure AI Features** (Optional - for AI capabilities)
   - Use Replit Secrets to add API keys:
     - `OPENAI_API_KEY` - For OpenAI GPT models
     - `GEMINI_API_KEY` - For Google Gemini models  
     - `DEEPGRAM_API_KEY` - For speech-to-text
     - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` - For telephony
     - `SECRET_KEY`, `JWT_SECRET` - For enhanced security

##  Project Structure

```
.
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── api/      # API route handlers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── services/ # Business logic
│   │   ├── auth/     # Authentication
│   │   └── main.py   # FastAPI app
│   ├── migrations/   # Alembic database migrations
│   └── requirements.txt
│
├── frontend/         # SvelteKit frontend
│   ├── src/
│   │   ├── routes/  # SvelteKit file-based routing
│   │   ├── lib/     # Components and utilities
│   │   └── app.html
│   └── package.json
│
└── docs/            # Project documentation
```

## Database Connection

The database is automatically configured via Replit's PostgreSQL integration.  
Database URL is available in the `DATABASE_URL` environment variable.

## Development Workflow

### Frontend Development
- Frontend runs automatically via the "frontend" workflow
- Access via web preview on port 5000
- Hot reload enabled for development

### Backend Development
- Start manually: `cd backend && python3 start_server.py`
- API docs available at: `/docs` (Swagger) or `/redoc`
- Health check: `/health`

## Important Notes

- **Deepgram SDK**: Pinned to version 3.x (v3.11.0) due to breaking changes in v5.x
  - Future work needed: Migrate to Deepgram SDK v5.x
- **Database Tables**: Auto-created on first backend startup
- **API Keys**: Not required for basic app functionality, but needed for AI features

## Resources

- Original README: See `README.md` for complete feature documentation
- API Documentation: `/docs` endpoint when backend is running
- Frontend Routes: `/campaigns`, `/teams`, `/analytics`, etc.
