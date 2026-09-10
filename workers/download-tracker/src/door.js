/**
 * Shared FragGate door. Human buttons, OpenAPI, and MCP all call these
 * same four ops. This Worker is not a second kernel — it proxies the
 * public aziel-runtime door (configurable via FRAGGATE_DOOR).
 *
 * `/v1/fraggate/*` is the door. `/v1/mesh/*` is the suite QNM rollup
 * PROXY (AZIEL_RUNTIME / https://aziel-runtime.vibelock.workers.dev).
 * Mesh paths are never rewritten onto `/v1/fraggate`.
 * QNS-CD-1.0 is a hub cite / Worker mesh cross-map only (no qnsd proxy).
 *
 * Author: Aziel Eliab only. Apache-2.0.
 */

import { attachQnsCd, QNS_CD, QNS_CD_SPEC } from "./mesh.js";

export const DEFAULT_DOOR = "https://aziel-runtime.vibelock.workers.dev";
export const KERNEL = "https://github.com/AzielEliab/fraggate";
export const HOST = "https://fraggate-download-tracker.vibelock.workers.dev";
export const VERSION = "0.1.0";
export const AUTHOR = "Aziel Eliab";
export const SIGIL = "https://www.azielcorpuslibrary.net/sigil.png";

export const OPS = Object.freeze({
  list: { method: "GET", path: "/v1/fraggate/list" },
  describe: { method: "GET", path: "/v1/fraggate/describe" },
  verify: { method: "POST", path: "/v1/fraggate/verify" },
  call: { method: "POST", path: "/v1/fraggate/call" },
  summary: { method: "GET", path: "/v1/fraggate" },
});

/** Allowlisted suite mesh PROXY paths. Not a Node Gate. Not local ops. */
export const MESH_ROUTE_METHODS = Object.freeze({
  "/v1/mesh": ["GET", "HEAD"],
  "/v1/mesh/status": ["GET", "HEAD"],
  "/v1/mesh/nodes": ["GET", "HEAD"],
  "/v1/mesh/enable": ["POST"],
  "/v1/mesh/disable": ["POST"],
  "/v1/mesh/join": ["POST"],
  "/v1/mesh/heartbeat": ["POST"],
  "/v1/mesh/leave": ["POST"],
  "/v1/mesh/broadcast": ["POST"],
});

export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
    "Access-Control-Allow-Headers":
      "Content-Type, Accept, Authorization, X-Aziel-Runtime-Token, MCP-Protocol-Version, mcp-session-id, User-Agent",
    "Access-Control-Expose-Headers": "X-Aziel-Runtime-Version, X-Aziel-FragGate-Door",
  };
}

/**
 * Normalize a door origin. Strips trailing slashes and a trailing
 * `/v1/fraggate` so spec paths can be appended once.
 */
