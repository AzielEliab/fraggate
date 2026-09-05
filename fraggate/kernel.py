"""FragGate FG-0.1 kernel.

Pipeline:
operator intent → CallEnvelope → Registry.require(tool) → Schema check →
DecisionGATE → handler (or dry-run) → Claim.validate → ResultEnvelope →
Ledger.append
"""

from __future__ import annotations

import weakref
from pathlib import Path
from typing import Any, Iterable, Mapping

from fraggate.builtins import builtin_specs, dispatch_builtin, kernel_grounding
from fraggate.claims import validate_artifact, validate_claims
from fraggate.constants import (
    BUILTIN_TOOLS,
    FG_ERR,
    FG_FRAG_ORPHAN,
    FG_HALLUC_FACT,
    MAGIC,
    PAPER,
    VERSION,
)
from fraggate.envelopes import (
    Artifact,
    CallEnvelope,
    Claim,
    GroundingRef,
    ResultEnvelope,
    ToolSpec,
    new_id,
)
from fraggate.errors import FragGateError, FragRefuse
from fraggate.gate import DecisionGate
from fraggate.ledger import Ledger
from fraggate.registry import Handler, Registry

_SESSIONS: weakref.WeakValueDictionary[str, "FragGate"] = weakref.WeakValueDictionary()


