# FragGate download tracker

Isolated Worker `fraggate-download-tracker`. Project `fraggate`.
v0.1.0 dual-surface UI for the FG-0.1 kernel. The Python kernel is unchanged.
**Not UI-only.** Buttons, OpenAPI, and MCP share List / Describe / Call / Verify.

Expected URL after deploy (workers.dev + account subdomain, same as sibling products):

`https://fraggate-download-tracker.vibelock.workers.dev`

- `GET /` — complete FragGate UI (wired list / describe / call / verify) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /v1/fraggate/*` — same four ops the buttons hit (proxy to `FRAGGATE_DOOR`)
- `GET /openapi.json` — documents those four ops
- `POST /mcp` — MCP tools `fraggate_list` / `fraggate_describe` / `fraggate_verify` / `fraggate_call`
- `GET /v1/health` · `/v1/skill` · `/v1/example` — do **not** increment downloads

KV binding `DOWNLOADS` (create `FRAGGATE_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`.

Canonical **agent path** remains aziel-runtime (configurable via `FRAGGATE_DOOR`):

- `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- `GET/POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/*`

This Worker **doubles** that door. It is not a second kernel.

## Button test matrix

Default door is live `https://aziel-runtime.vibelock.workers.dev`. Buttons call `/v1/fraggate/*` there.

| Button | Hits | Expected |
| --- | --- | --- |
| List registry | `GET {door}/v1/fraggate/list` | Hashed entries, registry digest, live/stub counts |
| LIVE ops | same list, show `live_ops` | Clickable `slug/op` chips fill the Call form |
| Describe | `GET {door}/v1/fraggate/describe?name=` | One catalog entry |
| Call op | `POST {door}/v1/fraggate/call` `{slug, op, payload}` | Result or typed refuse + ledger tip + DecisionGATE lineage |
| Verify | `POST {door}/v1/fraggate/verify` | `matched` + digest |
| OpenAPI | `/openapi.json` and catalog OpenAPI | Same four paths |
| MCP | `POST /mcp` and catalog `POST /mcp` | `fraggate_list`, `fraggate_describe`, `fraggate_verify`, `fraggate_call` |

Author: Aziel Eliab. Apache-2.0.
