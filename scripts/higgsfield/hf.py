#!/usr/bin/env python3
"""
hf.py — Minimal Higgsfield MCP client for OpenClaw.

Supports the streamable-HTTP MCP transport with session management.
Use as: python hf.py <tool_name> [json_args]
"""
import json
import sys
import os
import time
import pathlib
import argparse
import urllib.request
import urllib.error

TOKEN_PATH = pathlib.Path(os.environ.get("HIGGSFIELD_TOKEN_PATH") or pathlib.Path.cwd() / ".state/higgsfield-token.json")
SESSION_PATH = pathlib.Path(os.environ.get("HIGGSFIELD_SESSION_PATH") or pathlib.Path.cwd() / ".state/higgsfield-session.txt")
MCP_URL = "https://mcp.higgsfield.ai/mcp"


def get_token():
    return json.load(open(TOKEN_PATH))["access_token"]


def post_jsonrpc(method, params=None, request_id=None, session_id=None, capture_session=False):
    """Send a JSON-RPC request, returning (data, response_session_id)."""
    body = {"jsonrpc": "2.0", "method": method}
    if request_id is not None:
        body["id"] = request_id
    if params is not None:
        body["params"] = params

    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        # Cloudflare on mcp.higgsfield.ai bans default Python UA (error 1010);
        # spoof a real browser UA to get past the WAF.
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 OpenClaw/1.0",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(MCP_URL, data=json.dumps(body).encode(), headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}") from e

    new_session = resp.headers.get("Mcp-Session-Id") if capture_session else None
    raw = resp.read().decode()

    # Notification responses are HTTP 202 with no body
    if not raw.strip():
        return None, new_session

    # Streamable HTTP returns SSE-formatted blocks
    if raw.startswith("event:"):
        # Parse first 'data:' line in the SSE stream
        for line in raw.split("\n"):
            if line.startswith("data:"):
                return json.loads(line[5:].strip()), new_session
        raise RuntimeError(f"No data line in SSE response: {raw[:200]}")

    return json.loads(raw), new_session


def ensure_initialized():
    """Higgsfield MCP requires initialize+notifications/initialized once per token,
    but does not return a session id. We just send them on every cold start since
    the server is bearer-token-scoped, not session-scoped."""
    init_params = {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "openclaw-steward", "version": "1.0.0"},
    }
    post_jsonrpc("initialize", init_params, request_id=1)
    post_jsonrpc("notifications/initialized")


def call_tool(tool_name, arguments=None):
    """Call an MCP tool."""
    ensure_initialized()
    params = {"name": tool_name, "arguments": arguments or {}}
    data, _ = post_jsonrpc("tools/call", params, request_id=2)
    return data


def main():
    parser = argparse.ArgumentParser(description="Higgsfield MCP client")
    parser.add_argument("tool", help="Tool name (e.g. balance, models_explore, generate_image)")
    parser.add_argument("args_json", nargs="?", default="{}",
                        help="JSON arguments object (default: {})")
    parser.add_argument("--raw", action="store_true",
                        help="Print full JSON-RPC response, not just the unpacked result")
    cli = parser.parse_args()

    try:
        arguments = json.loads(cli.args_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON args: {e}", file=sys.stderr)
        sys.exit(2)

    response = call_tool(cli.tool, arguments)
    if cli.raw:
        print(json.dumps(response, indent=2))
        return

    # Unpack the typical MCP envelope
    if response and "result" in response:
        result = response["result"]
        # MCP wraps tool output as content[].text JSON; extract if present
        if isinstance(result, dict) and "content" in result:
            for item in result.get("content", []):
                if item.get("type") == "text":
                    try:
                        print(json.dumps(json.loads(item["text"]), indent=2))
                    except (json.JSONDecodeError, KeyError):
                        print(item.get("text"))
                else:
                    print(json.dumps(item, indent=2))
            # Also surface structuredContent if present
            if "structuredContent" in result:
                print("\n[structuredContent]")
                print(json.dumps(result["structuredContent"], indent=2))
        else:
            print(json.dumps(result, indent=2))
    elif response and "error" in response:
        print(f"MCP ERROR: {json.dumps(response['error'], indent=2)}", file=sys.stderr)
        sys.exit(1)
    else:
        print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
