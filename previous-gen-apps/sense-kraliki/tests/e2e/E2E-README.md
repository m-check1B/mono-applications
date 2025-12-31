# Sense by Kraliki Bot E2E Tests - Bot Commands

Comprehensive end-to-end tests for Sense by Kraliki Telegram bot.

## Overview

This test suite validates all major features of the Sense by Kraliki bot:
- Bot commands (/start, /help, /sense, /astro, /remedies, /bio, /forecast)
- User settings (/setbirthday, /setlocation)
- Subscription management (/status, /subscribe)
- Dream analysis with state machine
- Biorhythm calculations
- 12-month astrological forecasts
- Error handling and edge cases

## Test Architecture

### Files

- **conftest.py**: Test fixtures and mocks
  - Mock Redis (in-memory)
  - Mock Gemini AI client
  - Mock Telegram bot
  - Telegram update factory
  - Service mocks (sensitivity, biorhythm, astro, remedies)

- **test_bot_commands.py**: Bot command tests
  - All slash commands
  - User data management
  - Error handling

- **test_dream_analysis.py**: Feature-specific tests
  - Dream analysis flow
  - Biorhythm calculations
  - 12-month forecasts

- **LIN-VD-156.sh**: Verification script

## Running Tests

### Run all E2E tests
```bash
cd /home/adminmatej/github/applications/sense-kraliki
python -m pytest tests/e2e/ -v
```

### Run specific test file
```bash
python -m pytest tests/e2e/test_bot_commands.py -v
python -m pytest tests/e2e/test_dream_analysis.py -v
```

### Run specific test
```bash
python -m pytest tests/e2e/test_bot_commands.py::TestBotCommands::test_start_command -v
```

### Run with coverage
```bash
python -m pytest tests/e2e/ --cov=app --cov-report=html
```

## Verification

Run the verification script:
```bash
bash tests/e2e/LIN-VD-156.sh
```

## Design Decisions

1. **Pytest over Playwright**: Used pytest instead of Playwright for bot testing
   - Telegram bots don't have browser UI to test
   - pytest with async support is more natural for testing async handlers
   - Follows pattern from telegram-tldr tests

2. **Comprehensive Mocking**: All external dependencies mocked
   - No API calls required
   - Tests run anywhere (no network needed)
   - Deterministic test results

3. **State Machine Testing**: Dream analysis flow tests state transitions
   - /dream without text → waiting state
   - User sends text → analysis
   - State cleared after processing

4. **Error Coverage**: Tests verify graceful error handling
   - Invalid date formats
   - Invalid coordinate formats
   - Missing required data
   - Unknown commands

## Coverage

- **Bot Commands**: 13 tests
- **Dream Analysis**: 6 tests
- **Biorhythm**: 2 tests
- **Forecast**: 2 tests
- **Error Handling**: Valid/invalid inputs for all commands

Total: 26+ test cases covering >80% of main user flows

## Notes

- Tests skip gracefully if app modules not available
- No external API calls required
- Uses in-memory mock Redis
- Gemini AI responses mocked with predefined values
