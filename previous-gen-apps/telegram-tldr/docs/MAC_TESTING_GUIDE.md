# Mac Testing Guide for TL;DR Bot

This guide covers local testing of the Telegram TL;DR Bot on macOS for development and QA purposes.

## Prerequisites

- macOS 12+ (Monterey or newer)
- Python 3.11 or higher
- Redis (local or Docker)
- Telegram account
- Bot token from @BotFather
- Gemini API key

---

## 1. Python Setup

### Install Python with Homebrew

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.12

# Verify installation
python3 --version
```

### Install uv (Recommended Package Manager)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc

# Verify
uv --version
```

### Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd telegram-tldr

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

---

## 2. Redis Setup

### Option A: Using Homebrew (Native)

```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify Redis is running
redis-cli ping
# Should output: PONG

# Stop Redis when done
brew services stop redis
```

### Option B: Using Docker

```bash
# Start Redis container
docker run -d \
  --name tldr-redis-local \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --appendonly yes

# Verify Redis is running
docker exec tldr-redis-local redis-cli ping
# Should output: PONG

# Stop Redis when done
docker stop tldr-redis-local
docker rm tldr-redis-local
```

### Verify Redis Connection

```bash
# Test connection from Python
python3 -c "import redis; r = redis.Redis(); print('Connected!' if r.ping() else 'Failed')"
```

---

## 3. Telegram Bot Token Configuration

### Create a Test Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name (e.g., "TL;DR Test Bot")
4. Choose a username (must end with `bot`, e.g., `tldr_test_bot`)
5. Copy the bot token provided

### Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your values
nano .env
```

Configure the following in `.env`:

```bash
# Telegram Bot (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Leave these empty for local testing (polling mode)
TELEGRAM_WEBHOOK_URL=
TELEGRAM_WEBHOOK_SECRET=

# Gemini API Key (from https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Redis (local)
REDIS_URL=redis://localhost:6379/0

# Development settings
DEBUG=true

# Monetization (for testing)
FREE_SUMMARIES=3
SUBSCRIPTION_PRICE_STARS=250

# Your Telegram user ID for admin access (get from @userinfobot)
ADMIN_USER_IDS=your_telegram_user_id
```

### Get Your Telegram User ID

1. Open Telegram and search for `@userinfobot`
2. Send `/start`
3. Copy your user ID and add it to `ADMIN_USER_IDS`

---

## 4. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

---

## 5. Running the Bot Locally

### Polling Mode (Development)

For local testing, use polling mode (no webhook required):

```bash
# Activate virtual environment
source .venv/bin/activate

# Run in polling mode
python -m app.main
```

You should see output like:
```
2024-XX-XX HH:MM:SS - app.main - INFO - Starting in polling mode (development)...
```

### Test the Bot

1. Open Telegram
2. Search for your test bot by username
3. Send `/start` to verify it responds
4. Send `/help` to see available commands
5. Send `/health` to check bot status

---

## 6. Testing Summaries Locally

### Create a Test Group

1. Create a new Telegram group
2. Add your test bot to the group
3. Make the bot an admin (required for reading messages)

### Test Flow

```bash
# 1. Start the bot in polling mode
python -m app.main

# 2. In Telegram:
#    - Send several messages in the test group
#    - Wait a few seconds for messages to buffer
#    - Send /summary command

# 3. The bot should:
#    - Process your messages
#    - Generate an AI summary using Gemini
#    - Reply with formatted summary
```

### Verify Redis Buffering

```bash
# Check stored messages in Redis
redis-cli keys "tldr:*"

# View messages for a specific chat
redis-cli zrange "tldr:chat:<chat_id>:messages" 0 -1
```

---

## 7. Running Tests

### Run Unit Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test API Endpoints Manually

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

---

## 8. Webhook Testing (Optional)

For testing webhook mode locally, use ngrok:

```bash
# Install ngrok
brew install ngrok

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# Update .env
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok.io

# Run with FastAPI (webhook mode)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 9. Common Issues and Solutions

### Bot Not Responding

```bash
# Check if bot token is valid
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Should return bot info, not error
```

### Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# If using Docker, check container
docker ps | grep redis

# Restart Redis
brew services restart redis
# or
docker restart tldr-redis-local
```

### Gemini API Errors

```bash
# Test Gemini API directly
python3 -c "
import google.generativeai as genai
genai.configure(api_key='your_api_key')
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content('Hello')
print(response.text)
"
```

### Permission Denied in Group

- Ensure the bot is an admin in the group
- Check that the bot has "Read messages" permission
- Verify with `/health` command that Redis is connected

---

## 10. Development Workflow

### Recommended IDE Setup

```bash
# VS Code with Python extensions
code .

# Install recommended extensions:
# - Python (ms-python.python)
# - Pylance (ms-python.vscode-pylance)
# - Python Debugger (ms-python.debugpy)
```

### Code Formatting

```bash
# Format with ruff
ruff format app/

# Lint code
ruff check app/
```

### Hot Reload Development

```bash
# For webhook mode with auto-reload
uvicorn app.main:app --reload --port 8000

# For polling mode, restart manually after changes
python -m app.main
```

---

## 11. Cleanup

```bash
# Stop Redis
brew services stop redis
# or
docker stop tldr-redis-local

# Deactivate virtual environment
deactivate

# Remove test data from Redis
redis-cli FLUSHDB
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies |
| `python -m app.main` | Run in polling mode (dev) |
| `pytest` | Run tests |
| `redis-cli ping` | Check Redis |
| `/start` | Bot onboarding |
| `/summary` | Generate chat digest |
| `/health` | Bot status |
| `/status` | Usage info |

---

## Environment Variables Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `GEMINI_API_KEY` | Yes | API key from AI Studio |
| `REDIS_URL` | No | Redis connection (default: localhost:6379) |
| `DEBUG` | No | Enable debug logging (default: false) |
| `FREE_SUMMARIES` | No | Free tier limit (default: 3) |
| `ADMIN_USER_IDS` | No | Comma-separated admin user IDs |

---

*For production deployment, see the main README and docker-compose.yml configuration.*
