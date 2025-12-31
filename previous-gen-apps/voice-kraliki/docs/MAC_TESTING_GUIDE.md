# Mac Testing Guide - CC-Lite 2026

**Purpose:** Guide for testing CC-Lite voice/call center features on macOS.

**Last Updated:** December 2025

---

## 1. Prerequisites

### Required Software

```bash
# Check your macOS version (minimum: macOS 12 Monterey)
sw_vers

# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install node@20       # Node.js 20+ for frontend
brew install python@3.11   # Python 3.11+ for backend
brew install uv            # Modern Python package manager
brew install pnpm          # Fast Node.js package manager
brew install docker        # Docker Desktop for Mac
brew install postgresql@16 # PostgreSQL client (optional, for psql)
brew install redis         # Redis client (optional, for redis-cli)

# Verify installations
node --version     # Should be 20.x or higher
python3 --version  # Should be 3.11.x or higher
uv --version
pnpm --version
docker --version
```

### Hardware Requirements for Voice Testing

- **Microphone:** Built-in Mac microphone or external USB microphone
- **Speakers/Headphones:** For audio playback testing
- **Network:** Stable internet connection for AI API calls

### System Permissions (macOS)

Open **System Preferences > Security & Privacy > Privacy**:

1. **Microphone:** Grant access to Terminal and your browser
2. **Screen Recording:** May be needed for E2E testing tools
3. **Accessibility:** May be needed for certain automation tools

---

## 2. Local Setup Steps

### Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone git@github.com:m-check1B/cc-lite-2026.git
cd cc-lite-2026

# Switch to develop branch for latest features
git checkout develop
git pull origin develop
```

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required keys for voice features:
# - OPENAI_API_KEY (for OpenAI Realtime API)
# - GEMINI_API_KEY (for Gemini 2.5 Native Audio)
# - DEEPGRAM_API_KEY (for Deepgram STT/TTS)
# - TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN (for telephony)
# - TELNYX_API_KEY (alternative telephony provider)
```

**Minimum .env for local testing:**

```bash
# Database (Docker or local PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/cc_lite_2026

# Security (use any value for local dev)
SECRET_KEY=local-dev-secret-key-change-in-production

# Redis (Docker or local)
REDIS_URL=redis://localhost:6379/0

# AI Providers (add your keys)
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
DEEPGRAM_API_KEY=...

# Telephony (optional for local testing)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
```

### Step 3: Start Database Services

**Option A: Docker (Recommended)**

```bash
# Start PostgreSQL, Redis, and Qdrant
docker compose up -d postgres redis qdrant

# Verify services are running
docker compose ps
```

**Option B: Local PostgreSQL**

```bash
# Start PostgreSQL via Homebrew
brew services start postgresql@16

# Create database
createdb cc_lite_2026

# Start Redis via Homebrew
brew services start redis
```

### Step 4: Backend Setup

```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start backend server
uv run uvicorn app.main:app --reload --port 8000

# Backend now running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Step 5: Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Frontend now running at http://localhost:3000
```

---

## 3. Running the App Locally

### Quick Start (All-in-One)

```bash
# Terminal 1: Start database services
cd cc-lite-2026
docker compose up -d postgres redis qdrant

# Terminal 2: Start backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 3: Start frontend
cd frontend
pnpm dev
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:8000 | REST API endpoints |
| API Docs | http://localhost:8000/docs | Swagger UI for API testing |
| ReDoc | http://localhost:8000/redoc | Alternative API documentation |

### Test Credentials

```
Email: testuser@example.com
Password: test123
```

### Verify Installation

```bash
# Test backend health
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"test123"}'
```

---

## 4. Testing Voice Features on Mac

### 4.1 Browser Microphone Setup

1. Open http://localhost:3000 in Chrome or Safari
2. Navigate to a voice-enabled page (e.g., `/calls/outbound`)
3. Allow microphone access when prompted
4. Test microphone in browser:
   ```javascript
   // Open browser console (Cmd+Option+J in Chrome)
   navigator.mediaDevices.getUserMedia({ audio: true })
     .then(stream => console.log('Microphone access granted'))
     .catch(err => console.error('Microphone error:', err));
   ```

### 4.2 Voice AI Testing

#### OpenAI Realtime API

```bash
# Ensure OPENAI_API_KEY is set in .env
# Navigate to voice call interface
# Click "Start Call" to initiate real-time conversation

