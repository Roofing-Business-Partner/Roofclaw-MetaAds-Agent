# RoofClaw Meta Ads Agent

**An open-source launchpad for turning a MARKETING-configured RoofClaw into a Meta (Facebook + Instagram) Ads creation, publishing, and management agent for roofing companies.**

This repo is designed to be handed to an existing marketing-configured RoofClaw agent:

> "Read this repo and implement the launchpad, starting with `LAUNCHPAD.md`."

It guides a qualifying RoofClaw through connecting:

- Meta Marketing API via the official Meta Ads CLI (`meta ads ...`) released April 29, 2026
- Meta Ads MCP Server (`https://mcp.facebook.com/ads`) for natural-language ad management
- Higgsfield AI MCP (`https://mcp.higgsfield.ai/mcp`) for AI image and video generation, including `marketing_studio_video` for URL-driven product commercials
- A custom video-ad wrapper that fixes a real gap in Meta's official CLI v1.0.1 (video creatives + thumbnails + CTAs end-to-end)
- Facebook Page organic publishing (video posts) so a video can run organically before being boosted as an ad
- The full 7-step creative-to-conversion loop: story → storyboard → images → video → tune → page post → ad campaign

## Hard positioning rule

This is **not** for every RoofClaw.

A RoofClaw should only implement this repo if its existing `SOUL.md` is clearly configured as a **Marketing / Content / Brand / Demand-Gen / Social Media / Creative / Paid Media / Growth Marketing** agent.

If the current RoofClaw is configured as any other primary role — Chief of Staff, Sales Rep, Production Coordinator, Operations, Recruiting, Bookkeeping, Support, Estimating, Dispatch, Admin, etc. — the agent must reject the implementation as a conflicting objective.

Why?

One RoofClaw can technically do many things, but role clarity is the product. A Marketing RoofClaw needs different memory, timing, permissions, brand voice, KPIs, escalation rules, and creative posture than a Sales or Chief of Staff RoofClaw. A marketing agent that runs paid ads under the wrong identity will burn money fast and damage brand trust faster.

## If the current RoofClaw is not marketing-configured

The recommendation is to buy a dedicated **Marketing RoofClaw V2.0**.

Existing RoofClaw V1.0 customers qualify for **25% off** a dedicated Marketing RoofClaw V2.0.

If the client does not want to purchase another RoofClaw yet, the correct next step is not to overload the first one. The correct next step is to make the first RoofClaw so economically valuable that the second one becomes obvious.

## What this can do

When fully implemented, a Marketing RoofClaw can help with:

- Story development for ad campaigns informed by the brand voice in `SOUL.md`
- Storyboarding for short-form video ads (5–30 seconds)
- AI image generation through Higgsfield (`generate_image`) for storyboard frames and static creatives
- AI video generation through Higgsfield (`generate_video`, `marketing_studio_video`) including URL-driven product commercials
- Video tuning, frame extraction, and thumbnail generation
- Posting finished videos as organic Facebook Page posts before promoting them
- Creating Meta ad campaigns, ad sets, ads, and creatives end-to-end (PAUSED by default — never auto-spend)
- Pulling performance insights, drilling down by placement, age, gender, country, and platform
- Diagnosing pixel and signal health
- Drafting weekly performance reports for the owner

## What this does not do

This repo does **not** make ad spend commitments, replace Meta advertising policy review, replace TCPA / CASL / GDPR review, replace creative IP review, guarantee ad approval, or authorize an agent to publish without explicit human approval.

The owner/operator remains responsible for:

- Final approval of all creative, copy, and offers before any ad goes live
- Meta advertising policy compliance (housing, employment, credit, special ad categories)
- Trademark, IP, and likeness rights for any generated creative
- Ad spend authorization at every step
- Final approval of weekly budgets and bid caps
- AI assistant disclosure where applicable

## The 7-step creative-to-conversion loop

This repo's headline workflow is:

