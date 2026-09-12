"""Worker dual-surface: buttons, OpenAPI, and MCP share the same four ops.

Does not start a second kernel. Offline. Author Aziel Eliab.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "workers" / "download-tracker"
SRC = WORKER / "src"


def _read(*parts: str) -> str:
    return (WORKER.joinpath(*parts)).read_text(encoding="utf-8")


def test_worker_files_exist() -> None:
    for rel in (
        "src/index.js",
        "src/home.js",
        "src/runtime.js",
        "src/door.js",
        "src/mesh.js",
        "wrangler.toml",
        "README.md",
        "public/sigil.png",
        "public/fraggate-0.1.0.tar.gz",
    ):
        assert (WORKER / rel).is_file(), rel


def test_official_rose_star_brandmark() -> None:
    """Served /sigil.png is the official rose-star; public mark has empty alt."""
    import struct

    data = (WORKER / "public" / "sigil.png").read_bytes()
    assert len(data) == 75035, len(data)
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[12:16] == b"IHDR"
    width, height = struct.unpack(">II", data[16:24])
    assert (width, height) == (196, 139)
    home = _read("src/home.js")
    runtime = _read("src/runtime.js")
    assert 'class="brandmark" src="/sigil.png" width="40" height="40" alt=""' in home
    assert '<p class="stamp">Aziel Eliab</p>' in home
    assert 'title="Everblooming' not in home
    assert 'alt="Everblooming' not in home
    assert "Everblooming sigil" not in home
    assert 'src="/sigil.png" alt=""' in runtime
    assert 'alt="Everblooming' not in runtime
    assert "Everblooming sigil" not in runtime


def test_worker_name_and_url() -> None:
    toml = _read("wrangler.toml")
    assert 'name = "fraggate-download-tracker"' in toml
    assert "FRAGGATE_DOOR" in toml
    home = _read("src/home.js")
    door = _read("src/door.js")
    surface = home + door
    assert "https://fraggate-download-tracker.vibelock.workers.dev" in surface
    assert "https://aziel-runtime.vibelock.workers.dev" in surface


def test_four_ops_shared_across_surfaces() -> None:
    home = _read("src/home.js")
    runtime = _read("src/runtime.js")
    door = _read("src/door.js")
    for token in (
        "/v1/fraggate/list",
        "/v1/fraggate/describe",
        "/v1/fraggate/verify",
        "/v1/fraggate/call",
        "fraggate_list",
        "fraggate_describe",
        "fraggate_verify",
        "fraggate_call",
    ):
        assert token in home or token in runtime, token
        assert token in door or token in runtime, token
    assert "btn-list" in home
    assert "btn-describe" in home
    assert "btn-call" in home
    assert "btn-verify" in home
    assert "btn-live" in home
    assert "FG-HALLUC-TOOL" in home
    assert "ledger_tip" in home or "last-tip" in home
    assert 'value="${escapeHtml(HOST)}"' in home
    assert "hit(\"/v1/fraggate/list\"" in home
    assert "hit(\"/v1/fraggate/call\"" in home
    assert "TODO" not in home
    assert "coming soon" not in home.lower()
    assert "Not AZBrowser" in home or "Not AZBrowser" in _read("README.md")


def test_mcp_and_openapi_double_buttons() -> None:
    runtime = _read("src/runtime.js")
    assert "openapiSpec" in runtime
    assert "handleMcpJson" in runtime
    assert "tools/list" in runtime
    assert "tools/call" in runtime
    assert "POST https://aziel-runtime.vibelock.workers.dev/mcp" in runtime
    door = _read("src/door.js")
    assert "runFragGateOp" in door
    assert "mcpToolSchemas" in door


def test_not_a_second_kernel() -> None:
    runtime = _read("src/runtime.js")
    door = _read("src/door.js")
    assert "not a second kernel" in (runtime + door).lower() or "Not a second kernel" in runtime + door
    assert "bind_adapter" not in door


def test_docs_dual_surface_and_clients() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for text in (readme, skill):
        assert "Dual surface" in text or "Dual-surface" in text
        assert "aziel-runtime.vibelock.workers.dev/mcp" in text
        assert "/v1/fraggate/list" in text
        assert "ChatGPT" in text
        assert "Cursor" in text
        assert "Glama" in text
        assert "Cohere" in text
        assert "fraggate-download-tracker.vibelock.workers.dev" in text
    assert "Button test matrix" in readme


def test_skill_and_llms_cite_design_docs() -> None:
    runtime = _read("src/runtime.js")
    home = _read("src/home.js")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    wp = (ROOT / "docs" / "FG-WP-0.1.md").read_text(encoding="utf-8")
    spec = (ROOT / "docs" / "FragGate_v0_spec.md").read_text(encoding="utf-8")
    blob = "https://github.com/AzielEliab/fraggate/blob/main/docs/designs"
    tree = "https://github.com/AzielEliab/fraggate/tree/main/docs/designs"
    for text in (runtime, home, skill):
        assert f"{blob}/README.md" in text
        assert f"{blob}/SEC-FEAT-1.0.md" in text
        assert f"{blob}/AZL-WP-1.1.md" in text
        assert f"{blob}/AZL-VOL-1.0.md" in text
        assert "GET /v1/mesh never enables" in text
        assert "Aziel Eliab only" in text
    assert tree in home
    assert "Designs:" in home
    assert "docs/designs" in wp
    assert "SEC-FEAT-1.0" in wp
    assert "AZL-WP-1.1" in wp
    assert "AZL-VOL-1.0" in wp
    assert "docs/designs" in spec
    assert "GET never enables" in home


def test_kernel_version_unchanged() -> None:
    from fraggate.constants import MAGIC, VERSION

    assert MAGIC == "FGT1"
    assert VERSION == "0.1.0"


def test_mobile_scaffold() -> None:
    assert (ROOT / "mobile" / "lib" / "main.dart").is_file()
    dart = (ROOT / "mobile" / "lib" / "main.dart").read_text(encoding="utf-8")
    assert "fraggate_list" in dart
    assert "fraggate_call" in dart


def test_door_proxy_joins_origin_paths() -> None:
    door = _read("src/door.js")
    toml = _read("wrangler.toml")
    runtime = _read("src/runtime.js")
    assert "joinDoorUrl" in door
    assert "doorFetch" in door
    assert "doorService" in door
    assert "AZIEL_RUNTIME" in door
    assert 'SERVICE_BINDING_ORIGIN = "https://aziel-runtime"' in door
    assert "normalizeDoorOrigin" in door
    assert "door_url" in door
    assert "http_status" in door
    assert "content_type" in door
    assert "binding = \"AZIEL_RUNTIME\"" in toml
    assert 'service = "aziel-runtime"' in toml
    assert "run_worker_first = true" in toml
    assert "FRAGGATE_DOOR" in toml
    assert 'path === "/v1/fraggate/list"' in runtime
    assert "runFragGateOp(env, \"list\"" in runtime
    assert "runFragGateOp(env, \"call\"" in runtime
    assert "isMeshPath" in door
    assert "runMeshProxy" in door
    assert "joinOriginUrl" in door
    assert "originFetch" in door
    assert "runMeshProxy" in runtime
    assert "...meshOpenApiPaths()" in runtime


def test_verify_door_proxy_script() -> None:
    import shutil
    import subprocess

    script = WORKER / "scripts" / "verify-door-proxy.mjs"
    assert script.is_file()
    node = shutil.which("node")
    assert node, "node is required for the Worker door-proxy script"
    proc = subprocess.run([node, str(script)], cwd=WORKER, capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "JSON ok" in proc.stdout
