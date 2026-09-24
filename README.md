# FragGate

FragGate verifies kernels in the background. Suite and agents call this door. Each call is written to a local ledger.

**Author:** Aziel Eliab
**License:** [Apache-2.0](LICENSE)
**Version:** 0.1.0 · Magic `FGT1` · Paper [FG-WP-0.1](docs/FG-WP-0.1.md)

## Start

1. Install:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

2. Read the welcome:

```bash
fraggate
```

3. Ask whether this kernel is alive:

```bash
fraggate ping
```

`fraggate` and `python -m fraggate` are the same command. `fraggate doctor` prints a plain pass or fail. `fraggate service` listens on this computer and reports Running. `fraggate service status` reports Running or Quiet. Add `--json` for the ResultEnvelope.

## Diagnostics

`fraggate ui` is the same listener as `fraggate service`. On that page, Check kernel sits under Advanced. GET does not call the kernel.

```bash
fraggate list
fraggate verify runtime.ping
fraggate receipt "kernel is local"
fraggate --help
```

`fraggate call` runs any registered tool. Flags for arguments, dry-run, export, search, and destructive calls are under `fraggate call --help`.

```python
from fraggate import FragGate, ToolSpec

kernel = FragGate(session_id="demo", operator="Aziel Eliab", ledger_path="tmp/ledger.jsonl")
print(kernel.call(kernel.envelope("runtime.ping", intent="Ping the kernel for liveness.")).result)
kernel.close()
```

Each call appends `ledger.jsonl` under the home directory (default `./.fraggate`).

## Reference

