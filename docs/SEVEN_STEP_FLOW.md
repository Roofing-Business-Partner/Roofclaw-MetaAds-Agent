# SEVEN_STEP_FLOW.md

The headline workflow this repo enables. Everything else is in service of these seven steps.

```
1. Story          ─▶ RoofClaw drafts an ad concept
2. Storyboard     ─▶ RoofClaw produces shot-list + copy beats
3. Images         ─▶ Higgsfield generate_image — storyboard frames
4. Video          ─▶ Higgsfield generate_video — frames into video
5. Tune           ─▶ Edits, music, captions, thumbnail extraction
6. Page post      ─▶ Video posted to Facebook Page (organic warm-up)
7. Ad campaign    ─▶ Paid ad built around the post (PAUSED for approval)
```

## Why all 7 matter

A finished ad is not just a video file. Modern Meta delivery rewards content that has organic engagement signals before paid distribution kicks in. The 7-step flow produces:

- **Brand-coherent creative** (steps 1–2) because story and storyboard come from a Marketing-configured agent that knows the brand voice
- **High-quality visual assets** (steps 3–4) generated through Higgsfield's commercial-grade models
- **Polished output** (step 5) — auto-extracted thumbnails, frame trims, optional captions
- **Organic engagement signal** (step 6) — Meta sees the post earn likes/comments before it becomes an ad
- **Conversion-ready ad** (step 7) — fully wired campaign with proper targeting, creative, and PAUSED safety

## Step 1 — Story

The Marketing RoofClaw drafts an ad concept aligned to:

- The offer (e.g., "free 24-hour roof inspection after a hailstorm")
- The audience (e.g., suburban homeowners aged 35–65 in storm-affected zip codes)
- The brand voice (`SOUL.md` of the marketing agent)
- The campaign objective (awareness, traffic, leads, conversions)

Output is a 2–3 sentence creative brief. The agent should propose 3 alternatives and let the owner pick before moving to step 2.

## Step 2 — Storyboard

The agent expands the chosen story into a shot-list:

- 5–10 short scenes, each with one visual idea
- Aspect ratio (9:16 for Reels/Stories, 1:1 for Feed, 16:9 for in-stream)
- Total duration target (5s, 15s, 30s)
- On-screen copy beats (headline, CTA, supporting text)
- Music/voiceover hint

Output is a structured JSON or markdown table the agent can hand to step 3.

## Step 3 — Images

For each scene in the storyboard, call Higgsfield `generate_image`:

```python
hf.call_tool("generate_image", {
    "params": {
        "model": "marketing_studio_image",   # commercial-grade
        "prompt": "<scene description>",
        "aspect_ratio": "9:16",              # match step 2
        "count": 2                            # generate 2, owner picks one
    }
})
```

Save each chosen image's UUID. Higgsfield returns URLs and UUIDs in the result.

For best results: use `models_explore action=recommend` first with the scene context to pick the optimal model.

## Step 4 — Video

Two patterns, depending on storyboard complexity:

### Pattern A — Single shot
For a single-scene video, pass one image and a motion prompt:

```python
hf.call_tool("generate_video", {
    "params": {
        "model": "seedance_2_0",
        "prompt": "Camera slowly orbits the roofer at golden hour",
        "medias": [{"value": "<image_uuid>", "role": "start_image"}],
        "duration": 5,
        "aspect_ratio": "9:16"
    }
})
```

### Pattern B — URL-driven (Marketing Studio)
For commercials based on a real product/service URL:

```python
# 1. Pre-stage the URL
hf.call_tool("show_marketing_studio", {"action": "fetch", "url": "https://example.com/roofing-service"})
# 2. Generate the commercial
hf.call_tool("generate_video", {
    "params": {
        "model": "marketing_studio_video",
        "prompt": "30-second roofing service commercial highlighting fast inspection turnaround",
        "url": "https://example.com/roofing-service",
        "duration": 30,
        "aspect_ratio": "9:16"
    }
})
```

