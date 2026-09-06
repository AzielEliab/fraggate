#!/usr/bin/env node
/**
 * Assert Worker /v1/fraggate list+call proxy returns JSON ok.
 * Offline: mock AZIEL_RUNTIME service binding (same path the live Worker uses).
 * Optional live origin check if FRAGGATE_LIVE=1.
 * Author: Aziel Eliab. Apache-2.0.
 */
import assert from "node:assert/strict";
import {
  joinDoorUrl,
  joinOriginUrl,
  normalizeDoorOrigin,
  runFragGateOp,
  runMeshProxy,
  SERVICE_BINDING_ORIGIN,
  HOST,
} from "../src/door.js";
import { handleRuntimeApi } from "../src/runtime.js";
import { meshPointer } from "../src/mesh.js";

const ORIGIN = "https://aziel-runtime.vibelock.workers.dev";

assert.equal(normalizeDoorOrigin(`${ORIGIN}/v1/fraggate/`), ORIGIN);
assert.equal(joinDoorUrl(ORIGIN, "/v1/fraggate/list"), `${ORIGIN}/v1/fraggate/list`);
assert.equal(joinDoorUrl(`${ORIGIN}/v1/fraggate`, "/v1/fraggate/list"), `${ORIGIN}/v1/fraggate/list`);
assert.equal(joinDoorUrl(`${ORIGIN}/`, "/v1/fraggate/v1/fraggate/call"), `${ORIGIN}/v1/fraggate/call`);
assert.equal(
  joinDoorUrl(ORIGIN, "/v1/fraggate/describe?name=azbrowser"),
  `${ORIGIN}/v1/fraggate/describe?name=azbrowser`,
);
assert.notEqual(joinDoorUrl(ORIGIN, "/v1/fraggate/list"), `${ORIGIN}/v1/fraggate/v1/fraggate/list`);
assert.equal(joinOriginUrl(ORIGIN, "/v1/mesh"), `${ORIGIN}/v1/mesh`);
assert.equal(joinOriginUrl(ORIGIN, "/v1/mesh/nodes"), `${ORIGIN}/v1/mesh/nodes`);
assert.notEqual(joinDoorUrl(ORIGIN, "/v1/mesh"), `${ORIGIN}/v1/mesh`);
assert.equal(joinDoorUrl(ORIGIN, "/v1/mesh"), `${ORIGIN}/v1/fraggate/v1/mesh`);
assert.equal(meshPointer().enabled_default, false);
assert.equal(meshPointer().node_gate, false);
assert.equal(meshPointer().rollup, "live|locked|isolated");

