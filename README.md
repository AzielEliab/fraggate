# FragGate

**FG-0.1 kernel against tool fragmentation and model hallucination.**

Author: **Aziel Eliab**
License: [Apache-2.0](LICENSE)
Version: 0.1.0
Magic: `FGT1`
Paper: [FG-WP-0.1](docs/FG-WP-0.1.md)
Spec: [FragGate v0 field tables](docs/FragGate_v0_spec.md)
Kernel homepage (runtime door): https://aziel-runtime.vibelock.workers.dev/
Human Worker UI: https://fraggate-download-tracker.vibelock.workers.dev/

Forks are welcome and always allowed.

## Dual surface

FragGate is the **door**. aziel-runtime hosts the public mesh. This repo is the local FG-0.1 kernel **and** the human Worker / counted download / Flutter scaffold. Not UI-only.

1. **Agent / MCP / OpenAPI** — discover, route, refuse through the door. Canonical agent path:
   - `POST https://aziel-runtime.vibelock.workers.dev/mcp`
   - `GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list`
   - `GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/describe?name=`
   - `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/verify`
   - `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
2. **Human software** — Worker homepage, `mobile/`, local install, counted `/download`. Buttons are wired to the **same four ops**.

This Worker (`fraggate-download-tracker`) **doubles** those ops (proxy, not a second kernel):

- UI: https://fraggate-download-tracker.vibelock.workers.dev/
- OpenAPI: https://fraggate-download-tracker.vibelock.workers.dev/openapi.json
- MCP: `POST https://fraggate-download-tracker.vibelock.workers.dev/mcp`
- Routes: `/v1/fraggate/list` · `/describe` · `/verify` · `/call`

The Python kernel is unchanged FG-0.1. Do not open a second kernel for the same session.

## Compatible AI clients

ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic Desktop / custom tools), Cursor (MCP), Glama (Install Server / MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex AI, Mistral, Meta AI, Apple Intelligence / Applebot surfaces, Amazon Q / Amazonbot tooling, DuckAssist / DuckDuckGo AI, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.

Import catalog OpenAPI as a GPT Action / custom HTTP tool, or `POST` the catalog MCP. Always send `User-Agent: Mozilla/5.0`.

## What it is

A **kernel**, not a toolkit. Tools attach only through registration.

```
operator intent → CallEnvelope → Registry.require(tool) → Schema check
  → DecisionGATE → handler (or dry-run) → Claim.validate
  → ResultEnvelope → Ledger.append
```

v0.1 door tools: `runtime.ping`, `registry.list`, `registry.verify`, `claim.check`, `runtime.receipt`. Everything else binds with `bind_adapter`.

## What it is not

- Not another Lock product. GodLock, TemporalLock, DecisionGATE, and the rest stay products. They may attach as adapters.
- Not a chatbot personality and not a second identity.
- Not a network relay or public chat surface.
- Not a second kernel. The Worker proxies the public door; local FG-0.1 stays local.
- Not a rewrite of the Locks.
- Not a DOI mint.

Public identity is **Aziel Eliab** only. GodLock is a product name, not an author.

## Relation to aziel-runtime

**FragGate is the door. aziel-runtime hosts the public mesh.**

- This repo is the local kernel: envelopes, hashed registry, DecisionGATE stub, claim rules, JSONL ledger.
- [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) (`https://aziel-runtime.vibelock.workers.dev/`) is the catalog + session + in-process engines.
- A Lock should not remain a private runtime. It binds here. The runtime remains the public host.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Stdlib runtime. pytest is the dev extra.

One-click (counted) from the Worker:

```bash
curl -fsSL https://fraggate-download-tracker.vibelock.workers.dev/install.sh | bash
```

## Quickstart

```bash
python -m fraggate ping
python -m fraggate list
python -m fraggate verify runtime.ping
python -m fraggate call runtime.ping
python -m fraggate receipt "operator asserts the kernel is local"
```

Same verbs exist as the `fraggate` entrypoint. Each command builds a CallEnvelope, runs the pipeline, appends the ledger at `./.fraggate/ledger.jsonl`, and prints a ResultEnvelope.

```python
from fraggate import FragGate, ToolSpec

kernel = FragGate(session_id="demo", operator="Aziel Eliab", ledger_path="tmp/ledger.jsonl")
print(kernel.call(kernel.envelope("runtime.ping", intent="Ping the kernel for liveness.")).result)
kernel.close()
```

## Button test matrix

Human UI: https://fraggate-download-tracker.vibelock.workers.dev/

| Button | Hits | Expected |
| --- | --- | --- |
| List registry | `GET /v1/fraggate/list` | Hashed entries, registry digest, live/stub counts |
| LIVE ops | same list, show `live_ops` | Clickable `slug/op` chips fill the Call form |
| Describe | `GET /v1/fraggate/describe?name=` | One catalog entry |
| Call op | `POST /v1/fraggate/call` `{slug, op, payload}` | Result or typed refuse + ledger tip + DecisionGATE lineage |
| Verify | `POST /v1/fraggate/verify` | `matched` + digest |
| OpenAPI | `/openapi.json` and catalog OpenAPI | Same four paths |
| MCP | `POST /mcp` and catalog `POST /mcp` | `fraggate_list`, `fraggate_describe`, `fraggate_verify`, `fraggate_call` |

Blank door field uses this Worker (the OpenAPI/MCP double). Catalog door uses `https://aziel-runtime.vibelock.workers.dev`. Both are the same four FragGate ops.

Curl the doubles (Mozilla/5.0):

```bash
HOST=https://fraggate-download-tracker.vibelock.workers.dev
curl -sS -A 'Mozilla/5.0' "$HOST/v1/fraggate/list"
curl -sS -A 'Mozilla/5.0' "$HOST/v1/fraggate/describe?name=decisiongate"
curl -sS -A 'Mozilla/5.0' -X POST "$HOST/v1/fraggate/verify" -H 'content-type: application/json' -d '{"slug":"decisiongate"}'
curl -sS -A 'Mozilla/5.0' -X POST "$HOST/v1/fraggate/call" -H 'content-type: application/json' -d '{"slug":"decisiongate","op":"health","payload":{}}'
curl -sS -A 'Mozilla/5.0' -X POST "$HOST/mcp" -H 'content-type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Unknown names are `FG-HALLUC-TOOL`. Schema drift is `FG-FRAG-SCHEMA`. Ungrounded facts are `FG-HALLUC-FACT`. Invented artifacts are `FG-HALLUC-ARTIFACT`. DecisionGATE refuse is `FG-GATE`. Every call, including refuse, appends the ledger.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Offline. No network.

## Cite

Eliab, Aziel. (2026). FragGate FG-0.1 [Software]. Apache-2.0. https://github.com/AzielEliab/fraggate

Runtime door: https://aziel-runtime.vibelock.workers.dev/
Human Worker: https://fraggate-download-tracker.vibelock.workers.dev/
