from __future__ import annotations

import json
import socket
from pathlib import Path

from fraggate import FragGate
from fraggate.cli import main


def test_cli_ping_list_verify(tmp_path: Path, capsys) -> None:
    home = str(tmp_path / "home")
    session = "cli-test"
    base = ["--json", "--home", home, "--session", session]
    assert main([*base, "ping"]) == 0
    ping = json.loads(capsys.readouterr().out)
    assert ping["status"] == "ok"
    assert ping["result"]["alive"] is True

    kernel = FragGate(session_id="shape", operator="op", ledger_path=tmp_path / "shape.jsonl")
    try:
        sample = kernel.call(
            kernel.envelope("runtime.ping", intent="Ping FragGate kernel for liveness.")
        )
    finally:
        kernel.close()
    assert set(ping) == set(sample.to_dict())
    assert set(ping["result"]) == {
        "alive",
        "magic",
        "version",
        "paper",
        "author",
        "session_id",
        "ledger_tip",
        "registry_digest",
        "tools",
    }

    assert main([*base, "list"]) == 0
    listed = json.loads(capsys.readouterr().out)
    names = {row["name"] for row in listed["result"]["tools"]}
    assert "runtime.ping" in names

    assert main([*base, "verify", "runtime.ping"]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["result"]["bound"] is True

    assert main([*base, "call", "ghost.tool"]) == 2
    refused = json.loads(capsys.readouterr().out)
    assert refused["error_code"] == "FG-HALLUC-TOOL"
    assert "error_message" in refused

    ledger = Path(home) / "ledger.jsonl"
    lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 4


def test_help_is_short(capsys) -> None:
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "commands:" in out
    assert "advanced:" in out
    assert "examples:" in out
    assert "fraggate ping" in out
    commands = out.split("commands:", 1)[1].split("advanced:", 1)[0]
    advanced = out.split("advanced:", 1)[1].split("examples:", 1)[0]
    examples = out.split("examples:", 1)[1]
    assert "service" in commands
    assert "ui" not in commands
    assert "ui" in advanced
    assert "fraggate ui" not in examples
    assert "fraggate service" in examples
    assert "changelog" not in out.lower()
    assert "what this is not" not in out.lower()
    assert main(["ping", "--help"]) == 0
    assert "alive" in capsys.readouterr().out.lower()


def test_bare_welcome(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "background" in out
    assert "local ledger" in out
    assert "fraggate ping" in out
    assert "fraggate doctor" in out
    assert "fraggate service" in out
    assert "fraggate ui" not in out
    assert "Aziel Eliab" in out
    assert not out.lstrip().startswith("{")
    assert "what this is not" not in out.lower()


def test_welcome_json(capsys) -> None:
    assert main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["author"] == "Aziel Eliab"
    assert payload["next"] == "fraggate ping"
    assert payload["summary"].startswith("FragGate verifies kernels in the background")
    assert payload["commands"][:3] == ["ping", "doctor", "service"]
    assert "ui" not in payload["commands"]


def test_unknown_command(capsys) -> None:
    assert main(["bogus"]) == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus".' in err
    assert "fraggate --help" in err
    assert "Traceback" not in err


def test_verify_missing_name(capsys) -> None:
    assert main(["verify"]) == 2
    err = capsys.readouterr().err
    assert "tool name" in err
    assert "fraggate verify runtime.ping" in err
    assert "Traceback" not in err


def test_human_ping_and_refuse(tmp_path: Path, capsys) -> None:
    home = str(tmp_path / "home")
    session = "human"
    assert main(["--home", home, "--session", session, "ping"]) == 0
    out = capsys.readouterr().out
    assert "Kernel is alive." in out
    assert "Next: fraggate list" in out
    assert "Aziel Eliab" in out
    assert not out.lstrip().startswith("{")

    assert main(["--home", home, "--session", session, "call", "ghost.tool"]) == 2
    refused = capsys.readouterr().out
    assert "FG-HALLUC-TOOL" in refused
    assert "Next: fraggate list" in refused
    assert "Traceback" not in refused


def test_json_flag_after_command(tmp_path: Path, capsys) -> None:
    home = str(tmp_path / "home")
    assert main(["ping", "--json", "--home", home, "--session", "after"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tool"] == "runtime.ping"
    assert payload["result"]["alive"] is True


def test_bad_args_json(tmp_path: Path, capsys) -> None:
    assert main(["--home", str(tmp_path), "--session", "badjson", "call", "runtime.ping", "--args", "[]"]) == 1
    err = capsys.readouterr().err
    assert "JSON object" in err
    assert "fraggate call runtime.ping --args" in err
    assert "Traceback" not in err


def test_dry_run_does_not_claim_alive(tmp_path: Path, capsys) -> None:
    assert (
        main(
            [
                "--home",
                str(tmp_path),
                "--session",
                "dry",
                "call",
                "runtime.ping",
                "--dry-run",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "Dry run." in out
    assert "was not executed" in out
    assert "Kernel is alive" not in out


def test_doctor_pass(tmp_path: Path, capsys) -> None:
    home = str(tmp_path / "home")
    assert main(["--home", home, "--session", "doc", "doctor"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Pass. This kernel is alive.")
    assert main(["--json", "--home", home, "--session", "doc2", "doctor"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tool"] == "runtime.ping"
    assert payload["result"]["alive"] is True


def test_second_session_is_plain(tmp_path: Path, capsys) -> None:
    kernel = FragGate(session_id="same", operator="op", ledger_path=tmp_path / "a.jsonl")
    try:
        code = main(["--home", str(tmp_path / "home"), "--session", "same", "ping"])
    finally:
        kernel.close()
    assert code == 1
    err = capsys.readouterr().err
    assert "already has a kernel open" in err
    assert "fraggate --session new-session ping" in err
    assert "Traceback" not in err


def test_version_human_and_json(capsys) -> None:
    assert main(["version"]) == 0
    text = capsys.readouterr().out
    assert "Aziel Eliab" in text
    assert "0.1.0" in text
    assert main(["version", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["author"] == "Aziel Eliab"
    assert payload["version"] == "0.1.0"
    assert payload["magic"] == "FGT1"


def test_service_status_quiet(capsys) -> None:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    assert main(["service", "status", "--port", str(port)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Quiet.")
    assert "fraggate service" in out
    assert "Kernel is alive" not in out
    assert main(["--json", "service", "status", "--port", str(port)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "quiet"
    assert payload["port"] == port
