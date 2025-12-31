# AI-First UI Redesign - Focus by Kraliki

## Problem Statement
Current dashboard has:
- ❌ Tab-based navigation hiding the AI chat
- ❌ Bottom navigation bar covering content (scroll issues)
- ❌ Features shown all at once (patchwork)
- ❌ Chat only visible in "focus" tab
- ❌ Not truly AI-first - navigation fights the assistant

## New Architecture: AI-First with Contextual Features

### Core Principle
**The AI is always visible and central. Features appear contextually based on what's happening.**

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER                                                          │
│ [Logo] Focus by Kraliki        [Search] [Theme] [Profile] [Logout]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MAIN AREA (AI Chat - Always Visible)                          │
│  ┌───────────────────────────────────┐                         │
│  │                                   │                         │
│  │   AI Conversation                 │   [Contextual Panel]   │
│  │   - Text chat                     │   - Hidden by default   │
│  │   - Voice input                   │   - Slides from right  │
│  │   - Quick prompts                 │   - Shows on demand    │
│  │   - Workflow cards                │                        │
│  │                                   │                        │
│  └───────────────────────────────────┘                         │
│                                                                 │
│  INPUT BAR (Bottom)                                             │
│  [Voice] [Type your message...] [Model] [Send]                 │
└─────────────────────────────────────────────────────────────────┘
```

### Contextual Panel System

#### When to Show Panels

1. **User Command**
   - "show my tasks" → Tasks panel slides in
   - "open settings" → Settings panel
   - "what's on my calendar" → Calendar panel

2. **AI Suggestion**
   - AI: "I found 3 tasks, review?" → Tasks panel with highlights
   - AI: "Created workflow, approve?" → Workflow panel

3. **User Action**
   - Click task in chat → Task detail panel
   - Click workflow → Workflow detail panel

4. **Keyboard Shortcut**
   - `Cmd+K` → Command palette (search all features)
   - `Cmd+T` → Tasks panel
   - `Cmd+P` → Projects panel
   - `Cmd+,` → Settings panel

#### Panel Types

1. **Tasks** - View/edit/create tasks
2. **Projects** - Project management
3. **Knowledge** - Knowledge base items
4. **Calendar** - Events & scheduling
5. **Analytics** - Usage insights
6. **Settings** - App configuration
7. **Workflow** - Workflow approval/review

### UI Components Needed

#### New Components
1. `ContextPanel.svelte` - Sliding panel container
2. `CommandPalette.svelte` - Cmd+K search
3. `QuickActions.svelte` - Top-right quick buttons

#### Modified Components
1. `AssistantShell.svelte` - Remove bottom tabs, simplify
2. `dashboard/+page.svelte` - Single AI-first layout
3. `UnifiedCanvas.svelte` - Add panel triggers

### User Flow Examples

#### Example 1: Task Management
```
User: "What do I need to do today?"
AI: "You have 3 tasks: [1] Deploy backend [2] Review PR..."
     [View All Tasks →]

User clicks "View All Tasks"
→ Tasks panel slides from right
→ Chat stays visible on left
→ User can interact with both
```

#### Example 2: Settings
```
User presses: Cmd+,
→ Settings panel slides in
→ Chat visible but dimmed
→ ESC closes panel
```

#### Example 3: Voice Command
```
User: *holds voice button* "Create a task to call John tomorrow"
AI: "Task created: Call John. Due: Tomorrow 9 AM"
    [View Task →] [Edit →]

User clicks "View Task"
→ Task detail panel slides in
→ Can edit inline
```

### Benefits

✅ **AI Always Central** - Chat never hidden
✅ **Contextual** - Features appear when needed
✅ **No Navigation Clutter** - No bottom tabs
✅ **Keyboard-Friendly** - Cmd+K for power users
✅ **Voice-First Compatible** - Works with voice commands
✅ **Mobile-Friendly** - Panels become full-screen modals
✅ **Clean & Focused** - Brutalist, minimalist design

### Implementation Plan

1. **Phase 1: Core Layout** ✓
   - Remove bottom tab bar
   - Simplify AssistantShell
   - Make chat full-width

2. **Phase 2: Panel System**
   - Create ContextPanel component
   - Add slide-in animations
   - Implement panel routing

3. **Phase 3: Integration**
   - Add panel triggers to chat messages
   - Implement keyboard shortcuts
   - Add command palette

4. **Phase 4: Polish**
   - Smooth animations
   - Mobile responsiveness
   - Accessibility

### Technical Notes

- Use Svelte stores for panel state
- CSS transforms for smooth slides
- Keyboard trap in panels
- Backdrop blur when panel open
- Panel stack (multiple panels)
