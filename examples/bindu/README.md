# ContractGuard × Bindu — A2A agent integration

Run ContractGuard as a discoverable, DID-identified microservice that other AI
agents can call over the [A2A](https://github.com/getbindu/Bindu) JSON-RPC
protocol. Same analyzer, same `AnalysisResult` schema — now reachable on the
network with a verifiable identity and (optionally) pay-per-scan via x402.

## Why pair them?

ContractGuard is a great library, CLI, and Gradio app — but every integration
beyond that (Slack bot, VS Code extension, an orchestrator that chains it after
a "find me a lease" agent) ends up rebuilding the same plumbing: an HTTP
endpoint, an identity, an auth story, a way to charge for it.

[Bindu](https://github.com/getbindu/Bindu) is the plumbing. Wrap the analyzer
in one `bindufy(config, handler)` call and you get:

- **Discoverable agent card** at `/.well-known/agent.json` — agent
  marketplaces and orchestrators can find ContractGuard and know what it does.
- **DID-based identity** (`did:bindu:…`) — every analysis is attributable to a
  cryptographically-verifiable agent. Each result artifact is signed with the
  agent's Ed25519 key, so a contract review can be presented as
  tamper-evidence: "ContractGuard `did:bindu:…` said this at timestamp T."
- **A2A JSON-RPC** over HTTP — peers call `message/send` with either a `text`
  part (paste the contract) or a base64 `file` part (PDF / DOCX / TXT / MD /
  RTF), and get back the existing structured `AnalysisResult` as JSON.
- **Pay-per-scan via x402** — uncomment the `execution_cost` block in
  `agent.py` and the agent demands a USDC micropayment on Base before
  responding. No Stripe account, no login flow, no SaaS dashboard.
- **OAuth2 / mTLS** (optional) for B2B deployments.

The integration is purely additive: nothing in `contractguard/` changes,
`bindu` is not a required dependency, and the CLI / Python API / Gradio UI all
still work exactly as before.

## Setup

```bash
# From the ContractGuard repo root
pip install -e .            # core contractguard
pip install bindu           # adds the bindufy() wrapper

cp examples/bindu/.env.example .env
# edit .env: set OPENROUTER_API_KEY=sk-or-...
```

## Run

```bash
python examples/bindu/agent.py
```

You should see Bindu's startup banner and the agent listening on
<http://localhost:3773>. Three useful endpoints:

| Endpoint | What it is |
|---|---|
| `GET  /.well-known/agent.json` | Agent card — name, description, DID, skills, capabilities |
| `GET  /.well-known/did.json`   | DID document with the agent's public key |
| `POST /`                       | A2A JSON-RPC endpoint (use `method: "message/send"`) |

## Talk to it

### Inline text

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "kind": "message",
      "messageId": "00000000-0000-0000-0000-000000000001",
      "contextId": "00000000-0000-0000-0000-000000000002",
      "taskId":    "00000000-0000-0000-0000-000000000003",
      "parts": [
        { "kind": "text", "text": "review this contract" },
        { "kind": "text", "text": "<paste the full contract text here, multiple paragraphs OK>" }
      ]
    },
    "configuration": { "acceptedOutputModes": ["application/json"] }
  }
}
EOF
```

The first short `text` part is treated as a prompt and echoed back under
`prompt` in the result. Any subsequent text parts are concatenated and sent
through the analyzer.

### PDF / DOCX upload

A2A carries binary files as base64 inside a `file` part. One-liner to build
the payload from a real PDF:

```bash
B64=$(base64 -i my-lease.pdf | tr -d '\n')
cat > /tmp/req.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "kind": "message",
      "messageId": "00000000-0000-0000-0000-000000000001",
      "contextId": "00000000-0000-0000-0000-000000000002",
      "taskId":    "00000000-0000-0000-0000-000000000003",
      "parts": [
        { "kind": "text", "text": "review this lease" },
        { "kind": "file", "file": { "bytes": "$B64", "mimeType": "application/pdf" } }
      ]
    },
    "configuration": { "acceptedOutputModes": ["application/json"] }
  }
}
EOF

curl -sS http://localhost:3773/ -H "Content-Type: application/json" -d @/tmp/req.json
```

Supported `mimeType` values match the existing parser:

| MIME type | File type |
|---|---|
| `application/pdf` | PDF (parsed with `pdfplumber`) |
| `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | DOCX |
| `text/plain` | TXT |
| `text/markdown` | MD |
| `text/rtf` / `application/rtf` | RTF |

### Response shape

The handler returns the existing
[`AnalysisResult`](../../contractguard/models.py) serialised to JSON inside
the A2A response artifact. The full structure — `contract_type`, `summary`,
`parties`, `key_terms`, `red_flags[]`, `warnings[]`, `good_clauses[]`,
`missing_protections[]`, `fairness_score`, `fairness_grade` — is unchanged
from the CLI's `--json` output, so any code that already consumes
`contractguard scan --json` works without modification. The `prompt` field is
added when the caller supplied a leading prompt text part.

## Charging per scan (x402)

[x402](https://www.x402.org/) is an open micropayment protocol — Bindu speaks
it natively. Uncomment the `execution_cost` block in
[`agent.py`](agent.py) and fill in your wallet:

```python
"execution_cost": {
    "amount": "0.10",
    "token": "USDC",
    "network": "base-sepolia",
    "pay_to_address": "0xYOUR_ADDRESS_HERE",
},
```

The agent now responds with HTTP 402 to unauthenticated calls; the caller
attaches a USDC payment proof and the agent verifies + analyses. This is the
shortest path from "open-source CLI" to "monetised hosted service" without
adding a SaaS layer.

## Limits and notes

- **Not legal advice.** Same caveat as the upstream CLI — this is a first-pass
  filter, not a lawyer.
- **Contract length.** Inputs >120k chars are truncated (see
  `MAX_CONTRACT_CHARS` in `contractguard.analyzer`). For 60+ page contracts,
  pick a long-context model via `CONTRACTGUARD_MODEL=google/gemini-2.5-pro`.
- **Streaming** isn't enabled — analyses come back as a single artifact.
- **Auth defaults are off.** Suitable for localhost / trusted networks. For a
  public deployment set `AUTH__ENABLED=true` and follow Bindu's
  [`AUTH.md`](https://github.com/getbindu/Bindu/blob/main/docs/AUTH.md).
