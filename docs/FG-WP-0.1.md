# FragGate Whitepaper FG-WP-0.1

**Kernel against tool fragmentation and model hallucination**

- Paper: FG-WP-0.1
- Software: FragGate FG-0.1
- Version: 0.1.0
- Magic: FGT1
- Author: Aziel Eliab
- License: Apache-2.0
- Homepage (runtime door): https://aziel-runtime.vibelock.workers.dev/
- Human Worker UI: https://fraggate-download-tracker.vibelock.workers.dev/
- Repository: https://github.com/AzielEliab/fraggate
- Suite designs: [docs/designs/](designs/README.md) — [SEC-FEAT-1.0](designs/SEC-FEAT-1.0.md), [AZL-WP-1.1](designs/AZL-WP-1.1.md), [AZL-VOL-1.0](designs/AZL-VOL-1.0.md)

Historical note: an earlier draft of this paper used the dual credit line “Aziel / GodLock.AZ”. Public credit is **Aziel Eliab** only. GodLock is a product name in the Aziel Eliab catalog, not an author and not this kernel.

This paper does not invent a DOI.

## 1. What this is

FragGate is a **kernel**, not a toolkit and not a chatbot personality. Tools do not exist until they are registered. Facts do not exist until they are grounded. Artifacts that were not produced are errors, not drafts.

The public mesh of Aziel Eliab software is hosted by **aziel-runtime**. FragGate is the door those tools are meant to walk through: one hashed registry, one envelope pair, one ledger, one DecisionGATE check before a handler runs.

FragGate is not another Lock. Locks remain products. They attach with `bind_adapter`. They do not each remain a private runtime.

## 2. Dual failure mode

Two failures feed each other.

**Fragmentation.** Tools multiply without a hashed registry. Schemas drift. Handlers outlive names, or names outlive handlers. Orphans accumulate. Each new surface invents its own call shape.

**Hallucination.** A model invents a tool that was never bound, a fact that has no GroundingRef, an artifact that was never written, or an outcome that was never ledged. Fragmentation makes hallucination cheap: if anything can be a tool, anything can be claimed.

The kernel treats both as typed refuses, not as style problems.

## 3. Pipeline

```
operator intent
  → CallEnvelope
  → Registry.require(tool)
  → Schema check
  → DecisionGATE
  → handler (or dry-run)
  → Claim.validate
  → ResultEnvelope
  → Ledger.append
```

There is no other execution path. Convenience CLI verbs (`ping`, `list`, `verify`, `call`) build a CallEnvelope and enter this pipeline.

## 4. Built-in tools (v0.1 door)

| Name | Purpose |
| --- | --- |
| `runtime.ping` | Liveness, version, ledger tip, registry digest |
| `registry.list` | Bound tools |
| `registry.verify` | Is this name real |
| `claim.check` | Accept or refuse a claim bundle |
| `runtime.receipt` | Operator assertion → hash |

Everything else binds via `bind_adapter`.

## 5. Ten rules

1. No execution outside CallEnvelope.
2. No assertion outside ResultEnvelope.
3. No tool outside the hashed registry.
4. No fact without ≥1 GroundingRef.
5. No silent digest change.
6. No export side effect without `allow_export`.
7. No search grounding without `allow_search`.
8. No second kernel for the same operator session.
9. Ledger append is mandatory per call (success or refuse).
10. Invented artifacts are errors, not drafts.

## 6. Error codes

| Code | Meaning |
| --- | --- |
| `FG-HALLUC-TOOL` | Name is not in the hashed registry |
| `FG-HALLUC-FACT` | Fact or claim lacks valid grounding |
| `FG-HALLUC-ARTIFACT` | Artifact was invented (no digest/ref, or marked invented) |
| `FG-FRAG-SCHEMA` | Args drifted from ToolSpec, or silent spec mutation |
| `FG-FRAG-ORPHAN` | Name and handler/digest no longer agree |
| `FG-GATE` | DecisionGATE refuse (typed; no friendlier reread of the same `call_id`) |
| `FG-EXPORT` | Export side effect without `allow_export` |
| `FG-ERR` | Malformed envelope or kernel fault |

## 7. Grounding kinds

`registry`, `project_map`, `receipt`, `file`, `operator`, `search` (only if `allow_search`), `memory`, `schema`.

Search is not a default oracle. Memory is not a second kernel.

## 8. DecisionGATE (pre-exec, not sermon)

Five sequential gates, reused as a kernel stub — not a product fork of DecisionGATE:

1. **Definition** — intent must exist.
2. **Evidence** — builtins are grounded by the registry; destructive adapters need grounding or a claim.
3. **Impact** — destructive requires `CallEnvelope.destructive=true`.
4. **Integrity** — spec and envelope align; a refused `call_id` cannot pass on a friendlier reading.
5. **Responsibility** — one named operator.

Refuse is typed `FG-GATE`. Export is `FG-EXPORT`, not a lecture.

## 9. Ledger

Local JSONL. Previous-hash chained. Genesis `prev_hash` is 64 zero hex characters. Encoding is canonical JSON + SHA-256. The shape follows TemporalLock (hash-chained receipts anyone can verify). FragGate does not fork TemporalLock as a product; it keeps a ledger because a kernel without memory of refuses will hallucinate success.

## 10. Adapters

`bind_adapter(adapter_id, tools, handler)` is the only way a Lock or foreign tool enters the kernel. The registry digest changes in the open. A silent mutation of a bound ToolSpec is `FG-FRAG-SCHEMA`.

aziel-runtime remains the public mesh: catalog, pull, session, in-process engines. FragGate is the local door those engines should present to an operator session.

## 11. What this is not

- Not a chatbot personality.
- Not a second identity.
- Not a network relay or public chat surface.
- Not a second kernel. FG-0.1 stays local. A counted Worker UI may host the same tarball and **double** List / Describe / Call / Verify over the public door (OpenAPI + MCP). That surface is not UI-only and does not replace CallEnvelope.
- Not a rewrite of the Locks.
- Not legal advice, not a court, not a truth score.

## 12. Suite designs

Related suite papers (not this kernel paper) live in [docs/designs/](designs/README.md): [SEC-FEAT-1.0](designs/SEC-FEAT-1.0.md), [AZL-WP-1.1](designs/AZL-WP-1.1.md), [AZL-VOL-1.0](designs/AZL-VOL-1.0.md). Author: Aziel Eliab only. `GET /v1/mesh` never enables.

## 13. Cite

Eliab, Aziel. (2026). FragGate FG-0.1 (FG-WP-0.1) [Software]. Apache-2.0. https://github.com/AzielEliab/fraggate

Runtime door: https://aziel-runtime.vibelock.workers.dev/

Forks are welcome and always allowed.