function jsonRes(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

const mockList = {
  ok: true,
  door: "fraggate",
  kernel: "https://github.com/AzielEliab/fraggate",
  live_count: 1,
  entries: [{ slug: "azbrowser", status: "live" }],
};
const mockCall = {
  ok: true,
  code: "FG-OK",
  door: "fraggate",
  slug: "azbrowser",
  op: "ethical_search",
  result: { ok: true, product: "azbrowser", query: "x" },
};

const seen = [];
const env = {
  FRAGGATE_DOOR: ORIGIN,
  AZIEL_RUNTIME: {
    async fetch(request) {
      const url = new URL(request.url);
      seen.push({ method: request.method, href: url.href, path: url.pathname, search: url.search });
      assert.equal(url.origin, SERVICE_BINDING_ORIGIN);
      if (url.pathname === "/v1/fraggate/list" && request.method === "GET") return jsonRes(mockList);
      if (url.pathname === "/v1/fraggate/call" && request.method === "POST") {
        const body = await request.json();
        assert.equal(body.slug, "azbrowser");
        assert.equal(body.op, "ethical_search");
        return jsonRes(mockCall);
      }
      if (url.pathname === "/v1/mesh" && request.method === "GET") {
        return jsonRes({
          ok: true,
          code: "MESH-OK",
          enabled: false,
          radios: "off",
          mesh_default: "off",
          spec: "QNM-BUILD-1.0",
          rollup: { live: 0, locked: 0, isolated: 0 },
          live_nodes: 0,
          author: "Aziel Eliab",
        });
      }
      if (url.pathname === "/v1/mesh/enable" && request.method === "POST") {
        const body = await request.json();
        if (!body.bearer) return jsonRes({ ok: false, code: "MESH-NEED-BEARER", enabled: false }, 400);
        return jsonRes({ ok: true, code: "MESH-OK", enabled: true, radios: "on", bearers: [body.bearer] });
      }
      return jsonRes({ error: "not found", hint: "GET /v1/fraggate/list  POST /v1/fraggate/call  GET /v1/mesh" }, 404);
    },
  },
};

const listOp = await runFragGateOp(env, "list", {}, new Request(`${HOST}/v1/fraggate/list`));
assert.equal(listOp.status, 200);
assert.equal(listOp.data.ok, true);
assert.ok(listOp.data.entries);
assert.notEqual(listOp.data.code, "FG-ERR");
assert.notEqual(listOp.data.message, "Door returned non-JSON.");

const callOp = await runFragGateOp(
  env,
  "call",
  { slug: "azbrowser", op: "ethical_search", payload: { q: "x" } },
  new Request(`${HOST}/v1/fraggate/call`, { method: "POST" }),
);
assert.equal(callOp.status, 200);
assert.equal(callOp.data.ok, true);
assert.equal(callOp.data.code, "FG-OK");
assert.notEqual(callOp.data.message, "Door returned non-JSON.");

async function worker(path, method = "GET", body) {
  const req = new Request(`https://fraggate-download-tracker.vibelock.workers.dev${path}`, {
    method,
    headers: { Accept: "application/json", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const res = await handleRuntimeApi(req, new URL(req.url), env);
  assert.ok(res, `route ${method} ${path} must be handled`);
  const data = await res.json();
  assert.equal(typeof data, "object");
  assert.notEqual(data.message, "Door returned non-JSON.");
  return { status: res.status, data };
}

const listHttp = await worker("/v1/fraggate/list", "GET");
assert.equal(listHttp.status, 200);
assert.equal(listHttp.data.ok, true);

const callHttp = await worker("/v1/fraggate/call", "POST", {
  slug: "azbrowser",
  op: "ethical_search",
  payload: { q: "x" },
});
assert.equal(callHttp.status, 200);
assert.equal(callHttp.data.ok, true);
assert.equal(callHttp.data.code, "FG-OK");

assert.ok(seen.some((s) => s.method === "GET" && s.href === `${SERVICE_BINDING_ORIGIN}/v1/fraggate/list`));
assert.ok(seen.some((s) => s.method === "POST" && s.path === "/v1/fraggate/call"));

const meshOp = await runMeshProxy(env, new Request(`${HOST}/v1/mesh`), "/v1/mesh");
assert.equal(meshOp.status, 200);
assert.equal(meshOp.data.ok, true);
assert.equal(meshOp.data.enabled, false);
assert.equal(meshOp.data.code, "MESH-OK");
assert.deepEqual(meshOp.data.rollup, { live: 0, locked: 0, isolated: 0 });

const meshHttp = await worker("/v1/mesh", "GET");
assert.equal(meshHttp.status, 200);
assert.equal(meshHttp.data.ok, true);
assert.equal(meshHttp.data.enabled, false);

const enableEmpty = await worker("/v1/mesh/enable", "POST", {});
assert.equal(enableEmpty.status, 400);
assert.equal(enableEmpty.data.code, "MESH-NEED-BEARER");
assert.notEqual(enableEmpty.data.enabled, true);

const enableOk = await worker("/v1/mesh/enable", "POST", { bearer: "suite-presence" });
assert.equal(enableOk.status, 200);
assert.equal(enableOk.data.enabled, true);

assert.ok(seen.some((s) => s.method === "GET" && s.href === `${SERVICE_BINDING_ORIGIN}/v1/mesh`));
assert.ok(seen.some((s) => s.method === "POST" && s.path === "/v1/mesh/enable"));

const unknownMesh = await worker("/v1/mesh/gate", "GET");
assert.equal(unknownMesh.status, 404);
assert.equal(unknownMesh.data.code, "MESH-UNKNOWN");

const htmlEnv = {
  FRAGGATE_DOOR: ORIGIN,
  AZIEL_RUNTIME: {
    async fetch() {
      return new Response("<!doctype html><title>404</title>", {
        status: 404,
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    },
  },
};
const htmlOp = await runFragGateOp(htmlEnv, "list", {}, new Request(`${HOST}/v1/fraggate/list`));
assert.equal(htmlOp.data.code, "FG-ERR");
assert.equal(htmlOp.data.message, "Door returned non-JSON.");
assert.equal(htmlOp.data.door_url, `${ORIGIN}/v1/fraggate/list`);
assert.equal(htmlOp.data.http_status, 404);
assert.match(htmlOp.data.content_type, /text\/html/);
assert.equal(htmlOp.data.via, "service-binding");

if (process.env.FRAGGATE_LIVE === "1") {
  const liveList = await fetch(`${ORIGIN}/v1/fraggate/list`, {
    headers: { Accept: "application/json", "User-Agent": "Mozilla/5.0" },
  });
  const liveListJson = await liveList.json();
  assert.equal(liveList.ok, true);
  assert.equal(liveListJson.ok, true);
  const liveCall = await fetch(`${ORIGIN}/v1/fraggate/call`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0" },
    body: JSON.stringify({ slug: "azbrowser", op: "ethical_search", payload: { q: "x" } }),
  });
  const liveCallJson = await liveCall.json();
  assert.equal(liveCall.ok, true);
  assert.equal(liveCallJson.ok, true);
}

console.log("verify-door-proxy: list/call + /v1/mesh proxy returns JSON ok");
