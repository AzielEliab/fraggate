/**
 * Suite node mesh — QNM-BUILD-1.0 Live Nodes contract.
 * QNS-CD-1.0 cross-map (photon QNS1 packet transfer): hub cite only.
 * Local qnsd lives in AzielEliab/qnm-node. Runtime cites + catalog field
 * live in AzielEliab/aziel-runtime. AZInterface holds pair custody.
 * Default OFF. Public rollup is live|locked|isolated counts only.
 * No Node Gate. No auto-heal. Not an anonymity network.
 * No public qnsd proxy. Not a Softwares-tab product.
 * /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME binding).
 * FragGate remains the single door — do not invent a second mesh door.
 *
 * SPLIT THE WIRES (locked): tip-only 0.5–1s tick; pull-only payload;
 * update=proof not timer; 777s dwell after valid cite; equivocation ends
 * peer; emit last locally; Phoenix local only; partition no auto-splice;
 * heartbeat loss≠poison; 1s≠777s sockets.
 * COLD-COPY SURVIVAL (locked): multiply cold copies; refuse live body
 * sync; tip expensive to erase; server pull cannot wipe cold replicas;
 * data outlives creators.
 * REHEAL (locked): poisoned node heals from own last good tip +
 * verified pull of bytes already trusted OR phoenix-WAITs — not by
 * listening to neighbors. Allowed chatter: live/locked/isolated/tip-hash.
 * Forbidden: bodies, diffs, vote-to-fix, "here's what you should be."
 * Isolate, drop tether, local phoenix; other nodes keep chain.
 * Isolation is cure; neighbor reheal = majority fanfic / group hug
 * over a wound.
 * Author: Aziel Eliab only.
 */

const RUNTIME = "https://aziel-runtime.vibelock.workers.dev";
const FRAGGATE_MCP = "https://aziel-runtime.vibelock.workers.dev/mcp";
const FRAGGATE_CALL = "https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call";
const IDENTITY = "Aziel Eliab";

export const QNM_SPEC = "QNM-BUILD-1.0";
export const QNS_CD_SPEC = "QNS-CD-1.0";
export const MESH_KERNEL = "NM-0.1";
export const MESH_DEFAULT_OFF = true;
export const MESH_ANONYMITY_NETWORK = false;
export const MESH_NODE_GATE = false;
export const MESH_AUTO_HEAL = false;
export const MESH_IDENTITY = IDENTITY;
export const MESH_SLUG = "mesh";
export const MESH_PRODUCT = "fraggate";
export const MESH_PATH = "/v1/mesh";
export const MESH_STATUS_PATH = "/v1/mesh/status";
export const MESH_NODES_PATH = "/v1/mesh/nodes";
export const MESH_ENABLE_PATH = "/v1/mesh/enable";
export const MESH_DISABLE_PATH = "/v1/mesh/disable";
export const MESH_JOIN_PATH = "/v1/mesh/join";
export const MESH_HEARTBEAT_PATH = "/v1/mesh/heartbeat";
export const MESH_LEAVE_PATH = "/v1/mesh/leave";
export const MESH_BROADCAST_PATH = "/v1/mesh/broadcast";
export const ANON_BROADCAST = "https://github.com/AzielEliab/anon-broadcast";
export const QNM_NODE = "https://github.com/AzielEliab/qnm-node";
export const AZIEL_RUNTIME_REPO = "https://github.com/AzielEliab/aziel-runtime";
export const AZINTERFACE = "https://github.com/AzielEliab/azinterface";

/** Hub cite / Worker mesh cross-map. Not qnsd. Not a public proxy. */
export const QNS_CD = Object.freeze({
  spec: QNS_CD_SPEC,
  title: "photon QNS1 packet transfer",
  kind: "hub-cite",
  softwares_tab: false,
  public_proxy: false,
  public_qnsd_proxy: false,
  node_gate: false,
  default_off: true,
  local_daemon: "qnsd",
  local_node: QNM_NODE,
  runtime: AZIEL_RUNTIME_REPO,
  runtime_docs: AZIEL_RUNTIME_REPO + "/blob/main/docs/NODE_MESH.md",
  runtime_designs: AZIEL_RUNTIME_REPO + "/blob/main/docs/designs/README.md",
  runtime_catalog: RUNTIME + "/v1/software",
  pair_custody: AZINTERFACE,
  suite_designs: "https://github.com/AzielEliab/fraggate/blob/main/docs/designs/README.md",
  author: IDENTITY,
  identity: IDENTITY,
  note:
    "QNS-CD-1.0 photon QNS1 packet transfer. Local qnsd is coded in qnm-node. Runtime cites + catalog field live in aziel-runtime. AZInterface holds pair custody. Hub cite / Worker mesh cross-map only. Not a Softwares-tab product. No public qnsd proxy. No Node Gate. Mesh stays default OFF. Author: Aziel Eliab only.",
});

