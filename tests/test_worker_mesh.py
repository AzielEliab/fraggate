"""Suite mesh Live Nodes + QNM-BUILD-1.0 + QNS-CD-1.0 contract.

Default OFF. live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.
QNS-CD-1.0 is a hub cite / Worker mesh cross-map only. No public qnsd proxy.
SPLIT THE WIRES + COLD-COPY SURVIVAL + REHEAL refuse on rollup/status.
FragGate remains the single door.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = (ROOT / "workers/download-tracker/src/mesh.js").read_text(encoding="utf-8")
DOOR = (ROOT / "workers/download-tracker/src/door.js").read_text(encoding="utf-8")
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
HOME = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
WRANGLER = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
WORKER_README = (ROOT / "workers/download-tracker/README.md").read_text(encoding="utf-8")


def test_mesh_contract_default_off_qnm_law() -> None:
    assert 'QNM_SPEC = "QNM-BUILD-1.0"' in MESH
    assert 'QNS_CD_SPEC = "QNS-CD-1.0"' in MESH
    assert "export const QNS_CD" in MESH
    assert "photon QNS1 packet transfer" in MESH
    assert "https://github.com/AzielEliab/qnm-node" in MESH
    assert "https://github.com/AzielEliab/aziel-runtime" in MESH
    assert "https://github.com/AzielEliab/azinterface" in MESH
    assert "public_qnsd_proxy: false" in MESH
    assert "softwares_tab: false" in MESH
    assert "QNS-CD-1.0" in MESH
    assert "MESH_DEFAULT_OFF = true" in MESH
    assert "MESH_ANONYMITY_NETWORK = false" in MESH
    assert "MESH_NODE_GATE = false" in MESH
    assert "MESH_AUTO_HEAL = false" in MESH
    assert 'MESH_IDENTITY = IDENTITY' in MESH or '"Aziel Eliab"' in MESH
    assert 'MESH_PRODUCT = "fraggate"' in MESH
    assert 'MESH_PATH = "/v1/mesh"' in MESH
    assert "live|locked|isolated" in MESH
    assert "enabled_default: false" in MESH
    assert "anon_broadcast_publish_path: false" in MESH
    assert "Aziel Eliab" in MESH
    assert "QNS-CD-1.0" in MESH_NOTE_SOURCE()


def MESH_NOTE_SOURCE() -> str:
    marker = "export const MESH_NOTE ="
    start = MESH.find(marker)
    assert start != -1
    return MESH[start : start + 600]


def test_mesh_pointer_and_openapi_helpers() -> None:
    assert "export function meshPointer" in MESH
    assert "export function meshOpenApiPaths" in MESH
    assert "export function parseMeshDoc" in MESH
    assert "export function emptyMesh" in MESH
    assert "export function attachQnsCd" in MESH
    assert "export function attachMeshLaw" in MESH
    assert "export function attachMeshCite" in MESH
    assert "export function meshLawRefuse" in MESH
    assert "export function isNeighborRehealPath" in MESH
    assert "export function alignLiveNodes" in MESH
    assert "fraggate_slug: MESH_SLUG" in MESH
    assert "fraggate_mesh_" in MESH
    assert "qns_cd: QNS_CD" in MESH
    assert "qns_cd_spec: QNS_CD_SPEC" in MESH


def test_split_the_wires_and_cold_copy_survival_refuse() -> None:
    """Locked mesh law is rollup/status refuse text. Not a second door."""
    assert "SPLIT THE WIRES" in MESH
    assert "tip-only 0.5–1s tick" in MESH
    assert "pull-only payload" in MESH
    assert "update=proof not timer" in MESH
    assert "777s dwell after valid cite" in MESH
    assert "equivocation ends peer" in MESH
    assert "emit last locally" in MESH
    assert "Phoenix local only" in MESH
    assert "partition no auto-splice" in MESH
    assert "heartbeat loss≠poison" in MESH
    assert "1s≠777s sockets" in MESH
    assert "COLD-COPY SURVIVAL" in MESH
    assert "multiply cold copies" in MESH
    assert "refuse live body sync" in MESH
    assert "tip expensive to erase" in MESH
    assert "server pull cannot wipe cold replicas" in MESH
    assert "data outlives creators" in MESH
    assert "MESH-STW-REFUSED" in MESH
    assert "MESH-CCS-REFUSED" in MESH
    assert "MESH-LAW-REFUSED" in MESH
    assert "export const SPLIT_THE_WIRES_REFUSE" in MESH
    assert "export const COLD_COPY_SURVIVAL_REFUSE" in MESH
    assert "export const MESH_LAW_REFUSE" in MESH
    assert "second_mesh_door: false" in MESH
    assert "FragGate remains the single door" in MESH
    assert "not a second mesh door" in MESH
    assert "Aziel Eliab only" in MESH
    assert "SPLIT THE WIRES" in MESH_NOTE_SOURCE()
    assert "COLD-COPY SURVIVAL" in MESH_NOTE_SOURCE()
    assert "attachMeshCite" in DOOR
    assert 'door: "fraggate"' in DOOR
    assert "second_mesh_door: false" in DOOR
    assert "fraggate_single_door: true" in DOOR
    assert "/v1/fraggate" in DOOR
    assert "do not invent a second mesh door" in MESH


def test_reheal_refuse() -> None:
    """Poisoned node heals locally. Neighbor reheal is majority fanfic."""
    assert "REHEAL" in MESH
    assert "own last good tip" in MESH
    assert "verified pull of bytes already trusted" in MESH
    assert "phoenix-WAITs" in MESH
    assert "not by listening to neighbors" in MESH
    assert "live/locked/isolated/tip-hash" in MESH
    assert "vote-to-fix" in MESH
    assert "here's what you should be" in MESH
    assert "isolate, drop tether, local phoenix" in MESH
    assert "other nodes keep chain" in MESH
    assert "isolation is cure" in MESH
    assert "majority fanfic" in MESH
    assert "group hug over a wound" in MESH
    assert "MESH-REHEAL-REFUSED" in MESH
    assert "export const REHEAL_REFUSE" in MESH
    assert "export const REHEAL_LAW" in MESH
    assert "neighbor_reheal: false" in MESH
    assert "neighbor_reheal: false" in DOOR
    assert "isNeighborRehealPath" in DOOR
    assert 'meshLawRefuse("reheal")' in DOOR
    assert "REHEAL" in MESH_NOTE_SOURCE()
    assert "FragGate remains the single door" in MESH
    assert "Aziel Eliab only" in MESH


def test_door_proxies_mesh_via_aziel_runtime() -> None:
    assert "MESH_ROUTE_METHODS" in DOOR
    assert "isMeshPath" in DOOR
    assert "runMeshProxy" in DOOR
    assert "originFetch" in DOOR
    assert "joinOriginUrl" in DOOR
    assert '"/v1/mesh"' in DOOR
    assert '"/v1/mesh/"' in DOOR or 'startsWith("/v1/mesh/")' in DOOR
    assert "AZIEL_RUNTIME" in WRANGLER
    assert "aziel-runtime" in WRANGLER
    assert "/v1/mesh" in WRANGLER


def test_runtime_advertises_mesh_proxy_and_pointer() -> None:
    assert 'from "./mesh.js"' in RUNTIME
    assert "meshPointer" in RUNTIME
    assert "meshOpenApiPaths" in RUNTIME
    assert "...meshOpenApiPaths()" in RUNTIME
    assert "mesh: meshPointer()" in RUNTIME
    assert "/v1/mesh" in RUNTIME
    assert "QNM-BUILD-1.0" in RUNTIME
    assert "No Node Gate" in RUNTIME
    assert "runMeshProxy" in RUNTIME
    assert "isMeshPath" in RUNTIME
    assert "handleRuntimeApi(request, url, env)" in INDEX


def test_home_live_nodes_strip_no_node_gate() -> None:
    assert 'id="meshStrip"' in HOME
    assert 'id="meshLiveCount"' in HOME
    assert 'id="meshLine"' in HOME
    assert "Live Nodes" in HOME
    assert "QNM-BUILD-1.0" in HOME
    assert "No Node Gate" in HOME
    assert "No auto-heal" in HOME
    assert "Not an anonymity network" in HOME
    assert "/v1/mesh" in HOME
    assert 'product: "fraggate"' in HOME
    assert 'id="node-gate"' not in HOME
    assert 'href="/node-gate"' not in HOME
    assert "auto-heal this node" not in HOME


def test_docs_advertise_mesh_proxy() -> None:
    assert "/v1/mesh" in README
    assert "/v1/mesh" in SKILL
    assert "QNM-BUILD-1.0" in WORKER_README
    assert "QNS-CD-1.0" in README
    assert "QNS-CD-1.0" in SKILL
    assert "QNS-CD-1.0" in WORKER_README
    assert "QNS-CD-1.0" in RUNTIME
    assert "QNS-CD-1.0" in HOME
    assert "photon QNS1" in README
    assert "photon QNS1" in SKILL
    assert "No public qnsd proxy" in README
    assert "No public qnsd proxy" in SKILL
    assert "AZIEL_RUNTIME" in WORKER_README
    assert "Live Nodes" in WORKER_README
    assert "Aziel Eliab" in MESH
    assert "GET never enables" in DOOR
    assert "GET /v1/mesh never enables" in RUNTIME
    assert "GET /v1/mesh never enables" in HOME
    assert "attachMeshCite" in DOOR
    assert "Aziel Eliab only" in RUNTIME
    assert "Aziel Eliab only" in HOME
