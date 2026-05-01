# META_CLI_GOTCHAS.md

These are the real-world gotchas hit during implementation of this launchpad. They will save the next RoofClaw agent hours of confusion. They are written in the format **gotcha → why → fix.**

Last verified against `meta-ads` CLI **v1.0.1** on April 30, 2026, against the Meta Marketing API at v21.0.

## 1. Dev mode silently blocks ad creative creation

**Gotcha.** Image and video creatives fail with:

```
Error: API error (100): Invalid parameter
Ads creative post was created by an app that is in development mode.
It must be in public to create this ad.
```

**Why.** Every Meta API call comes from a registered app. When you generate a token in Graph API Explorer, it is issued under whichever app is selected in the dropdown. New apps default to **Development** mode, which sandboxes user-facing actions like ad creative creation. Read endpoints (campaigns, ad sets, insights) work fine in dev mode, so the issue does not surface until the first creative.

**Fix.** Switch the app to **Live** mode in the Meta Developer console:

1. Go to `https://developers.facebook.com/apps/<APP_ID>/`
2. Toggle the App Mode switch from Development to Live
3. Provide a Privacy Policy URL and category if prompted
4. Re-issue the access token from Graph API Explorer (existing tokens often keep working but a fresh token is safer)

This does not expose your ad accounts to anyone else. Live mode just allows the app to create real assets visible to real users.

## 2. CBO budget conflict between campaign and ad set

**Gotcha.** Creating an ad set fails with:

```
Error: API error (100): Invalid parameter
You can only set an ad set budget or a campaign budget.
```

**Why.** When the campaign was created with `--daily-budget`, Meta enables Campaign Budget Optimization (CBO) at the campaign level. CBO means budget lives on the campaign, and ad sets must not have their own budget.

**Fix.** Either:

- Create the campaign with `--daily-budget` and create ad sets WITHOUT `--daily-budget` (campaign-level CBO), OR
- Create the campaign with `--adset-budget-sharing` flag and put `--daily-budget` on each ad set instead

The CLI does not warn about this conflict; you have to know.

## 3. Budgets are in CENTS, not dollars

**Gotcha.** Setting `--daily-budget 500` produces a $5/day campaign, not a $500/day campaign. Setting `--daily-budget 50000` produces a $500/day campaign.

**Why.** Meta uses the smallest unit of the account currency. For USD/CAD/EUR/GBP that is cents.

**Fix.** Always document the budget in dollars in code comments and double-check before any live activation. A typo here can produce a 100x budget mistake.

## 4. `meta ads adset list` takes a positional campaign ID, not `--campaign-id`

**Gotcha.** `meta ads adset list --campaign-id 12345` returns:

```
Error: No such option: --campaign-id
```

**Why.** Inconsistent CLI design. Most other commands use named flags; ad-set listing uses a positional argument.

**Fix.** Use `meta ads adset list 12345`.

## 5. `meta ads adset list` (no filter) hangs on large accounts

**Gotcha.** Calling `meta ads adset list` or `meta ads ad list` against an account with hundreds of historical ad sets/ads can hang for minutes and may exhaust rate limits.

**Why.** No default pagination limit. The CLI tries to fetch all ad sets at once and Meta paginates them slowly.

**Fix.** Always use `--limit` (`-l`) or restrict by parent ID:

```
meta ads adset list --limit 25
meta ads ad list --limit 25
meta ads adset list <CAMPAIGN_ID> --limit 25
```

## 6. Insights date presets max out at `last_90d`

**Gotcha.** `meta ads insights get --date-preset last_year` fails with an enum-validation error.

**Why.** The CLI restricts presets to: `today, yesterday, last_3d, last_7d, last_14d, last_30d, last_90d, this_month, last_month`.

**Fix.** For longer ranges, use `--since YYYY-MM-DD --until YYYY-MM-DD` instead.

## 7. Rate limits are PER AD ACCOUNT, not per token

**Gotcha.** Heavy iteration on one ad account fails with:

