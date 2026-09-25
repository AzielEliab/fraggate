"""Human-readable FragGate text. Machines use --json for the ResultEnvelope."""

from __future__ import annotations

import json
from dataclasses import dataclass

from fraggate.constants import AUTHOR, MAGIC, PAPER, VERSION
from fraggate.envelopes import ResultEnvelope

_NEXT = {
    "FG-HALLUC-TOOL": "fraggate list",
    "FG-FRAG-SCHEMA": "fraggate call --help",
    "FG-FRAG-ORPHAN": "fraggate list",
    "FG-HALLUC-FACT": "fraggate call --help",
    "FG-HALLUC-ARTIFACT": "fraggate call --help",
    "FG-GATE": "fraggate call --help",
    "FG-EXPORT": "fraggate call <tool> --allow-export",
    "FG-ERR": "fraggate --help",
}

_FRIENDLY = {
    "runtime.ping": "fraggate ping",
    "registry.list": "fraggate list",
    "registry.verify": "fraggate verify <name>",
    "runtime.receipt": 'fraggate receipt "text"',
    "claim.check": "fraggate call claim.check --help",
}


@dataclass(frozen=True)
class HumanView:
    heading: str
    paragraphs: tuple[str, ...] = ()
    fields: tuple[tuple[str, str], ...] = ()
    lines: tuple[str, ...] = ()
    items: tuple[tuple[str, str], ...] = ()
    next_command: str = ""
    ok: bool = True


def welcome_text() -> str:
    return (
        "FragGate verifies kernels in the background. Suite and agents call this door.\n"
        "Each call is written to a local ledger.\n"
        "\n"
        "Next: ask whether this kernel is alive.\n"
        "\n"
        "  fraggate ping\n"
        "\n"
        "Also:\n"
        "  fraggate doctor\n"
        "  fraggate service\n"
        "\n"
        f"Author: {AUTHOR}\n"
        f"FragGate {VERSION} ({MAGIC})\n"
    )


def welcome_payload() -> dict[str, object]:
    return {
        "name": "FragGate",
        "version": VERSION,
        "magic": MAGIC,
        "paper": PAPER,
        "author": AUTHOR,
        "summary": "FragGate verifies kernels in the background.",
        "next": "fraggate ping",
        "commands": [
            "ping",
            "doctor",
            "service",
            "list",
            "verify",
            "receipt",
            "help",
            "call",
            "version",
        ],
    }


def root_help() -> str:
    return f"""fraggate — verify kernels in the background

usage:
  fraggate [--home DIR] [--session ID] [--operator NAME] [--json] <command> [args]

commands:
  ping                 Ask whether this kernel is alive
  doctor               Plain pass or fail for this kernel
  service              Listen on this computer and report Running
  list                 Show tools registered in this kernel
  verify <name>        Ask whether one tool name is registered
  receipt <text>       Hash an assertion into the local ledger
  help                 Show this help

advanced:
  ui                   Diagnostic page (same listener as service)
  call <tool>          Run a registered tool
  version              Print version, magic, and paper

options:
  --home DIR           Ledger directory (default: ./.fraggate)
  --session ID         Session id (default: cli)
  --operator NAME      Operator name (default: operator)
  --json               Print the ResultEnvelope as JSON
  -h, --help           Show this help

examples:
  fraggate
  fraggate ping
  fraggate doctor
  fraggate service
  fraggate service status
  fraggate ping --json

Author: {AUTHOR}
FragGate {VERSION} ({MAGIC}) paper {PAPER}
"""


def version_text() -> str:
    from fraggate.constants import HOMEPAGE

    return f"FragGate {VERSION} ({MAGIC}) paper {PAPER}\nAuthor: {AUTHOR}\nHomepage: {HOMEPAGE}\n"


def version_payload() -> dict[str, str]:
    from fraggate.constants import HOMEPAGE

    return {
        "name": "FragGate",
        "version": VERSION,
        "magic": MAGIC,
        "paper": PAPER,
        "author": AUTHOR,
        "homepage": HOMEPAGE,
    }


