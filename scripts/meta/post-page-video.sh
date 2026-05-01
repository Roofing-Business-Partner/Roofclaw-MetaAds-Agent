#!/bin/bash
# post-page-video.sh — Post a video to a Facebook Page as organic content.
#
# Usage:
#   bash scripts/meta/post-page-video.sh <video_path> <page_id> "<title>" "<description>"
#
# Requires:
#   - ACCESS_TOKEN (user token with publish_video scope) in env
#   - The user must manage the Page; we exchange to a Page token automatically.
set -euo pipefail

VIDEO_PATH="${1:-}"
PAGE_ID="${2:-}"
TITLE="${3:-}"
DESCRIPTION="${4:-}"

if [ -z "$VIDEO_PATH" ] || [ -z "$PAGE_ID" ]; then
  echo "Usage: $0 <video_path> <page_id> [title] [description]" >&2
  exit 2
fi

if [ -z "${ACCESS_TOKEN:-}" ]; then
  echo "ERROR: ACCESS_TOKEN env var required (user token with publish_video scope)" >&2
  exit 2
fi

if [ ! -f "$VIDEO_PATH" ]; then
  echo "ERROR: video file not found: $VIDEO_PATH" >&2
  exit 2
fi

API_VERSION="${API_VERSION:-v21.0}"
BASE="https://graph.facebook.com/$API_VERSION"

echo "▶ Fetching Page access token for $PAGE_ID..."
PAGE_TOKEN=$(curl -fsS "$BASE/$PAGE_ID?fields=access_token&access_token=$ACCESS_TOKEN" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('access_token',''))")

if [ -z "$PAGE_TOKEN" ]; then
  echo "ERROR: could not retrieve page access token. Confirm the user manages this Page." >&2
  exit 1
fi

echo "▶ Uploading video..."
RESPONSE=$(curl -fsS -X POST "$BASE/$PAGE_ID/videos" \
  -F "source=@$VIDEO_PATH" \
  -F "title=$TITLE" \
  -F "description=$DESCRIPTION" \
  -F "access_token=$PAGE_TOKEN")

echo "$RESPONSE"
echo ""
VIDEO_ID=$(echo "$RESPONSE" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('id',''))" 2>/dev/null || echo "")
if [ -n "$VIDEO_ID" ]; then
  echo "✅ Video uploaded. Video ID: $VIDEO_ID"
  echo "    URL pattern: https://facebook.com/$VIDEO_ID"
fi
