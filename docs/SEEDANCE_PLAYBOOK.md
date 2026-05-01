# Seedance 2.0 Playbook (Higgsfield)

> Source: "Stop Wasting Credits on Seedance 2.0, Do This Instead"
> Channel: Creating with Conor — uploaded April 26, 2026
> URL: https://youtu.be/SvhFnN-axJw

> 📌 **Companion read:** [`HIGGSFIELD_LESSONS_LEARNED.md`](./HIGGSFIELD_LESSONS_LEARNED.md) — model-selection matrix and character-casting pipeline distilled from live production. Read first if you have not already; this playbook covers Seedance specifically while that doc covers the broader model ecosystem.
> Captured: April 30, 2026 by Claudio

## TL;DR — The 7 things that separate winners from credit-burners

1. **Use `seedance_2_0`, NEVER `seedance_2_0_fast`** for any clip you actually plan to use. Fast is for previews/early testing; it skips refinement passes and outputs feel "soft."
2. **Set duration to 15 seconds** (the max). Shorter clips = more generations needed in the edit. 15s gives more material per credit and more flexibility.
3. **Aspect ratio matters at generation, not in post.** 16:9 for YouTube, 9:16 for Reels/TikTok. Cropping after kills composition.
4. **Always generate at the highest resolution** the plan allows.
5. **Always run output through Higgsfield's Topaz Video upscaler** to 4K before editing. It's free and the quality jump is real.
6. **Multi-shot prompts beat one-line prompts** — Seedance is a multi-shot model. Vague prompts let it improvise badly.
7. **Use the eligibility check button** before hitting generate. Saves credits when references or prompt language trip Meta-style content gates.

## The compound-knowledge moves (this is where hours and dollars are saved)

### 8. Build a CHARACTER REFERENCE SHEET before any project with a person in it

A character reference sheet is **one image** showing the character from **four angles** (front / side / back / three-quarter) in a single composite. This gives Seedance a complete picture instead of letting it guess what the back of the character looks like.

Without this, you get inconsistent face shapes, hair, clothing details across clips. With this, the same character comes back recognizable in every generation.

**Build it with `nano_banana_2`** (called Nano Banana Pro in the video) — straightforward prompt: "Generate [character description] from four angles in one image: front view, side view, back view, three-quarter view." Generate variations, pick the best, that's your reference for every clip in the project.

### 9. Stack ALL relevant references — don't stop at one image

Seedance 2.0 supports **9 image references + 3 video clips + 3 audio clips** per generation. Most people upload one image and stop.

