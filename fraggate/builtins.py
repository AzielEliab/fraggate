"""v0.1 door tools. Everything else binds via bind_adapter."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from fraggate.canon import sha256_hex
from fraggate.claims import validate_claims
from fraggate.constants import AUTHOR, MAGIC, PAPER, VERSION
from fraggate.envelopes import CallEnvelope, Claim, GroundingRef, ToolSpec, utc_now

if TYPE_CHECKING:
    from fraggate.kernel import FragGate


def builtin_specs() -> list[ToolSpec]:
    empty_object = {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
    return [
        ToolSpec(
            name="runtime.ping",
            version=VERSION,
            description="Liveness, version, ledger tip, registry digest.",
            input_schema=empty_object,
            adapter=None,
        ),
        ToolSpec(
            name="registry.list",
            version=VERSION,
            description="List bound tools in the hashed registry.",
            input_schema=empty_object,
            adapter=None,
        ),
        ToolSpec(
            name="registry.verify",
            version=VERSION,
            description="Ask whether a tool name is real (bound).",
            input_schema={
                "type": "object",
                "properties": {"name": {"type": "string", "minLength": 1}},
                "required": ["name"],
                "additionalProperties": False,
            },
            adapter=None,
        ),
        ToolSpec(
            name="claim.check",
            version=VERSION,
            description="Accept or refuse a claim bundle.",
            input_schema={
                "type": "object",
                "properties": {"claims": {"type": "array", "minItems": 1}},
                "required": ["claims"],
                "additionalProperties": False,
            },
            adapter=None,
        ),
        ToolSpec(
            name="runtime.receipt",
            version=VERSION,
            description="Hash an operator assertion.",
            input_schema={
                "type": "object",
                "properties": {"assertion": {"type": "string", "minLength": 1}},
                "required": ["assertion"],
                "additionalProperties": False,
            },
            adapter=None,
        ),
    ]


def dispatch_builtin(kernel: "FragGate", name: str, args: dict[str, Any], call: CallEnvelope) -> dict[str, Any]:
    if name == "runtime.ping":
        return {
            "alive": True,
            "magic": MAGIC,
            "version": VERSION,
            "paper": PAPER,
            "author": AUTHOR,
            "session_id": kernel.session_id,
            "ledger_tip": kernel.ledger.tip,
            "registry_digest": kernel.registry.digest(),
            "tools": kernel.registry.names(),
        }
    if name == "registry.list":
        return {
            "digest": kernel.registry.digest(),
            "tools": kernel.registry.list_specs(),
        }
    if name == "registry.verify":
        name_q = str(args["name"])
        bound = kernel.registry.get(name_q)
        if bound is None:
            return {"name": name_q, "bound": False}
        return {
            "name": name_q,
            "bound": True,
            "spec_hash": bound.spec_hash,
            "version": bound.spec.version,
            "adapter": bound.adapter,
        }
    if name == "claim.check":
        claims = [Claim.from_dict(c) for c in args["claims"]]
        validate_claims(claims, allow_search=call.allow_search)
        return {
            "accepted": True,
            "count": len(claims),
            "claims": [c.to_dict() for c in claims],
        }
    if name == "runtime.receipt":
        assertion = str(args["assertion"])
        ts = utc_now()
        digest = sha256_hex(
            {
                "assertion": assertion,
                "operator": call.operator,
                "session_id": call.session_id,
                "ts": ts,
            }
        )
        return {
            "assertion": assertion,
            "hash": digest,
            "ts": ts,
            "operator": call.operator,
        }
    raise RuntimeError(f"unhandled builtin {name}")


def kernel_grounding(kernel: "FragGate") -> list[GroundingRef]:
    return [
        GroundingRef(
            kind="registry",
            ref=f"fraggate:{kernel.registry.digest()}",
            digest=kernel.registry.digest(),
            note="hashed registry digest",
        ),
        GroundingRef(
            kind="operator",
            ref=kernel.operator,
            note="session operator",
        ),
    ]
