"""Loopback page for the local FragGate kernel. GET does not call the kernel."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from fraggate.builtins import builtin_specs
from fraggate.constants import AUTHOR, MAGIC, PAPER, VERSION
from fraggate.envelopes import ResultEnvelope
from fraggate.human import HumanView, render_text, root_help, view_for
from fraggate.kernel import FragGate

_MAX_BODY = 65536

_CSS = """
:root {
  color-scheme: light dark;
  --bg: #f6f4ef;
  --surface: #fffdf8;
  --text: #1c1915;
  --muted: #3f3a33;
  --line: #e4dfd4;
  --gold: #c9a227;
  --primary: #1c1915;
  --on-primary: #f6f4ef;
  --danger: #7a2e2e;
  --ok: #2d5a3d;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #12110f;
    --surface: #1c1b18;
    --text: #f3efe6;
    --muted: #d2cdc2;
    --line: #34322c;
    --gold: #c9a227;
    --primary: #c9a227;
    --on-primary: #1a160c;
    --danger: #f0b4b4;
    --ok: #b7d7c0;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  font-size: 1.05rem;
}
.wrap {
  width: min(40rem, 100%);
  margin: 0 auto;
  padding: 1.25rem 1.1rem 3rem;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.75rem;
}
.brand { font-weight: 650; letter-spacing: -0.02em; text-decoration: none; }
nav { display: flex; gap: 0.9rem; }
a { color: inherit; }
h1 {
  font-size: 1.7rem;
  line-height: 1.2;
  letter-spacing: -0.03em;
  font-weight: 650;
  margin: 0 0 0.6rem;
}
.lead { font-size: 1.08rem; max-width: 38rem; margin: 0 0 1.25rem; }
p { margin: 0 0 0.9rem; }
.muted { color: var(--muted); }
button, .btn {
  font: inherit;
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 0.7rem 1.15rem;
  min-height: 2.75rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.primary { background: var(--primary); color: var(--on-primary); }
.ghost { background: transparent; color: var(--text); border-color: var(--line); }
button:focus-visible, a:focus-visible, input:focus-visible,
textarea:focus-visible, summary:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 3px;
}
form { margin: 0 0 1rem; }
label { display: block; font-size: 0.92rem; margin: 0.8rem 0 0.3rem; }
input[type="text"], textarea {
  width: 100%;
  max-width: 100%;
  font: inherit;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
}
textarea { min-height: 5.5rem; resize: vertical; }
.check { display: flex; gap: 0.55rem; align-items: flex-start; margin: 0.45rem 0; }
.check input { margin-top: 0.35rem; }
details.advanced {
  margin-top: 1.5rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 0.35rem 0.95rem 0.8rem;
}
summary { cursor: pointer; font-weight: 650; padding: 0.7rem 0; }
.result {
  border-left: 3px solid var(--gold);
  padding-left: 0.9rem;
  margin-bottom: 1.1rem;
}
.result.bad { border-left-color: var(--danger); }
dl { margin: 0.4rem 0 0.8rem; }
dl div { margin: 0 0 0.45rem; }
dt { color: var(--muted); font-size: 0.92rem; }
dd { margin: 0; overflow-wrap: anywhere; }
.tools { margin: 0.2rem 0 0.8rem; padding: 0; list-style: none; }
.tools li { margin: 0 0 0.7rem; }
.tools span { display: block; color: var(--muted); }
pre, code { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.9rem 1rem;
}
footer { margin-top: 2rem; color: var(--muted); font-size: 0.92rem; }
@media (min-width: 480px) {
  dl div { display: grid; grid-template-columns: 9.5rem 1fr; gap: 0.5rem; }
}
@media (max-width: 480px) {
  .wrap { padding: 1rem 0.9rem 2.5rem; }
  button, .btn { width: 100%; }
  header { align-items: flex-start; }
}
"""


class InputProblem(Exception):
    def __init__(self, message: str, try_command: str) -> None:
        self.message = message
        self.try_command = try_command
        super().__init__(message)


class FragHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], kernel: FragGate, ledger_path: str) -> None:
        self.kernel = kernel
        self.ledger_path = ledger_path
        self.call_lock = threading.Lock()
        super().__init__(server_address, FragHandler)


class FragHandler(BaseHTTPRequestHandler):
    server: FragHTTPServer

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        if not self._host_ok():
            return
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        if path == "/":
            if _wants_json(self.headers.get("Accept", ""), query):
                self._send_json(200, _status_payload())
            else:
                self._send_html(200, _home_page())
            return
        if path == "/about":
            self._send_html(200, _about_page(self.server.ledger_path))
            return
        if path == "/help":
            self._send_html(200, _help_page())
            return
        self._send_miss()

    def do_POST(self) -> None:  # noqa: N802
        if not self._host_ok():
            return
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        as_json = _wants_json(self.headers.get("Accept", ""), query)
        try:
            form = self._read_form()
            view, envelope = self._dispatch(path, form)
        except InputProblem as exc:
            if as_json:
                self._send_json(
                    400,
                    {
                        "status": "error",
                        "error_message": exc.message,
                        "next": exc.try_command,
                    },
                )
            else:
                self._send_html(400, _problem_page(exc.message, exc.try_command))
            return
        except KeyError:
            self._send_miss()
            return
        if as_json:
            self._send_json(200 if envelope.status == "ok" else 422, envelope.to_dict())
            return
        self._send_html(200, _result_page(view))

    def _dispatch(self, path: str, form: dict[str, str]) -> tuple[HumanView, ResultEnvelope]:
        kernel = self.server.kernel
        ledger = self.server.ledger_path
        if path == "/ping":
            envelope = self._call(kernel, "runtime.ping", "Ping FragGate kernel for liveness, version, ledger tip, and registry digest.", {})
            return view_for(envelope, ledger_path=ledger), envelope
        if path == "/list":
            envelope = self._call(kernel, "registry.list", "List bound tools in the hashed registry.", {})
            return view_for(envelope, ledger_path=ledger), envelope
        if path == "/verify":
            name = form.get("name", "").strip()
            if not name:
                raise InputProblem("Enter a tool name.", "fraggate verify runtime.ping")
            envelope = self._call(
                kernel,
                "registry.verify",
                f"Verify whether tool {name} is bound in the hashed registry.",
                {"name": name},
            )
            return view_for(envelope, ledger_path=ledger), envelope
        if path == "/receipt":
            assertion = form.get("assertion", "").strip()
            if not assertion:
                raise InputProblem('Enter the text to hash.', 'fraggate receipt "kernel is local"')
            envelope = self._call(
                kernel,
                "runtime.receipt",
                "Hash an operator assertion into a FragGate receipt.",
                {"assertion": assertion},
            )
            return view_for(envelope, ledger_path=ledger), envelope
        if path == "/call":
            tool = form.get("tool", "").strip()
            if not tool:
                raise InputProblem("Enter a tool name.", "fraggate call runtime.ping")
            raw_args = form.get("args", "").strip() or "{}"
            try:
                payload = json.loads(raw_args)
            except json.JSONDecodeError as exc:
                raise InputProblem(
                    f"Arguments must be a JSON object ({exc.msg}).",
                    "fraggate call runtime.ping --args '{}'",
                ) from exc
            if not isinstance(payload, dict):
                raise InputProblem(
                    "Arguments must be a JSON object.",
                    "fraggate call runtime.ping --args '{}'",
                )
            intent = form.get("intent", "").strip() or f"Call registered tool {tool} through FragGate."
            envelope = self._call(
                kernel,
                tool,
                intent,
                payload,
                dry_run=form.get("dry_run") == "1",
                allow_export=form.get("allow_export") == "1",
                allow_search=form.get("allow_search") == "1",
                destructive=form.get("destructive") == "1",
            )
            return view_for(envelope, ledger_path=ledger), envelope
        raise KeyError(path)

    def _call(self, kernel: FragGate, tool: str, intent: str, args: dict[str, Any], **flags: bool) -> ResultEnvelope:
        with self.server.call_lock:
            return kernel.call(kernel.envelope(tool, intent=intent, args=args, **flags))

    def _read_form(self) -> dict[str, str]:
        length_raw = self.headers.get("Content-Length") or "0"
        try:
            length = int(length_raw)
        except ValueError as exc:
            raise InputProblem("The form body was not readable.", "fraggate ui") from exc
        if length < 0 or length > _MAX_BODY:
            raise InputProblem("That form is too large.", "fraggate ui")
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        parsed = parse_qs(raw, keep_blank_values=True)
        return {key: values[0] if values else "" for key, values in parsed.items()}

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").split(",")[0].strip().lower()
        name = host.split(":")[0]
        if name in {"127.0.0.1", "localhost"}:
            return True
        body = b"Open this page on 127.0.0.1.\n"
        self._send(403, body, "text/plain; charset=utf-8")
        return False

    def _send_miss(self) -> None:
        if _wants_json(self.headers.get("Accept", ""), parse_qs(urlparse(self.path).query)):
            self._send_json(
                404,
                {
                    "status": "error",
                    "error_message": "That page is not in FragGate.",
                    "next": "/",
                },
            )
            return
        self._send_html(
            404,
            _problem_page("That page is not in FragGate.", "fraggate ui"),
        )

    def _send_html(self, status: int, html: str) -> None:
        self._send(status, html.encode("utf-8"), "text/html; charset=utf-8")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def bind_server(kernel: FragGate, host: str, port: int, ledger_path: str) -> FragHTTPServer:
    if host != "127.0.0.1":
        raise OSError("FragGate ui listens on 127.0.0.1 only")
    return FragHTTPServer((host, port), kernel, ledger_path)


def _wants_json(accept: str, query: dict[str, list[str]]) -> bool:
    if query.get("format", [""])[0] == "json":
        return True
    types = [part.split(";", 1)[0].strip().lower() for part in accept.split(",") if part.strip()]
    if "text/html" in types:
        return False
    return "application/json" in types


def _status_payload() -> dict[str, Any]:
    return {
        "name": "FragGate",
        "version": VERSION,
        "magic": MAGIC,
        "paper": PAPER,
        "author": AUTHOR,
        "summary": "FragGate runs a registered tool and writes each call to a local ledger.",
        "loopback": "127.0.0.1",
        "next": "POST /ping",
    }


def _layout(title: str, main: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(title)}</title>\n<style>{_CSS}</style>\n</head>\n<body>\n"
        '<div class="wrap">\n<header>\n'
        '<a class="brand" href="/">FragGate</a>\n<nav>\n'
        '<a href="/about">About</a>\n<a href="/help">Help</a>\n</nav>\n</header>\n'
        f"<main>\n{main}\n</main>\n<footer><p>{_esc(AUTHOR)} · FragGate {_esc(VERSION)}</p></footer>\n"
        "</div>\n</body>\n</html>\n"
    )


def _home_page() -> str:
    main = (
        "<h1>Check this kernel</h1>\n"
        '<p class="lead">FragGate runs a registered tool and writes each call to a local ledger.</p>\n'
        '<form method="post" action="/ping">\n'
        '<button class="primary" type="submit">Check this kernel</button>\n'
        "</form>\n"
        + _advanced_html()
    )
    return _layout("FragGate", main)


def _about_page(ledger_path: str) -> str:
    items = []
    for spec in builtin_specs():
        items.append(f"<li><strong>{_esc(spec.name)}</strong> <span>{_esc(spec.description)}</span></li>")
    main = (
        "<h1>About</h1>\n"
        "<p>This page runs the FragGate kernel on this computer. "
        "Each button is a real call, and the call is appended to the ledger file.</p>\n"
        "<dl>\n"
        f"<div><dt>Author</dt><dd>{_esc(AUTHOR)}</dd></div>\n"
        f"<div><dt>Version</dt><dd>{_esc(VERSION)}</dd></div>\n"
        f"<div><dt>Magic</dt><dd>{_esc(MAGIC)}</dd></div>\n"
        f"<div><dt>Paper</dt><dd>{_esc(PAPER)}</dd></div>\n"
        f"<div><dt>Ledger file</dt><dd>{_esc(ledger_path)}</dd></div>\n"
        "</dl>\n"
        "<h2>Built-in tools</h2>\n"
        f'<ul class="tools">{"".join(items)}</ul>\n'
    )
    return _layout("About · FragGate", main)


def _help_page() -> str:
    main = "<h1>Help</h1>\n" + f"<pre>{_esc(root_help())}</pre>\n"
    return _layout("Help · FragGate", main)


def _problem_page(message: str, try_command: str) -> str:
    main = (
        f'<div class="result bad"><h1>{_esc(message)}</h1></div>\n'
        f"<p>Try: <code>{_esc(try_command)}</code></p>\n"
        '<p><a class="btn primary" href="/">Back home</a></p>\n'
        + _advanced_html()
    )
    return _layout("FragGate", main)


def _result_page(view: HumanView) -> str:
    klass = "result" if view.ok else "result bad"
    fields = "".join(
        f"<div><dt>{_esc(label)}</dt><dd>{_esc(value)}</dd></div>" for label, value in view.fields
    )
    paragraphs = "".join(f"<p>{_esc(paragraph)}</p>" for paragraph in view.paragraphs)
    lines = ""
    if view.items:
        rows = []
        for name, description in view.items:
            detail = f"<span>{_esc(description)}</span>" if description else ""
            rows.append(f"<li><strong>{_esc(name)}</strong>{detail}</li>")
        lines = '<ul class="tools">' + "".join(rows) + "</ul>"
    elif view.lines:
        lines = "<ul class=\"tools\">" + "".join(f"<li>{_esc(line)}</li>" for line in view.lines) + "</ul>"
    # Tool descriptions are indented lines. Keep them readable inside the list item text.
    next_html = ""
    if view.next_command:
        next_html = f"<p>Next: <code>{_esc(view.next_command)}</code></p>\n" + _next_button(view.next_command)
    main = (
        f'<div class="{klass}"><h1>{_esc(view.heading)}</h1>{paragraphs}'
        f"{lines}"
        f"{('<dl>' + fields + '</dl>') if fields else ''}</div>\n"
        f"{next_html}\n"
        + _advanced_html()
    )
    return _layout("FragGate", main)


def _next_button(command: str) -> str:
    parts = command.split()
    if len(parts) < 2 or parts[0] != "fraggate":
        return '<p><a class="btn primary" href="/">Back home</a></p>'
    cmd = parts[1]
    if cmd == "list":
        return _post_button("/list", "Show registered tools", {})
    if cmd == "ping":
        return _post_button("/ping", "Check this kernel", {})
    if cmd == "verify" and len(parts) >= 3 and not parts[2].startswith("<"):
        return _post_button("/verify", "Check this tool", {"name": parts[2]})
    if cmd == "call" and len(parts) >= 3 and not parts[2].startswith("<"):
        return _post_button("/call", "Run this tool", {"tool": parts[2], "args": "{}"})
    if cmd == "--help":
        return '<p><a class="btn primary" href="/help">Open help</a></p>'
    return '<p><a class="btn primary" href="/">Back home</a></p>'


def _post_button(action: str, label: str, fields: dict[str, str]) -> str:
    hidden = "".join(
        f'<input type="hidden" name="{_esc(key)}" value="{_esc(value)}">' for key, value in fields.items()
    )
    return (
        f'<form method="post" action="{_esc(action)}">\n{hidden}\n'
        f'<button class="primary" type="submit">{_esc(label)}</button>\n</form>\n'
    )


def _advanced_html() -> str:
    return """<details class="advanced">