class FragGate:
    """One kernel per operator session. Tools attach only through registration."""

    def __init__(
        self,
        *,
        session_id: str,
        operator: str,
        ledger_path: str | Path,
    ) -> None:
        session_id = str(session_id).strip()
        operator = str(operator).strip()
        if not session_id:
            raise FragGateError(FG_ERR, "session_id is required")
        if not operator:
            raise FragGateError(FG_ERR, "operator is required")
        existing = _SESSIONS.get(session_id)
        if existing is not None:
            raise FragGateError(
                FG_ERR,
                "no second kernel for the same operator session",
                {"session_id": session_id},
            )
        self.session_id = session_id
        self.operator = operator
        self.magic = MAGIC
        self.version = VERSION
        self.paper = PAPER
        self.registry = Registry()
        self.ledger = Ledger(ledger_path)
        self.gate = DecisionGate()
        self._closed = False
        for spec in builtin_specs():
            self.registry.bind(spec, self._builtin_handler, adapter=None)
        self.registry.snapshot_digest()
        _SESSIONS[session_id] = self

    def close(self) -> None:
        self._closed = True
        if _SESSIONS.get(self.session_id) is self:
            del _SESSIONS[self.session_id]

    @classmethod
    def session_bound(cls, session_id: str) -> bool:
        return session_id in _SESSIONS

    def bind_adapter(
        self,
        adapter_id: str,
        tools: Iterable[ToolSpec | Mapping[str, Any]],
        handler: Handler,
    ) -> dict[str, Any]:
        """Attach an existing Lock (or any adapter) without a private runtime."""
        self._ensure_open()
        adapter_id = str(adapter_id).strip()
        if not adapter_id:
            raise FragGateError(FG_ERR, "adapter_id is required")
        before = self.registry.digest()
        bound: list[str] = []
        for raw in tools:
            spec = raw if isinstance(raw, ToolSpec) else ToolSpec.from_dict(raw)
            spec.adapter = adapter_id
            self.registry.bind(spec, handler, adapter=adapter_id)
            bound.append(spec.name)
        after = self.registry.snapshot_digest()
        return {
            "adapter": adapter_id,
            "bound": bound,
            "digest_before": before,
            "digest_after": after,
            "digest_changed": before != after,
        }

    def unbind_adapter(self, adapter_id: str) -> dict[str, Any]:
        self._ensure_open()
        before = self.registry.digest()
        after = self.registry.unbind_adapter(adapter_id)
        return {
            "adapter": adapter_id,
            "digest_before": before,
            "digest_after": after,
            "digest_changed": before != after,
        }

    def call(self, envelope: CallEnvelope | Mapping[str, Any]) -> ResultEnvelope:
        """Only public execution path. Always appends the ledger."""
        self._ensure_open()
        call: CallEnvelope | None = None
        digest = self.registry.digest()
        try:
            call = CallEnvelope.from_dict(envelope)
            if call.session_id != self.session_id:
                raise FragRefuse(
                    FG_ERR,
                    "CallEnvelope.session_id does not match this kernel session",
                    {"envelope": call.session_id, "kernel": self.session_id},
                )
            bound = self.registry.require(call.tool)
            if bound.handler is None:
                raise FragRefuse(
                    FG_FRAG_ORPHAN,
                    f"orphan tool {call.tool!r}: bound without handler",
                    {"name": call.tool},
                )
            self.registry.check_args(bound.spec, call.args)
            gate_report = self.gate.evaluate(call, bound.spec)
            self.gate.check_export(call, bound.spec)
            if call.dry_run:
                raw: Any = {
                    "dry_run": True,
                    "tool": call.tool,
                    "args": call.args,
                    "would_invoke": True,
                }
            else:
                raw = bound.handler(call.tool, call.args, call)
            result, claims, artifacts, extra_grounding = self._normalize_handler(raw)
            if call.claims:
                claims = list(call.claims) + claims
            if claims:
                validate_claims(claims, allow_search=call.allow_search)
            for artifact in artifacts:
                validate_artifact(artifact, where="result.artifacts")
            grounding = kernel_grounding(self) + list(call.grounding) + extra_grounding
            if any(g.kind == "search" for g in grounding) and not call.allow_search:
                raise FragRefuse(
                    FG_HALLUC_FACT,
                    "search grounding refused without allow_search",
                )
            envelope_out = ResultEnvelope.ok(
                call,
                result,
                claims=claims,
                grounding=grounding,
                artifacts=artifacts,
                gate=gate_report.to_dict(),
                registry_digest=digest,
            )
        except FragRefuse as exc:
            envelope_out = ResultEnvelope.refuse(
                call,
                exc.code,
                exc.message,
                details=exc.details,
                gate=(exc.details or {}).get("gate"),
                registry_digest=digest,
                tool=getattr(call, "tool", None) if call else _peek_tool(envelope),
                session_id=self.session_id,
                call_id=getattr(call, "call_id", None) if call else _peek_call_id(envelope),
            )
        except Exception as exc:  # noqa: BLE001 — kernel must ledger every call
            envelope_out = ResultEnvelope.refuse(
                call,
                FG_ERR,
                str(exc),
                registry_digest=digest,
                session_id=self.session_id,
                tool=_peek_tool(envelope) if call is None else call.tool,
            )

        record = self.ledger.append(
            call_id=envelope_out.call_id,
            session_id=envelope_out.session_id or self.session_id,
            tool=envelope_out.tool,
            status=envelope_out.status,
            error_code=envelope_out.error_code,
            registry_digest=digest,
            payload=envelope_out.to_dict(),
        )
        envelope_out.ledger_hash = record.hash
        envelope_out.registry_digest = digest
        if envelope_out.status == STATUS_OK:
            envelope_out.grounding = list(envelope_out.grounding) + [
                GroundingRef(kind="receipt", ref=record.hash, digest=record.hash)
            ]
        return envelope_out

    def envelope(
        self,
        tool: str,
        *,
        intent: str,
        args: Mapping[str, Any] | None = None,
        operator: str | None = None,
        **flags: Any,
    ) -> CallEnvelope:
        return CallEnvelope(
            tool=tool,
            intent=intent,
            operator=operator if operator is not None else self.operator,
            session_id=self.session_id,
            args=dict(args or {}),
            dry_run=bool(flags.get("dry_run", False)),
            allow_export=bool(flags.get("allow_export", False)),
            allow_search=bool(flags.get("allow_search", False)),
            destructive=bool(flags.get("destructive", False)),
            call_id=str(flags["call_id"]) if flags.get("call_id") else new_id(),
        )

    def _builtin_handler(self, name: str, args: dict[str, Any], call: CallEnvelope) -> dict[str, Any]:
        if name not in BUILTIN_TOOLS:
            raise FragRefuse(FG_FRAG_ORPHAN, f"orphan builtin name {name!r}")
        return dispatch_builtin(self, name, args, call)

    def _normalize_handler(
        self, raw: Any
    ) -> tuple[dict[str, Any], list[Claim], list[Artifact], list[GroundingRef]]:
        if raw is None:
            return {}, [], [], []
        if isinstance(raw, ResultEnvelope):
            raise FragRefuse(FG_ERR, "handler must not emit a ResultEnvelope; the kernel does")
        if not isinstance(raw, dict):
            raise FragRefuse(FG_ERR, "handler must return an object")
        claims_raw = raw.get("claims") if "claims" in raw else None
        artifacts_raw = raw.get("artifacts") if "artifacts" in raw else None
        grounding_raw = raw.get("grounding") if "grounding" in raw else None
        if claims_raw is None and artifacts_raw is None and grounding_raw is None:
            return raw, [], [], []
        result = raw.get("result")
        if result is None:
            result = {
                k: v
                for k, v in raw.items()
                if k not in {"claims", "artifacts", "grounding"}
            }
        if not isinstance(result, dict):
            raise FragRefuse(FG_ERR, "handler result must be an object")
        claims = [c if isinstance(c, Claim) else Claim.from_dict(c) for c in (claims_raw or [])]
        artifacts = [
            a if isinstance(a, Artifact) else Artifact.from_dict(a) for a in (artifacts_raw or [])
        ]
        grounding = [
            g if isinstance(g, GroundingRef) else GroundingRef.from_dict(g)
            for g in (grounding_raw or [])
        ]
        return result, claims, artifacts, grounding

    def _ensure_open(self) -> None:
        if self._closed:
            raise FragGateError(FG_ERR, "kernel session is closed")


def _peek_tool(envelope: Any) -> str:
    if isinstance(envelope, CallEnvelope):
        return envelope.tool
    if isinstance(envelope, Mapping):
        return str(envelope.get("tool") or "")
    return ""


def _peek_call_id(envelope: Any) -> str | None:
    if isinstance(envelope, CallEnvelope):
        return envelope.call_id
    if isinstance(envelope, Mapping) and envelope.get("call_id"):
        return str(envelope["call_id"])
    return None


__all__ = ["FragGate"]
