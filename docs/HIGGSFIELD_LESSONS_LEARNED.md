# HIGGSFIELD_LESSONS_LEARNED.md

> Hard-won lessons from producing the **"An Ode to the Roofer"** brand-film demo live on stream, 2026-04-30. Read this BEFORE you generate anything. It will save you credits, time, and the embarrassment of shipping a wrong-model frame.

This document codifies what we learned by producing 8 versions of two hero frames, training two Soul ID characters, uploading 28 reference images, and watching three different Higgsfield models behave in three completely different ways under identical prompts.

If you are a Marketing RoofClaw implementing this agent, internalize these rules. They override anything in the Higgsfield official docs that contradicts them — these are field-tested.

---

## 🥇 The Cardinal Rule

> **Match the model to the job, or the model will silently override your brief.**

Higgsfield's model catalog looks similar at a glance — they all generate "cinematic images." They are not interchangeable. Each model has a strong bias baked in by its training data, and that bias will quietly defeat any prompt instruction that pulls against it.

### Model → Use Case Decision Matrix

| Job Type | Use This Model | Do NOT Use | Why |
|---|---|---|---|
| **Wide environmental establisher** (drone shot, lot, exterior, no character) | `cinematic_studio_2_5` | `soul_2`, `soul_cinematic` | Soul models are portrait specialists and will ignore wide framing |
| **Wide shot with TINY character through window/silhouette** | `nano_banana_2` (with reference images) | `soul_2`, `soul_cinematic` | Same — Soul models cannot render tiny figures in vast spaces |
| **Intimate character close-up / portrait** | `soul_2` with trained `soul_id` | `cinematic_studio_2_5`, `nano_banana_2` (worse identity lock) | Soul 2.0 is purpose-built for character likeness |
| **Dramatic-lit character moment / concept-art portrait** | `soul_cinematic` (with image reference) | `nano_banana_2` (less dramatic) | Soul Cinematic is tuned for extreme lighting |
| **Character ref-sheet (4-angle identity anchor)** | `nano_banana_2` (text-only) | `soul_2` (will refuse multi-angle layouts) | Nano Banana Pro renders structured grids well |
| **Product/commercial UGC ad** | `marketing_studio_image` | Anything else | Tag-matched for commercial intent |

**The diagnostic test:** if your model returns a tightly-framed portrait when you asked for a wide drone shot, you used the wrong model. Switch to a non-Soul model and try again. Don't waste 4 rerolls on prompt tweaks.

**Source:** "Ode to the Roofer" demo, Panel 14 mirror shot. Three attempts on Soul Cinematic and Soul 2.0 (with trained Marcus character) ALL ignored "extreme wide drone establisher" and produced portraits or near-empty wides with no character. Same prompt to `cinematic_studio_2_5` → produced a perfect 9/10 wide.

---

## 🎭 Character Casting Pipeline (The 28-Image Method)

The single biggest mistake in AI ad production is generating characters scene-by-scene without locking identity first. This is the proven pipeline.

### Phase 1: Generate the Identity Anchor (1 image, ~6 credits)

Use `nano_banana_2` to produce a clean 4-angle character reference sheet.

```json
{
  "params": {
    "model": "nano_banana_2",
    "prompt": "Professional character reference sheet, four angles in one image (front view, three-quarter left, full profile right, three-quarter back), of a [AGE] [GENDER] [ROLE]. Same character in all four angles, photorealistic. [DETAILED FACE/WARDROBE/BUILD]. Neutral medium gray studio backdrop, even soft cinema lighting, sharp focus, commercial photography quality, consistent identity across all four views.",
    "aspect_ratio": "16:9",
    "resolution": "2k"
  }
}
```

**Critical:** include "Absolutely no logos, no brand marks, no text on clothing." Higgsfield will hallucinate brand logos otherwise.

### Phase 2: Generate 28 Reference Variations (~168 credits, ~6 minutes parallel)

The Higgsfield Soul ID training docs say "20+ images." 28 is the working sweet spot. Distribution:

| Group | Count | Purpose |
|---|---|---|
| **A. Studio identity locks** | 8 | Spine — headshots front/3Q-left/3Q-right/profile-left/profile-right + medium torso + full body |
| **B. Real-world contexts** | 8 | Dropped into target scene environments (truck cab, rooftop, kitchen, etc.) |
| **C. Expression study** | 6 | Emotional vocabulary the film needs (tired-warm, determined, quiet-relief, focused, worn-out, calm) |
| **D. Lighting variations** | 6 | The lighting arc of the film (golden hour, overcast, harsh midday, low-key window, pre-dawn, phone-glow) |

