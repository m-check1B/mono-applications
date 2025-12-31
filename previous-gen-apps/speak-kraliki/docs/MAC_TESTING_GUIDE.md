# Speak by Kraliki - Mac Testing Guide

This guide covers setting up and testing Speak by Kraliki on macOS for local development and testing of voice features with Gemini Live.

## Prerequisites

### Required Software

1. **Python 3.11+** (3.13 recommended)
   ```bash
   # Install via Homebrew
   brew install python@3.13

   # Verify installation
   python3 --version  # Should show 3.11+
   ```

2. **Node.js 20+** (22 recommended)
   ```bash
   # Install via Homebrew
   brew install node@22

   # Or use nvm
   nvm install 22
   nvm use 22

   # Verify installation
   node --version  # Should show v20+
   npm --version
   ```

3. **PostgreSQL 15+** (17 recommended)
   ```bash
   # Install via Homebrew
   brew install postgresql@17

   # Start PostgreSQL
   brew services start postgresql@17

   # Create database
   createdb speak_kraliki
   ```

4. **Google Gemini API Key**
   - Get your API key from [Google AI Studio](https://aistudio.google.com/)
   - Required for voice conversation features

### Optional Tools

- **Docker Desktop** for containerized development
- **VS Code** with Python and Svelte extensions

---

## Backend Setup with FastAPI

### 1. Clone and Navigate

```bash
cd /path/to/speak-kraliki
cd backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** Some platform packages may need local installation:
```bash
# If using platform-2026 packages locally
pip install -e ../../../platform-2026/packages/voice-core[gemini]
pip install -e ../../../platform-2026/packages/auth-core
pip install -e ../../../platform-2026/packages/events-core[rabbitmq]
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/speak

# Security
JWT_SECRET_KEY=your-dev-secret-key-32-chars-min

# Gemini Live 2.5 Flash Native Audio
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=models/gemini-2.5-flash-native-audio-preview-12-2025

# Frontend URL for CORS
CORS_ORIGINS=["http://localhost:5173"]
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Verify:**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Frontend Setup with SvelteKit

### 1. Navigate to Frontend

```bash
cd /path/to/speak-kraliki/frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment (Optional)

Create `.env` if needed:

```bash
PUBLIC_API_URL=http://localhost:8000
```

### 4. Start Development Server

```bash
npm run dev
```

**Access:** http://localhost:5173

---

## Testing Voice Features with Gemini Live

### Understanding the Voice Architecture

Speak by Kraliki uses **Gemini 2.5 Flash Native Audio** (GA December 2025) for real-time voice conversations:

- **Model:** `models/gemini-2.5-flash-native-audio-preview-12-2025`
- **Input:** 16-bit PCM at 16kHz
- **Output:** 16-bit PCM at 24kHz
- **Capabilities:** Up to 1000 concurrent sessions

### Voice Testing Prerequisites

1. **Microphone access:** Ensure your browser has microphone permissions
2. **HTTPS for production:** Voice features require secure context (localhost works for dev)
3. **Valid Gemini API key:** Set in backend `.env`

### Manual Voice Testing

1. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && source .venv/bin/activate
   uvicorn app.main:app --reload --port 8000

   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

2. **Create a test survey:**
   - Login as HR/CEO user
   - Create a new survey with questions
   - Generate employee magic links

3. **Test employee voice flow:**
   - Open magic link in incognito window
   - Accept consent screen
   - Grant microphone permission
   - Start voice conversation
   - Verify AI responds in real-time

### WebSocket Voice Endpoint

The voice interface uses WebSocket at:
```
ws://localhost:8000/api/speak/voice/ws/{token}
```

**Testing with wscat:**
```bash
npm install -g wscat

# Connect (replace TOKEN with actual magic link token)
wscat -c "ws://localhost:8000/api/speak/voice/ws/TOKEN"
```

### Browser Console Debugging

Open Developer Tools (Cmd+Option+I) and check:
- **Console:** WebSocket connection status
- **Network:** WebSocket frames (filter by WS)
- **Application > Permissions:** Microphone access

---

## Running Tests

### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_voice.py -v
```

### Frontend Tests (E2E with Playwright)

```bash
cd frontend

# Install Playwright browsers
npx playwright install

# Run E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui
```

---

## Common Issues

### 1. PostgreSQL Connection Refused

**Symptom:** `connection refused` or `could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@17

# Verify connection
psql -d speak_kraliki -c "SELECT 1;"
```

### 2. Module Not Found (Python)

**Symptom:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# For platform packages
pip install -e ../../../platform-2026/packages/voice-core[gemini]
```

### 3. Port Already in Use

**Symptom:** `Address already in use`

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### 4. CORS Errors

**Symptom:** `Access-Control-Allow-Origin` errors in browser

**Solution:**
- Verify `CORS_ORIGINS` in `.env` includes your frontend URL
- Ensure frontend runs on expected port (5173)

### 5. Microphone Access Denied

**Symptom:** Voice features not working, no audio input

**Solution:**
1. Check System Preferences > Privacy & Security > Microphone
2. Ensure browser has microphone permission
3. Try different browser (Chrome works best)
4. Check browser permissions: chrome://settings/content/microphone

### 6. WebSocket Connection Failed

**Symptom:** `WebSocket connection to 'ws://...' failed`

**Solution:**
- Verify backend is running
- Check token is valid (not expired)
- Ensure no firewall blocking WebSocket
- Try: `curl http://localhost:8000/health`

### 7. Gemini API Errors

**Symptom:** `API key not valid` or `Quota exceeded`

**Solution:**
- Verify `GEMINI_API_KEY` in `.env`
- Check API quota at [Google AI Studio](https://aistudio.google.com/)
- Ensure model name is correct: `models/gemini-2.5-flash-native-audio-preview-12-2025`

### 8. Node.js Version Mismatch

**Symptom:** `The engine "node" is incompatible with this module`

**Solution:**
```bash
# Check current version
node --version

# Switch to correct version (using nvm)
nvm install 22
nvm use 22

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

## Quick Reference

| Component | URL | Port |
|-----------|-----|------|
| Frontend | http://localhost:5173 | 5173 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| Voice WebSocket | ws://localhost:8000/api/speak/voice/ws/{token} | 8000 |
| PostgreSQL | localhost | 5432 |

### Key Commands

```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Database migrations
cd backend && alembic upgrade head

# Tests
cd backend && pytest
cd frontend && npm run test:e2e
```

---

## Additional Resources

- [DEVELOPMENT.md](./DEVELOPMENT.md) - Full development guide
- [API.md](./API.md) - API documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [SECURITY.md](./SECURITY.md) - Security considerations

---

*Built with [Claude Code](https://claude.com/claude-code)*
