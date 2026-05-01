#!/usr/bin/env python3
"""
meta-video-ad.py — End-to-end video ad creation via Meta Marketing API direct.

Workaround for `meta ads creative create --video` not supporting --link-url
(broken in official CLI v1.0.1, even though Meta's own docs show the example).

This script:
  1. Uploads a video to the ad account's video library
  2. Uploads a thumbnail image and gets the image_hash
  3. Polls until the video is processed (videos must be 'ready' before creative use)
  4. Creates an ad creative with proper object_story_spec.video_data structure
  5. Optionally creates campaign + ad set + ad if --full-chain flag is passed

Usage:
  python meta-video-ad.py \
    --video promo.mp4 \
    --thumb thumbnail.jpg \
    --page-id 101012375933517 \
    --headline "Your Headline" \
    --body "Your ad copy" \
    --link "https://yoursite.com" \
    --cta WATCH_MORE \
    --full-chain  # optional: also creates campaign+adset+ad
"""

import os
import sys
import time
import json
import argparse
import requests

API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def upload_video(account_id, video_path, token):
    """Upload video to ad account video library. Returns video_id."""
    print(f"  ⬆ Uploading video {video_path}...")
    url = f"{BASE_URL}/{account_id}/advideos"
    with open(video_path, "rb") as f:
        files = {"source": f}
        data = {"access_token": token}
        r = requests.post(url, files=files, data=data, timeout=120)
    r.raise_for_status()
    video_id = r.json()["id"]
    print(f"  ✓ Video uploaded: {video_id}")
    return video_id


def upload_image_get_hash(account_id, image_path, token):
    """Upload image to ad account and return its image_hash."""
    print(f"  ⬆ Uploading thumbnail {image_path}...")
    url = f"{BASE_URL}/{account_id}/adimages"
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {"access_token": token}
        r = requests.post(url, files=files, data=data, timeout=60)
    r.raise_for_status()
    images = r.json()["images"]
    # Returned as {filename: {hash: ..., url: ...}} — grab the hash
    image_hash = next(iter(images.values()))["hash"]
    print(f"  ✓ Image uploaded, hash: {image_hash}")
    return image_hash


def wait_for_video_ready(video_id, token, max_wait=180):
    """Videos must reach status='ready' before they can be used in a creative."""
    print(f"  ⏳ Waiting for video {video_id} to be processed...")
    elapsed = 0
    while elapsed < max_wait:
        url = f"{BASE_URL}/{video_id}"
        r = requests.get(url, params={"fields": "status", "access_token": token}, timeout=30)
        r.raise_for_status()
        status = r.json().get("status", {}).get("video_status", "unknown")
        if status == "ready":
            print(f"  ✓ Video ready (took {elapsed}s)")
            return True
        if status == "error":
            raise RuntimeError(f"Video processing failed: {r.json()}")
        print(f"     ...status={status}, waited {elapsed}s")
        time.sleep(5)
        elapsed += 5
    print(f"  ⚠ Video still processing after {max_wait}s — proceeding anyway")
    return False


def create_video_creative(account_id, name, page_id, video_id, image_hash,
                          headline, body, link_url, cta, token):
    """Create ad creative with proper object_story_spec for video."""
    print(f"  🎨 Creating creative '{name}'...")
    url = f"{BASE_URL}/{account_id}/adcreatives"
    object_story_spec = {
        "page_id": page_id,
        "video_data": {
            "video_id": video_id,
            "image_hash": image_hash,
            "title": headline,
            "message": body,
            "call_to_action": {
                "type": cta,
                "value": {"link": link_url},
            },
        },
    }
    data = {
        "name": name,
        "object_story_spec": json.dumps(object_story_spec),
        "access_token": token,
    }
    r = requests.post(url, data=data, timeout=60)
    r.raise_for_status()
    creative_id = r.json()["id"]
    print(f"  ✓ Creative created: {creative_id}")
    return creative_id


