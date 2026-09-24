"""FragGate CLI: human text by default, ResultEnvelope JSON with --json."""

from __future__ import annotations

import argparse
import errno
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable

from fraggate.envelopes import ResultEnvelope
from fraggate.errors import FragGateError
from fraggate.human import (
    render_text,
    root_help,
    version_payload,
    version_text,
    view_for,
    welcome_payload,
    welcome_text,
)
from fraggate.kernel import FragGate
from fraggate.ui import bind_server


class UsageError(Exception):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__(text)


class FragParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        if getattr(self, "fraggate_root", False):
            return root_help()
        return super().format_help()

    def error(self, message: str) -> None:
        self.exit(2, explain_parse_error(self.prog, message) + "\n")


def _default_root() -> Path:
    override = os.environ.get("FRAGGATE_HOME")
    if override:
        return Path(override)
    return Path.cwd() / ".fraggate"


def _ledger_path(args: argparse.Namespace) -> Path:
    root = Path(args.home) if getattr(args, "home", None) else _default_root()
    return root / "ledger.jsonl"


def _open_kernel(args: argparse.Namespace) -> FragGate:
    root = Path(args.home) if getattr(args, "home", None) else _default_root()
    session_id = getattr(args, "session", None) or os.environ.get("FRAGGATE_SESSION") or "cli"
    operator = getattr(args, "operator", None) or os.environ.get("FRAGGATE_OPERATOR") or "operator"
    return FragGate(session_id=session_id, operator=operator, ledger_path=root / "ledger.jsonl")


def explain_kernel_open(exc: FragGateError) -> str:
    if exc.message == "no second kernel for the same operator session":
        return (
            "This session already has a kernel open.\n"
            f"Code: {exc.code}\n\n"
            "Try: fraggate --session new-session ping"
        )
    if exc.message == "session_id is required":
        return f"A session id is required.\nCode: {exc.code}\n\nTry: fraggate --session cli ping"
    if exc.message == "operator is required":
        return (
            "An operator name is required.\n"
            f"Code: {exc.code}\n\n"
            'Try: fraggate --operator "Aziel Eliab" ping'
        )
    return f"{exc.message}\nCode: {exc.code}\n\nTry: fraggate --help"


def explain_parse_error(prog: str, message: str) -> str:
    command = prog.split()[-1]
    if command == "fraggate":
        command = ""
    if "invalid choice" in message:
        match = re.search(r"invalid choice: '([^']*)'", message)
        name = match.group(1) if match else "that"
        return f'Unknown command "{name}".\n\nTry: fraggate --help'
    if "required" in message:
        missing = message.split(":")[-1].strip()
        if command == "verify" or missing == "name":
            return "verify needs a tool name.\n\nTry: fraggate verify runtime.ping"
        if command == "receipt" or missing == "assertion":
            return 'receipt needs the text to hash.\n\nTry: fraggate receipt "kernel is local"'
        if command == "call" or missing == "tool":
            return "call needs a tool name.\n\nTry: fraggate call runtime.ping"
    if message.startswith("unrecognized arguments"):
        extra = message.split(":", 1)[-1].strip()
        return f"Unknown option {extra}.\n\nTry: fraggate --help"
    if "invalid int value" in message:
        return "The port needs to be a number from 0 to 65535.\n\nTry: fraggate ui --port 8765"
    return f"{message}\n\nTry: fraggate --help"


def peel_globals(argv: list[str]) -> tuple[list[str], dict[str, Any]]:
    peeled: dict[str, Any] = {"json": False, "home": None, "session": None, "operator": None}
    valued = {"--home": "home", "--session": "session", "--operator": "operator"}
    out: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--":
            out.extend(argv[index + 1 :])
            break
        if token == "--json":
            peeled["json"] = True
            index += 1
            continue
        split_key = None
        for flag in valued:
            if token.startswith(flag + "="):
                split_key = flag
                break
        if split_key is not None:
            value = token.split("=", 1)[1]
            if value == "":
                raise UsageError(f"{split_key} needs a value.\n\nTry: fraggate {split_key} VALUE ping")
            peeled[valued[split_key]] = value
            index += 1
            continue
        if token in valued:
            if index + 1 >= len(argv) or argv[index + 1].startswith("-"):
                raise UsageError(f"{token} needs a value.\n\nTry: fraggate {token} VALUE ping")
            peeled[valued[token]] = argv[index + 1]
            index += 2
            continue
        out.append(token)
        index += 1
    return out, peeled


def _emit(result: ResultEnvelope, *, json_mode: bool, doctor: bool, ledger_path: str | None) -> int:
    if json_mode:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_text(view_for(result, doctor=doctor, ledger_path=ledger_path)), end="")
    if doctor:
        passed = result.status == "ok" and result.result.get("alive") is True and not result.dry_run
        return 0 if passed else 2
    return 0 if result.status == "ok" else 2