# Backend logs will show:
# [INFO] OpenAI Realtime connection established
# [INFO] Audio stream started
```

#### Gemini 2.5 Native Audio

```bash
# Ensure GEMINI_API_KEY is set in .env
# Select Gemini as provider in settings
# Test voice interaction

# Backend logs will show:
# [INFO] Gemini audio session initialized
```

#### Deepgram STT/TTS

```bash
# Ensure DEEPGRAM_API_KEY is set in .env
# Used for transcription and text-to-speech

# Test transcription endpoint:
curl -X POST http://localhost:8000/api/v1/voice/transcribe \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "audio=@test_audio.wav"
```

### 4.3 WebSocket Voice Streaming

The app uses WebSocket for real-time audio streaming:

```javascript
// Test WebSocket connection from browser console
const ws = new WebSocket('ws://localhost:8000/ws/voice');
ws.onopen = () => console.log('WebSocket connected');
ws.onmessage = (event) => console.log('Message:', event.data);
ws.onerror = (error) => console.error('WebSocket error:', error);
```

### 4.4 Telephony Testing (Twilio/Telnyx)

**Note:** Full telephony testing requires:
- Valid Twilio/Telnyx account with phone numbers
- Webhook endpoints accessible from the internet (use ngrok for local)

**Local Testing with ngrok:**

```bash
# Install ngrok
brew install ngrok

# Expose local backend
ngrok http 8000

# Update Twilio webhook URLs to ngrok URL:
# https://abc123.ngrok.io/api/v1/webhooks/twilio/voice
```

### 4.5 IVR Flow Testing

1. Navigate to http://localhost:3000/operations/ivr
2. Create a new IVR flow using the visual builder
3. Add nodes: Start > Menu > Transfer/End
4. Publish the flow
5. Test by initiating a call (via API or Twilio)

```bash
# Test IVR flow via API
curl -X POST http://localhost:8000/api/ivr/flows/1/test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": "1"}'
```

---

## 5. Common Issues and Solutions

### Issue: Microphone Not Detected

**Symptoms:** Browser shows "Permission denied" or no audio input

**Solutions:**

```bash
# 1. Check macOS permissions
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"

# 2. Reset Safari permissions (if using Safari)
# Safari > Preferences > Websites > Microphone

# 3. Reset Chrome permissions (if using Chrome)
# chrome://settings/content/microphone

# 4. Test microphone in System Preferences
open "x-apple.systempreferences:com.apple.preference.sound"
```

### Issue: WebSocket Connection Failed

**Symptoms:** "WebSocket connection to 'ws://localhost:8000/...' failed"

**Solutions:**

```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check for CORS issues (backend logs)
docker compose logs backend | grep -i cors

# 3. Verify WebSocket endpoint exists
curl -i http://localhost:8000/ws/voice
# Should return 426 Upgrade Required (normal for HTTP request to WS endpoint)

# 4. Check firewall settings
sudo pfctl -s all | grep 8000
```

### Issue: "Module Not Found" Errors

**Backend:**

```bash
cd backend
rm -rf .venv
uv sync
source .venv/bin/activate
```

**Frontend:**

```bash
cd frontend
rm -rf node_modules .svelte-kit
pnpm install
```

### Issue: Database Connection Failed

**Symptoms:** "could not connect to server" or "database does not exist"

**Solutions:**

```bash
# 1. Check PostgreSQL is running
docker compose ps | grep postgres
# or
brew services list | grep postgresql

# 2. Verify database exists
psql -h localhost -U postgres -c "\l" | grep cc_lite

