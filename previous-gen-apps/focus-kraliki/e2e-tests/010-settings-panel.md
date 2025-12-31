# Test 010: Settings Panel

**Priority:** P1 (High)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 8 minutes

## Objective

Verify the Settings context panel displays and allows configuration changes.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Open Settings Panel

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Click Settings FAB button OR press Ctrl+,

**Expected Results:**
- [ ] Settings panel slides in from the side
- [ ] Panel header shows "Settings"
- [ ] Close button is available
- [ ] Settings are organized in sections

### Scenario B: Theme Settings

1. Open Settings panel
2. Find theme/appearance section

**Expected Results:**
- [ ] Theme toggle is visible
- [ ] Options: Light, Dark, System
- [ ] Current theme is indicated
- [ ] Can switch between themes

### Scenario C: Toggle Dark Mode

1. Find dark mode toggle
2. Switch from current mode to opposite

**Expected Results:**
- [ ] Theme changes immediately
- [ ] All UI elements update (background, text, borders)
- [ ] Brutalist styling adapts (black borders in light, white in dark)
- [ ] Setting persists after page reload

### Scenario D: Profile Settings

1. Look for profile/account section

**Expected Results:**
- [ ] User name is displayed
- [ ] User email is displayed
- [ ] Option to update profile info
- [ ] Logout option available

### Scenario E: Feature Toggles

1. Find feature toggles section

**Expected Results:**
- [ ] Gemini File Search toggle
- [ ] II-Agent toggle
- [ ] Voice Transcription toggle
- [ ] Each can be enabled/disabled

### Scenario F: Toggle Feature

1. Find a feature toggle (e.g., Voice Transcription)
2. Toggle it off/on

**Expected Results:**
- [ ] Toggle state changes
- [ ] Setting is saved
- [ ] Related UI elements update accordingly
- [ ] Confirmation or auto-save indicator

### Scenario G: BYOK (Bring Your Own Key)

1. Look for API key configuration section

**Expected Results:**
- [ ] OpenRouter key field (or similar)
- [ ] Key can be entered (masked input)
- [ ] Instructions for obtaining keys
- [ ] Save/Apply button

### Scenario H: Privacy Settings

1. Look for privacy section

**Expected Results:**
- [ ] Data privacy acknowledgment status
- [ ] Privacy policy link
- [ ] Data handling preferences

## Settings Sections

| Section | Contents |
|---------|----------|
| Appearance | Theme toggle (Light/Dark/System) |
| Profile | Name, Email, Avatar |
| Features | Gemini, II-Agent, Voice toggles |
| BYOK | API key configuration |
| Privacy | Privacy preferences, policy |
| Notifications | Alert preferences |

## Deep Link

### Scenario I: Direct URL

1. Navigate directly to: `https://focus.verduona.dev/dashboard/settings`

**Expected Results:**
- [ ] Redirects to dashboard
- [ ] Settings panel opens automatically
- [ ] Uses PanelRedirect component

## Pass Criteria

- Settings panel opens and closes correctly
- Theme toggle works (light/dark)
- Feature toggles work
- Settings persist across sessions
- Deep link works

## Screenshots Required

1. Settings panel overview
2. Theme settings section
3. Feature toggles section
4. Dark mode applied
5. Light mode applied
