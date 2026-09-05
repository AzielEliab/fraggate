from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from fraggate import FragGate, FragGateError, ToolSpec
from fraggate.constants import (
    FG_EXPORT,
    FG_GATE,
    FG_HALLUC_ARTIFACT,
    FG_HALLUC_FACT,
    FG_HALLUC_TOOL,
    FG_FRAG_SCHEMA,
    GENESIS_PREV_HASH,
    MAGIC,
    VERSION,
)


def _echo_spec() -> ToolSpec:
    return ToolSpec(
        name="echo.say",
        version="0.1.0",
        description="Echo text",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    )


def test_unknown_tool_is_hallucination(kernel: FragGate) -> None:
    before = len(kernel.ledger)
    out = kernel.call(
        kernel.envelope(
            "not.a.real.tool",
            intent="Call a tool that was never registered.",
        )
    )
    assert out.status == "refuse"
    assert out.error_code == FG_HALLUC_TOOL
    assert out.magic == MAGIC
    assert len(kernel.ledger) == before + 1
    assert kernel.ledger.tip == out.ledger_hash
    assert kernel.ledger.tip != GENESIS_PREV_HASH


def test_schema_drift_is_fragmentation(kernel: FragGate) -> None:
    kernel.bind_adapter("echo", [_echo_spec()], lambda n, a, c: {"echo": a["text"]})
    out = kernel.call(
        kernel.envelope(
            "echo.say",
            intent="Call echo.say with a drifted schema.",
            args={"wrong": 1},
        )
    )
    assert out.status == "refuse"
    assert out.error_code == FG_FRAG_SCHEMA


def test_ungrounded_fact_is_hallucination(kernel: FragGate) -> None:
    out = kernel.call(
        kernel.envelope(
            "claim.check",
            intent="Check a claim that has no grounding.",
            args={
                "claims": [
                    {
                        "statement": "The sky is green on every world.",
                        "facts": [{"text": "The sky is green.", "grounding": []}],
                    }
                ]
            },
        )
    )
    assert out.status == "refuse"
    assert out.error_code == FG_HALLUC_FACT
    assert len(kernel.ledger) >= 1
    assert kernel.ledger.records()[-1].status == "refuse"
    assert kernel.ledger.records()[-1].error_code == FG_HALLUC_FACT


def test_decisiongate_refuse_is_typed(kernel: FragGate) -> None:
    call_id = str(uuid.uuid4())
    out = kernel.call(
        kernel.envelope(
            "runtime.ping",
            intent="Ping FragGate kernel for liveness.",
            operator="",
            call_id=call_id,
        )
    )
    assert out.status == "refuse"
    assert out.error_code == FG_GATE
    assert out.details["gate"]["blocked_at"] == "Responsibility"

    retry = kernel.call(
        kernel.envelope(
            "runtime.ping",
            intent="Ping FragGate kernel for liveness.",
            operator="Aziel Eliab",
            call_id=call_id,
        )
    )
    assert retry.status == "refuse"
    assert retry.error_code == FG_GATE


def test_ledger_appends_on_refuse(kernel: FragGate) -> None:
    assert len(kernel.ledger) == 0
    first = kernel.call(kernel.envelope("ghost.tool", intent="Invent a tool name."))
    second = kernel.call(kernel.envelope("ghost.tool", intent="Invent a tool name again."))
    assert first.status == "refuse"
    assert second.status == "refuse"
    assert len(kernel.ledger) == 2
    recs = kernel.ledger.records()
    assert recs[0].prev_hash == GENESIS_PREV_HASH
    assert recs[1].prev_hash == recs[0].hash
    assert recs[1].hash == second.ledger_hash
    kernel.ledger.verify()


def test_registry_digest_is_stable(tmp_path: Path) -> None:
    a = FragGate(session_id=f"a-{uuid.uuid4()}", operator="A", ledger_path=tmp_path / "a.jsonl")
    b = FragGate(session_id=f"b-{uuid.uuid4()}", operator="B", ledger_path=tmp_path / "b.jsonl")
    try:
        assert a.registry.digest() == b.registry.digest()
        first = a.registry.digest()
        a.call(a.envelope("runtime.ping", intent="Ping FragGate kernel for liveness."))
        assert a.registry.digest() == first
        spec = _echo_spec()
        a.bind_adapter("echo", [spec], lambda n, args, c: {"echo": args["text"]})
        b.bind_adapter("echo", [_echo_spec()], lambda n, args, c: {"echo": args["text"]})
        assert a.registry.digest() == b.registry.digest()
        assert a.registry.digest() != first
    finally:
        a.close()
        b.close()