export function normalizeDoorOrigin(raw) {
  let s = String(raw == null ? "" : raw).trim();
  if (!s) return DEFAULT_DOOR;
  s = s.replace(/^['"]+|['"]+$/g, "");
  s = s.replace(/\/+$/, "");
  s = s.replace(/\/v1\/fraggate$/i, "");
  s = s.replace(/\/+$/, "");
  return s || DEFAULT_DOOR;
}

export function doorBase(env) {
  const raw = env && typeof env.FRAGGATE_DOOR === "string" ? env.FRAGGATE_DOOR.trim() : "";
  return raw ? normalizeDoorOrigin(raw) : DEFAULT_DOOR;
}

/** Placeholder host for service-binding fetch. Hostname is not DNS-resolved. */
export const SERVICE_BINDING_ORIGIN = "https://aziel-runtime";

/**
 * Join door origin + FragGate path without doubling `/v1/fraggate`.
 * Origin list is GET `/v1/fraggate/list`. Origin call is POST `/v1/fraggate/call`.
 */
export function joinDoorUrl(base, pathAndQuery) {
  const origin = normalizeDoorOrigin(base);
  const raw = String(pathAndQuery == null ? "" : pathAndQuery);
  const qIndex = raw.indexOf("?");
  const pathOnly = qIndex >= 0 ? raw.slice(0, qIndex) : raw;
  const query = qIndex >= 0 ? raw.slice(qIndex) : "";
  let path = pathOnly.startsWith("/") ? pathOnly : `/${pathOnly}`;
  path = path.replace(/\/{2,}/g, "/");
  path = path.replace(/^(?:\/v1\/fraggate)+/i, "/v1/fraggate");
  if (path === "/" || path === "") path = "/v1/fraggate";
  else if (!/^\/v1\/fraggate(\/|$)/i.test(path)) path = `/v1/fraggate${path === "/" ? "" : path}`;
  return origin + path + query;
}

/** Join origin + path without rewriting onto `/v1/fraggate`. Used by /v1/mesh/*. */
export function joinOriginUrl(base, pathAndQuery) {
  const origin = normalizeDoorOrigin(base);
  const raw = String(pathAndQuery == null ? "" : pathAndQuery);
  const qIndex = raw.indexOf("?");
  const pathOnly = qIndex >= 0 ? raw.slice(0, qIndex) : raw;
  const query = qIndex >= 0 ? raw.slice(qIndex) : "";
  let path = pathOnly.startsWith("/") ? pathOnly : `/${pathOnly}`;
  path = path.replace(/\/{2,}/g, "/");
  if (!path || path === "/") path = "/";
  return origin + path + query;
}

export function normalizeMeshPath(pathname) {
  const raw = String(pathname == null ? "" : pathname);
  const noQuery = raw.split("?")[0];
  const path = noQuery.replace(/\/+$/, "") || "/";
  return path.startsWith("/") ? path : `/${path}`;
}

export function isMeshPath(pathname) {
  const path = normalizeMeshPath(pathname);
  return path === "/v1/mesh" || path.startsWith("/v1/mesh/");
}

export function doorService(env) {
  const bind = env && env.AZIEL_RUNTIME;
  if (bind && typeof bind === "object" && typeof bind.fetch === "function") return bind;
  return null;
}

function isSelfDoorUrl(url, request) {
  try {
    const there = new URL(url).origin;
    if (there === HOST) return true;
    if (request && request.url) {
      const here = new URL(request.url).origin;
      if (here && here === there) return true;
    }
  } catch {
    /* ignore */
  }
  return false;
}

function fgErrFields({ message, door_url, http_status, content_type, via, extra }) {
  return {
    ok: false,
    code: "FG-ERR",
    door: "fraggate",
    kernel: KERNEL,
    message,
    door_url: door_url || "",
    http_status: http_status == null ? null : http_status,
    content_type: content_type || "",
    via: via || "",
    ...(extra || {}),
  };
}

/**
 * Fetch one door path. Prefer env.AZIEL_RUNTIME service binding
 * (`https://aziel-runtime/v1/fraggate/…` — hostname is a placeholder).
 * Public FRAGGATE_DOOR HTTP only when the binding is unbound.
 */
export async function doorFetch(env, pathAndQuery, init, request) {
  const headers = new Headers((init && init.headers) || {});
  if (!headers.has("User-Agent") && !headers.has("user-agent")) headers.set("User-Agent", "Mozilla/5.0");
  if (!headers.has("Accept") && !headers.has("accept")) headers.set("Accept", "application/json");
  headers.set("X-Aziel-Runtime-Via", "fraggate-download-tracker");
  const next = { ...(init || {}), headers };
  if (!next.signal && typeof AbortSignal !== "undefined" && typeof AbortSignal.timeout === "function") {
    next.signal = AbortSignal.timeout(20000);
  }

  const door_url = joinDoorUrl(doorBase(env), pathAndQuery);
  const bind = doorService(env);
  if (bind) {
    const res = await bind.fetch(new Request(SERVICE_BINDING_ORIGIN + pathAndQuery, next));
    return { res, via: "service-binding", door_url };
  }

  if (isSelfDoorUrl(door_url, request)) {
    throw new Error("Door URL points at this Worker — refusing self-fetch loop.");
  }
  const res = await fetch(door_url, next);
  return { res, via: "http", door_url };
}

/**
 * Fetch an origin path as-is (no /v1/fraggate rewrite).
 * Prefer env.AZIEL_RUNTIME service binding. HTTP fallback when unbound.
 */
export async function originFetch(env, pathAndQuery, init, request) {
  const headers = new Headers((init && init.headers) || {});
  if (!headers.has("User-Agent") && !headers.has("user-agent")) headers.set("User-Agent", "Mozilla/5.0");
  if (!headers.has("Accept") && !headers.has("accept")) headers.set("Accept", "application/json");
  headers.set("X-Aziel-Runtime-Via", "fraggate-download-tracker");
  const next = { ...(init || {}), headers };
  if (!next.signal && typeof AbortSignal !== "undefined" && typeof AbortSignal.timeout === "function") {
    next.signal = AbortSignal.timeout(20000);
  }

  const raw = String(pathAndQuery == null ? "" : pathAndQuery);
  const path = raw.startsWith("/") ? raw : `/${raw}`;
  const door_url = joinOriginUrl(doorBase(env), path);
  const bind = doorService(env);
  if (bind) {
    const res = await bind.fetch(new Request(SERVICE_BINDING_ORIGIN + path, next));
    return { res, via: "service-binding", door_url };
  }

  if (isSelfDoorUrl(door_url, request)) {
    throw new Error("Door URL points at this Worker — refusing self-fetch loop.");
  }
  const res = await fetch(door_url, next);
  return { res, via: "http", door_url };
}

function meshErrFields({ message, door_url, http_status, content_type, via, extra }) {
  return attachQnsCd({
    ok: false,
    code: "MESH-ERR",
    door: "mesh",
    kernel: "mesh",
    spec: "QNM-BUILD-1.0",
    qns_cd: QNS_CD,
    qns_cd_spec: QNS_CD_SPEC,
    author: AUTHOR,
    identity: AUTHOR,
    node_gate: false,
    auto_heal: false,
    anonymity_network: false,
    message,
    door_url: door_url || "",
    http_status: http_status == null ? null : http_status,
    content_type: content_type || "",
    via: via || "",
    ...(extra || {}),
  });
}

/**
 * PROXY one allowlisted /v1/mesh/* path to aziel-runtime.
 * Not a local op. GET never enables. Default radios OFF.
 */
export async function runMeshProxy(env, request, pathAndQuery) {
  const pathOnly = normalizeMeshPath(pathAndQuery);
  const allowed = MESH_ROUTE_METHODS[pathOnly];
  if (!allowed) {
    return {
      status: 404,
      data: meshErrFields({
        message: "Unknown mesh path. Use GET /v1/mesh /status /nodes or POST /enable /disable /join /heartbeat /leave /broadcast.",
        extra: { code: "MESH-UNKNOWN", path: pathOnly },
      }),
    };
  }
  const method = String((request && request.method) || "GET").toUpperCase();
  if (!allowed.includes(method)) {
    return {
      status: 405,
      data: meshErrFields({
        message: "Method not allowed on " + pathOnly + ".",
        extra: { code: "MESH-METHOD", path: pathOnly, method },
      }),
    };
  }

  let search = "";
  try {
    if (pathAndQuery && String(pathAndQuery).includes("?")) {
      search = "?" + String(pathAndQuery).split("?").slice(1).join("?");
    } else if (request && request.url) {
      search = new URL(request.url).search || "";
    }
  } catch {
    search = "";
  }
  const path = pathOnly + search;

  let body;
  if (method === "POST") {
    try {
      body = await request.json();
    } catch {
      body = {};
    }
  }

  const headers = {
    Accept: "application/json",
    "User-Agent": "Mozilla/5.0",
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (request && request.headers) {
    const token = request.headers.get("Authorization") || request.headers.get("X-Aziel-Runtime-Token");
    if (token) {
      headers.Authorization = token.startsWith("Bearer ") || token.startsWith("bearer ") ? token : `Bearer ${token}`;
      headers["X-Aziel-Runtime-Token"] = token.replace(/^Bearer\s+/i, "");
    }
  }

  const door_url = joinOriginUrl(doorBase(env), path);
  let fetched;
  try {
    fetched = await originFetch(
      env,
      path,
      {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      },
      request,
    );
  } catch (err) {
    return {
      status: 502,
      data: meshErrFields({
        message: "Mesh door fetch failed.",
        door_url,
        http_status: null,
        content_type: "",
        via: doorService(env) ? "service-binding" : "http",
        extra: { detail: String(err && err.message ? err.message : err) },
      }),
    };
  }

  const res = fetched.res;
  const via = fetched.via;
  const len = Number(res.headers.get("Content-Length") || "0");
  if (Number.isFinite(len) && len > 2 * 1024 * 1024) {
    return {
      status: 502,
      data: meshErrFields({
        message: "Mesh response too large for this Worker proxy.",
        door_url: fetched.door_url || door_url,
        http_status: res.status,
        content_type: res.headers.get("Content-Type") || "",
        via,
      }),
    };
  }

  if (method === "HEAD") {
    return { status: res.status, data: { ok: res.ok, door: "mesh", via } };
  }

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!data || typeof data !== "object") {
    const preview = String(text || "").replace(/\s+/g, " ").slice(0, 160);
    return {
      status: res.status || 502,
      data: meshErrFields({
        message: "Mesh door returned non-JSON.",
        door_url: fetched.door_url || door_url,
        http_status: res.status,
        content_type: res.headers.get("Content-Type") || "",
        via,
        extra: { preview },
      }),
    };
  }
  return { status: res.status, data: attachQnsCd(data) };
}

export function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "private, no-store",
      ...corsHeaders(),
      ...extraHeaders,
    },
  });
}

