---
name: FragGate
description: >-
  Use when an agent would invent a tool, skip a registry, or assert an
  ungrounded fact. Dual surface: human Worker UI + agent MCP/OpenAPI over
  the same List/Describe/Call/Verify door. Local FG-0.1 kernel.
  Author Aziel Eliab.
---

# FragGate

Kernel against tool fragmentation and model hallucination. **Not** a Lock.
**Not** a chatbot personality. **Not** UI-only.

Author: **Aziel Eliab**. Version: 0.1.0. Magic: `FGT1`. Paper: FG-WP-0.1.
License: Apache-2.0.

**THIS IS:** a local FG-0.1 kernel plus a dual-surface product door. Tools exist
only in a hashed registry. Execution is CallEnvelope only. Assertion is
ResultEnvelope only. Every call appends a JSONL ledger.

**THIS IS NOT:** another Lock, a public chat personality, a network relay, a
second identity, or a second kernel. The Worker UI does not invent ops the
agent cannot call.

aziel-runtime hosts the public mesh. **FragGate is the door.** Do not credit
GodLock.AZ, Horton, or OpenAI as author.

## Dual-surface law

1. **Agent / MCP / OpenAPI** — Software runs through the door. Show
   `display.title`, `display.summary`, and typed refuse codes. Session ids and
   HTTP stay invisible unless the user asked for them.
2. **Human software** — Worker homepage, Flutter `mobile/`, local install, and
   counted `/download` stay complete developed software. Buttons are wired to
   the same four ops.

Canonical **agent path** (aziel-runtime):

- `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- `GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list`
- `GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/describe?name=`
- `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/verify`
- `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`

This Worker **doubles** those four ops (proxy, not a second kernel):

- Human UI: https://fraggate-download-tracker.vibelock.workers.dev/
- OpenAPI: https://fraggate-download-tracker.vibelock.workers.dev/openapi.json
- MCP: `POST https://fraggate-download-tracker.vibelock.workers.dev/mcp`
- Same routes: `/v1/fraggate/list` · `/describe` · `/verify` · `/call`

MCP tools that map 1:1 to the human buttons: `fraggate_list`,
`fraggate_describe`, `fraggate_verify`, `fraggate_call` (+ `runtime_skill`).

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Compatible AI clients

ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic Desktop /
custom tools), Cursor (MCP), Glama (Install Server / MCP), Perplexity,
Microsoft Copilot / Bing, Google Gemini / Vertex AI, Mistral, Meta AI, Apple
Intelligence / Applebot surfaces, Amazon Q / Amazonbot tooling, DuckAssist /
DuckDuckGo AI, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.

Practical pull + call:

- **ChatGPT** — GPT Actions → Import from URL →
  `https://aziel-runtime.vibelock.workers.dev/openapi.json`
- **Grok** — custom tool / OpenAPI / MCP remote → catalog OpenAPI or
  `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- **Venice** — custom HTTP tools / OpenAPI → same
- **Claude Desktop / Cursor / Glama** — MCP remote
  `POST https://aziel-runtime.vibelock.workers.dev/mcp`

## How an agent uses it

1. **Discover.** `runtime_skill` or `fraggate_list`. `fraggate_describe` one name.
   `fraggate_verify` a name or digest.
2. **Route.** `fraggate_call` with `{ name|slug, op, payload, claim? }`.
   DecisionGATE runs before exec.
3. **Refuse.** Unknown names return `FG-HALLUC-TOOL`. Stubs and `local_only` do
   not execute. Gate BLOCK/REVISE is ledgered.
4. **Show the output.** Results are `{ display, result, ledger_tip? }`. Show
   refuse codes clearly. Do not soften them.

Do **not** invent flat `{slug}_{op}` tool names. They are not the door.

## Local kernel

```bash
pip install -e ".[dev]"
python -m fraggate ping
python -m fraggate list
python -m fraggate verify NAME
python -m fraggate call TOOL --args '{}'
```

```python
from fraggate import FragGate
k = FragGate(session_id="s", operator="operator", ledger_path="tmp/ledger.jsonl")
k.call(k.envelope("runtime.ping", intent="Ping FragGate for liveness."))
k.close()
```

Builtins only: `runtime.ping`, `registry.list`, `registry.verify`, `claim.check`,
`runtime.receipt`. Bind anything else with `bind_adapter`.

## Refuse codes (do not soften)

| Code | When |
| --- | --- |
| `FG-HALLUC-TOOL` | Name not in the registry |
| `FG-HALLUC-FACT` | Fact without GroundingRef, or search without `allow_search` |
| `FG-HALLUC-ARTIFACT` | Invented artifact (error, not a draft) |
| `FG-FRAG-SCHEMA` | Args drifted, or silent spec mutation |
| `FG-FRAG-ORPHAN` | Name/handler/digest disagree |
| `FG-GATE` | DecisionGATE refuse; same `call_id` cannot retry friendlier |
| `FG-EXPORT` | Export without `allow_export` |
| `FG-ERR` | Bad envelope or kernel fault |
| `FG-STUB` | Hosted door: stub op, not live |
| `FG-UNKNOWN-OP` | Hosted door: name live, op missing or not allowlisted |

Do not invent tools, facts, artifacts, outcomes, or DOIs. Do not open a second
kernel for the same session.
