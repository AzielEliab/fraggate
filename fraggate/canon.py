"""Canonical JSON + SHA-256 for registry and ledger hashes.

UTF-8 JSON with sorted keys and no extra whitespace
(``separators=(",", ":")``, ``sort_keys=True``, ``ensure_ascii=False``).

This is TemporalLock-shaped encoding (sorted canonical JSON, SHA-256 hex),
not a product fork.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_dumps(value: Any) -> str:
    """Return canonical JSON text for ``value``."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(value: Any) -> bytes:
    """UTF-8 bytes of ``canonical_dumps(value)``."""
    return canonical_dumps(value).encode("utf-8")


def sha256_hex(value: Any) -> str:
    """SHA-256 (lowercase hex) of the canonical encoding of ``value``."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_text(text: str) -> str:
    """SHA-256 (lowercase hex) of UTF-8 ``text``."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
