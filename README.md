# FragGate

**FG-0.1 kernel against tool fragmentation and model hallucination.**

Author: **Aziel Eliab**
License: [Apache-2.0](LICENSE)
Version: 0.1.0
Magic: `FGT1`
Paper: [FG-WP-0.1](docs/FG-WP-0.1.md)
Spec: [FragGate v0 field tables](docs/FragGate_v0_spec.md)
Homepage (runtime door): https://aziel-runtime.vibelock.workers.dev/

Forks are welcome and always allowed.

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
- Not a counted download. FG-0.1 is local.
- Not a rewrite of the Locks.
- Not a DOI mint.

Public identity is **Aziel Eliab** only. GodLock is a product name, not an author.

## Relation to aziel-runtime

**FragGate is the door. aziel-runtime hosts the public mesh.**

- This repo is the local kernel: envelopes, hashed registry, DecisionGATE stub, claim rules, JSONL ledger.
- [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) (`https://aziel-runtime.vibelock.workers.dev/`) is the catalog + session + in-process engines for Aziel Eliab software.
- A Lock should not remain a private runtime. It binds here. The runtime remains the public host.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Stdlib runtime. pytest is the dev extra.

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

Bind an existing Lock (or any adapter) without giving it a private runtime:

```python
def handler(name, args, call):
    return {"echo": args["text"]}

kernel.bind_adapter(
    "echo",
    [ToolSpec(
        name="echo.say",
        version="0.1.0",
        description="Echo text",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    )],
    handler,
)
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