Marketing Studio is the killer feature. Roofers can hand their website URL and get a finished commercial.

Polling: video generation is async. Use `job_status` until `status: completed`.

## Step 5 — Tune

Once the video is `completed`:

- Download the video file (Higgsfield returns `rawUrl`)
- Extract a thumbnail frame (typically the brightest middle frame; ffmpeg one-liner)
- Optional: add captions via the brand template
- Optional: trim to exact platform-required durations
- Re-upload the final MP4 to a known location accessible to the Meta wrapper

Reference scripts: `scripts/tune/extract-thumbnail.sh`, `scripts/tune/add-captions.py` (placeholder).

## Step 6 — Page post

Post the finished video as an organic Page post for warm-up:

```bash
curl -X POST "https://graph.facebook.com/v21.0/<PAGE_ID>/videos" \
  -F "source=@finished-video.mp4" \
  -F "title=<title>" \
  -F "description=<copy>" \
  -F "access_token=<page_token>"
```

The Page token is different from the user token; obtain it via:

```bash
curl "https://graph.facebook.com/v21.0/<PAGE_ID>?fields=access_token&access_token=<USER_TOKEN>"
```

Wait 6–24 hours so the post earns organic signals before promoting.

A reference script is at `scripts/meta/post-page-video.sh` (to be added).

## Step 7 — Ad campaign

Two patterns:

### Pattern A — Boost the existing post
Reference the post by ID and create an ad creative against it:

```bash
meta ads creative create \
  --name "Boost: storm damage post" \
  --object-story-id <PAGE_ID>_<POST_ID> \
  --page-id <PAGE_ID>
```

(This avoids the broken video creative path entirely.)

### Pattern B — Fresh video ad (the moat)
Use the custom wrapper because the official CLI is broken for video creatives:

```bash
python scripts/meta-video-ad.py \
  --video finished-video.mp4 \
  --thumb thumbnail.jpg \
  --page-id <PAGE_ID> \
  --headline "Storm Damage? Free Inspection." \
  --body "We respond in 24 hours. Trusted by 1,500 homeowners." \
  --link "https://yourcompany.com/inspection" \
  --cta GET_QUOTE \
  --full-chain \
  --countries US \
  --daily-budget 2000   # $20.00/day
```

The script:

1. Uploads the video to `/advideos` and waits for processing
2. Uploads the thumbnail to `/adimages` and captures the hash
3. Builds a correct `object_story_spec.video_data` block (which the official CLI cannot do)
4. Creates the creative
5. Optionally creates campaign + ad set + ad with `--full-chain`
6. Everything PAUSED by default

## Approval gate

Between steps 6 and 7, send the owner a preview:

- Page post URL
- Thumbnail image
- Proposed ad copy + CTA + targeting + budget
- One approve / reject buttons

Only after explicit approval does the agent unpause the ad. Activation is never automatic.

## Cost summary

| Step | Provider | Cost (rough) |
|---|---|---|
| 1 | Marketing RoofClaw (LLM tokens) | $0.05 – $0.30 |
| 2 | Marketing RoofClaw (LLM tokens) | $0.10 – $0.50 |
| 3 | Higgsfield (per image) | ~5–15 credits |
| 4 | Higgsfield (per second of video) | ~10–40 credits |
| 5 | Local compute (ffmpeg) | $0 |
| 6 | Meta API (free) | $0 |
| 7 | Meta API (free) + ad spend | owner-controlled |

A typical 15-second roofing commercial uses ~150–600 Higgsfield credits depending on model.

## Failure modes and recovery

- **Higgsfield job fails** — retry with `models_explore` to find a fallback model
- **Video processing stalls on Meta** — wait, then re-upload; do not auto-retry forever
- **Page post rejected** — Meta sometimes flags AI-generated video as policy violation; provide an AI disclosure caption and resubmit
- **Ad disapproved** — Meta provides a rejection reason; the agent must surface it to the owner and not just "try a different ad"
- **Rate limit on the ad account** — switch to a different ad account for testing or wait 60 minutes