**Submit in waves of 6 in parallel.** Pass the Phase-1 anchor as `input_images` to every prompt. This locks identity across all 28.

### Phase 3: Upload to Higgsfield Workspace (no credits)

```python
# 1. Request presigned URLs in batch
files_payload = [{"filename": f, "content_type": "image/png"} for f in filenames]
resp = call("media_upload", {"method": "upload_url", "files": files_payload})
# 2. PUT each file to its presigned upload_url with Content-Type: image/png
# 3. Confirm in batch:
call("media_confirm", {"type": "image", "media_ids": [u["media_id"] for u in resp["uploads"]]})
```

Save the filename → media_id mapping to a `media_ids.json` file. You'll need these IDs for inference-time conditioning.

### Phase 4: Train Soul ID (~25 credits, ~10 min, web UI only)

Soul ID training is **NOT exposed via MCP.** The user must:
1. Open higgsfield.ai → Characters / Soul ID
2. Select all 28 uploaded images
3. Click "Train" — choose Soul 2.0 (for portrait/character work)
4. Optionally also train on Soul Cinematic (for dramatic-light moments)

**After training, the user must paste the soul_id UUID back to the agent.** The MCP cannot list trained Soul IDs — `show_marketing_studio` only returns 20 Marketing Studio preset avatars, not user-trained Soul IDs. Save the soul_id to project state immediately:

```markdown
# SOUL_IDS.md
- Marcus (Soul 2.0): `96662672-e38d-4565-b02b-849a8a20edb4`
- Marcus-Cinema (Soul Cinematic): `bfbd5321-defc-4da1-bbb7-acef72ad63ff`
```

---

## ⚙️ MCP Schema Quirks (Will Bite You If You Don't Know)

These caught us during the demo. Codify them so they don't catch your customer's agent.

### 1. `medias` parameter format differs by model

| Model | `medias` format | Example |
|---|---|---|
| `nano_banana_2` | accepts URL strings via `input_images` (NOT `medias`) | `"input_images": ["https://..."]` |
| `cinematic_studio_2_5` | requires `{"value": "...", "role": "image"}` objects | `"medias": [{"value": "<media_id>", "role": "image"}]` |
| `soul_2` | requires `{"value": "...", "role": "image"}` objects; ALSO accepts URL strings (will auto-upload) | `"medias": [{"value": "https://..."}]` works |
| `soul_cinematic` | requires `{"value": "<media_id>", "role": "image"}` from prior upload | Can NOT pass raw URLs directly |

**Symptom of getting it wrong:** `MCP error -32602: Invalid input: expected object, received string` → switch from `["url"]` to `[{"value": "url", "role": "image"}]`.

### 2. Soul ID invocation is parameter-level, not media-level

Pass the trained character UUID via the `soul_id` parameter, NOT the `medias` array:

```json
{
  "model": "soul_2",
  "soul_id": "96662672-e38d-4565-b02b-849a8a20edb4",
  "medias": [{"value": "<composition_reference_url>", "role": "image"}]
}
```

`soul_cinematic` does **NOT** expose `soul_id` via MCP (parameters: []). Soul Cinematic with trained characters works in the web UI only. If you must use a Soul Cinematic-trained character, fall back to passing the user's anchor portrait as the media reference.

### 3. Job submission returns instantly with status `pending`

Always poll with `sync: true`:

```json
{ "jobId": "<uuid>", "sync": true }
```

The HTTP request will hold open for up to 90s waiting for completion.

### 4. The Cloudflare User-Agent ban

The MCP sits behind Cloudflare. Default Python `urllib` User-Agent gets banned with error 1010. The reference `hf.py` client patches the UA to a real Safari string — preserve this.

### 5. `models_explore` recommendations are strong but not law

`models_explore action=recommend` returns ranked models with match scores. Top score isn't always right for your shot — consult the Decision Matrix above first. The recommender weighs tags, not framing intent.

---

## 🛑 Iteration Discipline

> Stop iterating on prompts at V4-V5. After that, fix in post or change models.

**The pattern we observed:**
- V1 → V2 → V3: each version often improves
- V4 onward: diminishing returns. Sometimes V5 is worse than V3.
- After 3 misses on the same brief, the model itself is wrong for the job.

**Decision tree when V3 doesn't land:**