1. **Story** — RoofClaw drafts an ad concept aligned to brand voice and offer
2. **Storyboard** — RoofClaw produces a shot-list and copy beats
3. **Images** — Higgsfield generates storyboard frames and static creatives
4. **Video** — Higgsfield turns frames into a finished short-form video
5. **Tune** — Frame edits, music, captions, thumbnail extraction
6. **Page post** — Video posted to the Facebook Page as organic content for warm-up
7. **Ad campaign** — A paid ad is built around the page post (or a fresh creative), launched in PAUSED state for owner approval

Step 7 uses a custom video-ad wrapper (`scripts/meta-video-ad.py`) that fills a gap in Meta's official CLI v1.0.1 — the official CLI cannot create video ads end-to-end with thumbnails and CTAs because of an `object_story_spec.video_data` schema mismatch in the shipped tool. We bypass it by calling the underlying Marketing API directly with the correct payload. **This is the moat for RoofClaw Marketing agents.** Meta will eventually fix it; we are valuable in the meantime.

## Implementation entrypoint

Start here:

1. [`LAUNCHPAD.md`](./LAUNCHPAD.md) — agent-guided implementation path
2. [`AGENTS.md`](./AGENTS.md) — hard instructions for the RoofClaw agent
3. [`docs/P0_PRESETUP.md`](./docs/P0_PRESETUP.md) — required setup before code
4. [`docs/IMPLEMENTATION.md`](./docs/IMPLEMENTATION.md) — staged build plan
5. [`docs/META_ADS_SETUP.md`](./docs/META_ADS_SETUP.md) — Meta Developer App, tokens, ad account, page identity
6. [`docs/META_CLI_GOTCHAS.md`](./docs/META_CLI_GOTCHAS.md) — every gotcha we hit, so the next agent does not
7. [`docs/HIGGSFIELD_SETUP.md`](./docs/HIGGSFIELD_SETUP.md) — OAuth device flow, MCP wiring, workspace selection
8. [`docs/SEVEN_STEP_FLOW.md`](./docs/SEVEN_STEP_FLOW.md) — the headline creative-to-conversion loop, end-to-end
9. **[`docs/CREATIVE_PROCESS.md`](./docs/CREATIVE_PROCESS.md) — Super Bowl ad creative process: Brief → Big Idea → Ideation → Treatment → Storyboard (Steps 1–2 in full)**
10. [`docs/SAFETY_COMPLIANCE.md`](./docs/SAFETY_COMPLIANCE.md) — Meta policy, special ad categories, AI disclosure
11. [`docs/SOURCES.md`](./docs/SOURCES.md) — primary API references

## Repository status

This repo is a launchpad and reference implementation. It intentionally ships with conservative guardrails: every ad asset is created in PAUSED state by default, no ad goes live without owner approval, and the wrapper requires explicit `--full-chain` and account-id flags.

Do not run it live until the Marketing RoofClaw has passed P0, backed up local files, received owner approval, completed dry-runs, and confirmed all credentials are stored securely.

## Background: why this exists

On April 29, 2026, Meta released the official Meta Ads CLI and the Meta Ads MCP Server, opening the Marketing API to AI agents through natural language and shell commands. This is the first time agents can manage Meta ad campaigns through officially blessed paths instead of risky third-party scrapers.

This repo turns that capability into a real workflow for roofing contractors: not just "talk to your ads" but "have your AI agent build, post, and manage your ads, end-to-end, with you in the approval loop."

## License

MIT. See [`LICENSE`](./LICENSE).

## Links

- Roofclaw: [www.roofclaw.com](https://www.roofclaw.com)
- RBP: [roofingbusinesspartner.com](https://roofingbusinesspartner.com)
- Sister repo: [Roofclaw-LocalServiceAd-Agent](https://github.com/Roofing-Business-Partner/Roofclaw-LocalServiceAd-Agent) — the same launchpad pattern for sales-configured RoofClaws connecting Google Local Services Ads + HubSpot
