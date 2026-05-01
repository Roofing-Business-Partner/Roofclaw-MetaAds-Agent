#!/bin/bash
# start-device-flow.sh — kick off Higgsfield OAuth device flow and poll for the token.
#
# Usage:
#   bash scripts/higgsfield/start-device-flow.sh
#
# After the owner approves at the printed URL, this script writes the token to
# .state/higgsfield-token.json (chmod 600).
set -euo pipefail

DEVICE_AUTH="https://fnf-device-auth.higgsfield.ai"
STATE_DIR="${STATE_DIR:-.state}"
TOKEN_PATH="$STATE_DIR/higgsfield-token.json"

mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"

echo "═══ Higgsfield device-flow authorization ═══"
echo ""
echo "▶ Requesting device code..."
RESPONSE=$(curl -fsS -X POST "$DEVICE_AUTH/authorize" \
  -H "Content-Type: application/json" \
  -d "{}")

DEVICE_CODE=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['device_code'])")
VERIFICATION_URI=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['verification_uri'])")
INTERVAL=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['interval'])")
EXPIRES_IN=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['expires_in'])")

echo ""
echo "▶ Owner: open this URL in your browser, log into Higgsfield, click Approve."
echo ""
echo "    $VERIFICATION_URI"
echo ""
echo "▶ Waiting up to $((EXPIRES_IN / 60)) minutes for approval..."
echo ""

DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$DIR/poll-token.sh" "$DEVICE_CODE" "$INTERVAL" "$TOKEN_PATH"
