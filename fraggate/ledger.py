"""Local JSONL ledger. Previous-hash chained. TemporalLock-shaped, not a fork."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from fraggate.canon import canonical_dumps, sha256_hex
from fraggate.constants import GENESIS_PREV_HASH, MAGIC, PAPER, VERSION
from fraggate.envelopes import utc_now
from fraggate.errors import FragGateError
from fraggate.constants import FG_ERR


def _record_hash(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "hash"}
    return sha256_hex(body)


@dataclass(frozen=True)
class LedgerRecord:
    seq: int
    prev_hash: str
    hash: str
    ts: str
    call_id: str
    session_id: str
    tool: str
    status: str
    error_code: str | None
    registry_digest: str
    payload_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "magic": MAGIC,
            "version": VERSION,
            "paper": PAPER,
            "seq": self.seq,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
            "ts": self.ts,
            "call_id": self.call_id,
            "session_id": self.session_id,
            "tool": self.tool,
            "status": self.status,
            "error_code": self.error_code,
            "registry_digest": self.registry_digest,
            "payload_digest": self.payload_digest,
        }


class Ledger:
    """Append-only JSONL. Mandatory on success and refuse."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[LedgerRecord] = []
        if self.path.is_file():
            self._load()

    def __len__(self) -> int:
        return len(self._records)

    @property
    def tip(self) -> str:
        if not self._records:
            return GENESIS_PREV_HASH
        return self._records[-1].hash

    def records(self) -> tuple[LedgerRecord, ...]:
        return tuple(self._records)

    def _load(self) -> None:
        text = self.path.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            self._records.append(
                LedgerRecord(
                    seq=int(data["seq"]),
                    prev_hash=str(data["prev_hash"]),
                    hash=str(data["hash"]),
                    ts=str(data["ts"]),
                    call_id=str(data["call_id"]),
                    session_id=str(data["session_id"]),
                    tool=str(data["tool"]),
                    status=str(data["status"]),
                    error_code=data.get("error_code"),
                    registry_digest=str(data.get("registry_digest") or ""),
                    payload_digest=str(data.get("payload_digest") or ""),
                )
            )
        self.verify()

    def verify(self) -> None:
        prev = GENESIS_PREV_HASH
        for i, rec in enumerate(self._records):
            if rec.prev_hash != prev:
                raise FragGateError(
                    FG_ERR,
                    f"ledger link broken at seq {rec.seq}: prev_hash {rec.prev_hash} != {prev}",
                )
            expected = _record_hash(rec.to_dict())
            if rec.hash != expected:
                raise FragGateError(
                    FG_ERR,
                    f"ledger hash mismatch at seq {rec.seq}: {rec.hash} != {expected}",
                )
            if rec.seq != i + 1:
                raise FragGateError(FG_ERR, f"ledger seq gap at index {i}: {rec.seq}")
            prev = rec.hash

    def append(
        self,
        *,
        call_id: str,
        session_id: str,
        tool: str,
        status: str,
        error_code: str | None,
        registry_digest: str,
        payload: Mapping[str, Any],
    ) -> LedgerRecord:
        prev = self.tip
        seq = len(self._records) + 1
        ts = utc_now()
        payload_digest = sha256_hex(dict(payload))
        unsigned = {
            "magic": MAGIC,
            "version": VERSION,
            "paper": PAPER,
            "seq": seq,
            "prev_hash": prev,
            "ts": ts,
            "call_id": call_id,
            "session_id": session_id,
            "tool": tool,
            "status": status,
            "error_code": error_code,
            "registry_digest": registry_digest,
            "payload_digest": payload_digest,
        }
        digest = sha256_hex(unsigned)
        record = LedgerRecord(
            seq=seq,
            prev_hash=prev,
            hash=digest,
            ts=ts,
            call_id=call_id,
            session_id=session_id,
            tool=tool,
            status=status,
            error_code=error_code,
            registry_digest=registry_digest,
            payload_digest=payload_digest,
        )
        line = canonical_dumps(record.to_dict())
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.write("\n")
            fh.flush()
        self._records.append(record)
        return record
