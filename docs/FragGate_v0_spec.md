# FragGate v0 field spec (FG-0.1)

Normative types for the FG-0.1 kernel. Paper: [FG-WP-0.1](FG-WP-0.1.md). Magic `FGT1`. Version `0.1.0`. Author: Aziel Eliab. Suite designs (not kernel types): [docs/designs/](designs/README.md) — [SEC-FEAT-1.0](designs/SEC-FEAT-1.0.md), [AZL-WP-1.1](designs/AZL-WP-1.1.md), [AZL-VOL-1.0](designs/AZL-VOL-1.0.md).

Canonical encoding: UTF-8 JSON, `sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`. Hashes are SHA-256 lowercase hex of those bytes.

## CallEnvelope

Only legal execution input. Rule 1.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `magic` | string | yes | Must be `FGT1` |
| `version` | string | yes | `0.1.x` |
| `paper` | string | no | `FG-WP-0.1` (emitted on `to_dict`) |
| `call_id` | string | yes | UUID; reused after a gate refuse is still a refuse |
| `session_id` | string | yes | Must match the kernel session |
| `operator` | string | yes | Blank → DecisionGATE `FG-GATE` (Responsibility) |
| `intent` | string | yes | Blank → DecisionGATE `FG-GATE` (Definition) |
| `tool` | string | yes | Registered name |
| `args` | object | yes | Must satisfy `ToolSpec.input_schema` |
| `dry_run` | bool | no | Default false. Handler is not invoked |
| `allow_export` | bool | no | Default false. Required if spec.export |
| `allow_search` | bool | no | Default false. Required for `kind=search` |
| `destructive` | bool | no | Default false. Required if spec.destructive |
| `grounding` | GroundingRef[] | no | Call-level locators |
| `claims` | Claim[] | no | Validated if present |
| `ts` | string | yes | UTC ISO-8601, `Z` |

## ResultEnvelope

Only legal assertion output. Rule 2. Produced by the kernel, never by a handler.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `magic` | string | yes | `FGT1` |
| `version` | string | yes | `0.1.0` |
| `paper` | string | yes | `FG-WP-0.1` |
| `call_id` | string | yes | Echo of the call |
| `session_id` | string | yes | Echo of the session |
| `tool` | string | yes | Echo of the tool (may be empty if envelope never parsed) |
| `status` | string | yes | `ok` or `refuse` |
| `result` | object | yes | Handler payload on success; empty on refuse |
| `error_code` | string \| null | yes | One of the FG-* codes on refuse |
| `error_message` | string \| null | yes | Typed refuse text |
| `details` | object | yes | Gate report, schema errors, etc. |
| `claims` | Claim[] | yes | Validated claims |
| `grounding` | GroundingRef[] | yes | At least registry + operator on success; receipt after ledger |
| `artifacts` | Artifact[] | yes | Invented artifacts refuse the call |
| `gate` | object \| null | yes | DecisionGATE lineage |
| `ledger_hash` | string \| null | yes | Hash of the mandatory append |
| `registry_digest` | string \| null | yes | Digest at call time |
| `dry_run` | bool | yes | Echo |
| `ts` | string | yes | UTC ISO-8601, `Z` |

## ToolSpec

Hashed with canonical JSON of the identity fields. The hash is the tool.

| Field | Type | Required | In hash | Notes |
| --- | --- | --- | --- | --- |
| `name` | string | yes | yes | Unique in the registry |
| `version` | string | yes | yes | Adapter or builtin version |
| `description` | string | yes | yes | What the tool does |
| `input_schema` | object | yes | yes | JSON Schema subset |
| `output_schema` | object \| null | no | yes | Optional |
| `destructive` | bool | no | yes | Default false |
| `export` | bool | no | yes | Default false; needs `allow_export` |
| `adapter` | string \| null | no | yes | `null` for builtins |
| `spec_hash` | string | emitted | no | SHA-256 of identity fields |

**Registry digest** = SHA-256 of canonical `{name: spec_hash}` sorted by name.

Builtins (`adapter=null`): `runtime.ping`, `registry.list`, `registry.verify`, `claim.check`, `runtime.receipt`.

## GroundingRef

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `kind` | string | yes | One of: `registry`, `project_map`, `receipt`, `file`, `operator`, `search`, `memory`, `schema` |
| `ref` | string | yes | Locator (digest, path, name, URL, id) |
| `digest` | string \| null | no | Optional content hash |
| `note` | string | no | Human hint; not a fact |

`kind=search` is invalid unless the CallEnvelope has `allow_search=true`.

## Claim

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `statement` | string | yes | What is being asserted |
| `facts` | Fact[] | no | Each Fact requires ≥1 GroundingRef |
| `artifacts` | Artifact[] | no | See Artifact |
| `grounding` | GroundingRef[] | no | Claim-level locators; required if `facts` is empty |

### Fact

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `text` | string | yes | The fact |
| `grounding` | GroundingRef[] | yes | Length ≥ 1 |

### Artifact

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Local name |
| `kind` | string | yes | `file`, `receipt`, `export`, … |
| `digest` | string \| null | no | Required unless `ref` is set |
| `ref` | string \| null | no | Required unless `digest` is set |
| `invented` | bool | no | If true → `FG-HALLUC-ARTIFACT` |

An artifact with neither `digest` nor `ref` is invented. Invented artifacts are errors, not drafts.

## DecisionGATE report

| Field | Type | Notes |
| --- | --- | --- |
| `lineage` | `{name, state, feedback}[]` | Definition → Evidence → Impact → Integrity → Responsibility |
| `final_state` | string | `PASS`, `REVISE`, or `BLOCK` |
| `blocked_at` | string \| null | First failing gate |

`REVISE` and `BLOCK` both refuse the call as `FG-GATE`. The same `call_id` cannot later pass.

## Ledger record

Local JSONL, previous-hash chained. TemporalLock-shaped, not a product fork.

| Field | Type | Notes |
| --- | --- | --- |
| `magic` | string | `FGT1` |
| `version` | string | `0.1.0` |
| `paper` | string | `FG-WP-0.1` |
| `seq` | integer | 1-based |
| `prev_hash` | string | Genesis is 64 zero hex chars |
| `hash` | string | SHA-256 of the record without `hash` |
| `ts` | string | UTC |
| `call_id` | string | |
| `session_id` | string | |
| `tool` | string | |
| `status` | string | `ok` or `refuse` |
| `error_code` | string \| null | |
| `registry_digest` | string | Digest at append time |
| `payload_digest` | string | Canonical hash of the ResultEnvelope |

Append is mandatory on success and on refuse.

## Pipeline order

1. Parse CallEnvelope (`FG-ERR` if magic/session/tool missing).
2. `Registry.require(tool)` → `FG-HALLUC-TOOL` or `FG-FRAG-ORPHAN` / silent digest `FG-FRAG-SCHEMA`.
3. Schema check → `FG-FRAG-SCHEMA`.
4. DecisionGATE → `FG-GATE`.
5. Export flag → `FG-EXPORT`.
6. Handler or dry-run.
7. `Claim.validate` → `FG-HALLUC-FACT` / `FG-HALLUC-ARTIFACT`.
8. ResultEnvelope.
9. Ledger.append (always).