export const SPLIT_THE_WIRES = "SPLIT THE WIRES";
export const COLD_COPY_SURVIVAL = "COLD-COPY SURVIVAL";
export const REHEAL = "REHEAL";
export const MESH_STW_REFUSED = "MESH-STW-REFUSED";
export const MESH_CCS_REFUSED = "MESH-CCS-REFUSED";
export const MESH_REHEAL_REFUSED = "MESH-REHEAL-REFUSED";
export const MESH_LAW_REFUSED = "MESH-LAW-REFUSED";
export const MESH_SINGLE_DOOR = "fraggate";
export const MESH_SECOND_DOOR = false;

/** Locked SPLIT THE WIRES clauses. Rollup/status refuse cites these verbatim. */
export const SPLIT_THE_WIRES_LAW = Object.freeze({
  name: SPLIT_THE_WIRES,
  author: IDENTITY,
  identity: IDENTITY,
  door: MESH_SINGLE_DOOR,
  second_mesh_door: MESH_SECOND_DOOR,
  tip_only: "tip-only 0.5–1s tick",
  payload: "pull-only payload",
  update: "update=proof not timer",
  dwell: "777s dwell after valid cite",
  equivocation: "equivocation ends peer",
  emit_last: "emit last locally",
  phoenix: "Phoenix local only",
  partition: "partition no auto-splice",
  heartbeat_loss: "heartbeat loss≠poison",
  sockets: "1s≠777s sockets",
});

/** Locked COLD-COPY SURVIVAL clauses. Rollup/status refuse cites these verbatim. */
export const COLD_COPY_SURVIVAL_LAW = Object.freeze({
  name: COLD_COPY_SURVIVAL,
  author: IDENTITY,
  identity: IDENTITY,
  door: MESH_SINGLE_DOOR,
  second_mesh_door: MESH_SECOND_DOOR,
  multiply: "multiply cold copies",
  live_body_sync: false,
  live_body_sync_refuse: "refuse live body sync",
  tip: "tip expensive to erase",
  server_pull_wipe: false,
  server_pull: "server pull cannot wipe cold replicas",
  outlives: "data outlives creators",
});

/** Locked REHEAL clauses. Rollup/status refuse cites these verbatim. */
export const REHEAL_LAW = Object.freeze({
  name: REHEAL,
  author: IDENTITY,
  identity: IDENTITY,
  door: MESH_SINGLE_DOOR,
  second_mesh_door: MESH_SECOND_DOOR,
  heal: "heal from own last good tip",
  pull: "verified pull of bytes already trusted",
  phoenix_wait: "phoenix-WAITs",
  neighbor_listen: false,
  neighbor_reheal: false,
  allowed_chatter: "live/locked/isolated/tip-hash",
  forbidden_bodies: false,
  forbidden_diffs: false,
  forbidden_vote_to_fix: false,
  forbidden: "bodies, diffs, vote-to-fix, here's what you should be",
  isolate: "isolate, drop tether, local phoenix",
  peers: "other nodes keep chain",
  isolation: "isolation is cure",
  neighbor_reheal_refuse: "majority fanfic / group hug over a wound",
});

export const SPLIT_THE_WIRES_REFUSE =
  "SPLIT THE WIRES refuse. Tip-only 0.5–1s tick. Pull-only payload. Update=proof not timer. 777s dwell after valid cite. Equivocation ends peer. Emit last locally. Phoenix local only. Partition no auto-splice. Heartbeat loss≠poison. 1s≠777s sockets. FragGate remains the single door — not a second mesh door. Author: Aziel Eliab only.";

export const COLD_COPY_SURVIVAL_REFUSE =
  "COLD-COPY SURVIVAL refuse. Multiply cold copies. Refuse live body sync. Tip expensive to erase. Server pull cannot wipe cold replicas. Data outlives creators. FragGate remains the single door — not a second mesh door. Author: Aziel Eliab only.";

