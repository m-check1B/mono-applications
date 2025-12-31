# HW-024: Configure EspoCRM Lead Capture

**Created:** 2025-12-21
**Priority:** HIGH
**Status:** PENDING
**Blocks:** Launch Phase 1 (Lead Capture)

## Context
The "Brace the AI Impact" campaign relies on capturing leads from static landing pages into EspoCRM. The forms on the websites need a backend endpoint to submit data to.

## Action Required

1.  **Log in to EspoCRM admin.**
2.  **Navigate to Administration > Web-to-Lead (or similar integration settings).**
3.  **Create a new Web-to-Lead entry for:**
    *   **Name:** `Education Landing Capture`
    *   **Target List:** `Education Leads 2026`
    *   **Return URL:** `https://verduona.com/thank-you` (or appropriate page)
4.  **Generate the Form HTML/Script.**
5.  **Identify the Endpoint URL and API Key/Token** (if applicable) that the static site needs to POST to.
6.  **Update the Static Site Configuration:**
    *   Provide the Endpoint URL and Hidden Field IDs to the development team (or update `content/operations/crm_config.md` if it exists).

## Verification
*   Submit a test lead from the generated HTML or a test tool (Postman).
*   Verify the lead appears in EspoCRM under the correct Target List.

## Notes
*   If using a custom backend service (e.g. `applications/backend`), ensure it is authorized to write to EspoCRM via API.
