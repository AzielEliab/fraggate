"""CallEnvelope, ResultEnvelope, ToolSpec, GroundingRef, Claim."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from fraggate.canon import sha256_hex
from fraggate.constants import (
    GROUNDING_KINDS,
    MAGIC,
    PAPER,
    STATUS_OK,
    STATUS_REFUSE,
    VERSION,
)
from fraggate.errors import FragRefuse
from fraggate.constants import FG_ERR


def utc_now() -> str:
    """UTC timestamp with second precision and Z suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class GroundingRef:
    """One locator that grounds a fact, claim, or result."""

    kind: str
    ref: str
    digest: str | None = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"kind": self.kind, "ref": self.ref}
        if self.digest:
            payload["digest"] = self.digest
        if self.note:
            payload["note"] = self.note
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GroundingRef":
        if not isinstance(data, Mapping):
            raise FragRefuse(FG_ERR, "GroundingRef must be an object")
        kind = str(data.get("kind") or "").strip()
        ref = str(data.get("ref") or "").strip()
        if kind not in GROUNDING_KINDS:
            raise FragRefuse(FG_ERR, f"unknown grounding kind {kind!r}")
        if not ref:
            raise FragRefuse(FG_ERR, "GroundingRef.ref is required")
        digest = data.get("digest")
        return cls(
            kind=kind,
            ref=ref,
            digest=str(digest) if digest else None,
            note=str(data.get("note") or ""),
        )


@dataclass
class Artifact:
    """Named output object. Invented artifacts are errors, not drafts."""

    id: str
    kind: str
    digest: str | None = None
    ref: str | None = None
    invented: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"id": self.id, "kind": self.kind}
        if self.digest:
            payload["digest"] = self.digest
        if self.ref:
            payload["ref"] = self.ref
        if self.invented:
            payload["invented"] = True
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Artifact":
        if not isinstance(data, Mapping):
            raise FragRefuse(FG_ERR, "Artifact must be an object")
        ident = str(data.get("id") or "").strip()
        kind = str(data.get("kind") or "").strip()
        if not ident or not kind:
            raise FragRefuse(FG_ERR, "Artifact.id and Artifact.kind are required")
        digest = data.get("digest")
        ref = data.get("ref")
        return cls(
            id=ident,
            kind=kind,
            digest=str(digest) if digest else None,
            ref=str(ref) if ref else None,
            invented=bool(data.get("invented", False)),
        )


