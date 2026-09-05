from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from fraggate import FragGate


@pytest.fixture
def kernel(tmp_path: Path) -> FragGate:
    k = FragGate(
        session_id=f"test-{uuid.uuid4()}",
        operator="Aziel Eliab",
        ledger_path=tmp_path / "ledger.jsonl",
    )
    yield k
    k.close()