def test_ping_lists_and_verify(kernel: FragGate) -> None:
    ping = kernel.call(kernel.envelope("runtime.ping", intent="Ping FragGate kernel for liveness."))
    assert ping.status == "ok"
    assert ping.result["alive"] is True
    assert ping.result["version"] == VERSION
    assert ping.result["ledger_tip"]
    listed = kernel.call(kernel.envelope("registry.list", intent="List bound FragGate tools."))
    names = {row["name"] for row in listed.result["tools"]}
    assert names == {
        "runtime.ping",
        "registry.list",
        "registry.verify",
        "claim.check",
        "runtime.receipt",
    }
    real = kernel.call(
        kernel.envelope(
            "registry.verify",
            intent="Verify that runtime.ping is bound.",
            args={"name": "runtime.ping"},
        )
    )
    assert real.result["bound"] is True
    fake = kernel.call(
        kernel.envelope(
            "registry.verify",
            intent="Verify that a ghost name is not bound.",
            args={"name": "ghost.tool"},
        )
    )
    assert fake.status == "ok"
    assert fake.result["bound"] is False


def test_invented_artifact_is_error(kernel: FragGate) -> None:
    def handler(_name, _args, _call):
        return {
            "result": {"ok": True},
            "artifacts": [{"id": "draft.txt", "kind": "file", "invented": True}],
        }

    kernel.bind_adapter(
        "forge",
        [
            ToolSpec(
                name="forge.make",
                version="0.1.0",
                description="Pretend to make a file",
                input_schema={"type": "object", "additionalProperties": False},
            )
        ],
        handler,
    )
    out = kernel.call(kernel.envelope("forge.make", intent="Make an invented artifact on purpose."))
    assert out.status == "refuse"
    assert out.error_code == FG_HALLUC_ARTIFACT


def test_export_requires_flag(kernel: FragGate) -> None:
    spec = ToolSpec(
        name="ship.out",
        version="0.1.0",
        description="Export a blob",
        input_schema={"type": "object", "additionalProperties": False},
        export=True,
    )
    kernel.bind_adapter("ship", [spec], lambda n, a, c: {"shipped": False})
    refused = kernel.call(kernel.envelope("ship.out", intent="Export a blob without permission."))
    assert refused.status == "refuse"
    assert refused.error_code == FG_EXPORT
    allowed = kernel.call(
        kernel.envelope("ship.out", intent="Export a blob with permission.", allow_export=True)
    )
    assert allowed.status == "ok"


def test_no_second_kernel(tmp_path: Path) -> None:
    sid = f"once-{uuid.uuid4()}"
    first = FragGate(session_id=sid, operator="A", ledger_path=tmp_path / "one.jsonl")
    with pytest.raises(FragGateError) as exc:
        FragGate(session_id=sid, operator="A", ledger_path=tmp_path / "two.jsonl")
    assert exc.value.code == "FG-ERR"
    first.close()
    second = FragGate(session_id=sid, operator="A", ledger_path=tmp_path / "two.jsonl")
    second.close()


def test_grounded_claim_accepts(kernel: FragGate) -> None:
    digest = kernel.registry.digest()
    out = kernel.call(
        kernel.envelope(
            "claim.check",
            intent="Check a grounded claim against the registry.",
            args={
                "claims": [
                    {
                        "statement": "runtime.ping is a builtin tool.",
                        "facts": [
                            {
                                "text": "runtime.ping is bound.",
                                "grounding": [
                                    {"kind": "registry", "ref": f"fraggate:{digest}", "digest": digest}
                                ],
                            }
                        ],
                    }
                ]
            },
        )
    )
    assert out.status == "ok"
    assert out.result["accepted"] is True


def test_silent_digest_change_refused(kernel: FragGate) -> None:
    spec = _echo_spec()
    kernel.bind_adapter("echo", [spec], lambda n, a, c: {"echo": a["text"]})
    spec.input_schema = {"type": "object"}
    out = kernel.call(
        kernel.envelope("echo.say", intent="Call echo after a silent schema mutation.", args={"text": "x"})
    )
    assert out.status == "refuse"
    assert out.error_code == FG_FRAG_SCHEMA


def test_receipt_hashes_assertion(kernel: FragGate) -> None:
    out = kernel.call(
        kernel.envelope(
            "runtime.receipt",
            intent="Hash an operator assertion.",
            args={"assertion": "the kernel is local"},
        )
    )
    assert out.status == "ok"
    assert out.result["hash"]
    assert out.result["assertion"] == "the kernel is local"
