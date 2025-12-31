# Focus by Kraliki E2E Test Plans

**App URL:** https://focus.verduona.dev
**Created:** 2025-12-25
**Last Updated:** 2025-12-25

## Overview

This directory contains end-to-end (E2E) test plans for Focus by Kraliki, an AI-first productivity system.
Tests are designed to be executed via the Claude Code Chrome extension.

## Test Categories

| Test ID | Name | Priority | Status |
|---------|------|----------|--------|
| 001 | Homepage & Auth Redirect | P0 | Pending |
| 002 | Login Flow | P0 | Pending |
| 003 | Registration Flow | P0 | Pending |
| 004 | Google OAuth Flow | P1 | Pending |
| 005 | Dashboard Main View | P0 | Pending |
| 006 | AI Chat / Command Center | P0 | Pending |
| 007 | Quick Action Buttons | P1 | Pending |
| 008 | Tasks Panel | P0 | Pending |
| 009 | Timer / Pomodoro Panel | P1 | Pending |
| 010 | Settings Panel | P1 | Pending |
| 011 | Voice Recording | P2 | Pending |
| 012 | Onboarding Flow | P1 | Pending |
| 013 | Dark Mode Toggle | P2 | Pending |
| 014 | Keyboard Shortcuts | P2 | Pending |
| 015 | Knowledge Panel | P1 | Pending |

## Priority Legend

- **P0**: Critical - Must pass for release
- **P1**: High - Important functionality
- **P2**: Medium - Nice to have
- **P3**: Low - Edge cases

## Test Execution

### Via Claude Code Chrome Extension

1. Open Chrome with Claude extension
2. Navigate to Focus by Kraliki URL
3. Paste test instructions from test file
4. Execute and record results

### Results

Results are stored in the `results/` subdirectory with format:
- `YYYY-MM-DD_TESTID_result.md`

## App Architecture Notes

Focus by Kraliki uses an AI-first architecture:
- Homepage (`/`) redirects to `/login` or `/dashboard` based on auth state
- Dashboard is the main interface with floating action buttons
- Features open as slide-in context panels (not separate pages)
- Routes like `/dashboard/tasks` redirect to dashboard and open the tasks panel

### Key Routes

| Route | Description |
|-------|-------------|
| `/` | Auth redirect (to /login or /dashboard) |
| `/login` | Email/password + Google OAuth login |
| `/register` | Account registration |
| `/onboarding` | 4-step persona onboarding |
| `/dashboard` | Main AI command center |
| `/dashboard/tasks` | Opens tasks panel |
| `/dashboard/time` | Opens timer/pomodoro panel |
| `/dashboard/settings` | Opens settings panel |
| `/dashboard/knowledge` | Opens knowledge panel |
| `/dashboard/calendar` | Opens calendar panel |

### UI Components

- **Floating Action Buttons**: Tasks, Knowledge, Calendar, Timer, Settings
- **AI Canvas**: Central chat/command interface
- **Quick Prompts**: Pre-defined action buttons
- **Context Panels**: Slide-in panels for features
- **Command Palette**: Ctrl+K for quick access

## Contact

Issues should be logged in Linear via `/e2e-results-pickup` skill.