export const REHEAL_REFUSE =
  "REHEAL refuse. Poisoned node heals from own last good tip + verified pull of bytes already trusted OR phoenix-WAITs — not by listening to neighbors. Allowed chatter: live/locked/isolated/tip-hash. Forbidden: bodies, diffs, vote-to-fix, \"here's what you should be.\" Isolate, drop tether, local phoenix; other nodes keep chain. Isolation is cure; neighbor reheal = majority fanfic / group hug over a wound. FragGate remains the single door — not a second mesh door. Author: Aziel Eliab only.";

export const MESH_LAW_REFUSE = SPLIT_THE_WIRES_REFUSE + " " + COLD_COPY_SURVIVAL_REFUSE + " " + REHEAL_REFUSE;

export const MESH_NOTE =
  "QNM-BUILD-1.0. QNS-CD-1.0 photon QNS1 packet transfer. Suite mesh default off. Live|locked|isolated counts only. No Node Gate. No auto-heal. Not an anonymity network. No public qnsd proxy. Not a Softwares-tab product. SPLIT THE WIRES. COLD-COPY SURVIVAL. REHEAL. FragGate remains the single door. Author: Aziel Eliab only.";

export const MESH_OPS = Object.freeze([
  "status",
  "enable",
  "disable",
  "join",
  "heartbeat",
  "leave",
  "nodes",
  "broadcast",
]);

export const MESH_PROXY_ROUTES = Object.freeze([
  { path: MESH_PATH, methods: ["get", "head"], op: "status", summary: "PROXY to aziel-runtime GET /v1/mesh. Suite mesh status. Default OFF. Not a local op." },
  { path: MESH_STATUS_PATH, methods: ["get"], op: "status", summary: "PROXY alias of GET /v1/mesh. Not a local op." },
  { path: MESH_NODES_PATH, methods: ["get"], op: "nodes", summary: "PROXY to aziel-runtime GET /v1/mesh/nodes. Live Nodes (5-minute presence). Not a local op." },
  { path: MESH_ENABLE_PATH, methods: ["post"], op: "enable", summary: "PROXY to aziel-runtime POST /v1/mesh/enable. Operator bearer required. Rate-limited. Not a local op." },
  { path: MESH_DISABLE_PATH, methods: ["post"], op: "disable", summary: "PROXY to aziel-runtime POST /v1/mesh/disable. Always allowed. Not a local op." },
  { path: MESH_JOIN_PATH, methods: ["post"], op: "join", summary: "PROXY to aziel-runtime POST /v1/mesh/join. Body {product, node_id?, label?, presence?}. Refused while OFF. Not a local op." },
  { path: MESH_HEARTBEAT_PATH, methods: ["post"], op: "heartbeat", summary: "PROXY to aziel-runtime POST /v1/mesh/heartbeat. Body {node_id}. Not a local op." },
  { path: MESH_LEAVE_PATH, methods: ["post"], op: "leave", summary: "PROXY to aziel-runtime POST /v1/mesh/leave. Body {node_id}. Not a local op." },
  { path: MESH_BROADCAST_PATH, methods: ["post"], op: "broadcast", summary: "PROXY to aziel-runtime POST /v1/mesh/broadcast. SHA-256 receipt only. Not AnonBroadcast upload. Not a local op." },
]);

function firstNum(...vals) {
  for (const raw of vals) {
    if (raw == null || raw === "") continue;
    const n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
    if (Number.isFinite(n) && n >= 0) return Math.floor(n);
  }
  return null;
}

function asList(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === "object") return Object.values(value);
  return [];
}

function truthyEnabled(value) {
  if (value === true || value === 1) return true;
  const s = String(value || "").trim().toLowerCase();
  return s === "on" || s === "enabled" || s === "true" || s === "live";
}

export function emptyRollup() {
  return { live: 0, locked: 0, isolated: 0 };
}

export function meshRollup(mesh) {
  const m = mesh && typeof mesh === "object" ? mesh : {};
  const r = m.rollup && typeof m.rollup === "object" && !Array.isArray(m.rollup) ? m.rollup : {};
  return {
    live: firstNum(r.live, m.live_nodes, m.live) ?? 0,
    locked: firstNum(r.locked, m.locked_nodes, m.locked) ?? 0,
    isolated: firstNum(r.isolated, m.isolated_nodes, m.isolated) ?? 0,
  };
}

