/**
 * FragGate Worker runtime: skill, OpenAPI, MCP, and /v1/fraggate/* proxies.
 * The four human buttons (List, Describe, Call, Verify) hit these same ops.
 * This is not a second kernel. Agent path on aziel-runtime is /mcp + /v1/fraggate/*.
 *
 * Author: Aziel Eliab only. Apache-2.0.
 */

import {
  AUTHOR,
  DEFAULT_DOOR,
  HOST,
  KERNEL,
  SIGIL,
  VERSION,
  corsHeaders,
  doorBase,
  doorHeaders,
  json,
  mcpToolSchemas,
  runFragGateOp,
} from "./door.js";

export const SKILL_MD = `---
name: FragGate
description: >-
  Use when an agent would invent a tool, skip a registry, or assert an
  ungrounded fact. Dual surface: human Worker UI + agent MCP/OpenAPI over
  the same List/Describe/Call/Verify door. Kernel FG-0.1. Author Aziel Eliab.
---

# FragGate

Kernel against tool fragmentation and model hallucination. **Not** a Lock.
**Not** a chatbot personality. **Not** UI-only.

Author: **Aziel Eliab**. Version: ${VERSION}. Magic: \`FGT1\`. Paper: FG-WP-0.1.
License: Apache-2.0.

**THIS IS:** a local FG-0.1 kernel plus a dual-surface product door.
Tools exist only in a hashed registry. Execution is CallEnvelope only.
Assertion is ResultEnvelope only. Every call appends a ledger.

**THIS IS NOT:** another Lock, a public chat personality, a network relay,
a second identity, or a second kernel. The Worker UI does not invent ops
the agent cannot call.

## Dual-surface law

1. **Agent / MCP / OpenAPI** — Software runs through the door. Show
   \`display.title\`, \`display.summary\`, and refuse codes. Session ids and
   HTTP stay invisible unless the user asked for them.
2. **Human software** — Worker homepage, Flutter \`mobile/\`, local install,
   and counted \`/download\` stay complete developed software. Buttons are
   wired to the same four ops the agent uses.

Canonical **agent path** (aziel-runtime):

- \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`
- \`GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list\`
- \`GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/describe?name=\`
- \`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/verify\`
- \`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call\`

This Worker **doubles** those four ops (proxy, not a second kernel):

- Human UI: \`${HOST}/\`
- OpenAPI: \`${HOST}/openapi.json\`
- MCP: \`POST ${HOST}/mcp\`
- Same routes: \`${HOST}/v1/fraggate/list|describe|verify|call\`

Always send \`User-Agent: Mozilla/5.0\`. Cloudflare Workers may 403 an empty agent.

## Compatible AI clients

ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic Desktop / custom tools),
Cursor (MCP), Glama (Install Server / MCP), Perplexity, Microsoft Copilot / Bing,
Google Gemini / Vertex AI, Mistral, Meta AI, Apple Intelligence / Applebot surfaces,
Amazon Q / Amazonbot tooling, DuckAssist / DuckDuckGo AI, You.com, Cohere,
plus other MCP/OpenAPI-capable assistants.

Practical pull + call:

- **ChatGPT** — GPT Actions → Import from URL → \`https://aziel-runtime.vibelock.workers.dev/openapi.json\` (or this Worker \`/openapi.json\`)
- **Grok** — custom tool / OpenAPI / MCP remote → catalog OpenAPI or \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`
- **Venice** — custom HTTP tools / OpenAPI → same
- **Claude Desktop / Cursor / Glama** — MCP remote \`POST https://aziel-runtime.vibelock.workers.dev/mcp\` (this Worker \`POST /mcp\` doubles List/Describe/Call/Verify)

## How an agent uses it

1. **Discover.** \`runtime_skill\` or \`fraggate_list\`. \`fraggate_describe\` one name. \`fraggate_verify\` a name or digest.
2. **Route.** \`fraggate_call\` with \`{ name|slug, op, payload, claim? }\`. DecisionGATE runs before exec.
3. **Refuse.** Unknown names return \`FG-HALLUC-TOOL\`. Stubs and \`local_only\` do not execute. Gate BLOCK/REVISE is ledgered.
4. **Show the output.** Results are \`{ display, result, ledger_tip? }\`. Show refuse codes clearly. Do not soften them.

Do **not** invent flat \`{slug}_{op}\` tool names. They are not the door.

Local kernel builtins (Python, unchanged FG-0.1): \`runtime.ping\`, \`registry.list\`, \`registry.verify\`, \`claim.check\`, \`runtime.receipt\`. Bind anything else with \`bind_adapter\`.

## Refuse codes (do not soften)

| Code | When |
| --- | --- |
| \`FG-HALLUC-TOOL\` | Name not in the registry |
| \`FG-HALLUC-FACT\` | Fact without GroundingRef, or search without \`allow_search\` |
| \`FG-HALLUC-ARTIFACT\` | Invented artifact (error, not a draft) |
| \`FG-FRAG-SCHEMA\` | Args drifted, or silent spec mutation |
| \`FG-FRAG-ORPHAN\` | Name/handler/digest disagree |
| \`FG-GATE\` | DecisionGATE refuse; same \`call_id\` cannot retry friendlier |
| \`FG-EXPORT\` | Export without \`allow_export\` |
| \`FG-ERR\` | Bad envelope or kernel fault |
| \`FG-STUB\` | Hosted door: stub op, not live |
| \`FG-UNKNOWN-OP\` | Hosted door: name live, op missing or not allowlisted |

Do not invent tools, facts, artifacts, outcomes, or DOIs. Do not open a second kernel for the same session.

Cite GitHub and this Worker. No Zenodo DOI is invented here.
Apache-2.0. Forks are welcome and always allowed.
`;