**FragGate is the single door (FG-0.1).** Host: [Aziel Runtime](https://github.com/AzielEliab/aziel-runtime) **2.0.0-rc1**.

Spec: [FragGate v0 field tables](docs/FragGate_v0_spec.md)
Kernel homepage: https://aziel-runtime.vibelock.workers.dev/
Human Worker UI: https://fraggate-download-tracker.vibelock.workers.dev/

Forks are welcome and always allowed.

## Official Aziel ecosystem

| Surface | URL |
|---------|-----|
| Official site (Person `@id`) | https://www.azieleliab.com/ — [`#aziel`](https://www.azieleliab.com/#aziel) |
| Runtime hub (`@id` `#runtime`) | https://www.azieleliab.com/runtime#runtime |
| Aziel Corpus Library | https://www.azielcorpuslibrary.net/ |
| GodLock.uk | https://godlock.uk/ |
| Aziel Runtime (host, **2.0.0-rc1**) | https://github.com/AzielEliab/aziel-runtime |
| **Try on Glama** (primary MCP) | https://glama.ai/mcp/servers/AzielEliab/aziel-runtime |
| Runtime Worker (secondary) | https://aziel-runtime.vibelock.workers.dev/ |
| Human Worker UI (this repo) | https://fraggate-download-tracker.vibelock.workers.dev/ |

**[Try on Glama](https://glama.ai/mcp/servers/AzielEliab/aziel-runtime)** is the primary Install Server / MCP distribution door. The Worker origin stays the execution / OpenAPI surface (secondary). GitHub About lock: [docs/github-seo.md](docs/github-seo.md).

## Dual surface

FragGate is the **door**. aziel-runtime hosts the public mesh. This repository is the local FG-0.1 kernel, the human Worker, the counted download, and the Flutter scaffold.

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
- Suite mesh PROXY: `/v1/mesh/*` via `AZIEL_RUNTIME` / `https://aziel-runtime.vibelock.workers.dev`. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (local qnsd in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog field in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair custody in [AZInterface](https://github.com/AzielEliab/azinterface)). Not a Softwares-tab product. No public qnsd proxy. No Node Gate. Catalog MCP `mesh_*` + FragGate `slug=mesh`.

The Python kernel is FG-0.1. One kernel stays open per session.

## Compatible AI clients

ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic Desktop / custom tools), Cursor (MCP), Glama (Install Server / MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex AI, Mistral, Meta AI, Apple Intelligence / Applebot surfaces, Amazon Q / Amazonbot tooling, DuckAssist / DuckDuckGo AI, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.

Import catalog OpenAPI as a GPT Action / custom HTTP tool, or `POST` the catalog MCP. Always send `User-Agent: Mozilla/5.0`.

## Kernel

Tools attach through registration.

```
operator intent → CallEnvelope → Registry.require(tool) → Schema check
  → DecisionGATE → handler (or dry-run) → Claim.validate
  → ResultEnvelope → Ledger.append
```

v0.1 door tools: `runtime.ping`, `registry.list`, `registry.verify`, `claim.check`, `runtime.receipt`. Other tools bind with `bind_adapter`.

## Notes

Public identity is **Aziel Eliab**. Aziel Elroi Eliab (Elroi) is an alternate name. GodLock is a product name.

This repository is the local FG-0.1 kernel: envelopes, a hashed registry, a DecisionGATE check, claim rules, and a JSONL ledger. Lock products stay their own products and may attach with `bind_adapter`. One kernel stays open per session. The Worker proxies the public door; the local kernel stays on this computer. Aziel Runtime hosts the public mesh. This kernel does not mint DOIs.

## Relation to aziel-runtime

**FragGate is THE single door (FG-0.1). Aziel Runtime 2.0.0-rc1 hosts the public mesh.**

- This repo is the local kernel: envelopes, hashed registry, DecisionGATE stub, claim rules, JSONL ledger.
- [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) **2.0.0-rc1** (`https://aziel-runtime.vibelock.workers.dev/`) is the catalog + session + in-process engines.
- Primary MCP install: **[Try on Glama](https://glama.ai/mcp/servers/AzielEliab/aziel-runtime)**. Worker origin is secondary.
- A Lock should not remain a private runtime. It binds here. The runtime remains the public host.

## Counted install

```bash
curl -fsSL https://fraggate-download-tracker.vibelock.workers.dev/install.sh | bash
fraggate ping
```

Stdlib runtime. pytest is the dev extra: `pip install -e ".[dev]"`.

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
| MCP | `POST /mcp` and catalog `POST /mcp` | `fraggate_list`, `fraggate_describe`, `fraggate_verify`, `fraggate_call`. Mesh pointer: catalog `mesh_*` + FragGate `slug=mesh` |
| Live Nodes | `GET /v1/mesh` PROXY | Default OFF. QNM live\|locked\|isolated. QNS-CD-1.0 cross-map (photon QNS1; no qnsd proxy). GET never enables. No Node Gate |

Default door in the UI is **this Worker**. Buttons call same-origin `/v1/fraggate/*`, which proxies to `https://aziel-runtime.vibelock.workers.dev` (service binding `AZIEL_RUNTIME`, then public URL). Origin methods: **GET** list/describe, **POST** verify/call. Suite mesh `/v1/mesh/*` PROXY (default OFF). “Catalog door” talks to aziel-runtime directly. Not AZBrowser. Not a Node Gate.

Curl the **Worker double the buttons hit** (Mozilla/5.0):

```bash
HOST=https://fraggate-download-tracker.vibelock.workers.dev
curl -sS -A 'Mozilla/5.0' "$HOST/v1/fraggate/list"
curl -sS -A 'Mozilla/5.0' "$HOST/v1/fraggate/describe?name=decisiongate"
curl -sS -A 'Mozilla/5.0' -X POST "$HOST/v1/fraggate/verify" -H 'content-type: application/json' -d '{"slug":"decisiongate"}'
curl -sS -A 'Mozilla/5.0' -X POST "$HOST/v1/fraggate/call" -H 'content-type: application/json' -d '{"slug":"azbrowser","op":"ethical_search","payload":{"q":"x"}}'
curl -sS -A 'Mozilla/5.0' "$HOST/v1/mesh"
```

Same paths on the catalog door (`https://aziel-runtime.vibelock.workers.dev`). Offline check: `node workers/download-tracker/scripts/verify-door-proxy.mjs`.

Unknown names are `FG-HALLUC-TOOL`. Schema drift is `FG-FRAG-SCHEMA`. Ungrounded facts are `FG-HALLUC-FACT`. Invented artifacts are `FG-HALLUC-ARTIFACT`. DecisionGATE refuse is `FG-GATE`. Every call, including refuse, appends the ledger.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Offline. No network.

## Cite

Eliab, Aziel. (2026). FragGate FG-0.1 [Software]. Apache-2.0. https://github.com/AzielEliab/fraggate

Host: Aziel Runtime 2.0.0-rc1 — https://github.com/AzielEliab/aziel-runtime
Person `@id`: https://www.azieleliab.com/#aziel
Runtime `@id`: https://www.azieleliab.com/runtime#runtime
Try on Glama (primary MCP): https://glama.ai/mcp/servers/AzielEliab/aziel-runtime
Runtime door (secondary): https://aziel-runtime.vibelock.workers.dev/
Human Worker: https://fraggate-download-tracker.vibelock.workers.dev/
