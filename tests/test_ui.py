from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPConnection
from pathlib import Path

import pytest

from fraggate import FragGate
from fraggate.cli import main
from fraggate.ui import bind_server


@pytest.fixture
def ui_server(tmp_path: Path):
    ledger = tmp_path / "ledger.jsonl"
    kernel = FragGate(session_id=f"ui-{tmp_path.name}", operator="operator", ledger_path=ledger)
    server = bind_server(kernel, "127.0.0.1", 0, str(ledger))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        yield server, port, ledger
    finally:
        server.shutdown()
        server.server_close()
        kernel.close()


def _get(port: int, path: str, accept: str | None = None) -> tuple[int, str]:
    headers = {}
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def _post(port: int, path: str, form: dict[str, str] | None = None, accept: str | None = None) -> tuple[int, str]:
    data = urllib.parse.urlencode(form or {}).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def test_bind_is_loopback_only(tmp_path: Path) -> None:
    kernel = FragGate(session_id="bind", operator="op", ledger_path=tmp_path / "ledger.jsonl")
    try:
        with pytest.raises(OSError):
            bind_server(kernel, "0.0.0.0", 0, str(tmp_path / "ledger.jsonl"))
    finally:
        kernel.close()


def test_home_is_human_and_get_does_not_call(ui_server) -> None:
    _server, port, ledger = ui_server
    assert _server.server_address[0] == "127.0.0.1"
    status, html = _get(port, "/")
    assert status == 200
    assert "Running" in html
    assert "Background" in html
    assert "verifies this kernel in the background" in html
    assert "Check kernel" in html.split("<details", 1)[1]
    assert "Check this kernel" not in html
    assert 'name="viewport"' in html
    assert "prefers-color-scheme" in html
    assert ":focus-visible" in html
    assert "#c9a227" in html
    assert "<details" in html
    assert "Advanced" in html
    assert "open" not in html.split("<details", 1)[1].split(">", 1)[0]
    assert "what this is not" not in html.lower()
    assert "Aziel Eliab" in html
    before_details = html.split("<details", 1)[0]
    assert 'class="primary"' not in before_details
    assert "Open http" not in html
    assert not ledger.exists()

    status, payload = _get(port, "/?format=json")
    assert status == 200
    body = json.loads(payload)
    assert body["author"] == "Aziel Eliab"
    assert body["status"] == "running"
    assert body["next"] == "fraggate ping"
    assert "alive" not in body
    assert not ledger.exists()


def test_ping_html_and_json(ui_server) -> None:
    _server, port, ledger = ui_server
    status, html = _post(port, "/ping")
    assert status == 200
    assert "Kernel is alive." in html
    assert "Show registered tools" in html
    assert ledger.exists()
    lines_after_ping = [
        line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(lines_after_ping) == 1

    status, raw = _post(port, "/ping", accept="application/json")
    assert status == 200
    payload = json.loads(raw)
    assert payload["status"] == "ok"
    assert payload["tool"] == "runtime.ping"
    assert payload["result"]["alive"] is True
    assert "ledger_hash" in payload


def test_bad_name_is_escaped_and_plain(ui_server) -> None:
    _server, port, _ledger = ui_server
    status, html = _post(port, "/verify", {"name": "<script>"})
    assert status == 200
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "is not registered" in html

    status, html = _post(port, "/verify", {"name": ""})
    assert status == 400
    assert "Enter a tool name." in html
    assert "fraggate verify runtime.ping" in html


def test_service_status_reports_running_without_a_call(ui_server, capsys) -> None:
    _server, port, ledger = ui_server
    assert main(["service", "status", "--port", str(port)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Running.")
    assert "background" in out
    assert "Kernel is alive" not in out
    assert not ledger.exists()
    assert main(["--json", "service", "status", "--port", str(port)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "running"
    assert payload["port"] == port
    assert "alive" not in payload
    assert not ledger.exists()


def test_foreign_host_is_refused(ui_server) -> None:
    _server, port, ledger = ui_server
    connection = HTTPConnection("127.0.0.1", port, timeout=3)
    connection.request("GET", "/", headers={"Host": "evil.example"})
    response = connection.getresponse()
    assert response.status == 403
    response.read()
    assert not ledger.exists()
