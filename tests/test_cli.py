from __future__ import annotations

import json
from pathlib import Path

from fraggate.cli import main


def test_cli_ping_list_verify(tmp_path: Path, capsys) -> None:
    home = str(tmp_path / "home")
    session = "cli-test"
    assert main(["--home", home, "--session", session, "ping"]) == 0
    ping = json.loads(capsys.readouterr().out)
    assert ping["status"] == "ok"
    assert ping["result"]["alive"] is True

    assert main(["--home", home, "--session", session, "list"]) == 0
    listed = json.loads(capsys.readouterr().out)
    names = {row["name"] for row in listed["result"]["tools"]}
    assert "runtime.ping" in names

    assert main(["--home", home, "--session", session, "verify", "runtime.ping"]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["result"]["bound"] is True

    assert main(["--home", home, "--session", session, "call", "ghost.tool"]) == 2
    refused = json.loads(capsys.readouterr().out)
    assert refused["error_code"] == "FG-HALLUC-TOOL"

    ledger = Path(home) / "ledger.jsonl"
    lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 4
