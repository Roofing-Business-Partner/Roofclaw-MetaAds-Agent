# HIGGSFIELD_SETUP.md

Connecting a RoofClaw to Higgsfield AI via MCP.

Higgsfield is the image and video generation provider for the 7-step creative-to-conversion loop. They expose a Model Context Protocol (MCP) server with 14 tools including `generate_image`, `generate_video`, `models_explore`, and the headline `marketing_studio_video` (URL-driven product commercials).

## Prerequisites

- Higgsfield account at `https://higgsfield.ai`. Team plan recommended for shared workspaces.
- Credits in the workspace (Higgsfield charges per generation; a typical 5-second video costs roughly 10–40 credits depending on model).
- Owner has approved this RoofClaw to spend Higgsfield credits.

## 1. Discovery

The MCP server publishes its OAuth metadata at:

```
https://mcp.higgsfield.ai/.well-known/oauth-protected-resource
```

Two flows are advertised:

- `authorization_code_pkce` against `https://clerk.higgsfield.ai` — for clients that can receive an OAuth redirect (Claude Desktop, ChatGPT, Cursor)
- `device_code` against `https://fnf-device-auth.higgsfield.ai` — for clients that cannot receive a redirect (RoofClaw, headless agents, CLIs)

RoofClaw uses the **device code** flow.

## 2. Device code flow

The device-auth server exposes (FastAPI / OpenAPI):

- `POST /authorize` — returns `device_code`, `verification_uri`, `expires_in`, `interval`
- `POST /token` — pollable, returns `access_token` once the user approves
- `POST /approve` — what the verification page hits when the user clicks approve

### Step-by-step

```bash
# 1. Request a device code
curl -s -X POST "https://fnf-device-auth.higgsfield.ai/authorize" \
  -H "Content-Type: application/json" \
  -d "{}"
# → { "device_code": "...", "verification_uri": "https://higgsfield.ai/device?code=...",
#     "expires_in": 900, "interval": 5 }

# 2. Display the verification_uri to the owner. They open it in any browser
#    (laptop, phone, etc), log into Higgsfield, and click Approve.

# 3. Poll the token endpoint every `interval` seconds until you get a token
#    or the device_code expires (15 minutes default).
DEVICE_CODE="..."
while true; do
  RESPONSE=$(curl -s -X POST "https://fnf-device-auth.higgsfield.ai/token" \
    -H "Content-Type: application/json" \
    -d "{\"device_code\":\"$DEVICE_CODE\"}")
  if echo "$RESPONSE" | grep -q access_token; then
    echo "$RESPONSE" > .state/higgsfield-token.json
    chmod 600 .state/higgsfield-token.json
    break
  fi
  sleep 5
done
```

A reference Bash poller is included at `scripts/higgsfield/poll-token.sh`.

The token is a Bearer token. It is valid for 24 hours by default. There is currently no documented refresh endpoint; re-run the device flow to renew.

## 3. MCP wiring

The MCP server endpoint is:

```
https://mcp.higgsfield.ai/mcp
```

It uses streamable HTTP MCP transport, JSON-RPC framed in Server-Sent Events.

**Important: Cloudflare WAF blocks the default Python urllib User-Agent (error 1010).** Set a real browser UA on every request:

```
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 OpenClaw/1.0
```

Curl works out of the box. Python clients must set the header explicitly.

### MCP handshake

Send `initialize`, then `notifications/initialized`, then any `tools/call`. The Higgsfield server is bearer-token-scoped, NOT session-scoped — it does not return an `Mcp-Session-Id` header, and you do not need to track session ids between calls.

## 4. Reference Python client

A minimal client is at `scripts/higgsfield/hf.py`. Usage:

