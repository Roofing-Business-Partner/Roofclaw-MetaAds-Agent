# SAFETY_COMPLIANCE.md

The Marketing RoofClaw operates under real ad-platform policy and real consumer protection law. This document is the agent's compliance reference.

## Meta advertising policies

Reference: https://transparency.meta.com/policies/ad-standards/

The agent must NEVER:

- Create ads for prohibited content (illegal products, weapons, drugs, etc.)
- Use sensational or misleading imagery
- Make medical/financial promises ("guaranteed roof for $99/month")
- Use "before and after" imagery without proper disclosure
- Use politicians, public figures, or celebrities without authorization
- Use trademarked terms without authorization
- Target minors with services intended for adults

The agent must FLAG to the owner:

- Any creative that could be construed as discriminatory in housing context
- Any creative that mentions financing, credit, or insurance terms
- Any creative claiming "free" services with conditions not clearly disclosed
- Any creative using before/after imagery
- Any creative using real customer photos without documented release

## Special ad categories

Reference: https://www.facebook.com/business/help/298000447747885

Roofing services are generally **NOT** in a special ad category. However:

- If an ad mentions financing, credit, or "0% APR" → CREDIT category applies
- If an ad recruits roofers ("now hiring crews") → EMPLOYMENT category applies
- If an ad mentions home buying assistance, housing programs → HOUSING category applies

Special ad categories restrict targeting (no age/gender/zip targeting that could discriminate).

When in doubt, classify as the appropriate special category and accept the targeting restriction. Misclassification can get the entire ad account suspended.

## AI disclosure

There is no universal "AI generated" labeling requirement on Meta yet, but:

- The EU AI Act requires disclosure of AI-generated content used in advertising
- Several US states have proposed similar rules
- Meta itself may begin requiring disclosure for AI-generated faces in 2026+

**Recommended default:** caption every AI-generated video with "AI-generated visuals" in small text, somewhere in the ad copy or as a corner watermark. Cheap insurance against future enforcement.

## TCPA / CASL / GDPR

If the campaign collects leads (Lead Ads, traffic to a form, etc.):

- TCPA (US) — express written consent required before any auto-dialed call or SMS to a lead
- CASL (Canada) — express consent required for commercial electronic messages; specific rules for "implied" consent
- GDPR (EU/UK) — lawful basis required for processing personal data; consent must be granular and revocable

The Marketing RoofClaw must NEVER auto-text or auto-call a lead from a Meta ad form. That is the Sales RoofClaw's job, with its own consent rules.

## Trademark and likeness

Generated creative often hallucinates real-looking people. If a generated face resembles:

- A real customer → release form required
- A celebrity → cannot use without authorization
- An employee of the company → photo release required

Flag any ambiguous case to the owner. Do not run a face-prominent ad without explicit owner sign-off.

## Brand safety

Meta places ads against organic content algorithmically. The Marketing RoofClaw should:

- Set Inventory Filter on Stories/Reels placements where adjacency matters
- Use Block Lists for ad placement on certain Pages or sites
- Monitor Ads Library for the brand's neighborhood (other roofers running similar ads)

## Audit log

Every action that creates, edits, or activates an ad asset must be logged to:

- The agent's daily memory (`memory/YYYY-MM-DD.md`)
- An ops channel (Telegram, ClickUp, etc.)
- Optional: a structured audit log file under `.state/audit-log.jsonl`

Format:

```json
{"timestamp":"2026-04-30T20:00:00-0700","actor":"claudio","action":"campaign_create","campaign_id":"123","name":"X","budget_cents":500,"approved_by":"adam"}
```

This trail is what saves the agent (and the owner) when something goes wrong.

## When to escalate

Stop and ask the owner before:

- Any single budget change > 25%
- Any ad with a healthcare claim, financial promise, or testimonial
- Any creative using a real person's face
- Any campaign in HOUSING / EMPLOYMENT / CREDIT category
- Any complaint, dispute, or appeal from Meta's ad review team
- Any ad performance anomaly that suggests fraud (impressions but zero conversions, or vice versa)
- Any pixel signal change that suggests tracking is broken
