"""Typed FragGate refuse / error types."""

from __future__ import annotations

from typing import Any

from fraggate.constants import ERROR_CODES, FG_ERR


class FragGateError(Exception):
    """Kernel-level failure that is not a typed call refuse."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        if code not in ERROR_CODES:
            code = FG_ERR
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{code}: {message}")


class FragRefuse(Exception):
    """Typed pipeline refuse. Always becomes a ResultEnvelope + ledger append."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        if code not in ERROR_CODES:
            code = FG_ERR
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{code}: {message}")
