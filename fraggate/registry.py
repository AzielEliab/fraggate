"""Hashed tool registry. No tool exists outside it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from fraggate.canon import sha256_hex
from fraggate.constants import FG_FRAG_ORPHAN, FG_FRAG_SCHEMA, FG_HALLUC_TOOL
from fraggate.envelopes import ToolSpec
from fraggate.errors import FragRefuse
from fraggate.schema import validate_schema

Handler = Callable[[str, dict[str, Any], Any], Any]


@dataclass
class BoundTool:
    spec: ToolSpec
    spec_hash: str
    handler: Handler
    adapter: str | None


class Registry:
    """Canonical-JSON hashed ToolSpec map + registry digest."""

    def __init__(self) -> None:
        self._tools: dict[str, BoundTool] = {}
        self._last_digest: str | None = None

    def digest(self) -> str:
        mapping = {name: bound.spec_hash for name, bound in sorted(self._tools.items())}
        return sha256_hex(mapping)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def get(self, name: str) -> BoundTool | None:
        return self._tools.get(name)

    def list_specs(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for name in self.names():
            bound = self._tools[name]
            rows.append(
                {
                    "name": name,
                    "version": bound.spec.version,
                    "description": bound.spec.description,
                    "spec_hash": bound.spec_hash,
                    "adapter": bound.adapter,
                    "destructive": bound.spec.destructive,
                    "export": bound.spec.export,
                }
            )
        return rows

    def bind(self, spec: ToolSpec, handler: Handler, adapter: str | None = None) -> str:
        """Bind a tool. Digest change is explicit (returned)."""
        if spec.adapter is None and adapter:
            spec.adapter = adapter
        stored_hash = spec.spec_hash()
        existing = self._tools.get(spec.name)
        if existing is not None and existing.spec_hash != stored_hash:
            raise FragRefuse(
                FG_FRAG_SCHEMA,
                f"schema drift on rebind of {spec.name!r}: hash {existing.spec_hash} → {stored_hash}",
                {"name": spec.name, "old_hash": existing.spec_hash, "new_hash": stored_hash},
            )
        self._tools[spec.name] = BoundTool(
            spec=spec,
            spec_hash=stored_hash,
            handler=handler,
            adapter=spec.adapter,
        )
        digest = self.digest()
        self._last_digest = digest
        return digest

    def unbind_adapter(self, adapter: str) -> str:
        victims = [name for name, bound in self._tools.items() if bound.adapter == adapter]
        for name in victims:
            del self._tools[name]
        digest = self.digest()
        self._last_digest = digest
        return digest

    def require(self, name: str) -> BoundTool:
        bound = self._tools.get(name)
        if bound is None:
            raise FragRefuse(
                FG_HALLUC_TOOL,
                f"tool {name!r} is not in the hashed registry",
                {"name": name},
            )
        live = bound.spec.spec_hash()
        if live != bound.spec_hash:
            raise FragRefuse(
                FG_FRAG_SCHEMA,
                f"silent digest change refused for {name!r}",
                {"name": name, "stored": bound.spec_hash, "live": live},
            )
        if self._last_digest is not None and self._last_digest != self.digest():
            raise FragRefuse(
                FG_FRAG_ORPHAN,
                "registry digest changed without bind/unbind",
                {"stored": self._last_digest, "live": self.digest()},
            )
        return bound

    def check_args(self, spec: ToolSpec, args: Mapping[str, Any]) -> None:
        errors = validate_schema(dict(args), spec.input_schema)
        if errors:
            raise FragRefuse(
                FG_FRAG_SCHEMA,
                f"schema drift for {spec.name}: " + "; ".join(errors),
                {"name": spec.name, "errors": errors},
            )

    def snapshot_digest(self) -> str:
        digest = self.digest()
        self._last_digest = digest
        return digest
