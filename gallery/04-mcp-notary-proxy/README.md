# Scenario 04: LogisticsCo Supply Chain Agent — MCP Notary (exit 0)

## Scenario

An AI agent retrieves weather data, checks warehouse inventory, and calculates
shipping risk through MCP-served tools. Every tool call passes through the Assay
MCP Notary Proxy, which receipts each invocation with timing, arguments, results,
and outcome. The proof pack is signed and verifiable without trusting the agent,
the tool server, or the platform.

## Buyer Question

> "Our agents use dozens of MCP tools. Can you prove which tools were called,
> with what arguments, and what they returned — without us changing any server code?"

## Verdict

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **N/A** (integrity-only) |
| Verifier exit code | `0` |

## What This Proves

- 3 MCP tool calls were notarized: `get_weather`, `check_inventory`, `calculate_risk`
- Each receipt records: tool name, arguments, result, duration, server ID, outcome
- The proof pack is signed with Ed25519 and all file hashes are verified
- No MCP server code was modified — the proxy sits between client and server
- The evidence cannot be altered without breaking the signature

## What This Does NOT Prove

- That every tool call was intercepted (only proxied calls are receipted)
- That tool results are correct (the proxy records what happened, not what should have)
- That the signer key was not compromised
- That timestamps are externally anchored (local clock was used)

## One Sentence

**An MCP-served action is notarized and independently verifiable.**

## Run Locally

```bash
pip install assay-ai
assay verify-pack ./proof_pack
# Expected: exit 0 (PASS)
```

Or run the bundled script:

```bash
bash verify.sh
```

## How This Was Built

The demo server (`demo_server.py`) is a minimal NDJSON MCP server with three
tools. The Assay MCP Notary Proxy wraps it transparently:

```bash
assay mcp-proxy --store-args --store-results \
  --server-id gallery-demo-server \
  -- python3 demo_server.py
```

The proxy intercepts every `tools/call` request and response, mints an
`mcp_tool_call` receipt for each, and builds a signed proof pack on session end.
No changes to the server. No SDK integration required.

## Files in This Pack

```
proof_pack/
  pack_manifest.json      # SHA-256 hashes of all pack files + Ed25519 signature
  pack_signature.sig      # Raw Ed25519 signature bytes
  receipt_pack.jsonl      # 3 MCP tool-call receipts (one per line)
  verify_report.json      # Machine-readable verification result
  verify_transcript.md    # Human-readable verification transcript
  PACK_SUMMARY.md         # What happened, what it proves, what it does not
demo_server.py            # The MCP server used to generate this scenario
```

## Why This Matters

MCP is becoming the universal protocol for AI tool calls. Every tool call that
passes through an MCP server is a governance event: the agent acted on the world,
consumed data, or made a decision. The MCP Notary Proxy converts these events
into tamper-evident, independently verifiable evidence without touching the
server, the agent, or the deployment.

This is the answer to: *"How do we audit what our agents actually did?"*
