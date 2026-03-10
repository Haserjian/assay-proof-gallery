#!/usr/bin/env python3
"""
Minimal MCP server for Assay Proof Gallery Scenario 04.

Speaks NDJSON JSON-RPC 2.0. Handles initialize, tools/list, and tools/call.
No real API calls — all tool results are synthetic but structurally valid.

This server is wrapped by `assay mcp-proxy` to demonstrate tool-call auditing.
"""
import json
import sys

TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "inputSchema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "check_inventory",
        "description": "Check product inventory levels",
        "inputSchema": {
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
        },
    },
    {
        "name": "calculate_risk",
        "description": "Calculate risk score for a transaction",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "category": {"type": "string"},
            },
            "required": ["amount"],
        },
    },
]

TOOL_RESULTS = {
    "get_weather": lambda args: f"72°F, Partly Cloudy in {args.get('city', 'Unknown')}",
    "check_inventory": lambda args: json.dumps(
        {"product_id": args.get("product_id", "?"), "in_stock": 142, "warehouse": "US-WEST-2"}
    ),
    "calculate_risk": lambda args: json.dumps(
        {"score": 0.23, "level": "low", "amount": args.get("amount", 0)}
    ),
}


def handle_request(msg):
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "gallery-demo-server", "version": "0.1.0"},
            },
        }
    elif method == "notifications/initialized":
        return None  # notification, no response
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result_fn = TOOL_RESULTS.get(tool_name)
        if result_fn:
            text = result_fn(arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": text}],
                    "isError": False,
                },
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }
    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        return None  # notification


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_request(msg)
        if response:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