function queryFromParams(params) {
  const usp = new URLSearchParams();
  for (const key of ["name", "slug", "digest"]) {
    if (params && params[key] != null && String(params[key]).trim() !== "") {
      usp.set(key, String(params[key]).trim());
    }
  }
  const q = usp.toString();
  return q ? `?${q}` : "";
}

/**
 * Run one of the four FragGate ops against the configured door.
 * Used by Worker /v1/fraggate/*, OpenAPI, MCP tools, and (via those
 * routes) the human buttons. Not a local kernel.
 */
export async function runFragGateOp(env, op, params = {}, request) {
  const spec = OPS[op];
  if (!spec) {
    return {
      status: 400,
      data: {
        ok: false,
        code: "FG-ERR",
        door: "fraggate",
        kernel: KERNEL,
        message: "Unknown FragGate op. Use list, describe, verify, or call.",
      },
    };
  }

  let path = spec.path;
  let method = spec.method;
  let body;

  if (op === "list" || op === "summary") {
    method = "GET";
    body = undefined;
  } else if (op === "describe") {
    method = "GET";
    path = spec.path + queryFromParams(params);
    body = undefined;
  } else if (op === "verify") {
    method = "POST";
    body = {
      name: params.name,
      slug: params.slug,
      digest: params.digest,
    };
  } else if (op === "call") {
    method = "POST";
    body = {
      name: params.name,
      slug: params.slug,
      op: params.op,
      payload: params.payload && typeof params.payload === "object" ? params.payload : {},
    };
    if (params.claim && typeof params.claim === "object") body.claim = params.claim;
  }

  const headers = {
    Accept: "application/json",
    "User-Agent": "Mozilla/5.0",
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (request && request.headers) {
    const token = request.headers.get("Authorization") || request.headers.get("X-Aziel-Runtime-Token");
    if (token) {
      headers.Authorization = token.startsWith("Bearer ") || token.startsWith("bearer ") ? token : `Bearer ${token}`;
      headers["X-Aziel-Runtime-Token"] = token.replace(/^Bearer\s+/i, "");
    }
  }

  const door_url = joinDoorUrl(doorBase(env), path);
  let fetched;
  try {
    fetched = await doorFetch(
      env,
      path,
      {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      },
      request,
    );
  } catch (err) {
    return {
      status: 502,
      data: fgErrFields({
        message: "Door fetch failed.",
        door_url,
        http_status: null,
        content_type: "",
        via: doorService(env) ? "service-binding" : "http",
        extra: { detail: String(err && err.message ? err.message : err) },
      }),
    };
  }

  const res = fetched.res;
  const via = fetched.via;
  const len = Number(res.headers.get("Content-Length") || "0");
  if (Number.isFinite(len) && len > 2 * 1024 * 1024) {
    return {
      status: 502,
      data: fgErrFields({
        message: "Door response too large for this Worker proxy.",
        door_url: fetched.door_url || door_url,
        http_status: res.status,
        content_type: res.headers.get("Content-Type") || "",
        via,
      }),
    };
  }

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!data || typeof data !== "object") {
    const preview = String(text || "").replace(/\s+/g, " ").slice(0, 160);
    return {
      status: res.status || 502,
      data: fgErrFields({
        message: "Door returned non-JSON.",
        door_url: fetched.door_url || door_url,
        http_status: res.status,
        content_type: res.headers.get("Content-Type") || "",
        via,
        extra: { preview },
      }),
    };
  }
  return { status: res.status, data };
}

