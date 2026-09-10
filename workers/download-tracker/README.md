# FragGate download tracker

Isolated Worker `fraggate-download-tracker`. Project `fraggate`.
v0.1.0 dual-surface UI for the FG-0.1 kernel. The Python kernel is unchanged.
**Not UI-only.** Buttons, OpenAPI, and MCP share List / Describe / Call / Verify.

Expected URL after deploy (workers.dev + account subdomain, same as sibling products):

`https://fraggate-download-tracker.vibelock.workers.dev`

- `GET /` — complete FragGate UI (wired list / describe / call / verify) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /v1/fraggate/list` · `GET /v1/fraggate/describe` — proxy to `FRAGGATE_DOOR` / `AZIEL_RUNTIME` (service binding first)
- `POST /v1/fraggate/verify` · `POST /v1/fraggate/call` — same door, JSON body
- `GET /v1/mesh` · `GET /v1/mesh/nodes` · `POST /v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` — suite mesh PROXY via `AZIEL_RUNTIME`. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (local qnsd in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime)). Not a Softwares-tab product. No public qnsd proxy. No Node Gate
- `GET /openapi.json` — documents those four ops plus the mesh pointer
- `POST /mcp` — MCP tools `fraggate_list` / `fraggate_describe` / `fraggate_verify` / `fraggate_call` (mesh pointer: catalog `mesh_*` + FragGate `slug=mesh`)
- `GET /v1/health` · `/v1/skill` · `/v1/example` — do **not** increment downloads

KV binding `DOWNLOADS` (create `FRAGGATE_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`.

Canonical **agent path** remains aziel-runtime (configurable via `FRAGGATE_DOOR`):

- `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- `GET/POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/*`

This Worker **doubles** that door. It is not a second kernel.

## Button test matrix

Default door is **this Worker**. Buttons call same-origin `/v1/fraggate/*`, which forwards to `https://aziel-runtime.vibelock.workers.dev` via the `AZIEL_RUNTIME` service binding (public URL fallback). Origin methods: **GET** `/v1/fraggate/list` and `/describe`; **POST** `/v1/fraggate/verify` and `/call`. Suite mesh `/v1/mesh/*` PROXY (default OFF). Not AZBrowser. Not a Node Gate.

| Button | Hits | Expected |
| --- | --- | --- |
| List registry | `GET {door}/v1/fraggate/list` | Hashed entries, registry digest, live/stub counts |
| LIVE ops | same list, show `live_ops` | Clickable `slug/op` chips fill the Call form |
| Describe | `GET {door}/v1/fraggate/describe?name=` | One catalog entry |
| Call op | `POST {door}/v1/fraggate/call` `{slug, op, payload}` | Result or typed refuse + ledger tip + DecisionGATE lineage |
| Verify | `POST {door}/v1/fraggate/verify` | `matched` + digest |
| OpenAPI | `/openapi.json` and catalog OpenAPI | Same four paths |
| MCP | `POST /mcp` and catalog `POST /mcp` | `fraggate_list`, `fraggate_describe`, `fraggate_verify`, `fraggate_call`. Mesh pointer: catalog `mesh_*` + FragGate `slug=mesh` |
| Live Nodes | `GET /v1/mesh` PROXY | Default OFF. QNM-BUILD-1.0 live\|locked\|isolated. QNS-CD-1.0 cross-map (photon QNS1; no qnsd proxy). No Node Gate. No auto-heal |

Author: Aziel Eliab. Apache-2.0.