def render_text(view: HumanView) -> str:
    parts: list[str] = [view.heading, ""]
    for paragraph in view.paragraphs:
        parts.append(paragraph)
        parts.append("")
    for name, description in view.items:
        parts.append(name)
        if description:
            parts.append(f"  {description}")
    if view.items:
        parts.append("")
    for line in view.lines:
        parts.append(line)
    if view.lines:
        parts.append("")
    for label, value in view.fields:
        parts.append(f"{label}: {value}")
    if view.fields:
        parts.append("")
    if view.next_command:
        parts.append(f"Next: {view.next_command}")
    text = "\n".join(parts).rstrip() + "\n"
    return text


def view_for(
    result: ResultEnvelope,
    *,
    doctor: bool = False,
    ledger_path: str | None = None,
) -> HumanView:
    if doctor:
        return _doctor_view(result, ledger_path=ledger_path)
    if result.status != "ok":
        return _refuse_view(result)
    if result.dry_run:
        return _dry_run_view(result)
    data = result.result or {}
    if result.tool == "runtime.ping":
        return _ping_view(result, data, ledger_path=ledger_path)
    if result.tool == "registry.list":
        return _list_view(data)
    if result.tool == "registry.verify":
        return _verify_view(data)
    if result.tool == "runtime.receipt":
        return _receipt_view(data)
    if result.tool == "claim.check":
        return _claim_view(data)
    return _generic_view(result, data)


def _doctor_view(result: ResultEnvelope, *, ledger_path: str | None) -> HumanView:
    data = result.result or {}
    if result.status == "ok" and data.get("alive") is True and not result.dry_run:
        ping = _ping_view(result, data, ledger_path=ledger_path, next_command="fraggate list")
        return HumanView(
            heading="Pass. This kernel is alive.",
            paragraphs=ping.paragraphs,
            fields=ping.fields,
            lines=ping.lines,
            next_command=ping.next_command,
            ok=True,
        )
    if result.status != "ok":
        refused = _refuse_view(result)
        heading = refused.heading
        if heading.startswith("Refused. "):
            heading = "Fail. " + heading[len("Refused. ") :]
        else:
            heading = "Fail. " + heading
        return HumanView(
            heading=heading,
            paragraphs=refused.paragraphs,
            fields=refused.fields,
            lines=refused.lines,
            next_command=refused.next_command,
            ok=False,
        )
    return HumanView(
        heading="Fail. This kernel did not report alive.",
        next_command="fraggate --help",
        ok=False,
    )


def _refuse_view(result: ResultEnvelope) -> HumanView:
    message = (result.error_message or "The kernel refused this call.").strip()
    fields: list[tuple[str, str]] = []
    if result.error_code:
        fields.append(("Code", result.error_code))
    if result.tool:
        fields.append(("Tool", result.tool))
    gate = result.gate or {}
    stopped = gate.get("blocked_at") if isinstance(gate, dict) else None
    if isinstance(stopped, str) and stopped:
        fields.append(("Stopped at", stopped))
    next_command = _NEXT.get(result.error_code or "", "fraggate --help")
    if result.error_code == "FG-EXPORT" and result.tool:
        next_command = f"fraggate call {result.tool} --allow-export"
    return HumanView(
        heading=f"Refused. {message}",
        fields=tuple(fields),
        next_command=next_command,
        ok=False,
    )


def _dry_run_view(result: ResultEnvelope) -> HumanView:
    tool = result.tool or "this tool"
    data = result.result or {}
    fields: list[tuple[str, str]] = [("Tool", tool)]
    args = data.get("args")
    if isinstance(args, dict) and args:
        fields.append(("Arguments", json.dumps(args, sort_keys=True)))
    return HumanView(
        heading=f"Dry run. {tool} was not executed.",
        paragraphs=("This dry run is recorded in the local ledger.",),
        fields=tuple(fields),
        next_command=f"fraggate call {tool}" if result.tool else "fraggate --help",
        ok=True,
    )