export const EXAMPLE = {
  list: { method: "GET", path: "/v1/fraggate/list" },
  describe: { method: "GET", path: "/v1/fraggate/describe?name=decisiongate" },
  verify: { method: "POST", path: "/v1/fraggate/verify", body: { slug: "decisiongate" } },
  call: {
    method: "POST",
    path: "/v1/fraggate/call",
    body: { slug: "decisiongate", op: "health", payload: {} },
  },
  note: "Same four ops as the human buttons and as MCP tools fraggate_list / fraggate_describe / fraggate_verify / fraggate_call. Canonical agent door: " + DEFAULT_DOOR,
};

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

export function openapiSpec(origin, env) {
  const door = doorBase(env);
  return {
    openapi: "3.1.0",
    info: {
      title: "FragGate",
      version: VERSION,
      summary:
        "Dual surface: human Worker UI + agent MCP/OpenAPI. Same four ops: list, describe, call, verify. Not a second kernel.",
      description:
        "FragGate FG-0.1 door. Human buttons on this Worker call /v1/fraggate/*. MCP tools fraggate_list / fraggate_describe / fraggate_verify / fraggate_call map to those same routes (proxied to " +
        door +
        "). Canonical agent path: POST " +
        door +
        "/mcp and " +
        door +
        "/v1/fraggate/*. Author Aziel Eliab. Apache-2.0.",
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: AUTHOR, url: KERNEL },
    },
    servers: [
      { url: origin, description: "This Worker (human UI + OpenAPI/MCP doubles)" },
      { url: door, description: "aziel-runtime FragGate door (canonical agent path)" },
    ],
    paths: {
      "/v1/health": {
        get: {
          operationId: "fraggate_health",
          summary: "Liveness. Does not increment downloads.",
          responses: { "200": { description: "ok" } },
        },
      },
      "/v1/skill": {
        get: {
          operationId: "fraggate_skill",
          summary: "Skill markdown for assistants. Dual-surface law.",
          responses: { "200": { description: "markdown" } },
        },
      },
      "/v1/example": {
        get: {
          operationId: "fraggate_example",
          summary: "Sample List/Describe/Call/Verify payloads.",
          responses: { "200": { description: "ok" } },
        },
      },
      "/v1/fraggate": {
        get: {
          operationId: "fraggate_summary",
          summary: "Door summary (registry digest, live/stub counts). Same as catalog GET /v1/fraggate.",
          responses: { "200": { description: "summary" } },
        },
      },
      "/v1/fraggate/list": {
        get: {
          operationId: "fraggate_list",
          summary: "List hashed registry / LIVE ops. Same as the human List button and MCP fraggate_list.",
          responses: { "200": { description: "registry" } },
        },
      },
      "/v1/fraggate/describe": {
        get: {
          operationId: "fraggate_describe",
          summary: "Describe one name. Same as the human Describe button and MCP fraggate_describe.",
          parameters: [
            { name: "name", in: "query", schema: { type: "string" } },
            { name: "slug", in: "query", schema: { type: "string" } },
          ],
          responses: { "200": { description: "entry" } },
        },
      },
      "/v1/fraggate/verify": {
        post: {
          operationId: "fraggate_verify",
          summary: "Verify a name or digest. Same as the human Verify button and MCP fraggate_verify.",
          requestBody: {
            required: true,
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  properties: {
                    name: { type: "string" },
                    slug: { type: "string" },
                    digest: { type: "string" },
                  },
                },
                example: { slug: "decisiongate" },
              },
            },
          },
          responses: { "200": { description: "verify" } },
        },
      },
      "/v1/fraggate/call": {
        post: {
          operationId: "fraggate_call",
          summary: "CallEnvelope → DecisionGATE → handler or refuse. Same as the human Call button and MCP fraggate_call.",
          requestBody: {
            required: true,
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  properties: {
                    name: { type: "string" },
                    slug: { type: "string" },
                    op: { type: "string" },
                    payload: { type: "object" },
                    claim: { type: "object" },
                  },
                  required: ["op"],
                },
                example: { slug: "decisiongate", op: "health", payload: {} },
              },
            },
          },
          responses: {
            "200": { description: "result or typed refuse (FG-HALLUC-TOOL, FG-GATE, FG-STUB, …)" },
          },
        },
      },
      "/mcp": {
        post: {
          operationId: "fraggate_mcp",
          summary:
            "JSON-RPC MCP. Tools: runtime_skill, fraggate_list, fraggate_describe, fraggate_verify, fraggate_call. Canonical catalog MCP remains POST " +
            door +
            "/mcp.",
          requestBody: {
            required: true,
            content: { "application/json": { schema: { type: "object" } } },
          },
          responses: { "200": { description: "JSON-RPC" } },
        },
      },
    },
  };
}

