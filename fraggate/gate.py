"""DecisionGATE stub (pre-exec, not a sermon).

Five sequential gates: Definition, Evidence, Impact, Integrity, Responsibility.
Refuse is typed FG-GATE. No retry under a friendlier reading of the same call_id.
Destructive requires intent + the destructive flag. Export is FG-EXPORT, not a sermon.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fraggate.constants import (
    BLOCK,
    BUILTIN_TOOLS,
    FG_EXPORT,
    FG_GATE,
    GATE_NAMES,
    PASS,
    REVISE,
)
from fraggate.envelopes import CallEnvelope, ToolSpec
from fraggate.errors import FragRefuse


@dataclass
class GateResult:
    name: str
    state: str
    feedback: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "state": self.state, "feedback": self.feedback}


@dataclass
class GateReport:
    lineage: list[GateResult] = field(default_factory=list)
    final_state: str = PASS
    blocked_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage": [g.to_dict() for g in self.lineage],
            "final_state": self.final_state,
            "blocked_at": self.blocked_at,
        }


class DecisionGate:
    """Kernel-embedded five-gate filter. Not the DecisionGATE product fork."""

    def __init__(self) -> None:
        self._refused_call_ids: set[str] = set()

    def evaluate(self, call: CallEnvelope, spec: ToolSpec) -> GateReport:
        if call.call_id in self._refused_call_ids:
            report = GateReport(
                lineage=[
                    GateResult(
                        name="Integrity",
                        state=BLOCK,
                        feedback=(
                            "Same call_id was already refused. "
                            "No retry under a friendlier reading."
                        ),
                    )
                ],
                final_state=BLOCK,
                blocked_at="Integrity",
            )
            raise FragRefuse(
                FG_GATE,
                "DecisionGATE refused: no retry under a friendlier reading",
                {"gate": report.to_dict(), "call_id": call.call_id},
            )

        lineage: list[GateResult] = []
        for name, fn in (
            ("Definition", self._definition),
            ("Evidence", self._evidence),
            ("Impact", self._impact),
            ("Integrity", self._integrity),
            ("Responsibility", self._responsibility),
        ):
            result = fn(call, spec)
            lineage.append(result)
            if result.state in (REVISE, BLOCK):
                report = GateReport(
                    lineage=lineage,
                    final_state=result.state,
                    blocked_at=name,
                )
                self._refused_call_ids.add(call.call_id)
                raise FragRefuse(
                    FG_GATE,
                    f"DecisionGATE refused at {name}: {result.feedback}",
                    {"gate": report.to_dict()},
                )

        return GateReport(lineage=lineage, final_state=PASS)

    def check_export(self, call: CallEnvelope, spec: ToolSpec) -> None:
        if spec.export and not call.allow_export:
            raise FragRefuse(
                FG_EXPORT,
                f"export side effect of {spec.name!r} requires allow_export",
                {"name": spec.name},
            )

    def _definition(self, call: CallEnvelope, spec: ToolSpec) -> GateResult:
        intent = call.intent.strip()
        if not intent:
            return GateResult(
                name="Definition",
                state=BLOCK,
                feedback="Intent is empty. No execution without operator intent.",
            )
        if spec.name not in BUILTIN_TOOLS and len(intent.split()) < 3:
            return GateResult(
                name="Definition",
                state=REVISE,
                feedback="Intent is too thin for a bound adapter tool. Say what and why.",
            )
        return GateResult(name="Definition", state=PASS, feedback="Intent is present.")

    def _evidence(self, call: CallEnvelope, spec: ToolSpec) -> GateResult:
        if spec.name in BUILTIN_TOOLS:
            return GateResult(
                name="Evidence",
                state=PASS,
                feedback="Builtin tool is grounded by the hashed registry.",
            )
        if spec.destructive and not (call.grounding or call.claims):
            return GateResult(
                name="Evidence",
                state=REVISE,
                feedback="Destructive tool requires grounding or a claim bundle.",
            )
        return GateResult(name="Evidence", state=PASS, feedback="Evidence gate passed.")

    def _impact(self, call: CallEnvelope, spec: ToolSpec) -> GateResult:
        if spec.destructive and not call.destructive:
            return GateResult(
                name="Impact",
                state=BLOCK,
                feedback="Destructive tool requires CallEnvelope.destructive=true (intent).",
            )
        return GateResult(name="Impact", state=PASS, feedback="Impact flag matches spec.")

    def _integrity(self, call: CallEnvelope, spec: ToolSpec) -> GateResult:
        if spec.name != call.tool:
            return GateResult(
                name="Integrity",
                state=BLOCK,
                feedback="Envelope tool does not match bound spec.",
            )
        return GateResult(name="Integrity", state=PASS, feedback="Spec and envelope align.")

    def _responsibility(self, call: CallEnvelope, spec: ToolSpec) -> GateResult:
        if not call.operator.strip():
            return GateResult(
                name="Responsibility",
                state=BLOCK,
                feedback="Operator is blank. Name one accountable operator.",
            )
        return GateResult(
            name="Responsibility",
            state=PASS,
            feedback=f"Operator named: {call.operator.strip()}.",
        )


assert GATE_NAMES == (
    "Definition",
    "Evidence",
    "Impact",
    "Integrity",
    "Responsibility",
)
