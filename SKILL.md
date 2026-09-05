---
name: FragGate
description: >-
  Use when an agent would invent a tool, skip a registry, or assert an ungrounded
  fact. Local FG-0.1 kernel. Author Aziel Eliab.
---

# FragGate

Kernel against tool fragmentation and model hallucination. **Not** a Lock. **Not** a chatbot personality.

Author: **Aziel Eliab**. Version: 0.1.0. Magic: `FGT1`. Paper: FG-WP-0.1.
License: Apache-2.0. Homepage (runtime door): https://aziel-runtime.vibelock.workers.dev/

**THIS IS:** a local kernel. Tools exist only in a hashed registry. Execution is CallEnvelope only. Assertion is ResultEnvelope only. Every call appends a JSONL ledger.

**THIS IS NOT:** another Lock, a public chat surface, a network relay, a second identity, or a counted download.

aziel-runtime hosts the public mesh. FragGate is the door. Do not credit GodLock.AZ, Horton, or OpenAI as author.

## How to use it

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

Builtins only: `runtime.ping`, `registry.list`, `registry.verify`, `claim.check`, `runtime.receipt`. Bind anything else with `bind_adapter`.

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

Do not invent tools, facts, artifacts, outcomes, or DOIs. Do not open a second kernel for the same session.
