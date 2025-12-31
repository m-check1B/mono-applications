# Acme Corp - Website Redesign Project

## Project Overview

**Client:** Acme Corp (Demo)
**Project:** Marketing Website Redesign
**Timeline:** 2-week sprint (simulated)
**Budget:** $15,000 (simulated)

## Client Brief

Acme Corp is a B2B SaaS company offering project management tools. They need a modern marketing website that:

- Clearly communicates their value proposition
- Converts visitors to free trial signups
- Works on mobile devices
- Loads fast (< 3 seconds)
- Supports dark mode

## Brand Assets

### Colors
- Primary: `#2563EB` (Blue)
- Secondary: `#1E40AF` (Dark Blue)
- Accent: `#F59E0B` (Amber)
- Background: `#F8FAFC` (Light) / `#0F172A` (Dark)

### Typography
- Headlines: Inter, 700 weight
- Body: Inter, 400 weight
- Monospace: JetBrains Mono

### Logo
- SVG logo in `/assets/logo.svg`
- Favicon in `/assets/favicon.ico`

## Sitemap

```
Home
├── Features
│   ├── Task Management
│   ├── Team Collaboration
│   └── Reporting
├── Pricing
├── About
│   ├── Company
│   └── Team
├── Resources
│   ├── Blog
│   ├── Documentation
│   └── API Reference
└── Contact
```

## Key Sections (Home Page)

1. **Hero Section**
   - Headline: "Project Management That Gets Out of Your Way"
   - Subheadline: "Spend less time managing, more time building"
   - CTA: "Start Free Trial" / "Book a Demo"

2. **Problem/Solution**
   - Pain points visual
   - How Acme solves them

3. **Features Overview**
   - 3 key features with icons
   - Link to feature pages

4. **Social Proof**
   - Customer logos
   - Testimonial carousel
   - Stats (X users, Y companies, Z projects)

5. **Pricing Preview**
   - 3 tiers summary
   - Link to pricing page

6. **CTA Section**
   - Final call to action
   - Email capture or trial button

## Technical Requirements

- Framework: Svelte or Astro
- CSS: Tailwind CSS
- Hosting: Vercel or Cloudflare Pages
- Analytics: PostHog or Plausible
- Forms: Formspree or custom backend

## Content Provided

| Section | Status | Notes |
|---------|--------|-------|
| Headlines | Ready | In content.md |
| Features copy | Ready | In content.md |
| Testimonials | Ready | 3 provided |
| Team bios | Pending | Need photos |
| Blog posts | N/A | Future phase |

## Demo Instructions

This project demonstrates the **Build-Audit-Fix** pattern:

1. **Build Phase** (Gemini): Generate the landing page structure and content
2. **Audit Phase** (Codex): Review for SEO, accessibility, performance
3. **Fix Phase** (Opus): Incorporate audit findings and polish

```bash
# Example demo command
claude "Build the Acme Corp landing page using the brief in PROJECT.md.
Use the Build-Audit-Fix pattern:
1. Have Gemini create the initial HTML/CSS
2. Have Codex audit for issues
3. Fix all issues and deliver final version"
```

---

*Demo project for Lab by Kraliki Pro*