def create_campaign(account_id, name, objective, daily_budget_cents, token):
    print(f"  📋 Creating campaign '{name}'...")
    url = f"{BASE_URL}/{account_id}/campaigns"
    data = {
        "name": name,
        "objective": objective.upper(),
        "status": "PAUSED",
        "daily_budget": daily_budget_cents,
        "special_ad_categories": "[]",
        "access_token": token,
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    cid = r.json()["id"]
    print(f"  ✓ Campaign: {cid}")
    return cid


def create_adset(account_id, campaign_id, name, countries, token):
    print(f"  📋 Creating ad set '{name}'...")
    url = f"{BASE_URL}/{account_id}/adsets"
    targeting = {"geo_locations": {"countries": countries}}
    data = {
        "name": name,
        "campaign_id": campaign_id,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "THRUPLAY",  # video-friendly goal
        "bid_amount": 100,
        "targeting": json.dumps(targeting),
        "status": "PAUSED",
        "access_token": token,
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    aid = r.json()["id"]
    print(f"  ✓ Ad set: {aid}")
    return aid


def create_ad(account_id, name, adset_id, creative_id, token):
    print(f"  📋 Creating ad '{name}'...")
    url = f"{BASE_URL}/{account_id}/ads"
    data = {
        "name": name,
        "adset_id": adset_id,
        "creative": json.dumps({"creative_id": creative_id}),
        "status": "PAUSED",
        "access_token": token,
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    ad_id = r.json()["id"]
    print(f"  ✓ Ad: {ad_id}")
    return ad_id


def main():
    parser = argparse.ArgumentParser(description="Create a Meta video ad end-to-end (CLI workaround)")
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--thumb", required=True, help="Path to thumbnail image")
    parser.add_argument("--page-id", required=True, help="Facebook Page ID for ad identity")
    parser.add_argument("--headline", required=True, help="Ad headline")
    parser.add_argument("--body", required=True, help="Ad body text")
    parser.add_argument("--link", required=True, help="Destination URL")
    parser.add_argument("--cta", default="LEARN_MORE",
                        help="CTA type (LEARN_MORE, WATCH_MORE, SHOP_NOW, etc.)")
    parser.add_argument("--name-prefix", default="VideoAd",
                        help="Prefix for created resources")
    parser.add_argument("--full-chain", action="store_true",
                        help="Also create campaign+adset+ad")
    parser.add_argument("--objective", default="OUTCOME_TRAFFIC",
                        help="Campaign objective (full-chain only)")
    parser.add_argument("--daily-budget", type=int, default=500,
                        help="Daily budget in cents (full-chain only). Default 500=$5")
    parser.add_argument("--countries", nargs="+", default=["US"],
                        help="Target countries (full-chain only)")
    parser.add_argument("--account-id", default=os.getenv("AD_ACCOUNT_ID"),
                        help="Ad account (act_xxx). Defaults to $AD_ACCOUNT_ID")
    parser.add_argument("--token", default=os.getenv("ACCESS_TOKEN"),
                        help="Access token. Defaults to $ACCESS_TOKEN")
    args = parser.parse_args()

    if not args.account_id:
        print("ERROR: --account-id or AD_ACCOUNT_ID env var required", file=sys.stderr)
        sys.exit(2)
    if not args.token:
        print("ERROR: --token or ACCESS_TOKEN env var required", file=sys.stderr)
        sys.exit(2)
    if not args.account_id.startswith("act_"):
        args.account_id = f"act_{args.account_id}"

    print(f"═══ Meta Video Ad Builder ═══")
    print(f"Account: {args.account_id}")
    print(f"Page:    {args.page_id}")
    print(f"Video:   {args.video}")
    print(f"Thumb:   {args.thumb}")
    print()

    # Step 1: Upload assets
    video_id = upload_video(args.account_id, args.video, args.token)
    image_hash = upload_image_get_hash(args.account_id, args.thumb, args.token)

    # Step 2: Wait for video ready
    wait_for_video_ready(video_id, args.token)

    # Step 3: Create creative
    creative_name = f"{args.name_prefix} Creative"
    creative_id = create_video_creative(
        args.account_id, creative_name, args.page_id,
        video_id, image_hash, args.headline, args.body,
        args.link, args.cta.upper(), args.token,
    )

    result = {
        "video_id": video_id,
        "image_hash": image_hash,
        "creative_id": creative_id,
    }

    # Step 4 (optional): full chain
    if args.full_chain:
        campaign_id = create_campaign(
            args.account_id, f"{args.name_prefix} Campaign",
            args.objective, args.daily_budget, args.token,
        )
        adset_id = create_adset(
            args.account_id, campaign_id, f"{args.name_prefix} AdSet",
            args.countries, args.token,
        )
        ad_id = create_ad(
            args.account_id, f"{args.name_prefix} Ad",
            adset_id, creative_id, args.token,
        )
        result.update({
            "campaign_id": campaign_id,
            "adset_id": adset_id,
            "ad_id": ad_id,
        })

    print()
    print("═══ DONE — All resources PAUSED ═══")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
