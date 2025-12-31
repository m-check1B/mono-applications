# HW-004: Configure EspoCRM Web-to-Lead Form

**Status:** PENDING
**Blocks:** Lead capture from websites
**Created:** 2025-12-09
**Priority:** MEDIUM

---

## What You Need To Do

1. Access EspoCRM at http://localhost:8080 (via VS Code port forward)
2. Login with admin credentials (check `/github/secrets/espocrm_creds.txt`)
3. Go to: Administration → Lead Capture
4. Create a new Web-to-Lead form:
   - Name: "Website Contact"
   - Fields: Name, Email, Company (optional), Message
   - Target List: Create "Website Leads" list
5. Get the API endpoint and form code

---

## Expected Output

Web-to-Lead endpoint URL and any API key needed.

Example:
```
Endpoint: http://localhost:8080/api/v1/LeadCapture/XXXXX
API Key: (if needed)
```

---

## When Done

1. Paste the endpoint details in Result section
2. Change Status above to: **DONE**

Agent will:
- Add contact form to website landing pages
- Connect form submission to EspoCRM endpoint
- Test lead creation

---

## Result

```
Endpoint URL: [PASTE HERE]
API Key: [PASTE IF NEEDED]
Form Fields Available: [LIST THEM]
```