def _with_kernel(args: argparse.Namespace, fn: Callable[[FragGate], int]) -> int:
    try:
        kernel = _open_kernel(args)
    except FragGateError as exc:
        print(explain_kernel_open(exc), file=sys.stderr)
        return 1
    try:
        return fn(kernel)
    finally:
        kernel.close()


def _parse_object(text: str, label: str) -> dict[str, Any]:
    hint = "fraggate call runtime.ping --args '{}'"
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UsageError(f"Could not read {label} as JSON ({exc.msg}).\n\nTry: {hint}") from exc
    if not isinstance(value, dict):
        raise UsageError(f"{label} must be a JSON object.\n\nTry: {hint}")
    return value


def _load_call_args(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if args.args:
        payload = _parse_object(args.args, "--args")
    if args.args_file:
        try:
            text = Path(args.args_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise UsageError(
                f"Could not read --args-file ({exc.strerror or exc}).\n\n"
                "Try: fraggate call runtime.ping --args '{}'"
            ) from exc
        payload = _parse_object(text, "--args-file")
    return payload


def cmd_ping(args: argparse.Namespace) -> int:
    ledger = str(_ledger_path(args))

    def run(kernel: FragGate) -> int:
        out = kernel.call(
            kernel.envelope(
                "runtime.ping",
                intent="Ping FragGate kernel for liveness, version, ledger tip, and registry digest.",
            )
        )
        return _emit(out, json_mode=args.json, doctor=False, ledger_path=ledger)

    return _with_kernel(args, run)


def cmd_list(args: argparse.Namespace) -> int:
    def run(kernel: FragGate) -> int:
        out = kernel.call(
            kernel.envelope(
                "registry.list",
                intent="List bound tools in the hashed registry.",
            )
        )
        return _emit(out, json_mode=args.json, doctor=False, ledger_path=None)

    return _with_kernel(args, run)


def cmd_verify(args: argparse.Namespace) -> int:
    def run(kernel: FragGate) -> int:
        out = kernel.call(
            kernel.envelope(
                "registry.verify",
                intent=f"Verify whether tool {args.name} is bound in the hashed registry.",
                args={"name": args.name},
            )
        )
        return _emit(out, json_mode=args.json, doctor=False, ledger_path=None)

    return _with_kernel(args, run)


def cmd_call(args: argparse.Namespace) -> int:
    def run(kernel: FragGate) -> int:
        try:
            payload = _load_call_args(args)
        except UsageError as exc:
            print(exc.text, file=sys.stderr)
            return 1
        intent = args.intent or f"Call registered tool {args.tool} through FragGate."
        out = kernel.call(
            kernel.envelope(
                args.tool,
                intent=intent,
                args=payload,
                dry_run=args.dry_run,
                allow_export=args.allow_export,
                allow_search=args.allow_search,
                destructive=args.destructive,
            )
        )
        return _emit(out, json_mode=args.json, doctor=False, ledger_path=None)

    return _with_kernel(args, run)


def cmd_receipt(args: argparse.Namespace) -> int:
    def run(kernel: FragGate) -> int:
        out = kernel.call(
            kernel.envelope(
                "runtime.receipt",
                intent="Hash an operator assertion into a FragGate receipt.",
                args={"assertion": args.assertion},
            )
        )
        return _emit(out, json_mode=args.json, doctor=False, ledger_path=None)

    return _with_kernel(args, run)


def cmd_doctor(args: argparse.Namespace) -> int:
    ledger = str(_ledger_path(args))

    def run(kernel: FragGate) -> int:
        out = kernel.call(
            kernel.envelope(
                "runtime.ping",
                intent="Ping FragGate kernel for liveness, version, ledger tip, and registry digest.",
            )
        )
        return _emit(out, json_mode=args.json, doctor=True, ledger_path=ledger)

    return _with_kernel(args, run)


def cmd_version(args: argparse.Namespace) -> int:
    if args.json:
        print(json.dumps(version_payload(), indent=2, sort_keys=True))
    else:
        print(version_text(), end="")
    return 0


def cmd_help(_: argparse.Namespace) -> int:
    print(root_help(), end="")
    return 0


def cmd_ui(args: argparse.Namespace) -> int:
    port = int(args.port)
    if port < 0 or port > 65535:
        print(
            "The port needs to be a number from 0 to 65535.\n\nTry: fraggate ui --port 8765",
            file=sys.stderr,
        )
        return 1
    try:
        kernel = _open_kernel(args)
    except FragGateError as exc:
        print(explain_kernel_open(exc), file=sys.stderr)
        return 1
    try:
        try:
            server = bind_server(kernel, "127.0.0.1", port, str(_ledger_path(args)))
        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                suggested = 8766 if port in (0, 8765) else port + 1
                print(
                    f"Port {port} is already in use.\n\nTry: fraggate ui --port {suggested}",
                    file=sys.stderr,
                )
                return 1
            print(
                f"Could not listen on 127.0.0.1:{port} ({exc.strerror or exc}).\n\n"
                "Try: fraggate ui --port 8765",
                file=sys.stderr,
            )
            return 1
        bound_port = server.server_address[1]
        print(f"Open http://127.0.0.1:{bound_port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
        finally:
            server.server_close()
    finally:
        kernel.close()
    return 0


def _add_sub(sub: argparse._SubParsersAction, name: str, help_text: str, description: str) -> argparse.ArgumentParser:
    parser = sub.add_parser(
        name,
        help=help_text,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    return parser


def build_parser() -> FragParser:
    parser = FragParser(prog="fraggate", add_help=True)
    parser.fraggate_root = True
    sub = parser.add_subparsers(dest="cmd", required=False)

    ping = _add_sub(
        sub,
        "ping",
        "Check that this kernel is alive",
        "Check that this kernel is alive.\n\n"
        "  fraggate ping\n"
        "  fraggate ping --json",
    )
    ping.set_defaults(func=cmd_ping)

    listed = _add_sub(
        sub,
        "list",
        "Show tools registered in this kernel",
        "Show tools registered in this kernel.\n\n  fraggate list",
    )
    listed.set_defaults(func=cmd_list)

    verify = _add_sub(
        sub,
        "verify",
        "Ask whether one tool name is registered",
        "Ask whether one tool name is registered.\n\n  fraggate verify runtime.ping",
    )
    verify.add_argument("name", help="Tool name")
    verify.set_defaults(func=cmd_verify)

    receipt = _add_sub(
        sub,
        "receipt",
        "Hash an assertion into the local ledger",
        'Hash an assertion into the local ledger.\n\n  fraggate receipt "kernel is local"',
    )
    receipt.add_argument("assertion", help="Text to hash")
    receipt.set_defaults(func=cmd_receipt)

    ui = _add_sub(
        sub,
        "ui",
        "Open the local page on this computer",
        "Open the local page on 127.0.0.1.\n\n"
        "Prints one line: Open http://127.0.0.1:<port>/\n"
        "GET does not call the kernel. POST runs a real call.",
    )
    ui.add_argument("--port", type=int, default=8765, help="Loopback port (default: 8765)")
    ui.set_defaults(func=cmd_ui)

    doctor = _add_sub(
        sub,
        "doctor",
        "Plain pass or fail for this kernel",
        "Ping this kernel and print pass or fail.\n\n"
        "  fraggate doctor\n"
        "  fraggate doctor --json",
    )
    doctor.set_defaults(func=cmd_doctor)

    call = _add_sub(
        sub,
        "call",
        "Run a registered tool",
        "Run a registered tool through this kernel.\n\n"
        "  fraggate call runtime.ping\n"
        "  fraggate call runtime.ping --dry-run\n"
        "  fraggate call runtime.ping --json\n\n"
        "Global options (--home, --session, --operator, --json) may appear\n"
        "before or after the command. See fraggate --help.",
    )
    call.add_argument("tool", help="Registered tool name")
    call.add_argument("--args", help="JSON object of tool arguments")
    call.add_argument("--args-file", help="File containing a JSON object of tool arguments")
    call.add_argument("--intent", help="Why this call is being made")
    call.add_argument("--dry-run", action="store_true", help="Record the call without executing the tool")
    call.add_argument("--allow-export", action="store_true", help="Allow an export side effect")
    call.add_argument("--allow-search", action="store_true", help="Allow search grounding")
    call.add_argument("--destructive", action="store_true", help="Mark a destructive call")
    call.set_defaults(func=cmd_call)

    version = _add_sub(
        sub,
        "version",
        "Print version, magic, and paper",
        "Print version, magic, and paper.\n\n  fraggate version",
    )
    version.set_defaults(func=cmd_version)

    helper = _add_sub(sub, "help", "Show this help", "Show FragGate help.")
    helper.set_defaults(func=cmd_help)
    return parser


def _emit_welcome(as_json: bool) -> None:
    if as_json:
        print(json.dumps(welcome_payload(), indent=2, sort_keys=True))
    else:
        print(welcome_text(), end="")


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    try:
        peeled_argv, globals_ = peel_globals(raw)
    except UsageError as exc:
        print(exc.text, file=sys.stderr)
        return 2
    parser = build_parser()
    try:
        args = parser.parse_args(peeled_argv)
    except SystemExit as exc:
        code = exc.code
        if code in (None, 0):
            return 0
        return code if isinstance(code, int) else 2
    args.json = bool(globals_["json"])
    if globals_["home"]:
        args.home = globals_["home"]
    if globals_["session"]:
        args.session = globals_["session"]
    if globals_["operator"]:
        args.operator = globals_["operator"]
    if not getattr(args, "cmd", None):
        _emit_welcome(args.json)
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