function parseRollup(inner, listedLive) {
  const r = inner.rollup && typeof inner.rollup === "object" && !Array.isArray(inner.rollup) ? inner.rollup : {};
  const live = firstNum(
    r.live,
    r.live_nodes,
    r.live_count,
    inner.live,
    inner.live_nodes,
    inner.mesh_live_nodes,
    inner.live_count,
    inner.count,
    inner.n,
    inner.node_count,
    listedLive,
  );
  const locked = firstNum(r.locked, r.locked_nodes, r.locked_count, inner.locked, inner.locked_nodes, inner.locked_count);
  const isolated = firstNum(r.isolated, r.isolated_nodes, r.isolated_count, inner.isolated, inner.isolated_nodes, inner.isolated_count);
  return {
    live: live != null ? live : 0,
    locked: locked != null ? locked : 0,
    isolated: isolated != null ? isolated : 0,
  };
}

/** Stamp locked mesh-law refuse text onto rollup / status envelopes. */
export function attachMeshLaw(doc) {
  const law = {
    split_the_wires: SPLIT_THE_WIRES_LAW,
    cold_copy_survival: COLD_COPY_SURVIVAL_LAW,
    reheal: REHEAL_LAW,
    split_the_wires_refuse: SPLIT_THE_WIRES_REFUSE,
    cold_copy_survival_refuse: COLD_COPY_SURVIVAL_REFUSE,
    reheal_refuse: REHEAL_REFUSE,
    mesh_law_refuse: MESH_LAW_REFUSE,
    neighbor_reheal: false,
    fraggate_single_door: true,
    second_mesh_door: false,
    author: IDENTITY,
    identity: IDENTITY,
  };
  if (!doc || typeof doc !== "object" || Array.isArray(doc)) return law;
  return { ...doc, ...law };
}

/** Rollup/status refuse envelope for a locked-law violation. Not a second door. */
export function meshLawRefuse(kind = "law") {
  const k = String(kind || "law").trim().toLowerCase().replace(/[\s-]+/g, "_");
  const split = k === "split" || k === "stw" || k === "split_the_wires";
  const cold = k === "cold" || k === "ccs" || k === "cold_copy" || k === "cold_copy_survival";
  const reheal =
    k === "reheal" || k === "rh" || k === "heal" || k === "neighbor_reheal" || k === "neighbor";
  const code = split
    ? MESH_STW_REFUSED
    : cold
      ? MESH_CCS_REFUSED
      : reheal
        ? MESH_REHEAL_REFUSED
        : MESH_LAW_REFUSED;
  const message = split
    ? SPLIT_THE_WIRES_REFUSE
    : cold
      ? COLD_COPY_SURVIVAL_REFUSE
      : reheal
        ? REHEAL_REFUSE
        : MESH_LAW_REFUSE;
  return attachMeshCite({
    ok: false,
    code,
    door: MESH_SINGLE_DOOR,
    kernel: MESH_KERNEL,
    spec: QNM_SPEC,
    status: "refuse",
    message,
    rollup: emptyRollup(),
    node_gate: false,
    auto_heal: false,
    neighbor_reheal: false,
    anonymity_network: false,
    second_mesh_door: false,
    fraggate_single_door: true,
    author: IDENTITY,
    identity: IDENTITY,
  });
}

/** Neighbor reheal / vote-to-fix / heal paths. Not advertised ops. Isolation is cure. */
export const NEIGHBOR_REHEAL_PATHS = Object.freeze([
  "/v1/mesh/reheal",
  "/v1/mesh/heal",
  "/v1/mesh/neighbor-reheal",
  "/v1/mesh/neighbor_reheal",
  "/v1/mesh/vote-to-fix",
  "/v1/mesh/vote_to_fix",
]);

/** True when a path asks neighbors to rewrite a poisoned node. */
export function isNeighborRehealPath(pathname) {
  const raw = String(pathname == null ? "" : pathname).split("?")[0];
  let path = raw.replace(/\/+$/, "") || "/";
  if (!path.startsWith("/")) path = "/" + path;
  if (NEIGHBOR_REHEAL_PATHS.includes(path)) return true;
  const leaf = path.split("/").pop() || "";
  const k = leaf.toLowerCase().replace(/[\s-]+/g, "_");
  return k === "reheal" || k === "heal" || k === "neighbor_reheal" || k === "vote_to_fix";
}

/** Stamp the QNS-CD-1.0 cross-map so peers can see it on Live Nodes / status. */
export function attachQnsCd(doc) {
  if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
    return { qns_cd: QNS_CD, qns_cd_spec: QNS_CD_SPEC };
  }
  const incoming = doc.qns_cd && typeof doc.qns_cd === "object" && !Array.isArray(doc.qns_cd) ? doc.qns_cd : null;
  const qns_cd = incoming ? { ...QNS_CD, ...incoming, spec: incoming.spec || QNS_CD_SPEC } : QNS_CD;
  return { ...doc, qns_cd, qns_cd_spec: QNS_CD_SPEC };
}

