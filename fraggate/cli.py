"""FragGate CLI: ping / list / verify / call / receipt."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from fraggate.constants import AUTHOR, HOMEPAGE, MAGIC, PAPER, VERSION
from fraggate.envelopes import ResultEnvelope
from fraggate.kernel import FragGate


def _default_root() -> Path:
    override = os.environ.get("FRAGGATE_HOME")
    if override:
        return Path(override)
    return Path.cwd() / ".fraggate"


def _open_kernel(args: argparse.Namespace) -> FragGate:
    root = Path(args.home) if getattr(args, "home", None) else _default_root()
    session_id = getattr(args, "session", None) or os.environ.get("FRAGGATE_SESSION") or "cli"
    operator = getattr(args, "operator", None) or os.environ.get("FRAGGATE_OPERATOR") or "operator"
    ledger = root / "ledger.jsonl"
    return FragGate(session_id=session_id, operator=operator, ledger_path=ledger)


def _print(result: ResultEnvelope, *, raw: bool) -> int:
    payload = result.to_dict()
    if raw:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.status == "ok" else 2


def cmd_ping(args: argparse.Namespace) -> int:
    kernel = _open_kernel(args)
    try:
        out = kernel.call(
            kernel.envelope(
                "runtime.ping",
                intent="Ping FragGate kernel for liveness, version, ledger tip, and registry digest.",
            )
        )
        return _print(out, raw=args.json)
    finally:
        kernel.close()


def cmd_list(args: argparse.Namespace) -> int:
    kernel = _open_kernel(args)
    try:
        out = kernel.call(
            kernel.envelope(
                "registry.list",
                intent="List bound tools in the hashed FragGate registry.",
            )
        )
        return _print(out, raw=args.json)
    finally:
        kernel.close()


def cmd_verify(args: argparse.Namespace) -> int:
    kernel = _open_kernel(args)
    try:
        out = kernel.call(
            kernel.envelope(
                "registry.verify",
                intent=f"Verify whether tool {args.name} is bound in the hashed registry.",
                args={"name": args.name},
            )
        )
        return _print(out, raw=args.json)
    finally:
        kernel.close()


def cmd_call(args: argparse.Namespace) -> int:
    kernel = _open_kernel(args)
    try:
        payload: dict[str, Any] = {}
        if args.args:
            payload = json.loads(args.args)
            if not isinstance(payload, dict):
                print("error: --args must be a JSON object", file=sys.stderr)
                return 1
        if args.args_file:
            loaded = json.loads(Path(args.args_file).read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                print("error: --args-file must contain a JSON object", file=sys.stderr)
                return 1
            payload = loaded
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
        return _print(out, raw=args.json)
    finally:
        kernel.close()


def cmd_receipt(args: argparse.Namespace) -> int:
    kernel = _open_kernel(args)
    try:
        out = kernel.call(
            kernel.envelope(
                "runtime.receipt",
                intent="Hash an operator assertion into a FragGate receipt.",
                args={"assertion": args.assertion},
            )
        )
        return _print(out, raw=args.json)
    finally:
        kernel.close()


def cmd_version(_: argparse.Namespace) -> int:
    print(f"FragGate {VERSION} ({MAGIC}) paper {PAPER}")
    print(f"Author: {AUTHOR}")
    print(f"Homepage: {HOMEPAGE}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fraggate",
        description="FragGate FG-0.1 — kernel against tool fragmentation and model hallucination.",
    )
    parser.add_argument("--home", help="Directory for ledger.jsonl (default: ./.fraggate)")
    parser.add_argument("--session", help="Operator session id (default: cli)")
    parser.add_argument("--operator", help="Accountable operator name")
    parser.add_argument("--json", action="store_true", help="Print ResultEnvelope JSON (always on)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ping = sub.add_parser("ping", help="runtime.ping")
    p_ping.set_defaults(func=cmd_ping)

    p_list = sub.add_parser("list", help="registry.list")
    p_list.set_defaults(func=cmd_list)

    p_verify = sub.add_parser("verify", help="registry.verify")
    p_verify.add_argument("name")
    p_verify.set_defaults(func=cmd_verify)

    p_call = sub.add_parser("call", help="Call any bound tool through a CallEnvelope")
    p_call.add_argument("tool")
    p_call.add_argument("--args", help="JSON object of tool args")
    p_call.add_argument("--args-file", help="Path to JSON object of tool args")
    p_call.add_argument("--intent", help="Operator intent")
    p_call.add_argument("--dry-run", action="store_true")
    p_call.add_argument("--allow-export", action="store_true")
    p_call.add_argument("--allow-search", action="store_true")
    p_call.add_argument("--destructive", action="store_true")
    p_call.set_defaults(func=cmd_call)

    p_receipt = sub.add_parser("receipt", help="runtime.receipt")
    p_receipt.add_argument("assertion")
    p_receipt.set_defaults(func=cmd_receipt)

    p_ver = sub.add_parser("version", help="Print kernel version")
    p_ver.set_defaults(func=cmd_version)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