@dataclass
class Fact:
    """A single asserted fact. Requires ≥1 GroundingRef."""

    text: str
    grounding: list[GroundingRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "grounding": [g.to_dict() for g in self.grounding],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Fact":
        if not isinstance(data, Mapping):
            raise FragRefuse(FG_ERR, "Fact must be an object")
        text = str(data.get("text") or "").strip()
        if not text:
            raise FragRefuse(FG_ERR, "Fact.text is required")
        raw = data.get("grounding") or []
        if not isinstance(raw, list):
            raise FragRefuse(FG_ERR, "Fact.grounding must be an array")
        return cls(text=text, grounding=[GroundingRef.from_dict(g) for g in raw])


@dataclass
class Claim:
    """Operator or handler assertion bundle."""

    statement: str
    facts: list[Fact] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    grounding: list[GroundingRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "facts": [f.to_dict() for f in self.facts],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "grounding": [g.to_dict() for g in self.grounding],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Claim":
        if not isinstance(data, Mapping):
            raise FragRefuse(FG_ERR, "Claim must be an object")
        statement = str(data.get("statement") or "").strip()
        if not statement:
            raise FragRefuse(FG_ERR, "Claim.statement is required")
        facts = data.get("facts") or []
        artifacts = data.get("artifacts") or []
        grounding = data.get("grounding") or []
        if not isinstance(facts, list):
            raise FragRefuse(FG_ERR, "Claim.facts must be an array")
        if not isinstance(artifacts, list):
            raise FragRefuse(FG_ERR, "Claim.artifacts must be an array")
        if not isinstance(grounding, list):
            raise FragRefuse(FG_ERR, "Claim.grounding must be an array")
        return cls(
            statement=statement,
            facts=[Fact.from_dict(f) for f in facts],
            artifacts=[Artifact.from_dict(a) for a in artifacts],
            grounding=[GroundingRef.from_dict(g) for g in grounding],
        )


@dataclass
class ToolSpec:
    """Registered tool. Hash is canonical JSON of identity fields."""

    name: str
    version: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    destructive: bool = False
    export: bool = False
    adapter: str | None = None

    def identity(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "adapter": self.adapter,
            "description": self.description,
            "destructive": self.destructive,
            "export": self.export,
            "input_schema": self.input_schema,
            "name": self.name,
            "output_schema": self.output_schema,
            "version": self.version,
        }
        return payload

    def spec_hash(self) -> str:
        return sha256_hex(self.identity())

    def to_dict(self) -> dict[str, Any]:
        payload = self.identity()
        payload["spec_hash"] = self.spec_hash()
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ToolSpec":
        if not isinstance(data, Mapping):
            raise FragRefuse(FG_ERR, "ToolSpec must be an object")
        name = str(data.get("name") or "").strip()
        if not name:
            raise FragRefuse(FG_ERR, "ToolSpec.name is required")
        schema = data.get("input_schema") or {"type": "object"}
        if not isinstance(schema, dict):
            raise FragRefuse(FG_ERR, "ToolSpec.input_schema must be an object")
        output = data.get("output_schema")
        if output is not None and not isinstance(output, dict):
            raise FragRefuse(FG_ERR, "ToolSpec.output_schema must be an object")
        return cls(
            name=name,
            version=str(data.get("version") or VERSION),
            description=str(data.get("description") or ""),
            input_schema=schema,
            output_schema=output,
            destructive=bool(data.get("destructive", False)),
            export=bool(data.get("export", False)),
            adapter=str(data["adapter"]) if data.get("adapter") else None,
        )


@dataclass
class CallEnvelope:
    """Only legal execution input. Rule 1."""

    tool: str
    intent: str
    operator: str
    session_id: str
    args: dict[str, Any] = field(default_factory=dict)
    magic: str = MAGIC
    version: str = VERSION
    call_id: str = field(default_factory=new_id)
    dry_run: bool = False
    allow_export: bool = False
    allow_search: bool = False
    destructive: bool = False
    grounding: list[GroundingRef] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    ts: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "magic": self.magic,
            "version": self.version,
            "paper": PAPER,
            "call_id": self.call_id,
            "session_id": self.session_id,
            "operator": self.operator,
            "intent": self.intent,
            "tool": self.tool,
            "args": self.args,
            "dry_run": self.dry_run,
            "allow_export": self.allow_export,
            "allow_search": self.allow_search,
            "destructive": self.destructive,
            "grounding": [g.to_dict() for g in self.grounding],
            "claims": [c.to_dict() for c in self.claims],
            "ts": self.ts,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | "CallEnvelope") -> "CallEnvelope":
        if isinstance(data, CallEnvelope):
            return data
        if not isinstance(data, Mapping):
            raise FragRefuse(FG_ERR, "execution requires a CallEnvelope")
        magic = str(data.get("magic") or MAGIC)
        if magic != MAGIC:
            raise FragRefuse(FG_ERR, f"magic must be {MAGIC}, got {magic!r}")
        version = str(data.get("version") or VERSION)
        if not version.startswith("0.1."):
            raise FragRefuse(FG_ERR, f"unsupported version {version!r}")
        tool = str(data.get("tool") or "").strip()
        if not tool:
            raise FragRefuse(FG_ERR, "CallEnvelope.tool is required")
        session_id = str(data.get("session_id") or "").strip()
        if not session_id:
            raise FragRefuse(FG_ERR, "CallEnvelope.session_id is required")
        args = data.get("args") or {}
        if not isinstance(args, dict):
            raise FragRefuse(FG_ERR, "CallEnvelope.args must be an object")
        grounding = data.get("grounding") or []
        claims = data.get("claims") or []
        if not isinstance(grounding, list):
            raise FragRefuse(FG_ERR, "CallEnvelope.grounding must be an array")
        if not isinstance(claims, list):
            raise FragRefuse(FG_ERR, "CallEnvelope.claims must be an array")
        return cls(
            magic=magic,
            version=version,
            call_id=str(data.get("call_id") or new_id()),
            session_id=session_id,
            operator=str(data.get("operator") or ""),
            intent=str(data.get("intent") or ""),
            tool=tool,
            args=args,
            dry_run=bool(data.get("dry_run", False)),
            allow_export=bool(data.get("allow_export", False)),
            allow_search=bool(data.get("allow_search", False)),
            destructive=bool(data.get("destructive", False)),
            grounding=[GroundingRef.from_dict(g) for g in grounding],
            claims=[Claim.from_dict(c) for c in claims],
            ts=str(data.get("ts") or utc_now()),
        )


@dataclass
class ResultEnvelope:
    """Only legal assertion output. Rule 2."""

    call_id: str
    session_id: str
    tool: str
    status: str
    result: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    claims: list[Claim] = field(default_factory=list)
    grounding: list[GroundingRef] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    gate: dict[str, Any] | None = None
    ledger_hash: str | None = None
    registry_digest: str | None = None
    dry_run: bool = False
    magic: str = MAGIC
    version: str = VERSION
    paper: str = PAPER
    ts: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "magic": self.magic,
            "version": self.version,
            "paper": self.paper,
            "call_id": self.call_id,
            "session_id": self.session_id,
            "tool": self.tool,
            "status": self.status,
            "result": self.result,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details,
            "claims": [c.to_dict() for c in self.claims],
            "grounding": [g.to_dict() for g in self.grounding],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "gate": self.gate,
            "ledger_hash": self.ledger_hash,
            "registry_digest": self.registry_digest,
            "dry_run": self.dry_run,
            "ts": self.ts,
        }

    @classmethod
    def ok(
        cls,
        call: CallEnvelope,
        result: dict[str, Any],
        *,
        claims: list[Claim] | None = None,
        grounding: list[GroundingRef] | None = None,
        artifacts: list[Artifact] | None = None,
        gate: dict[str, Any] | None = None,
        registry_digest: str | None = None,
    ) -> "ResultEnvelope":
        return cls(
            call_id=call.call_id,
            session_id=call.session_id,
            tool=call.tool,
            status=STATUS_OK,
            result=result,
            claims=claims or [],
            grounding=grounding or [],
            artifacts=artifacts or [],
            gate=gate,
            registry_digest=registry_digest,
            dry_run=call.dry_run,
        )

    @classmethod
    def refuse(
        cls,
        call: CallEnvelope | None,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        gate: dict[str, Any] | None = None,
        registry_digest: str | None = None,
        tool: str | None = None,
        session_id: str | None = None,
        call_id: str | None = None,
    ) -> "ResultEnvelope":
        return cls(
            call_id=call.call_id if call else (call_id or new_id()),
            session_id=call.session_id if call else (session_id or ""),
            tool=call.tool if call else (tool or ""),
            status=STATUS_REFUSE,
            error_code=code,
            error_message=message,
            details=details or {},
            gate=gate,
            registry_digest=registry_digest,
            dry_run=call.dry_run if call else False,
        )
