# IMPLEMENTATION.md

Staged build plan for the Marketing RoofClaw. Do not skip stages. Each stage has a verification step that gates the next stage.

## Stage 0 — Soul gate + P0

See `LAUNCHPAD.md` and `docs/P0_PRESETUP.md`. Do not proceed past P0 until every box is checked.

## Stage 1 — Install Meta Ads CLI

```bash
mkdir -p ~/.openclaw/workspace/tools/meta-ads
cd ~/.openclaw/workspace/tools/meta-ads
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install meta-ads requests
meta --version
```

**Verify:** `meta --version` prints `1.0.1` or later.

## Stage 2 — Meta auth

Set `ACCESS_TOKEN` and `AD_ACCOUNT_ID` from `.env`. Run:

```bash
meta auth status
meta ads adaccount get
```

**Verify:** auth status shows the truncated token; `adaccount get` shows the account name.

## Stage 3 — Meta read-only sweep

```bash
meta ads campaign list -l 5
meta --business-id $BUSINESS_ID ads page list
meta --business-id $BUSINESS_ID ads dataset list
meta ads insights get --date-preset last_30d
```

**Verify:** all four commands return data without errors. Note: insights may return `{"data":[]}` if there is no recent spend, that is fine.

## Stage 4 — Meta image-creative dry run

Pick a low-blast-radius ad account (`act_<test_account_id>`) and a low-blast-radius Page.

```bash
# 1. Campaign
meta ads campaign create --name "P0 Image Smoke - DELETE" --objective outcome_traffic --daily-budget 500
# capture CAMPAIGN_ID

# 2. Ad set (no daily-budget; campaign owns it)
meta ads adset create $CAMPAIGN_ID --name "Smoke AdSet" --optimization-goal link_clicks --billing-event impressions --bid-amount 100 --targeting-countries US

# 3. Image creative
meta ads creative create --name "Smoke Creative" --image ./test-banner.jpg --page-id $PAGE_ID --body "Smoke test" --title "Smoke Test" --link-url "https://example.com" --call-to-action learn_more

# 4. Ad
meta ads ad create $ADSET_ID --name "Smoke Ad" --creative-id $CREATIVE_ID

# 5. Cleanup
meta ads campaign delete $CAMPAIGN_ID --force
meta ads creative delete $CREATIVE_ID --force
```

**Verify:** entire chain creates without errors; final campaign list shows no `Smoke` entries.

## Stage 5 — Higgsfield connect

Run the device flow:

```bash
bash scripts/higgsfield/start-device-flow.sh
# Owner opens the verification URL, approves, poller catches the token
```

**Verify:** `python scripts/higgsfield/hf.py balance` returns credits and email.

## Stage 6 — Higgsfield image dry run

```bash
python scripts/higgsfield/hf.py generate_image '{"params":{"model":"marketing_studio_image","prompt":"A small test image of a blue square","count":1,"aspect_ratio":"1:1"}}'
```

**Verify:** result includes a `rawUrl` to a PNG/JPEG. Open the URL.

## Stage 7 — Higgsfield video dry run

```bash
python scripts/higgsfield/hf.py generate_video '{"params":{"model":"seedance_2_0","prompt":"Tiny 3-second test video, abstract motion","duration":3,"aspect_ratio":"1:1"}}'
# Capture job_id, then poll:
python scripts/higgsfield/hf.py job_status '{"id":"<job_id>"}'
```

**Verify:** job reaches `status: completed`; result includes a video URL.

## Stage 8 — Page video post dry run

Pick a low-stakes Page (e.g., owner's personal brand Page).

```bash
bash scripts/meta/post-page-video.sh ./finished-video.mp4 $PAGE_ID "Test post" "Test description"
```

**Verify:** the video appears on the Page within ~60 seconds. Optionally delete it after verification.

## Stage 9 — Custom video-ad wrapper dry run

```bash
python scripts/meta-video-ad.py \
  --video ./finished-video.mp4 \
  --thumb ./thumbnail.jpg \
  --page-id $PAGE_ID \
  --headline "P0 video ad smoke" \
  --body "Smoke test of video ad wrapper" \
  --link "https://example.com" \
  --cta WATCH_MORE \
  --name-prefix "P0VideoSmoke" \
  --full-chain
```

**Verify:** wrapper prints campaign_id, adset_id, creative_id, ad_id; status is PAUSED; campaign appears in Ads Manager. Then clean up.

## Stage 10 — Owner walk-through

Schedule a 30-minute call with the owner. Demo the full 7-step flow with a real test campaign idea. Owner approves go-live or sends back changes.

## Stage 11 — Live mode

Flip `META_ADS_LIVE_MODE=true` in `.env` only after the owner sign-off in Stage 10. Activate ONE ad. Monitor its first 24 hours manually before activating any others.

## Stage 12 — Steady state

Add the agent to its operating rhythm:

- Daily heartbeat to check pixel health, account rate-limit headroom, and any pending owner approvals
- Weekly performance summary to the approval channel (Tara-style report)
- Monthly creative refresh proposal (3 new ad concepts based on top performers)
