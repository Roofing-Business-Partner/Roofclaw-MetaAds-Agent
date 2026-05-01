# P0_PRESETUP.md

Checklist a Marketing RoofClaw must complete before writing any code, changing any config, or making any API calls.

## Owner confirmations

- [ ] Owner has explicitly authorized this RoofClaw to manage Meta ads under the brand(s) named below.
- [ ] Owner has explicitly authorized this RoofClaw to spend Higgsfield credits.
- [ ] Owner has named the approval channel (Telegram, Slack, ClickUp, etc.) where draft ads will be reviewed.
- [ ] Owner has named a daily budget cap and an autonomous-action ceiling.

## Brands and identities

- [ ] Business Portfolio ID(s): _______________
- [ ] Ad Account ID(s) (act_xxx): _______________
- [ ] Default Page ID for ad identity: _______________
- [ ] Currency confirmed for each ad account: _______________
- [ ] Approved Pixel/Dataset ID for conversion tracking: _______________

## Credentials

- [ ] Meta Developer App ID: _______________
- [ ] Meta Developer App is in **Live mode** (not Development): _______________
- [ ] Long-lived (60-day) Meta access token OR system user token issued: _______________
- [ ] Token scopes verified: ads_management, ads_read, pages_show_list, pages_read_engagement, pages_manage_ads, business_management, publish_video
- [ ] Higgsfield account exists, owner has logged in and approved billing: _______________
- [ ] Higgsfield workspace ID confirmed: _______________

## Environment

- [ ] Python 3.12+ available (`python3 --version`)
- [ ] `.env` file created from `.env.example` with all required values
- [ ] `.env` is `chmod 600` and gitignored
- [ ] `.gitignore` includes `.env`, `.state/`, `*-token.json`
- [ ] `META_ADS_LIVE_MODE=false` for v0
- [ ] Backup copies of `SOUL.md`, `TOOLS.md`, `HEARTBEAT.md`, prior `.env`, and any cron jobs taken before any change

## Compliance

- [ ] Special ad category determined (NONE for most roofing; HOUSING / EMPLOYMENT / CREDIT only if applicable)
- [ ] AI disclosure rule decided (caption all AI-generated video? caption only when required by jurisdiction?)
- [ ] Trademark / likeness review: are any people, properties, or brands shown that need clearance?
- [ ] TCPA / CASL / GDPR review (if the campaign collects leads)

## Risk caps

- [ ] Maximum autonomous daily budget per ad account: _______________ (recommended: $50)
- [ ] Maximum number of simultaneous PAUSED ads pending approval: _______________ (recommended: 5)
- [ ] Maximum percentage budget increase per edit: _______________ (recommended: 25%)

## Sign-off

- [ ] Owner reviewed this checklist on date: _______________
- [ ] RoofClaw confirms its `SOUL.md` classifies as MARKETING (not borderline): _______________
- [ ] Implementation is allowed to proceed to `docs/IMPLEMENTATION.md`

If any box is unchecked, do not proceed. Report the blocker to the owner and stop.
