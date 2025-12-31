# User Research - Focus by Kraliki

**Purpose:** Document typical users, their workflows, needs, objections, and feature requests
**Created:** 2025-11-14
**Status:** Living document - continuously updated

---

## 📁 Directory Structure

```
user-research/
├── README.md                    # This file - overview and navigation
├── personas/                    # User persona definitions
│   ├── 01-solo-developer.md
│   ├── 02-freelancer.md
│   ├── 03-small-business-owner.md
│   ├── 04-knowledge-worker.md
│   └── 05-team-lead.md
├── workflows/                   # Real user workflows and usage patterns
│   ├── daily-planning.md
│   ├── project-management.md
│   ├── knowledge-capture.md
│   └── team-collaboration.md
├── requests/                    # Feature requests from real users
│   ├── BACKLOG.md
│   └── [dated-request-files].md
└── objections/                  # Common objections and concerns
    └── common-objections.md
```

---

## 🎯 User Groups (Personas)

### Primary Users (80% of usage)

1. **Solo Developer** - Individual developer managing personal projects
   - Needs: Task management, time tracking, project planning
   - Pain points: Context switching, procrastination, overwhelm
   - Usage: Daily planning, code project tracking

2. **Freelancer** - Independent contractor juggling multiple clients
   - Needs: Client management, billing tracking, deadline management
   - Pain points: Time estimation, client communication, scope creep
   - Usage: Multi-project management, time tracking, invoicing prep

3. **Knowledge Worker** - Writer, researcher, analyst
   - Needs: Note-taking, idea management, research organization
   - Pain points: Information overload, idea capture, synthesis
   - Usage: Knowledge base, daily journaling, idea evaluation

### Secondary Users (15% of usage)

4. **Small Business Owner** - Running 1-10 person business
   - Needs: Team coordination, goal tracking, operational planning
   - Pain points: Delegation, priority setting, strategic planning
   - Usage: Team workspaces, goal → task breakdown, team analytics

5. **Team Lead** - Managing 3-8 person team
   - Needs: Team productivity, bottleneck identification, planning
   - Pain points: Visibility, coordination, performance tracking
   - Usage: Team analytics, shared projects, workflow automation

### Edge Users (5% of usage)

6. **Power User** - Advanced automation seeker
7. **Student** - Academic project management
8. **Creator** - Content creation pipeline

---

## 📊 Usage Patterns

### High-Frequency Actions (Daily)
- Create tasks from natural language
- Check daily schedule / plan day
- Start/stop time tracking
- Add notes to knowledge base
- Voice capture ideas

### Medium-Frequency Actions (Weekly)
- Review productivity patterns
- Plan upcoming week
- Evaluate ideas / choose next project
- Review team progress (team users)
- Generate weekly reports

### Low-Frequency Actions (Monthly)
- Set quarterly goals
- Deep shadow analysis
- Clean up projects
- Analyze bottlenecks
- Generate monthly reports

---

## 🔥 Top 10 Real User Requests

Based on user interviews and feature requests:

1. **"Show me priority tasks for today, plan my day"** (80% of users, daily)
2. **"Add task: [natural language]"** (90% of users, multiple times daily)
3. **"What did I work on last week?"** (60% of users, weekly)
4. **"Help me choose which idea to pursue"** (40% of users, monthly)
5. **"Break down [goal] into tasks"** (50% of users, weekly)
6. **"Analyze my productivity patterns"** (30% of users, monthly)
7. **"Sync my calendar and create prep tasks"** (35% of users, weekly)
8. **"Voice: create task for Monday morning"** (25% of users, daily)
9. **"I'm feeling overwhelmed, help reorganize"** (20% of users, weekly)
10. **"Generate my weekly review with insights"** (40% of users, weekly)

---

## ⚠️ Common Objections

### Before Sign-Up

1. **"Another productivity app? I've tried dozens"**
   - Response: Shadow Analysis + AI insights are unique
   - Proof: Show 30-day unlock, Jungian psychology approach

2. **"I don't trust AI with my personal data"**
   - Response: BYOK (Bring Your Own Keys), local-first options
   - Proof: Show data export, privacy controls

3. **"Too expensive / can't justify subscription"**
   - Response: Free tier + credit-based usage
   - Proof: Show cost calculator, ROI metrics

### During Onboarding

4. **"Learning curve is too steep"**
   - Response: Natural language input, voice commands
   - Proof: Show examples, interactive tutorial

5. **"My workflow is too specific"**
   - Response: Workflow automation, templates
   - Proof: Show customization options

### During Usage

6. **"AI responses are too slow"**
   - Response: Most actions < 5 seconds, caching
   - Proof: Show performance metrics

7. **"Not enough integrations"**
   - Response: Google Calendar, future: Notion, Linear, etc.
   - Proof: Show roadmap, API access

8. **"Team features are lacking"**
   - Response: Workspaces, team analytics
   - Proof: Show team collaboration features

---

## 🎨 Design Principles (From User Research)

### Simply In, Simply Out
- Voice input: "Create task review code tomorrow"
- NL input: "Show me what I worked on last week"
- Zero friction capture

### Context-Aware Intelligence
- Don't ask what I already told you
- Remember my preferences
- Learn my patterns

### Progressive Complexity
- Simple tasks: instant
- Medium tasks: smart workflows
- Complex tasks: AI orchestration

### Respectful AI
- Fast for simple things
- Deep analysis when needed
- Always explain reasoning

---

## 📈 Metrics to Track

### User Satisfaction
- Task completion rate
- Daily active usage
- Feature adoption
- Net Promoter Score

### Performance
- Time to create task (< 2s target)
- Time to plan day (< 5s target)
- AI response time (< 10s target)
- Uptime (99.9% target)

### Business
- Conversion rate (free → paid)
- Retention (30-day, 90-day)
- Feature usage distribution
- Support ticket volume

---

## 🔄 How to Use This Research

### For Product Decisions
1. **New Feature Idea?** → Check if it aligns with persona needs
2. **Prioritization?** → Use frequency data (high/medium/low)
3. **Design Choice?** → Refer to design principles

### For Development
1. **Building Workflow?** → Reference real user requests
2. **Performance Target?** → Check metrics section
3. **Edge Case?** → Review objections

### For Marketing
1. **Landing Page?** → Address top objections
2. **Value Prop?** → Use top 10 requests
3. **Testimonials?** → Match to personas

---

## 📝 Contributing

### Adding New Persona
1. Create file in `personas/` with template
2. Include: demographics, goals, pain points, workflows
3. Update this README

### Adding User Request
1. Add to `requests/BACKLOG.md`
2. Tag with persona, priority, frequency
3. Link to relevant workflow if exists

### Updating Workflows
1. Document actual user behavior (not assumptions)
2. Include context, triggers, outcomes
3. Map to personas

---

**Last Updated:** 2025-11-14
**Next Review:** Every sprint (2 weeks)
**Owner:** Product team

---

## Quick Links

- [Solo Developer Persona](personas/01-solo-developer.md)
- [Real User Workflows](workflows/)
- [Feature Request Backlog](requests/BACKLOG.md)
- [Common Objections](objections/common-objections.md)