For each clip, attach:
- **Character sheet** (consistency anchor)
- **Key visual** of the scene (environment + composition anchor)
- **Location reference** (if separate from key visual)
- **Audio reference** (see #11)

The more anchors, the less the model guesses.

### 10. For multi-scene continuity, upload the PREVIOUS CLIP as a video reference — not a screenshot

The amateur move: screenshot the last frame of clip 1 and use it as the starting image for clip 2. This gives Seedance one frozen frame with no motion data.

The pro move: upload the **entire previous clip** in the video-reference slot. The model reads camera speed, direction, motion trajectory, and lighting changes across the whole clip. The next scene then carries that energy forward — same camera language, same light, same momentum.

Workflow per scene:
1. Generate scene 1
2. Open scene 2 panel
3. Upload character sheet + new key visual as image references (as usual)
4. Upload **scene 1's finished video clip** as the video reference
5. Write the prompt for scene 2's new action/location
6. Generate
7. Repeat — each new scene uses the previous clip as its video reference

### 11. Use the AUDIO REFERENCE for voice consistency — Seedance does TTS too

Seedance 2.0 has an audio-reference input. Upload any short clip of a voice you want to match (tone, cadence, style). In the prompt, write the dialogue + delivery notes + the instruction "match the reference voice."

Then for every section of your script, swap in the **same audio reference** and update the dialogue. You get a complete narration in one consistent voice — no separate voice tool, no file-juggling, no inconsistency between segments.

Keep each generation's spoken content within 15 seconds.

## Prompt structure that actually works

**Bad:** `A chef preparing food in a restaurant kitchen.`

**Good:** Multi-shot description with:
- Shot type per beat (wide, medium, close-up, over-shoulder)
- Camera movement per beat (push-in, dolly, pan, static)
- Subject action per beat
- Environment / lighting / mood notes
- Transitions between shots

**Shortcut for non-cinematographers:** dump your rough idea into Claude / GPT / Gemini and ask: "Expand this into a detailed multi-shot cinematic prompt for Seedance 2.0." The LLM returns a structured version with shot types, camera movements, transitions, and lighting notes. Paste into Seedance.

## Audio toggle gotcha

The audio toggle in the generation panel is **off by default for some users**. If you generate with audio off and need audio, you re-run the whole thing and lose the credits. **Always check before hitting generate.**

## Eligibility check — the "do this or eat a dead credit" step

Every image, video, and audio reference goes through an automatic eligibility check on upload. So does the text prompt. Reasons for failure:
- Copyrighted commercial film references
- Public figures
- Certain protected content categories
- Prompt language that trips the content policy (even on benign prompts)

**Use the "Check Eligibility" button next to each reference** before generating. If something fails:
- For references: replace or modify
- For text: paste into Claude / GPT and ask "rewrite this prompt without changing the idea, just the specific language that may have triggered Higgsfield's content policy." Copy back, recheck, generate.

If you skip the eligibility check and hit generate, the credit is consumed before the failure is reported.

## Pre-generation checklist (the "fewer credits, more first-try wins" loop)

```
[ ] Model = seedance_2_0 (NOT _fast) — unless explicitly previewing
[ ] Duration = 15 seconds
[ ] Aspect ratio = 16:9 (YouTube/Meta horizontal) or 9:16 (Reels/TikTok)
[ ] Resolution = max available
[ ] Audio toggle ON if dialogue or ambient sound needed
[ ] Character reference sheet uploaded (if person involved)
[ ] Key visual uploaded
[ ] Video reference uploaded (if continuing a sequence)
[ ] Audio reference uploaded (if matching voice)
[ ] Eligibility check passed on every reference + the text prompt
[ ] Prompt is multi-shot structured (used Claude/GPT to expand if needed)
```

## Post-generation pipeline

```
1. Topaz Video upscale → 4K
2. Optional: bump frame rate in advanced settings if motion feels choppy
3. Bring all clips into editor in sequence order
4. Audit continuity: face, wardrobe, light, camera direction
5. Export
```

## Implications for our skill (RoofClaw Meta Ads Agent — Higgsfield skill)

We need to encode these as **defaults in `scripts/higgsfield/hf.py` and the seven-step orchestrator:**

1. **Default model selector**: when the agent picks a video model for production output, default to `seedance_2_0` and explicitly forbid `seedance_2_0_fast` unless the operator passes `--draft` or `--preview`.
2. **Default duration**: 15 seconds when the model supports it.
3. **Default workflow for human characters**: before any video generation involving a human, prompt the operator: "Do you have a character reference sheet?" If no, generate one with `nano_banana_2` first, store it as a project asset, and reuse it across all generations.
4. **Default workflow for multi-scene**: encode the "previous clip as video reference" pattern in the orchestrator. After scene N completes, scene N+1 must include that clip as a video reference.
5. **Eligibility pre-flight**: build a step that runs eligibility checks before any `generate_video` call. If a reference fails, halt and notify the operator. If the prompt fails, route through an LLM rewrite and recheck before retry.
6. **Audio toggle awareness**: when the prompt mentions speech, dialogue, voiceover, or specific sound, automatically enable audio + suggest an audio reference.
7. **Post-process upscale**: after `generate_video` completes, automatically queue Topaz upscale to 4K before delivering the asset to the next pipeline step.
8. **Prompt expansion helper**: if the operator passes a one-liner like "roofer on a roof during a storm," the agent expands it through Claude into a multi-shot Seedance-shaped prompt before calling `generate_video`.

This is the moat. It's not access to Seedance — anyone can pay for that. It's encoding the **pre-flight discipline** so a roofer never has to think about it.