export function doorHeaders(env) {
  return {
    ...corsHeaders(),
    "X-Aziel-FragGate-Door": doorBase(env),
    "Cache-Control": "private, no-store",
  };
}

export function mcpToolSchemas() {
  return [
    {
      name: "runtime_skill",
      title: "How to use FragGate",
      description:
        "Read dual-surface law: human Worker UI vs agent MCP/OpenAPI. Canonical agent path is aziel-runtime /mcp + /v1/fraggate/*. This Worker doubles List/Describe/Call/Verify.",
      annotations: { title: "How to use FragGate", readOnlyHint: true, openWorldHint: false },
      inputSchema: { type: "object", additionalProperties: true },
    },
    {
      name: "fraggate_list",
      title: "List FragGate registry",
      description:
        "Same op as the human List / LIVE ops buttons. GET /v1/fraggate/list on the door (this Worker proxies, or POST aziel-runtime /mcp).",
      annotations: { title: "List FragGate registry", readOnlyHint: true, openWorldHint: false },
      inputSchema: { type: "object", additionalProperties: true },
    },
    {
      name: "fraggate_describe",
      title: "Describe a catalog name",
      description:
        "Same op as the human Describe button. GET /v1/fraggate/describe?name= / ?slug=. Unknown names are not invented.",
      annotations: { title: "Describe a catalog name", readOnlyHint: true, openWorldHint: false },
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string" },
          slug: { type: "string" },
        },
        additionalProperties: true,
      },
    },
    {
      name: "fraggate_verify",
      title: "Verify a name or digest",
      description:
        "Same op as the human Verify button. POST /v1/fraggate/verify. Shows registry match + ledger tip when present.",
      annotations: { title: "Verify a name or digest", readOnlyHint: true, openWorldHint: false },
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string" },
          slug: { type: "string" },
          digest: { type: "string" },
        },
        additionalProperties: true,
      },
    },
    {
      name: "fraggate_call",
      title: "Call a FragGate op",
      description:
        "Same op as the human Call button. POST /v1/fraggate/call {slug|name, op, payload, claim?}. DecisionGATE runs before exec. Unknown names refuse FG-HALLUC-TOOL. Canonical catalog MCP: POST https://aziel-runtime.vibelock.workers.dev/mcp",
      annotations: { title: "Call a FragGate op", readOnlyHint: false, openWorldHint: false },
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string", description: "Registry name or slug" },
          slug: { type: "string" },
          op: { type: "string", description: "Public allowlisted op" },
          payload: { type: "object" },
          claim: { type: "object" },
        },
        required: ["op"],
        additionalProperties: true,
      },
    },
  ];
}
