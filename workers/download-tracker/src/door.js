/**
 * Shared FragGate door. Human buttons, OpenAPI, and MCP all call these
 * same four ops. This Worker is not a second kernel — it proxies the
 * public aziel-runtime door (configurable via FRAGGATE_DOOR).
 *
 * Author: Aziel Eliab only. Apache-2.0.
 */

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

export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
    "Access-Control-Allow-Headers":
      "Content-Type, Accept, Authorization, X-Aziel-Runtime-Token, MCP-Protocol-Version, mcp-session-id, User-Agent",
    "Access-Control-Expose-Headers": "X-Aziel-Runtime-Version, X-Aziel-FragGate-Door",
  };
}

export function doorBase(env) {
  const raw = env && typeof env.FRAGGATE_DOOR === "string" ? env.FRAGGATE_DOOR.trim() : "";
  if (raw) return raw.replace(/\/+$/, "");
  return DEFAULT_DOOR;
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

  const url = doorBase(env) + path;
  let res;
  try {
    res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    return {
      status: 502,
      data: {
        ok: false,
        code: "FG-ERR",
        door: "fraggate",
        kernel: KERNEL,
        message: "Door fetch failed.",
        detail: String(err && err.message ? err.message : err),
        door_url: url,
      },
    };
  }

  const len = Number(res.headers.get("Content-Length") || "0");
  if (Number.isFinite(len) && len > 2 * 1024 * 1024) {
    return {
      status: 502,
      data: {
        ok: false,
        code: "FG-ERR",
        door: "fraggate",
        message: "Door response too large for this Worker proxy.",
      },
    };
  }

  let data;
  try {
    data = await res.json();
  } catch {
    data = {
      ok: false,
      code: "FG-ERR",
      door: "fraggate",
      message: "Door returned non-JSON.",
      http_status: res.status,
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
