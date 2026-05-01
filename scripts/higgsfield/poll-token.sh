#!/bin/bash
# poll-token.sh — Poll Higgsfield device-flow token endpoint until user authorizes.
#
# Usage:
#   bash scripts/higgsfield/poll-token.sh <device_code> [interval_seconds] [token_path]
set -euo pipefail

DEVICE_CODE="${1:-}"
INTERVAL="${2:-5}"
TOKEN_PATH="${3:-.state/higgsfield-token.json}"

if [ -z "$DEVICE_CODE" ]; then
  echo "Usage: $0 <device_code> [interval] [token_path]" >&2
  exit 2
fi

mkdir -p "$(dirname "$TOKEN_PATH")"

MAX_WAIT=900   # 15 min
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
  RESPONSE=$(curl -fsS -X POST "https://fnf-device-auth.higgsfield.ai/token" \
    -H "Content-Type: application/json" \
    -d "{\"device_code\":\"$DEVICE_CODE\"}" || true)

  if echo "$RESPONSE" | grep -q "access_token"; then
    echo "$RESPONSE" > "$TOKEN_PATH"
    chmod 600 "$TOKEN_PATH"
    echo "✅ AUTHORIZED at $(date '+%H:%M:%S')"
    echo "Token stored at $TOKEN_PATH"
    exit 0
  fi

  echo "[$(date '+%H:%M:%S')] waited ${ELAPSED}s — $RESPONSE"
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo "⏱ TIMEOUT — owner did not authorize within $MAX_WAIT seconds." >&2
exit 1