/** QNS-CD cite plus locked SPLIT THE WIRES / COLD-COPY SURVIVAL / REHEAL refuse text. */
export function attachMeshCite(doc) {
  return attachMeshLaw(attachQnsCd(doc));
}

export function emptyMesh(extra = {}) {
  const rollup =
    extra.rollup && typeof extra.rollup === "object" ? { ...emptyRollup(), ...extra.rollup } : emptyRollup();
  return attachMeshCite({
    ok: true,
    spec: QNM_SPEC,
    kernel: MESH_KERNEL,
    enabled: false,
    default_off: true,
    live_nodes: 0,
    status: extra.status || "off",
    source: extra.source || "fallback",
    node_gate: false,
    auto_heal: false,
    neighbor_reheal: false,
    anonymity_network: false,
    author: MESH_IDENTITY,
    identity: MESH_IDENTITY,
    note: MESH_NOTE,
    door: MESH_PATH,
    ...extra,
    spec: QNM_SPEC,
    qns_cd: QNS_CD,
    qns_cd_spec: QNS_CD_SPEC,
    rollup,
    node_gate: false,
    auto_heal: false,
    neighbor_reheal: false,
    anonymity_network: false,
    author: MESH_IDENTITY,
    identity: MESH_IDENTITY,
  });
}

export function compactMeshNode(raw) {
  if (raw == null) return null;
  if (typeof raw === "string") {
    const id = raw.trim();
    return id ? { id } : null;
  }
  if (typeof raw !== "object") return null;
  const id = String(raw.id || raw.node_id || raw.session_id || raw.peer || raw.name || "").trim();
  const product = String(raw.product || raw.slug || raw.suite || "").trim();
  const seen = raw.last_utc || raw.last_seen || raw.seen_utc || raw.heartbeat_utc || "";
  if (!id && !product && !seen) return null;
  const out = {};
  if (id) out.id = id;
  if (product) out.product = product;
  if (seen) out.last_utc = String(seen);
  return out;
}

export function parseMeshDoc(body) {
  if (body == null) return emptyMesh({ status: "unavailable", source: "empty" });
  if (typeof body !== "object" || Array.isArray(body)) {
    return emptyMesh({ status: "unavailable", source: "empty" });
  }
  const inner =
    body.result && typeof body.result === "object" && !Array.isArray(body.result)
      ? { ...body, ...body.result }
      : body.mesh && typeof body.mesh === "object" && !Array.isArray(body.mesh)
        ? { ...body, ...body.mesh }
        : body;
  const listed = asList(inner.nodes || inner.list || inner.peers || inner.live_nodes_list)
    .map(compactMeshNode)
    .filter(Boolean);
  const rollup = parseRollup(inner, listed.length ? listed.length : null);
  const enabled =
    truthyEnabled(inner.enabled) || truthyEnabled(inner.mesh_enabled) || String(inner.status || "").toLowerCase() === "on";
  const unavailable =
    inner.ok === false && !enabled && (inner.error || inner.status === "unavailable" || inner.status === "not_found");
  const status = enabled ? "on" : unavailable ? "unavailable" : "off";
  const live = enabled ? rollup.live : 0;
  const locked = enabled ? rollup.locked : 0;
  const isolated = enabled ? rollup.isolated : 0;
  const products = asList(inner.products_present || inner.products)
    .map((p) => (typeof p === "string" ? p : (p && (p.product || p.slug || p.name)) || ""))
    .map((s) => String(s).trim())
    .filter(Boolean);
  return emptyMesh({
    ok: inner.ok !== false,
    enabled,
    default_off: inner.default_off !== false,
    live_nodes: live,
    rollup: { live, locked, isolated },
    products_present: products,
    nodes: listed,
    status,
    source: inner.source || "parsed",
    door: inner.door || MESH_PATH,
    note: enabled
      ? "QNM-BUILD-1.0. QNS-CD-1.0 photon QNS1 packet transfer. Suite mesh is on. Live|locked|isolated counts only. No Node Gate. No auto-heal. Not an anonymity network. No public qnsd proxy. SPLIT THE WIRES. COLD-COPY SURVIVAL. REHEAL. FragGate remains the single door."
      : MESH_NOTE,
  });
}