def _ping_view(
    result: ResultEnvelope,
    data: dict,
    *,
    ledger_path: str | None,
    next_command: str = "fraggate list",
) -> HumanView:
    alive = data.get("alive") is True
    heading = "Kernel is alive." if alive else "Kernel answered without reporting alive."
    fields: list[tuple[str, str]] = []
    _add(fields, "Version", data.get("version"))
    _add(fields, "Magic", data.get("magic"))
    _add(fields, "Paper", data.get("paper"))
    _add(fields, "Author", data.get("author"))
    _add(fields, "Session", data.get("session_id"))
    tools = data.get("tools")
    if isinstance(tools, list):
        fields.append(("Tools", str(len(tools))))
    if ledger_path:
        fields.append(("Ledger file", ledger_path))
    _add(fields, "Ledger receipt", result.ledger_hash)
    _add(fields, "Registry", result.registry_digest or data.get("registry_digest"))
    return HumanView(
        heading=heading,
        fields=tuple(fields),
        next_command=next_command,
        ok=alive,
    )


def _list_view(data: dict) -> HumanView:
    tools = data.get("tools")
    items: list[tuple[str, str]] = []
    if isinstance(tools, list):
        count = len(tools)
        heading = "1 registered tool" if count == 1 else f"{count} registered tools"
        for row in tools:
            if isinstance(row, dict):
                name = str(row.get("name") or "").strip()
                if not name:
                    continue
                items.append((name, str(row.get("description") or "").strip()))
            elif isinstance(row, str) and row.strip():
                items.append((row.strip(), ""))
    else:
        heading = "Registered tools"
    fields: list[tuple[str, str]] = []
    _add(fields, "Registry", data.get("digest"))
    return HumanView(
        heading=heading,
        fields=tuple(fields),
        items=tuple(items),
        next_command="fraggate verify runtime.ping",
        ok=True,
    )


def _verify_view(data: dict) -> HumanView:
    name = str(data.get("name") or "").strip() or "This name"
    if data.get("bound") is True:
        fields: list[tuple[str, str]] = []
        _add(fields, "Version", data.get("version"))
        _add(fields, "Spec hash", data.get("spec_hash"))
        _add(fields, "Adapter", data.get("adapter"))
        nxt = _FRIENDLY.get(name, f"fraggate call {name}")
        return HumanView(
            heading=f"{name} is registered.",
            fields=tuple(fields),
            next_command=nxt,
            ok=True,
        )
    if data.get("bound") is False:
        return HumanView(
            heading=f"{name} is not registered.",
            next_command="fraggate list",
            ok=True,
        )
    return HumanView(
        heading="Verify finished without a bound answer.",
        next_command="fraggate list",
        ok=True,
    )


def _receipt_view(data: dict) -> HumanView:
    fields: list[tuple[str, str]] = []
    _add(fields, "Hash", data.get("hash"))
    _add(fields, "Time", data.get("ts"))
    _add(fields, "Operator", data.get("operator"))
    assertion = data.get("assertion")
    paragraphs: tuple[str, ...] = ()
    if isinstance(assertion, str) and assertion:
        paragraphs = (assertion,)
    return HumanView(
        heading="Receipt written.",
        paragraphs=paragraphs,
        fields=tuple(fields),
        next_command="fraggate list",
        ok=True,
    )


def _claim_view(data: dict) -> HumanView:
    if data.get("accepted") is True:
        fields: list[tuple[str, str]] = []
        count = data.get("count")
        if isinstance(count, int):
            fields.append(("Count", str(count)))
        return HumanView(
            heading="Claim accepted.",
            fields=tuple(fields),
            next_command="fraggate list",
            ok=True,
        )
    return _generic_view_data("claim.check", data)


def _generic_view(result: ResultEnvelope, data: dict) -> HumanView:
    return _generic_view_data(result.tool or "tool", data)


def _generic_view_data(tool: str, data: dict) -> HumanView:
    fields: list[tuple[str, str]] = []
    lines: list[str] = []
    for key in sorted(data):
        value = data[key]
        if isinstance(value, (dict, list)):
            lines.append(f"{key}:")
            lines.append(json.dumps(value, indent=2, sort_keys=True))
        elif value is not None:
            fields.append((str(key), str(value)))
    return HumanView(
        heading=f"Finished {tool}.",
        fields=tuple(fields),
        lines=tuple(lines),
        next_command="fraggate list",
        ok=True,
    )


def _add(fields: list[tuple[str, str]], label: str, value: object) -> None:
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    fields.append((label, text))