```bash
# Check balance + plan
python scripts/higgsfield/hf.py balance

# List workspaces
python scripts/higgsfield/hf.py list_workspaces

# Select a workspace (persists across sessions)
python scripts/higgsfield/hf.py select_workspace '{"workspace_id":"..."}'

# Find image models for product photography
python scripts/higgsfield/hf.py models_explore '{"action":"recommend","query":"roofing product hero image","type":"image"}'

# Generate an image
python scripts/higgsfield/hf.py generate_image '{"params":{"model":"marketing_studio_image","prompt":"A roofer on a sunny suburban roof installing shingles, photorealistic"}}'

# Generate a video from a reference image
python scripts/higgsfield/hf.py generate_video '{"params":{"model":"seedance_2_0","prompt":"Camera slowly orbits the roofer at golden hour","medias":[{"value":"<image_uuid>","role":"start_image"}],"duration":5}}'

# Poll a job
python scripts/higgsfield/hf.py job_status '{"id":"<job_id>"}'
```

## 5. Tool catalog (14 tools)

### Generation
- `generate_image` — image generation
- `generate_video` — video generation
- `models_explore` — find/recommend models for a goal
- `job_status` — poll async generations
- `job_display` — re-render past results
- `show_generations` — browse history

### Marketing Studio (the headline)
- `show_marketing_studio` — load product/avatar libraries, fetch from URLs (e.g., a product page URL)

This is the killer tool for roofing demos. Pass a contractor's website URL and Higgsfield extracts hero imagery, product/service context, and pre-stages assets for `marketing_studio_video`. Then generate a finished commercial in one call.

### Asset management
- `media_upload` — upload a file
- `media_confirm` — finalize an upload
- `show_medias` — list uploaded assets

### Account
- `balance` — credits, plan, email
- `transactions` — credit history
- `list_workspaces` — workspaces accessible
- `select_workspace` — set active workspace

## 6. Recommended models (April 2026)

### Image
- `marketing_studio_image` — commercial / product / ads (default for ad creative)
- `nano_banana_2` — top quality, 4K, text/diagrams
- `soul_2` — portraits, fashion, UGC, editorial
- `soul_cast` — text-only character/avatar generation

### Video
- `marketing_studio_video` — commercials, URL-driven
- `seedance_2_0` — reference-driven, strong identity preservation
- `kling3_0` — multi-shot, with audio, motion transfer

Always run `models_explore action=get model_id=<id>` before a generation to confirm:

- `aspect_ratios` supported
- `durations` supported (videos only)
- `parameters` accepted
- `medias[].roles` declared (e.g. `start_image`, `end_image`, `reference_image`)
- `credits_per_unit` and `credit_unit` (`per_image` or `per_second`)

Models change frequently. Do not hardcode parameters; query first.

## 7. Workspace selection

If the owner has multiple Higgsfield workspaces (e.g., a personal one and a team one), the agent must select the correct workspace before any generation. Selection persists across sessions.

```bash
python scripts/higgsfield/hf.py list_workspaces
# Pick the workspace ID owned by the right business
python scripts/higgsfield/hf.py select_workspace '{"workspace_id":"<id>"}'
```

Generations charged to the wrong workspace charge the wrong credit pool — small but real spend governance issue.

## 8. Token storage

The Bearer token is sensitive but lower-risk than Meta tokens (it cannot post under your brand). Still store it as `.state/higgsfield-token.json` with `chmod 600`. Add to `.gitignore`. Rotate every 24 hours.

## 9. Troubleshooting

### `error 1010: Access denied` from Cloudflare
Default Python UA is banned. Set a browser UA on every request.

### `RuntimeError: Server did not return Mcp-Session-Id header`
Your client expected MCP session tracking. Higgsfield's MCP is bearer-scoped, not session-scoped. Drop session-id logic.

### `authorization_pending` polling forever
The owner has not yet approved at the verification URI. Check their browser. Check the device_code is not expired (15 min limit).

### `403 Forbidden` after the token works once
Token rotated or workspace lost selection. Re-select workspace; rerun device flow if `validate` confirms the token is invalid.
