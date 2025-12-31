# Partner Program Integration Playbook

Tracks and operationalizes partner program integrations for VD-299.

## Overview

Partner programs targeted:
- Pleo (expense management)
- Make.com (automation platform)
- Deel (global HR and payroll)

This integration adds a lightweight tracker and notification flow:
- Status and ownership stored in `data/partner-programs.json`
- Updates broadcast to Kraliki Comm Hub (`http://127.0.0.1:8199`)
- Optional n8n webhook trigger for downstream automation

## Quick Start

```bash
python3 integrations/partner_programs.py init
python3 integrations/partner_programs.py list
python3 integrations/partner_programs.py update --partner pleo --status applied --owner "BD" --next-action "Await approval" --notify
```

## Automation Flow

1. Update status in the tracker.
2. Comm hub broadcasts the change for team visibility.
3. Optional n8n webhook receives the payload for:
   - CRM enrichment
   - Task creation
   - Weekly status summaries

To enable n8n notifications, set:
- `N8N_PARTNER_WEBHOOK=http://127.0.0.1:5678/webhook/<id>`
or add a `partner-program` entry in `integrations/n8n_webhooks.json`.

## Partner Playbooks

### Pleo

Goal: expense automation deployments for SME customers.

Application checklist:
- Case study: expense approvals or card reconciliation automation
- Implementation scope and timeline (2-4 weeks)
- Revenue model: setup fee + commission

Integration plan:
- Capture intake: company size, expense system, approvers, card provider
- Proposed automation: receipt OCR, Slack approvals, accounting sync
- Delivery: n8n workflow + reporting pack

### Make.com

Goal: certified partner status plus managed automation services.

Application checklist:
- Certification booking (3-5 days)
- Portfolio examples: multi-step automations with webhooks and CRM sync

Integration plan:
- Standardize automation templates for clients
- Define support tier (monthly monitoring + optimization)
- Use n8n to mirror Make scenarios for internal QA

### Deel

Goal: HR and payroll automation for distributed teams.

Application checklist:
- Use cases: onboarding, contract generation, payroll alerts
- Compliance notes for EU clients

Integration plan:
- Intake: contractor count, hiring regions, current HR stack
- Automation: onboarding docs, payroll reminders, compliance alerts
- Reporting: monthly HR ops dashboard

## Data Schema

Tracked fields in `data/partner-programs.json`:
- `id`, `name`, `program_url`
- `status`, `owner`, `next_action`
- `commission`, `notes`

## Next Steps

- Add CRM sync once EspoCRM API details are confirmed.
- Create n8n workflow to digest weekly partner status changes.
