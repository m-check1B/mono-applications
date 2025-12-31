# Focus Lite User Guide

> **Version**: 2.1.0
> **Last Updated**: November 14, 2025
> **Audience**: End users, productivity enthusiasts

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Knowledge Hub](#knowledge-hub)
3. [Agent Workbench](#agent-workbench)
4. [Bring Your Own Key (BYOK)](#bring-your-own-key-byok)
5. [Core Features](#core-features)
6. [Tips & Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is Focus Lite?

Focus Lite is an AI-first productivity system that combines intelligent task management, natural language processing, and a flexible knowledge layer. Unlike traditional productivity apps, Focus Lite understands context, learns from your patterns, and helps you work smarter through AI-powered assistance.

### Key Features at a Glance

- **Knowledge Hub**: Organize ideas, notes, tasks, and plans with custom item types
- **Agent Workbench**: AI-powered assistant that can create and manage your work items
- **BYOK Support**: Use your own OpenRouter API key for unlimited AI access
- **Smart Task Management**: Priority-based tasks with AI scheduling
- **Shadow Analysis**: Jungian psychology-based productivity insights
- **Voice Interface**: Natural speech-to-task conversion
- **Flow Memory**: Persistent context across sessions

### Quick Start (5 Minutes)

1. **Create an Account**
   - Navigate to `/register`
   - Enter your email and password
   - Verify your email (if required)

2. **Access the Dashboard**
   - Log in at `/login`
   - You'll see the main dashboard with:
     - Task list
     - Project overview
     - Quick actions

3. **Create Your First Task**
   ```
   Click "Add Task" → Enter title → Set priority → Save
   ```

4. **Try the AI Assistant**
   - Navigate to the AI chat section
   - Ask: "Create a task to review project documentation"
   - Watch the AI parse and create your task automatically

---

## Knowledge Hub

The Knowledge Hub is Focus Lite's flexible knowledge management system, inspired by modern note-taking apps but powered by AI.

### Understanding Item Types

**What are Item Types?**

Item types are categories that define what kind of knowledge items you can create. Think of them as "templates" or "schemas" for your content.

**Default Item Types** (created automatically on first use):

- **Ideas**: Capture creative thoughts and brainstorming
- **Notes**: General-purpose note-taking
- **Tasks**: Action items and to-dos
- **Plans**: Project plans and strategic thinking
- **Resources**: Links, references, and learning materials

### Creating Custom Item Types

You can create your own item types to match your workflow:

1. **Access Item Type Management**
   - Navigate to Settings → Knowledge Hub
   - Click "Manage Item Types"

2. **Create New Type**
   ```
   Name: "Meeting Notes"
   Icon: "calendar"
   Color: "#4A90E2"
   ```

3. **Use Your Custom Type**
   - New item types appear in the Knowledge Hub dropdown
   - Create items with your custom classification

### Working with Knowledge Items

**Creating Knowledge Items**

1. **Via the UI**
   ```
   Knowledge Hub → New Item → Select Type
   ↓
   Enter Title: "Q4 Product Strategy"
   Enter Content: "Focus areas: 1. User retention..."
   Add Metadata: { priority: "high", deadline: "2025-12-15" }
   ↓
   Save
   ```

2. **Via AI Assistant** (see Agent Workbench section)
   ```
   Ask: "Create an idea about improving user onboarding"
   → AI creates knowledge item automatically
   ```

**Organizing Knowledge Items**

- **Filter by Type**: Use dropdown to see only specific types
- **Mark as Complete**: Toggle completion status for tasks/action items
- **Search**: Full-text search across titles and content
- **Metadata**: Add custom JSON metadata for advanced organization

**Best Practices**

- Use **Ideas** for raw, unprocessed thoughts
- Convert **Ideas** to **Plans** when they mature
- Link **Tasks** to specific **Plans** via metadata
- Use **Notes** for meeting summaries and documentation
- Keep **Resources** for external links and references

### Knowledge Item Metadata

Metadata is stored as JSON and can include any custom fields:

```json
{
  "priority": "high",
  "status": "in-progress",
  "tags": ["marketing", "urgent"],
  "deadline": "2025-12-31",
  "assignee": "team-alpha",
  "estimatedHours": 8
}
```

**Common Metadata Patterns**

- **Priority**: "low" | "medium" | "high" | "critical"
- **Status**: "draft" | "in-progress" | "review" | "complete"
- **Tags**: Array of strings for categorization
- **Links**: References to other items or external URLs
- **Dates**: ISO 8601 format for deadlines and milestones

---

## Agent Workbench

The Agent Workbench is where Focus Lite's AI capabilities shine. It uses advanced language models to understand your intent and take action.

### What is the Agent?

The Agent is an AI assistant powered by:
- **Claude 3.5 Sonnet**: For complex reasoning and planning
- **OpenRouter Models**: For flexible model selection with BYOK
- **Function Calling**: Direct integration with Focus Lite's database

Unlike simple chatbots, the Agent can:
- Create and update knowledge items
- Manage tasks and projects
- Search and retrieve context
- Learn from your patterns

### Getting Started with the Agent

1. **Start a Conversation**
   - Navigate to Agent Workbench
   - Type a natural language request
   - Press Enter or click Send

2. **Example Conversations**

   **Creating Items**
   ```
   You: "I have an idea about using AI for customer support automation"

   Agent: "Great idea! I've created a new knowledge item:
           - Type: Ideas
           - Title: AI for customer support automation
           - Status: Open

           Would you like me to help develop this into a plan?"
   ```

   **Managing Tasks**
   ```
   You: "Create 3 tasks for preparing the Q4 board presentation"

   Agent: "I've created the following tasks:
           1. Gather Q3 performance data
           2. Draft presentation outline
           3. Create slides and visuals

           All set with medium priority and due next Friday."
   ```

   **Information Retrieval**
   ```
   You: "Show me all my high-priority tasks for this week"

   Agent: "Here are your high-priority tasks:
           - Complete API documentation (due Wed)
           - Review security audit (due Thu)
           - Finalize marketing copy (due Fri)"
   ```

### Advanced Agent Features

**Context Awareness**

The Agent maintains conversation context and can reference previous items:

```
You: "Create a plan for implementing the customer support AI idea"
Agent: [References the idea you created earlier]

You: "Add that to my Q4 roadmap project"
Agent: [Links the plan to your existing project]
```

**Multi-Step Actions**

The Agent can execute complex workflows:

```
You: "Set up a new project for the website redesign with initial tasks"

Agent: Creates:
       1. Project: "Website Redesign"
       2. Plan: "Redesign Strategy"
       3. Tasks: Research, Design, Development, Testing
       4. Knowledge items: Notes and resources
```

**Learning and Adaptation**

Over time, the Agent learns:
- Your preferred organization patterns
- Common task types and priorities
- Project structures you frequently use
- Communication style preferences

### Agent Permissions

The Agent can:
- ✅ Create, read, update knowledge items
- ✅ Create and update tasks
- ✅ Create projects
- ✅ Search your data
- ❌ Delete items (requires explicit confirmation)
- ❌ Access other users' data
- ❌ Perform system administration

---

## Bring Your Own Key (BYOK)

BYOK allows you to use your own OpenRouter API key, giving you:
- **Unlimited AI usage** (no rate limits)
- **Model selection** (choose from 100+ models)
- **Cost control** (pay only for what you use)
- **Privacy** (your API key, your data)

### What is OpenRouter?

[OpenRouter](https://openrouter.ai) is a unified API for accessing multiple AI models:
- Anthropic Claude
- OpenAI GPT-4
- Google Gemini
- Meta Llama
- And 100+ more models

### Setting Up BYOK

**Step 1: Get an OpenRouter API Key**

1. Visit [openrouter.ai](https://openrouter.ai)
2. Create an account
3. Navigate to Keys section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)

**Step 2: Add Key to Focus Lite**

1. In Focus Lite, go to Settings → API Keys
2. Click "Add OpenRouter Key"
3. Paste your key
4. Click "Test Key" to verify
5. Save

**Step 3: Start Using**

Once configured:
- Free usage limits are removed
- You can select specific models
- Usage is billed to your OpenRouter account

### BYOK Best Practices

**Cost Management**

- Monitor usage on OpenRouter dashboard
- Set budget alerts
- Use cheaper models for simple tasks:
  - `gpt-3.5-turbo` for basic chat
  - `claude-3-haiku` for quick responses
  - `claude-3.5-sonnet` for complex reasoning

**Security**

- Never share your API key
- Rotate keys periodically
- Use read-only keys if available
- Remove keys when not in use

**Model Selection Guide**

| Use Case | Recommended Model | Cost |
|----------|------------------|------|
| Basic chat | GPT-3.5 Turbo | $ |
| Quick tasks | Claude 3 Haiku | $ |
| Complex reasoning | Claude 3.5 Sonnet | $$$ |
| Long context | GPT-4 Turbo | $$ |
| Code generation | GPT-4 | $$$ |

### Removing BYOK

To revert to default (limited) usage:

1. Settings → API Keys
2. Click "Remove Key"
3. Confirm removal
4. You'll return to free tier limits

---

## Core Features

### Task Management

**Creating Tasks**

- **Manual**: Click "Add Task" → Fill form
- **Voice**: Use voice command (if enabled)
- **AI**: Ask Agent to create task
- **Natural Language**: Use `/ai/parse-task` endpoint

**Task Properties**

- Title (required)
- Description (optional, supports Markdown)
- Status: Pending, In Progress, Completed, Cancelled
- Priority: 1-5 (1 = lowest, 5 = highest)
- Due Date
- Estimated Time (minutes)
- Project Association
- Tags and Metadata

**Smart Scheduling**

Focus Lite includes AI-powered scheduling:

```
Navigate to AI Scheduler → Select tasks → Generate schedule
→ AI optimizes based on:
  - Priority
  - Estimated time
  - Energy levels
  - Dependencies
```

### Project Management

**Creating Projects**

```
Projects → New Project
↓
Name: "Q4 Website Redesign"
Description: "Complete overhaul of public website"
Color: #FF6B6B
Icon: "globe"
```

**Project Features**

- Task grouping and filtering
- Progress tracking
- Timeline visualization
- Resource allocation
- Milestone tracking

### Time Tracking

**Manual Tracking**

```
Task → Start Timer → Work → Stop Timer
→ Time entry created automatically
```

**Time Entry Properties**

- Task association
- Start/end time
- Duration
- Notes
- Billable status

**Reports**

- Daily/weekly/monthly summaries
- Project time breakdowns
- Productivity patterns
- Export to CSV

### Shadow Analysis

Shadow Analysis uses Jungian psychology to identify unconscious productivity patterns.

**What is Shadow Work?**

Your "shadow" represents hidden patterns affecting productivity:
- Procrastination triggers
- Energy cycles
- Emotional blocks
- Motivation patterns

**Progressive Unlock (30 Days)**

- Days 1-7: Basic pattern detection
- Days 8-14: Trend analysis
- Days 15-21: Deeper insights
- Days 22-30: Full shadow profile

**Using Shadow Insights**

1. Check Shadow Dashboard daily
2. Acknowledge insights to unlock more
3. Apply recommendations
4. Track improvement over time

### Voice Interface

**Supported Providers**

- **Gemini 2.5 Flash**: Native audio processing (live)
- **OpenAI Realtime**: GPT-4 real-time audio (live)
- **Deepgram**: Speech-to-text transcription

**Voice Commands**

```
"Create a task to review the documentation"
→ Task created: "Review the documentation"

"What are my tasks for today?"
→ Lists today's tasks

"Schedule a meeting with the team next Tuesday at 2 PM"
→ Calendar event created
```

---

## Tips and Best Practices

### Organization

**Weekly Review Ritual**

Every Monday:
1. Review completed tasks from last week
2. Archive or delete outdated knowledge items
3. Plan week's priorities
4. Update project statuses

**Item Type Strategy**

- Start with default types
- Add custom types only when needed
- Keep type names short and clear
- Use consistent icons and colors

### AI Usage

**Effective Prompting**

Good:
```
"Create a plan for implementing user authentication with JWT,
including setup, testing, and deployment tasks"
```

Bad:
```
"auth stuff"
```

**Conversation Flow**

1. Start with context
2. Be specific about desired outcome
3. Confirm before major actions
4. Reference previous items

### Performance

**Search Optimization**

- Use specific keywords
- Filter by type before searching
- Leverage metadata for advanced queries
- Keep titles descriptive

**Database Health**

- Archive completed items monthly
- Delete unused custom types
- Review and merge duplicate projects
- Export data backups regularly

### Workflow Integration

**Morning Routine**

1. Check Agent Workbench for overnight insights
2. Review high-priority tasks
3. Time-block deep work
4. Set daily intention

**Evening Routine**

1. Complete time entries
2. Update task statuses
3. Capture tomorrow's priorities
4. Acknowledge shadow insights

---

## Troubleshooting

### Common Issues

**AI Not Responding**

1. Check API key status (Settings → API Keys)
2. Verify internet connection
3. Check browser console for errors
4. Try refreshing the page

**Knowledge Items Not Saving**

1. Verify all required fields are filled
2. Check metadata JSON is valid
3. Ensure type exists
4. Try creating via Agent instead

**BYOK Key Invalid**

1. Verify key starts with `sk-or-v1-`
2. Check for extra spaces when pasting
3. Confirm key is active on OpenRouter
4. Test with OpenRouter dashboard

### Getting Help

**Documentation**

- User Guide (this document)
- [API Reference](/docs/API_REFERENCE.md)
- [Developer Guide](/docs/DEVELOPER_GUIDE.md)

**Support Channels**

- GitHub Issues: Bug reports and feature requests
- Email: support@focuslite.app
- Community: Discord server (link in dashboard)

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Item type not found" | Referenced type doesn't exist | Create type or use existing one |
| "Usage limit exceeded" | Free tier limit reached | Add BYOK key or upgrade |
| "Invalid metadata JSON" | Malformed JSON in metadata field | Validate JSON syntax |
| "Agent session expired" | Token expired | Refresh page to create new session |

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New Task | `Ctrl+N` |
| Quick Search | `Ctrl+K` |
| Open AI Chat | `Ctrl+/` |
| Toggle Sidebar | `Ctrl+B` |
| Save | `Ctrl+S` |
| Cancel | `Esc` |

---

## What's Next?

- Explore the [API Reference](/docs/API_REFERENCE.md) for programmatic access
- Read the [Developer Guide](/docs/DEVELOPER_GUIDE.md) to extend Focus Lite
- Check the [Changelog](/CHANGELOG.md) for latest updates
- Join our community to share workflows and tips

---

**Focus Lite** - Simply In, Simply Out

*Empowering productivity through AI and thoughtful design.*