1. Is the brief asking for something OUTSIDE the model's specialty? → Switch models.
2. Is one specific physics detail (phone-glow underlight, specific reflections) failing? → Accept the base frame, plan to comp the detail in After Effects / Photoshop / Higgsfield's `edit_image`.
3. Is the issue a wardrobe/identity drift? → Add stricter character anchors, OR train Soul ID and use `soul_id` param.
4. Is the framing wrong? → That's a model bias problem. Switch models.

**Cost discipline:** A typical hero frame should cost <30 credits across all attempts. If you've spent >50 credits on one frame, stop and reconsider the approach.

---

## 🎬 Storyboard-to-Model Translation (Pre-Flight Check)

Before generating, classify each storyboard panel using this matrix. This prevents 80% of the misses we hit during the demo.

| Storyboard panel describes... | Pick model |
|---|---|
| Drone descending toward empty lot, no character | `cinematic_studio_2_5` |
| Wide shot, character barely visible through window | `nano_banana_2` + 4 reference images |
| Tight CU on character's face, emotional moment | `soul_2` with trained `soul_id` |
| Dramatic-light close-up (phone glow, monitor glow, candlelight) | `soul_cinematic` with image ref OR `soul_2` with trained `soul_id` |
| Character at work in environment, mid-shot | `soul_2` with trained `soul_id` + environment description |
| Product shot or commercial UGC | `marketing_studio_image` |
| Mirror shot rhyming an earlier panel | Same model as the original frame, pass original as composition reference |

**The wide-mirror trap (we fell into this):**
A wide-to-wide visual rhyme between an opening establisher and a final closer is cinematically powerful — but if both ends require character visibility, the Soul models will reject the wide framing. Either:
- Make BOTH wides character-less and add the emotional close-up as a separate intercut shot (the storyboard-correct move), OR
- Accept the wide closer will be a "post" job — generate the wide environmental version and composite the character via edit_image / external comp tools

---

## 📝 Reference Image Curation (The 6-Anchor Method)

When using image-based conditioning (`input_images` for nano_banana_2, `medias` for cinematic_studio_2_5/soul_2), pass **4-6 anchors maximum**, not all 28.

The model gets confused by too many references. Pick anchors that span:

1. **Identity baseline** — A1 front headshot
2. **Angle variation** — A2 or A3 (3/4 angle)  
3. **Build/proportion** — A6 medium front
4. **Emotional baseline** — C6 (calm) or C2 (determined)
5. **Lighting reference** (if relevant to shot) — D-series lighting variation matching the target shot's light
6. **Composition reference** (if mirroring) — the prior frame URL

Each anchor should contribute ONE specific thing. If two anchors do the same job, you're wasting a slot.

---

## 🚦 Pre-Generation Checklist

Before you call `generate_image`, verify:

- [ ] **Model matches job type** (consulted the Decision Matrix)
- [ ] **Soul ID invoked correctly** if character is featured (parameter-level, not media-level)
- [ ] **Reference images chosen** (4-6 max, each contributing distinct value)
- [ ] **Negative-prompt-style instructions included** for known model drift ("no Chevy, no crew cab, no extended cab")
- [ ] **Aspect ratio matches storyboard intent** (16:9 for cinema, 9:16 for Reels/TikTok)
- [ ] **Resolution declared** (2k for hero frames, 1k for drafts)
- [ ] **Prior version URL passed as composition reference** if this is a sequel/mirror shot
- [ ] **Lighting discipline explicit** ("the ONLY warm light source is X")
- [ ] **Iteration budget set** (max V5 before model swap or post-comp)

---

## 🎓 The Three Truths

If your customer's RoofClaw remembers nothing else from this document, remember:

1. **Soul models are portrait specialists. Cinematic models are environment specialists. Don't mix them up.**
2. **The trained Soul ID lives only in the web UI. The user must paste the UUID. Save it to project state.**
3. **Stop iterating at V5. After that, switch models or fix in post.**

---

## Source

These lessons were derived from the live production of "An Ode to the Roofer" brand-film demo on 2026-04-30, run by Adam Sand (RBP/RoofClaw founder) and the Steward agent. The session produced:

- 28 character reference images for "Marcus" (the lead character)
- 2 trained Soul IDs (Soul 2.0 and Soul Cinematic)
- 4 versions of the opening establisher frame
- 4 versions of the final mirror frame
- Confirmed model behavior across `cinematic_studio_2_5`, `nano_banana_2`, `soul_2`, and `soul_cinematic`

Total spend: ~$8 in Higgsfield credits. Total wall-clock: ~2 hours including discovery and iteration.

The lessons here represent failed and successful patterns observed in production. They are not theoretical.