# 3. Create database if missing
createdb cc_lite_2026

# 4. Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Issue: Audio Quality Problems

**Symptoms:** Choppy audio, delays, or distortion

**Solutions:**

1. **Check network latency:**
   ```bash
   ping api.openai.com
   ping api.deepgram.com
   ```

2. **Increase buffer size:** Edit voice configuration in settings

3. **Use wired headphones:** Reduces Bluetooth latency

4. **Close other audio apps:** Prevent resource conflicts

### Issue: API Keys Not Working

**Symptoms:** 401 Unauthorized or provider-specific errors

**Solutions:**

```bash
# 1. Verify keys are set
cat .env | grep API_KEY

# 2. Test OpenAI key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 3. Test Deepgram key
curl https://api.deepgram.com/v1/listen \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/test.wav"}'

# 4. Restart backend after .env changes
# Ctrl+C in backend terminal, then:
uv run uvicorn app.main:app --reload --port 8000
```

### Issue: Port Already in Use

**Symptoms:** "Address already in use" error

**Solutions:**

```bash
# Find process using port
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port

# Kill the process
kill -9 <PID>

# Or use different port
uv run uvicorn app.main:app --reload --port 8001
```

---

## 6. Testing Checklist

### Basic Functionality

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Login works with test credentials
- [ ] Dashboard displays correctly
- [ ] API docs accessible at /docs

### Voice Features

- [ ] Microphone permission granted in browser
- [ ] WebSocket connection establishes
- [ ] Voice input is captured (check waveform/level indicator)
- [ ] AI responds to voice input
- [ ] Audio playback works
- [ ] Multiple voice providers work (OpenAI, Gemini, Deepgram)

### Call Center Features

- [ ] IVR builder loads and is interactive
- [ ] IVR flows can be created and saved
- [ ] Call routing rules can be configured
- [ ] Recording playback works
- [ ] Voicemail transcription works

### Multi-Language

- [ ] Language switcher works (EN, ES, CS)
- [ ] All UI elements translate correctly

---

## 7. Development Tools for Mac

### Recommended VS Code Extensions

```bash
# Install via CLI
code --install-extension ms-python.python
code --install-extension svelte.svelte-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension bradlc.vscode-tailwindcss
```

### Database GUI Tools

- **TablePlus:** `brew install --cask tableplus`
- **DBeaver:** `brew install --cask dbeaver-community`
- **Postico:** `brew install --cask postico`

### API Testing Tools

- **Insomnia:** `brew install --cask insomnia`
- **Postman:** `brew install --cask postman`
- **HTTPie:** `brew install httpie`

### Audio Testing Tools

- **Audacity:** `brew install --cask audacity` (for audio file editing)
- **SoX:** `brew install sox` (command-line audio processing)

```bash
# Record test audio with SoX
sox -d test_audio.wav trim 0 5  # Records 5 seconds

# Convert audio format
sox input.mp3 output.wav
```

---

## 8. Quick Reference Commands

```bash
# Start all services
docker compose up -d && cd backend && uv run uvicorn app.main:app --reload &
cd ../frontend && pnpm dev

# Stop all services
docker compose down
pkill -f uvicorn
pkill -f "node.*vite"

# View logs
docker compose logs -f          # Database logs
tail -f backend/server.log      # Backend logs

# Run tests
cd backend && uv run pytest tests/ -v
cd frontend && pnpm test

# Database operations
docker exec -it cc-lite-postgres psql -U postgres -d cc_lite_2026

# Check service health
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 9. Additional Resources

- **Project README:** `/README.md`
- **API Documentation:** http://localhost:8000/docs
- **Technical Guide:** `/docs/TECHNICAL_IMPLEMENTATION_GUIDE.md`
- **Quick Start:** `/docs/QUICK_START_GUIDE.md`
- **Architecture:** `/docs/architecture/`

---

**Happy Testing!** If you encounter issues not covered here, check the project's GitHub issues or the main documentation.