function aiHtml(origin, env) {
  const door = doorBase(env);
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>FragGate — AI runtime</title>
<style>:root{color-scheme:dark}body{font:16px/1.45 system-ui,sans-serif;max-width:46rem;margin:3rem auto;padding:0 1.25rem;background:#0b0b0b;color:#e8e0d0}a{color:#c9a227}.banner{border:1px solid #5c4a1a;background:#241c0d;color:#f0d78c;padding:.85rem 1rem;border-radius:8px}pre{background:#141414;padding:.85rem 1rem;overflow:auto;border-radius:8px}</style></head>
<body>
<img src="${SIGIL}" alt="Everblooming sigil — Aziel Eliab" width="48" height="48">
<h1>FragGate runtime</h1>
<p class="banner">Dual surface. Human UI is the Worker homepage. Agent path is MCP/OpenAPI over the same List / Describe / Call / Verify ops. Not a second kernel. Author Aziel Eliab.</p>
<p>Canonical agent door: <code>POST ${door}/mcp</code> and <code>${door}/v1/fraggate/*</code></p>
<p>This Worker doubles those four ops: <code>POST ${origin}/mcp</code> · <a href="${origin}/openapi.json">${origin}/openapi.json</a> · <a href="${origin}/v1/skill">skill</a></p>
<pre>curl -sS -A 'Mozilla/5.0' ${origin}/v1/fraggate/list
curl -sS -A 'Mozilla/5.0' '${origin}/v1/fraggate/describe?name=decisiongate'
curl -sS -A 'Mozilla/5.0' -X POST ${origin}/v1/fraggate/verify -H 'content-type: application/json' -d '{"slug":"decisiongate"}'
curl -sS -A 'Mozilla/5.0' -X POST ${origin}/v1/fraggate/call -H 'content-type: application/json' -d '{"slug":"decisiongate","op":"health","payload":{}}'
curl -sS -A 'Mozilla/5.0' -X POST ${door}/mcp -H 'content-type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'</pre>
<p>Works with ChatGPT, Grok, Venice, Claude, Cursor, Glama, Perplexity, Copilot, Gemini, Mistral, Meta AI, Apple Intelligence, Amazon Q, DuckAssist, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.</p>
<p><a href="/">Human UI</a></p>
</body></html>`;
}

function mcpInitialize(env) {
  return {
    protocolVersion: "2025-03-26",
    capabilities: { tools: { listChanged: false } },
    serverInfo: { name: "fraggate", version: VERSION },
    instructions:
      "FragGate FG-0.1 — one door, discover / route / refuse. Dual surface: human Worker UI and this MCP share List/Describe/Call/Verify. Canonical catalog agent path is POST " +
      doorBase(env) +
      "/mcp and " +
      doorBase(env) +
      "/v1/fraggate/*. Start with runtime_skill or fraggate_list. Unknown names refuse FG-HALLUC-TOOL. Show display and refuse codes. Author Aziel Eliab only.",
  };
}

async function handleMcpJson(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }, 400);
  }

  const id = body && Object.prototype.hasOwnProperty.call(body, "id") ? body.id : null;
  const method = body && body.method;
  const params = (body && body.params) || {};

  if (method === "initialize") {
    return json({ jsonrpc: "2.0", id, result: mcpInitialize(env) });
  }
  if (method === "notifications/initialized" || method === "initialized") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (method === "ping") {
    return json({ jsonrpc: "2.0", id, result: {} });
  }
  if (method === "tools/list") {
    return json({ jsonrpc: "2.0", id, result: { tools: mcpToolSchemas() } });
  }
  if (method === "tools/call") {
    const name = params.name;
    const args = params.arguments && typeof params.arguments === "object" ? params.arguments : {};
    if (name === "runtime_skill") {
      return json({
        jsonrpc: "2.0",
        id,
        result: { content: [{ type: "text", text: SKILL_MD }] },
      });
    }
    const map = { fraggate_list: "list", fraggate_describe: "describe", fraggate_verify: "verify", fraggate_call: "call" };
    const op = map[name];
    if (!op) {
      return json({
        jsonrpc: "2.0",
        id,
        result: {
          isError: true,
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  ok: false,
                  code: "FG-HALLUC-TOOL",
                  message: "Unknown MCP tool. Use fraggate_list, fraggate_describe, fraggate_verify, fraggate_call, or runtime_skill. Canonical catalog MCP: " + doorBase(env) + "/mcp",
                },
                null,
                2,
              ),
            },
          ],
        },
      });
    }
    const out = await runFragGateOp(env, op, args, request);
    const text = JSON.stringify(out.data, null, 2);
    return json({
      jsonrpc: "2.0",
      id,
      result: {
        isError: out.data && out.data.ok === false,
        content: [{ type: "text", text }],
      },
    });
  }

  return json({
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: "Method not found. Use initialize, tools/list, tools/call." },
  });
}

async function readJsonBody(request) {
  try {
    return await request.json();
  } catch {
    return {};
  }
}

export { SKILL_MD as SKILL };

export async function handleRuntimeApi(request, url, env) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  const extra = doorHeaders(env);

  if (path === "/mcp") {
    if (request.method === "GET" || request.method === "HEAD") {
      const body = {
        ok: true,
        door: "fraggate",
        kernel: KERNEL,
        this_worker_mcp: originOf(request) + "/mcp",
        catalog_mcp: doorBase(env) + "/mcp",
        catalog_openapi: doorBase(env) + "/openapi.json",
        worker_openapi: originOf(request) + "/openapi.json",
        ops: ["fraggate_list", "fraggate_describe", "fraggate_verify", "fraggate_call", "runtime_skill"],
        note: "POST JSON-RPC here to double the human buttons. Canonical agent path is the catalog MCP on aziel-runtime.",
        author: AUTHOR,
      };
      if (request.method === "HEAD") return new Response(null, { status: 200, headers: extra });
      return json(body);
    }
    if (request.method === "POST") return handleMcpJson(request, env);
  }

  if (path === "/v1/health" && (request.method === "GET" || request.method === "HEAD")) {
    const body = {
      ok: true,
      product: "fraggate",
      version: VERSION,
      magic: "FGT1",
      paper: "FG-WP-0.1",
      kernel: KERNEL,
      door: "fraggate",
      door_url: doorBase(env),
      kv_increment: false,
      second_kernel: false,
      ops: ["list", "describe", "verify", "call"],
      catalog_mcp: doorBase(env) + "/mcp",
      catalog_openapi: doorBase(env) + "/openapi.json",
      author: AUTHOR,
      sigil: SIGIL,
      limitation:
        "THIS IS: FG-0.1 kernel + dual-surface door (Worker UI and MCP/OpenAPI share List/Describe/Call/Verify). THIS IS NOT: a second kernel, a Lock, or UI-only FragGate.",
    };
    if (request.method === "HEAD") return new Response(null, { status: 200, headers: extra });
    return json(body);
  }

  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL_MD, {
      status: 200,
      headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...extra },
    });
  }

  if (path === "/v1/example" && (request.method === "GET" || request.method === "HEAD")) {
    return json({ ok: true, product: "fraggate", author: AUTHOR, example: EXAMPLE, kv_increment: false });
  }

  if (path === "/openapi.json" && request.method === "GET") {
    return json(openapiSpec(originOf(request), env));
  }

  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return new Response(aiHtml(originOf(request), env), {
      headers: { "Content-Type": "text/html; charset=utf-8", ...extra },
    });
  }

  if (path === "/v1/fraggate" && (request.method === "GET" || request.method === "HEAD" || request.method === "POST")) {
    const out = await runFragGateOp(env, "summary", {}, request);
    if (request.method === "HEAD") return new Response(null, { status: out.status, headers: extra });
    return json(out.data, out.status, extra);
  }
  if (path === "/v1/fraggate/list" && (request.method === "GET" || request.method === "HEAD" || request.method === "POST")) {
    const out = await runFragGateOp(env, "list", {}, request);
    if (request.method === "HEAD") return new Response(null, { status: out.status, headers: extra });
    return json(out.data, out.status, extra);
  }
  if (path === "/v1/fraggate/describe" && (request.method === "GET" || request.method === "POST")) {
    const params = request.method === "GET" ? { name: url.searchParams.get("name"), slug: url.searchParams.get("slug") } : await readJsonBody(request);
    const out = await runFragGateOp(env, "describe", params, request);
    return json(out.data, out.status, extra);
  }
  if (path === "/v1/fraggate/verify" && (request.method === "GET" || request.method === "POST")) {
    const params =
      request.method === "GET"
        ? { name: url.searchParams.get("name"), slug: url.searchParams.get("slug"), digest: url.searchParams.get("digest") }
        : await readJsonBody(request);
    const out = await runFragGateOp(env, "verify", params, request);
    return json(out.data, out.status, extra);
  }
  if (path === "/v1/fraggate/call" && request.method === "POST") {
    const params = await readJsonBody(request);
    const out = await runFragGateOp(env, "call", params, request);
    return json(out.data, out.status, extra);
  }

  if (path.startsWith("/v1/") || path === "/v1") {
    return json(
      {
        error: "not found",
        hint: "GET /v1/health /v1/skill /v1/example /v1/fraggate /v1/fraggate/list /v1/fraggate/describe  POST /v1/fraggate/verify /v1/fraggate/call  POST /mcp",
        catalog_agent: doorBase(env) + "/mcp",
      },
      404,
    );
  }
  return null;
}