<summary>Advanced</summary>
<form method="post" action="/list">
<button class="ghost" type="submit">Show registered tools</button>
</form>
<form method="post" action="/verify">
<label for="verify-name">Check one tool name</label>
<input id="verify-name" name="name" type="text" autocomplete="off" spellcheck="false" placeholder="runtime.ping">
<button class="ghost" type="submit">Check this name</button>
</form>
<form method="post" action="/receipt">
<label for="assertion">Hash an assertion</label>
<textarea id="assertion" name="assertion" placeholder="kernel is local"></textarea>
<button class="ghost" type="submit">Write receipt</button>
</form>
<form method="post" action="/call">
<label for="call-tool">Run a registered tool</label>
<input id="call-tool" name="tool" type="text" autocomplete="off" spellcheck="false" placeholder="runtime.ping">
<label for="call-args">Arguments JSON</label>
<textarea id="call-args" name="args">{}</textarea>
<label for="call-intent">Intent</label>
<input id="call-intent" name="intent" type="text" autocomplete="off">
<label class="check"><input type="checkbox" name="dry_run" value="1"> Dry run (record the call, do not execute the tool)</label>
<label class="check"><input type="checkbox" name="allow_export" value="1"> Allow export</label>
<label class="check"><input type="checkbox" name="allow_search" value="1"> Allow search grounding</label>
<label class="check"><input type="checkbox" name="destructive" value="1"> Destructive call</label>
<button class="ghost" type="submit">Run tool</button>
</form>
</details>
"""


def _esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
