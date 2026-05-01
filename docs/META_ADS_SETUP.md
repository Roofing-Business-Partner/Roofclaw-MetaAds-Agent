# META_ADS_SETUP.md

Setting up Meta Marketing API access for a Marketing RoofClaw.

## Prerequisites

- A Meta business account (Business Manager / Business Portfolio).
- One or more ad accounts the owner has authorized this RoofClaw to manage.
- One or more Facebook Pages the owner has authorized this RoofClaw to use as ad identities.
- Optional: a Meta Pixel and/or Conversions API setup. Not required for awareness/traffic campaigns.

## 1. Install the Meta Ads CLI

The CLI requires Python 3.12+. Use a dedicated venv to avoid polluting system Python.

```bash
mkdir -p ~/.openclaw/workspace/tools/meta-ads
cd ~/.openclaw/workspace/tools/meta-ads
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install meta-ads requests
meta --version   # should print 1.0.1 or later
```

`meta-ads` brings in `facebook-business`, `requests`, `click`, and other dependencies as transitive installs.

## 2. Create or pick a Meta Developer App

Every Marketing API call must come from a registered Meta app. You have two options.

### Option A — Reuse an existing app

Find your apps at `https://developers.facebook.com/apps/`. Pick an app that is in **Live** mode and has the **Marketing API** product enabled. If the app is in Development mode, switch it to Live (see `META_CLI_GOTCHAS.md` #1).

### Option B — Create a fresh app

1. `https://developers.facebook.com/apps/create/`
2. Choose **Other → Business**
3. Name it something descriptive: e.g., `Acme Roofing Marketing Agent`
4. Add the **Marketing API** product
5. In Settings → Basic, fill in Privacy Policy URL, App Icon, Category
6. Switch App Mode from Development to **Live**

The App ID and App Secret will be visible under Settings → Basic. You will not need them for daily operations if you use long-lived user tokens or system user tokens, but they are required if you ever need to exchange tokens.

## 3. Generate an access token

### Option A — Long-lived user token (60-day, fine for v0)

1. Go to `https://developers.facebook.com/tools/explorer/`
2. Top-right dropdown: select your app
3. Click **Generate Access Token**
4. Authorize the requested permissions:
   - `ads_management`
   - `ads_read`
   - `pages_read_engagement`
   - `pages_show_list`
   - `pages_manage_ads`
   - `business_management`
   - `publish_video` (only if posting videos to Pages)
   - `leads_retrieval` (only if you also pull lead-form submissions)
5. Copy the short-lived token from the explorer
6. Exchange it for a long-lived (60-day) token:

```bash
curl "https://graph.facebook.com/v21.0/oauth/access_token\
?grant_type=fb_exchange_token\
&client_id=YOUR_APP_ID\
&client_secret=YOUR_APP_SECRET\
&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

7. Store the long-lived token in `.env` as `ACCESS_TOKEN=...`. Permissions on `.env` should be `600`.

### Option B — System user token (no expiry, recommended for production)

1. Go to Business Manager → Business Settings → Users → System Users
2. Create a new system user. Name it `roofclaw-marketing-agent` or similar.
3. Assign the system user to the relevant ad accounts and Pages with full access
4. Generate a token with the same permission set as Option A
5. Token never expires unless revoked

System user tokens bypass app dev-mode restrictions entirely and are the right answer for production.

## 4. Verify access

```bash
cd ~/.openclaw/workspace/tools/meta-ads
source .venv/bin/activate
export ACCESS_TOKEN=<your_token>
export AD_ACCOUNT_ID=act_<your_account_id>
export BUSINESS_ID=<your_business_portfolio_id>

meta auth status
meta ads adaccount get
meta ads adaccount list
meta ads page list                    # requires BUSINESS_ID
meta ads dataset list                 # requires BUSINESS_ID
meta ads campaign list -l 5
```

If `meta auth status` shows the truncated token and `adaccount get` returns your account name, you are connected.

## 5. Token reach inspection

To see the full footprint your token can manage, hit the Graph API directly:

```bash
# Business portfolios accessible
curl -s "https://graph.facebook.com/v21.0/me/businesses\
?access_token=$ACCESS_TOKEN&fields=id,name,verification_status" | jq

# Pages accessible
curl -s "https://graph.facebook.com/v21.0/me/accounts\
?access_token=$ACCESS_TOKEN&fields=id,name,category,fan_count&limit=50" | jq

# Ad accounts under a specific business
curl -s "https://graph.facebook.com/v21.0/<BUSINESS_ID>/owned_ad_accounts\
?access_token=$ACCESS_TOKEN&fields=id,name,account_status,amount_spent,currency" | jq

# Token health
curl -s "https://graph.facebook.com/v21.0/debug_token\
?input_token=$ACCESS_TOKEN&access_token=$ACCESS_TOKEN" | jq
```

`debug_token` is especially useful: it shows the App ID that issued the token, scopes granted, expiration, and validity.

## 6. Pick the demo ad account

For first runs and demos, pick an ad account that:

- Has zero or negligible recent spend (so test campaigns do not contaminate reporting)
- Is not the primary production account
- Is in a currency the owner is comfortable with

A personal-brand or sandbox ad account is ideal. Avoid the main production ad account until P0 is complete.

## 7. Pick the page identity

The Page identity is the visible "from" of the ad. Roofing audiences trust local brands. Pick a Page that:

- Is owned by the same Business Portfolio as the ad account, OR is shared into it
- Has at least some organic content already (Pages with zero followers and zero posts get penalized in delivery)
- Matches the offer/audience of the campaign

Set `DEFAULT_PAGE_ID` in `.env` to your default. Override per-creative when needed.

## 8. Common scopes summary

| Scope | What it allows |
|---|---|
| `ads_management` | Read + write ad campaigns, ad sets, ads, creatives |
| `ads_read` | Read insights and reports |
| `pages_show_list` | Discover which Pages the user can manage |
| `pages_read_engagement` | Read Page-level engagement data |
| `pages_manage_ads` | Run ads from a Page identity |
| `business_management` | Manage business assets (catalogs, datasets) |
| `publish_video` | Post videos to a Page (organic) |
| `leads_retrieval` | Pull Lead Ads form submissions |

Stick to the minimum needed scopes. Do not request `manage_pages` or `pages_manage_posts` unless you actually post to Page feeds.

## 9. Token rotation

Long-lived tokens expire every 60 days. Add a cron reminder 7 days before expiry:

```
0 9 23 */2 *  /path/to/scripts/notify-token-rotation.sh
```

System user tokens do not expire.