export function publicMesh(mesh) {
  const m = mesh && typeof mesh === "object" ? mesh : emptyMesh();
  const enabled = !!m.enabled;
  const rollup = enabled ? meshRollup(m) : emptyRollup();
  return attachMeshCite({
    spec: QNM_SPEC,
    qns_cd: QNS_CD,
    qns_cd_spec: QNS_CD_SPEC,
    kernel: MESH_KERNEL,
    enabled,
    default_off: m.default_off !== false,
    live_nodes: enabled ? rollup.live : 0,
    rollup,
    status: enabled ? "on" : m.status === "unavailable" ? "unavailable" : "off",
    source: m.source || "fallback",
    node_gate: false,
    auto_heal: false,
    neighbor_reheal: false,
    anonymity_network: false,
    author: MESH_IDENTITY,
    identity: MESH_IDENTITY,
    door: MESH_PATH,
    status_path: MESH_STATUS_PATH,
    nodes_path: MESH_NODES_PATH,
    join: MESH_JOIN_PATH,
    heartbeat: MESH_HEARTBEAT_PATH,
    enable: MESH_ENABLE_PATH,
    disable: MESH_DISABLE_PATH,
    leave: MESH_LEAVE_PATH,
    broadcast: MESH_BROADCAST_PATH,
    mcp: FRAGGATE_MCP,
    fraggate: FRAGGATE_CALL,
    slug: MESH_SLUG,
    product: MESH_PRODUCT,
    ops: MESH_OPS.slice(),
    origin: RUNTIME + MESH_PATH,
    note: m.note || MESH_NOTE,
  });
}

export function meshStatusLine(mesh) {
  const m = mesh && typeof mesh === "object" ? mesh : emptyMesh();
  if (m.enabled) {
    const r = meshRollup(m);
    return "Suite mesh: on · live " + r.live + " · locked " + r.locked + " · isolated " + r.isolated + ". SPLIT THE WIRES. COLD-COPY SURVIVAL. REHEAL. FragGate remains the single door. Not an anonymity network.";
  }
  if (m.status === "unavailable") {
    return "Suite mesh: off (unavailable). QNM-BUILD-1.0. QNS-CD-1.0. SPLIT THE WIRES. COLD-COPY SURVIVAL. REHEAL. FragGate remains the single door. Not an anonymity network.";
  }
  return "Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. SPLIT THE WIRES. COLD-COPY SURVIVAL. REHEAL. FragGate remains the single door. Not an anonymity network.";
}

/** Public Live Nodes count. Never auto-heal a visiting floor. */
export function alignLiveNodes({ mesh } = {}) {
  if (mesh && mesh.enabled) return meshRollup(mesh).live;
  return 0;
}

export function meshPointer() {
  return attachMeshCite({
    pointer: true,
    path: MESH_PATH,
    enabled_default: false,
    spec: QNM_SPEC,
    qns_cd: QNS_CD,
    qns_cd_spec: QNS_CD_SPEC,
    kernel: MESH_KERNEL,
    rollup: "live|locked|isolated",
    node_gate: false,
    auto_heal: false,
    neighbor_reheal: false,
    anonymity_network: false,
    author: MESH_IDENTITY,
    identity: MESH_IDENTITY,
    catalog_mcp: FRAGGATE_MCP,
    fraggate_slug: MESH_SLUG,
    origin: RUNTIME + MESH_PATH,
    note:
      "PROXY to aziel-runtime /v1/mesh/* via AZIEL_RUNTIME. Not a local op. Not AnonBroadcast. Not AZMail's product-local ring. FragGate remains the single door — not a second mesh door. Full node process is local qnm-node/. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only — not a public qnsd proxy. SPLIT THE WIRES. COLD-COPY SURVIVAL. REHEAL. " +
      MESH_NOTE,
    anon_broadcast: ANON_BROADCAST,
    anon_broadcast_publish_path: false,
  });
}

export function meshOpenApiPaths() {
  const paths = {};
  for (const route of MESH_PROXY_ROUTES) {
    const entry = paths[route.path] || {};
    for (const method of route.methods) {
      entry[method] = {
        operationId: "fraggate_mesh_" + route.op + (method === "head" ? "_head" : "") + "_proxy",
        summary: route.summary,
        tags: ["mesh"],
        responses: { "200": { description: "aziel-runtime mesh envelope" } },
      };
      if (method === "post") {
        entry[method].requestBody = { content: { "application/json": { schema: { type: "object" } } } };
      }
    }
    paths[route.path] = entry;
  }
  return paths;
}