```
Error: API error (80004): There have been too many calls to this ad-account.
Wait a bit and try again.
```

**Why.** Meta scopes the Marketing API rate limit to each ad account independently. Switching ad accounts (`AD_ACCOUNT_ID=...`) gives you a fresh rate-limit bucket.

**Fix.** Spread reads across multiple ad accounts when possible. Avoid running a tight loop on one account during testing. Cooldown is typically 1 hour.

## 8. Video creatives reject `--link-url` (broken in v1.0.1)

**Gotcha.** `meta ads creative create --video x.mp4 --link-url https://example.com ...` fails with:

```
Error: API error (100): Invalid parameter
The field link_url is not supported in the field video_data of object_story_spec.
```

This happens even though Meta's own help text shows an example using `--link-url` on video creatives.

**Why.** The CLI builds an `object_story_spec.video_data` block but Meta's API rejects `link_url` in the `video_data` schema. Meta's documentation lies.

**Fix.** **Do not use the official CLI for video ad creation.** Use the wrapper at `scripts/meta-video-ad.py` which calls the Marketing API directly with the correct payload structure (video_id + image_hash + call_to_action.value.link inside the right nested fields).

## 9. Video creatives require a thumbnail and the CLI cannot attach one

**Gotcha.** Even if you drop `--link-url`, a video creative still fails with:

```
Error: API error (100): Invalid parameter
Please specify one of image_hash or image_url in the video_data field of object_story_spec.
```

And `meta ads creative create --video x.mp4 --image y.jpg ...` fails with:

```
Error: Provide --image or --video, not both.
```

**Why.** Meta requires a thumbnail (`image_hash`) on every video ad. The CLI v1.0.1 does not expose a way to provide one.

**Fix.** Use the `scripts/meta-video-ad.py` wrapper. It uploads the video, uploads the thumbnail to `/adimages` to get a hash, polls until the video is processed, and then assembles the correct `object_story_spec.video_data` block with both the video_id and image_hash.

## 10. Videos need 30+ seconds to process before they can be used in a creative

**Gotcha.** Creating a creative immediately after `POST /advideos` fails because the video is still in `processing` status.

**Why.** Meta processes uploaded videos asynchronously (transcoding, virus scan, etc.). The video must be in `ready` status before any creative can reference it.

**Fix.** Poll `GET /{video_id}?fields=status` until `video_status` is `ready`. The wrapper at `scripts/meta-video-ad.py` does this automatically with a 5-second poll interval and a 180-second timeout.

## 11. `ad list` output table includes campaign IDs but not URLs

**Gotcha.** When the table view shows IDs, copying them into Ads Manager URLs requires manual URL construction.

**Why.** Just a UX gap.

**Fix.** Ads Manager URL pattern:

```
https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=<AD_ACCOUNT_ID_WITHOUT_act_>&selected_campaign_ids=<CAMPAIGN_ID>
```

Useful for posting links in approval channels.

## 12. `IN_PROCESS` is normal right after creation

**Gotcha.** `meta ads adset get` immediately after creation shows `EFFECTIVE_STATUS: IN_PROCESS` instead of `PAUSED`.

**Why.** Meta provisions the ad set asynchronously (validates targeting, allocates budget tracking, etc.). Takes 30–60 seconds.

**Fix.** Wait 60 seconds, re-fetch. It will flip to `PAUSED`. Do not assume something is broken.

## 13. Cleanup orphan creatives separately

**Gotcha.** `meta ads campaign delete --force` cascades to ad sets and ads, but **not** to ad creatives.

**Why.** Creatives are reusable across ads, so Meta does not auto-delete them.

**Fix.** Delete creatives explicitly with `meta ads creative delete <ID> --force` after the parent campaign is gone. The wrapper logs creative IDs separately so cleanup is easy.

## 14. `--no-input` does not work on `creative delete`; use `--force`

**Gotcha.** Trying to skip the confirmation prompt with `--no-input` fails:

```
Error: No such option: --no-input
```

**Why.** Inconsistent CLI flags. Different commands use different flag names for the same intent.

**Fix.** Use `--force` (`-f`) on delete commands.

## 15. Page list and dataset list need `--business-id`, not `--ad-account-id`

**Gotcha.** `meta ads page list` and `meta ads dataset list` against a personal ad account return:

```
Error: No business ID available.
```

**Why.** Pages and Pixels are owned by Business Portfolios, not by individual ad accounts. The CLI needs to know which business to query.

**Fix.** Set `BUSINESS_ID=<business_portfolio_id>` in `.env`, or pass `--business-id <id>` on the `meta ads ...` subcommand (NOT on the top-level `meta` command).

## 16. The MCP server URL works for ChatGPT, Claude, Cursor, Windsurf, Gemini CLI

**Gotcha.** Different MCP clients have different setup flows. The MCP server itself is the same.

**Why.** MCP is a standard; client implementations vary.

**Fix.** Server URL: `https://mcp.facebook.com/ads`. Authentication is via Facebook business login on first connect. Each AI client has its own connector setup UI.

## 17. Campaign creation requires `is_adset_budget_sharing_enabled` on Marketing API v22+

**Gotcha.** Creating a campaign via direct Marketing API call fails with:

```
{"error":{"message":"Invalid parameter","type":"OAuthException","code":100,"error_subcode":4834011,"error_user_title":"Must specify True or False in is_adset_budget_sharing_enabled field","error_user_msg":"You must specify True or False in the field is_adset_budget_sharing_enabled if you are not using campaign budget. Passing in True will enable your ad sets to share 20% of their budget to optimize overall performance."}}
```

**Why.** Meta Marketing API v22 made `is_adset_budget_sharing_enabled` a required field on every campaign create call when the campaign is NOT using Campaign Budget Optimization (CBO). Older API versions (v18–v21) defaulted this to `false` silently. The official `meta-ads` CLI v1.0.1 has not yet been updated to set this field automatically when the user provides ad-set-level budgets.

**Fix.** Always include `"is_adset_budget_sharing_enabled": "false"` in the campaign create payload when you are not using CBO. Set to `"true"` only if you explicitly want ad sets in this campaign to share 20% of their budget pool for optimization. The boolean must be a string in form-encoded payloads.

Minimal Python pattern:

```python
post(f"{AD_ACCOUNT}/campaigns", {
    "name": "My Campaign",
    "objective": "OUTCOME_TRAFFIC",
    "status": "PAUSED",
    "special_ad_categories": "[]",
    "is_adset_budget_sharing_enabled": "false",  # ← required on v22+
    "access_token": ACCESS_TOKEN,
})
```

## 18. Long-running lives outlast access tokens

**Gotcha.** Meta access tokens issued from Graph API Explorer typically last 2 hours. A live demo that runs longer than the token's lifetime will hit a `Session has expired` error mid-stream:

```
{"error":{"message":"Error validating access token: Session has expired on Thursday, 30-Apr-26 21:00:00 PDT...","code":190,"error_subcode":463}}
```

**Why.** Short-lived user tokens default to ~2 hours. Even a Live-mode app with full ad permissions issues short-lived tokens by default through Graph API Explorer.

**Fix.** Two options:

1. **Exchange for a long-lived token (recommended for production):** Use Meta's `/oauth/access_token?grant_type=fb_exchange_token` flow. Long-lived user tokens last 60 days; system user tokens for business apps can be set to never expire.

2. **Refresh mid-flow (acceptable for live demos):** Generate a new short-lived token from Graph API Explorer, paste it back to the agent. The agent updates `.env` and resumes. We did this during the "Ode to the Roofer" Facebook Live when the original token expired during the second half of the stream.

For any RoofClaw running unattended, use option 1. Option 2 is fine for human-in-the-loop demos.

---

If you hit a new gotcha, add it here in a PR. Future agents will thank you.
