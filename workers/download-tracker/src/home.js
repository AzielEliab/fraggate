/**
 * FragGate product homepage — software UI, not a downloads shell.
 * Buttons call the same /v1/fraggate/* ops as OpenAPI and MCP.
 * Author: Aziel Eliab only. Apache-2.0. Forks welcome.
 */

import { AUTHOR, DEFAULT_DOOR, HOST, KERNEL, VERSION, corsHeaders } from "./door.js";

const GITHUB_REPO = KERNEL;
const GITHUB_LATEST = KERNEL + "/releases/latest";
const CATALOG = DEFAULT_DOOR + "/";
const CATALOG_MCP = DEFAULT_DOOR + "/mcp";
const CATALOG_OPENAPI = DEFAULT_DOOR + "/openapi.json";
const LICENSE = "https://www.apache.org/licenses/LICENSE-2.0";
const TITLE = "FragGate — Aziel Eliab";
const DEFAULT_ASSET = "fraggate-0.1.0.tar.gz";
const INSTALL_LINE = "curl -fsSL https://fraggate-download-tracker.vibelock.workers.dev/install.sh | bash";
const DESCRIPTION =
  "FragGate is Aziel Eliab software: FG-0.1 kernel against tool fragmentation and model hallucination. Dual surface — Worker UI and MCP/OpenAPI share List / Describe / Call / Verify. Apache-2.0.";
const HONEST =
  "THIS IS: the FG-0.1 door. Human buttons and MCP/OpenAPI call the same four ops (list, describe, call, verify) on /v1/fraggate/*. THIS IS NOT: a second kernel, a Lock, a chatbot personality, or UI-only chrome. Unknown names refuse FG-HALLUC-TOOL. Author Aziel Eliab.";
const HOW_TO_CITE =
  "Eliab, Aziel. (2026). FragGate FG-0.1 [Software]. Apache-2.0. https://github.com/AzielEliab/fraggate · https://fraggate-download-tracker.vibelock.workers.dev/";

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function citePayload() {
  return {
    author: AUTHOR,
    title: "FragGate",
    version: VERSION,
    homepage: HOST + "/",
    github: GITHUB_REPO,
    download: HOST + "/download",
    install: HOST + "/install.sh",
    openapi: HOST + "/openapi.json",
    skill: HOST + "/v1/skill",
    mcp: HOST + "/mcp",
    catalog: CATALOG,
    catalog_mcp: CATALOG_MCP,
    catalog_openapi: CATALOG_OPENAPI,
    mesh: HOST + "/v1/mesh",
    mesh_catalog: CATALOG + "v1/mesh",
    license: "Apache-2.0",
    license_url: LICENSE,
    one_line: DESCRIPTION,
    how_to_cite: HOW_TO_CITE,
    apa: "Eliab, A. (2026). FragGate (Version 0.1.0) [Computer software]. https://fraggate-download-tracker.vibelock.workers.dev/",
    bibtex:
      "@software{eliab_fraggate_2026, author = {Eliab, Aziel}, title = {FragGate}, version = {0.1.0}, year = {2026}, license = {Apache-2.0}, url = {https://fraggate-download-tracker.vibelock.workers.dev/}, publisher = {GitHub}, howpublished = {\\url{https://github.com/AzielEliab/fraggate}}}",
    zenodo_status: "placeholder_no_doi_invented",
    software_deposit_needed: true,
    note: "No DOI is invented here. Cite GitHub and this Worker. Identity is Aziel Eliab only. Forks welcome.",
    identity: "Aziel Eliab only",
    forks: "welcome and always allowed",
    dual_surface: "Worker UI + MCP/OpenAPI share list/describe/call/verify. Suite mesh GET /v1/mesh PROXY (default OFF). Canonical agent path is aziel-runtime /mcp + /v1/fraggate/*.",
  };
}

export function jsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "FragGate",
    alternateName: TITLE,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Linux, macOS, Windows, Cloudflare Workers",
    softwareVersion: VERSION,
    author: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    creator: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    codeRepository: GITHUB_REPO,
    downloadUrl: HOST + "/download",
    installUrl: HOST + "/install.sh",
    license: LICENSE,
    url: HOST + "/",
    description: DESCRIPTION,
    keywords: "FragGate, FG-0.1, DecisionGATE, registry, hallucination, Aziel Eliab",
    isAccessibleForFree: true,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    sameAs: [GITHUB_REPO, CATALOG],
  };
}

function sitemapXml() {
  const paths = [
    "/",
    "/download",
    "/install.sh",
    "/v1/skill",
    "/v1/example",
    "/v1/health",
    "/v1/fraggate",
    "/v1/fraggate/list",
    "/v1/mesh",
    "/openapi.json",
    "/mcp",
    "/cite.json",
    "/llms.txt",
    "/ai",
  ];
  const urls = paths.map((p) => `  <url><loc>${HOST}${p === "/" ? "/" : p}</loc></url>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
  <url><loc>${GITHUB_REPO}</loc></url>
  <url><loc>${DEFAULT_DOOR}/v1/fraggate</loc></url>
</urlset>
`;
}

function robotsTxt() {
  return `User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: Diffbot
Allow: /

User-agent: Omgilibot
Allow: /

User-agent: Amazonbot
Allow: /

Sitemap: ${HOST}/sitemap.xml
`;
}

function llmsTxt() {
  return `# FragGate

Author: Aziel Eliab
One-line: ${DESCRIPTION}
GitHub: ${GITHUB_REPO}
Homepage: ${HOST}/
Download: ${HOST}/download
Install: ${HOST}/install.sh
OpenAPI: ${HOST}/openapi.json
MCP: POST ${HOST}/mcp
Skill: ${HOST}/v1/skill
Cite: ${HOST}/cite.json
Ops (human buttons = OpenAPI = MCP): GET /v1/fraggate/list, GET /v1/fraggate/describe, POST /v1/fraggate/verify, POST /v1/fraggate/call
Suite mesh: GET ${HOST}/v1/mesh PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. Catalog MCP mesh_* + FragGate slug=mesh.
Canonical agent path: POST ${CATALOG_MCP} and ${DEFAULT_DOOR}/v1/fraggate/*
Identity: Aziel Eliab only
License: Apache-2.0
Forks: welcome and always allowed
DOI: none invented; software deposit still needed.

Indexing, metadata scrape, and AI grounding of public pages are allowed.
`;
}

export function handleSeoRoutes(request, url) {
  if (request.method !== "GET" && request.method !== "HEAD") return null;
  const headers = { ...corsHeaders(), "Cache-Control": "private, no-store" };
  if (url.pathname === "/cite.json" || url.pathname === "/cite.json/") {
    return new Response(JSON.stringify(citePayload(), null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
    });
  }
  if (url.pathname === "/sitemap.xml" || url.pathname === "/sitemap.xml/") {
    return new Response(sitemapXml(), { status: 200, headers: { "Content-Type": "application/xml; charset=utf-8", ...headers } });
  }
  if (url.pathname === "/robots.txt" || url.pathname === "/robots.txt/") {
    return new Response(robotsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  if (url.pathname === "/llms.txt" || url.pathname === "/ai.txt") {
    return new Response(llmsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  return null;
}

function breakdownList(stats) {
  const rows = stats.breakdown || [];
  if (!rows.length) return "<li>none yet</li>";
  return rows
    .map(
      (b) =>
        `<li><code>${escapeHtml(b.owner)}/${escapeHtml(b.repo)}</code> branch <code>${escapeHtml(b.branch)}</code> fork=${escapeHtml(b.fork)} → ${escapeHtml(b.count)}</li>`,
    )
    .join("");
}

export function renderHome(stats, opts = {}) {
  const views = Number(stats.views) || 0;
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const gh = stats.github || {};
  const ld = JSON.stringify(jsonLd());
  const door = opts.door || DEFAULT_DOOR;
  const boot = JSON.stringify({
    door,
    catalog: DEFAULT_DOOR,
    version: VERSION,
    host: HOST,
  });
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${TITLE}</title>
<meta name="description" content="${escapeHtml(DESCRIPTION)}">
<meta name="author" content="${AUTHOR}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="${HOST}/">
<link rel="sitemap" type="application/xml" href="${HOST}/sitemap.xml">
<link rel="icon" type="image/png" href="/sigil.png">
<meta property="og:type" content="website">
<meta property="og:title" content="${TITLE}">
<meta property="og:description" content="${escapeHtml(DESCRIPTION)}">
<meta property="og:url" content="${HOST}/">
<meta property="og:site_name" content="Aziel Eliab">
<meta property="og:image" content="${HOST}/sigil.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${TITLE}">
<meta name="twitter:description" content="${escapeHtml(DESCRIPTION)}">
<meta name="twitter:image" content="${HOST}/sigil.png">
<script type="application/ld+json">${ld}</script>
<style>
  :root {
    color-scheme: dark;
    --bg: #0b0b0b; --panel: #141414; --ink: #e8e0d0; --muted: #9aa3b2;
    --line: #2a2414; --gold: #c9a227; --gold-dim: #c9a227; --pass: #3dba7a; --bad: #d4534b; --warn: #e0a14b; --focus: #e6d19a;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink); }
  body { font: 16px/1.5 system-ui, "Segoe UI", sans-serif; }
  a { color: #e6d19a; }
  code, pre, .mono { font-family: ui-monospace, Menlo, Consolas, monospace; }
  .wrap { max-width: 58rem; margin: 0 auto; padding: 1.4rem 1.2rem 4.5rem; }
  .brandrow { display: flex; align-items: center; gap: 12px; margin: 0 0 12px; }
  .brandmark { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 auto; box-shadow: 0 0 0 1px #d4af3733; }
  .stamp { margin: 0; color: var(--gold); font-size: .88rem; letter-spacing: .02em; }
  .appbar { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
  h1 { font-size: 2rem; letter-spacing: .02em; margin: 0 0 .2rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 .7rem; }
  .lede { color: var(--muted); margin: 0 0 1rem; max-width: 46rem; }
  .pill { font: 650 .78rem/1 ui-monospace, Menlo, Consolas, monospace; letter-spacing: .06em; text-transform: uppercase; border: 1px solid var(--line); border-radius: 999px; padding: .4rem .7rem; color: var(--muted); background: #101010; }
  .pill.ok { color: var(--pass); border-color: #2f6b48; }
  .pill.bad { color: var(--bad); border-color: #7a2f2c; }
  nav.toc { display: flex; flex-wrap: wrap; gap: .55rem; margin: 0 0 1.1rem; }
  nav.toc a { text-decoration: none; color: var(--ink); border: 1px solid var(--line); background: var(--panel); border-radius: 999px; padding: .35rem .75rem; font-size: .88rem; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .9rem 1rem; border-radius: 10px; margin: 0 0 1.15rem; font-size: .94rem; }
  .card, .workspace, .cite { border: 1px solid var(--line); border-radius: 14px; padding: 1.15rem 1.2rem 1.25rem; background: var(--panel); margin: 0 0 1.1rem; }
  .workspace { box-shadow: 0 0 0 1px #d4af3714, 0 16px 40px #0006; }
  h2 { font-size: 1.12rem; margin: 0 0 .45rem; letter-spacing: .04em; }
  .kicker { display: block; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--gold); margin-bottom: .15rem; font-family: ui-monospace, Menlo, Consolas, monospace; }
  .workgrid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: 1rem; }
  @media (max-width: 820px) { .workgrid { grid-template-columns: 1fr; } }
  label { display: block; font-size: .92rem; margin: .75rem 0 .28rem; }
  input[type="text"], input[type="url"], textarea, select { width: 100%; padding: .58rem .7rem; border: 1px solid var(--line); border-radius: 8px; background: #0e0e0e; color: var(--ink); font: inherit; }
  input:focus, textarea:focus, select:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  textarea { min-height: 7rem; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .86rem; }
  .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; }
  @media (max-width: 520px) { .row2 { grid-template-columns: 1fr; } }
  .actions { display: flex; flex-wrap: wrap; gap: .5rem; margin: .95rem 0 .2rem; }
  button, a.btn { font: 700 .88rem/1.1 ui-monospace, Menlo, Consolas, monospace; letter-spacing: .03em; padding: .72rem .9rem; border-radius: 9px; border: 1px solid transparent; cursor: pointer; text-decoration: none; display: inline-block; }
  button.gold, a.btn.gold { background: var(--gold-dim); color: #14110a; }
  button.ink, a.btn.ink { background: var(--ink); color: var(--bg); }
  button.ghost, a.btn.ghost { background: transparent; color: var(--ink); border-color: var(--line); }
  button.copied { background: var(--pass); color: #0e1014; }
  .status { margin: 0 0 .8rem; padding: .75rem .85rem; border-radius: 10px; border: 1px solid var(--line); background: #101010; color: var(--muted); white-space: pre-wrap; }
  .status.ok { color: var(--pass); border-color: #2f6b48; }
  .status.bad { color: var(--bad); border-color: #7a2f2c; }
  .status.warn { color: var(--warn); border-color: #7a5a1c; }
  .metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; margin: 0 0 .85rem; }
  @media (max-width: 720px) { .metrics { grid-template-columns: 1fr; } }
  .metric { border: 1px solid var(--line); border-radius: 10px; padding: .55rem .65rem; background: #101010; }
  .metric b { display: block; font-size: .72rem; color: var(--muted); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
  .metric span { display: block; font-size: .78rem; word-break: break-all; color: var(--ink); }
  .ops { display: flex; flex-wrap: wrap; gap: .4rem; margin: 0 0 .8rem; }
  .ops button { font-size: .72rem; padding: .4rem .55rem; }
  .gate { border: 1px solid var(--line); border-radius: 10px; padding: .65rem .75rem; background: #101010; margin: 0 0 .7rem; }
  .gate h3 { margin: 0 0 .35rem; font-size: .92rem; }
  .gate li { font-size: .85rem; }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.1rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { display: block; font-size: .92rem; font-weight: 500; color: var(--muted); }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 520px) { .btns { grid-template-columns: 1fr; } }
  a.btn.block, button.btn.block { display: block; width: 100%; text-align: center; font-size: 1.15rem; padding: 1rem 1.1rem; }
  a.btn.primary { background: #e8eaef; color: #0e1014; }
  button.btn.install { background: var(--gold-dim); color: #14110a; }
  pre { background: #0e0e0e; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; }
  .meta { margin-top: 1rem; color: var(--muted); font-size: .92rem; }
  details.raw { margin-top: .8rem; }
  details.raw pre { max-height: 22rem; }
  footer { color: var(--muted); font-size: .9rem; }
  table.matrix { width: 100%; border-collapse: collapse; font-size: .86rem; }
  table.matrix th, table.matrix td { border: 1px solid var(--line); padding: .45rem .5rem; text-align: left; }
  table.matrix th { color: var(--gold); font-weight: 600; }
  #meshStrip { border: 1px solid var(--gold); border-radius: 14px; padding: .85rem 1rem; background: var(--panel); margin: 0 0 1.1rem; display: flex; flex-wrap: wrap; align-items: center; gap: .7rem 1rem; font-size: .88rem; color: var(--muted); }
  #meshStrip .live { color: var(--ink); }
  #meshStrip .live b { color: var(--gold); font-size: 1.35rem; margin-right: .35rem; }
  #meshStrip .rollup b { color: var(--gold); }
  #meshStrip button { font: 700 .78rem/1 ui-monospace, Menlo, Consolas, monospace; height: 2rem; padding: 0 .75rem; border-radius: 8px; background: #101010; color: var(--ink); border: 1px solid var(--gold); cursor: pointer; }
  #meshStrip button:hover { background: #241c0d; color: var(--gold); }
  #meshStrip input { width: 10rem; padding: .4rem .55rem; border: 1px solid var(--gold); border-radius: 8px; background: #0e0e0e; color: var(--ink); font: inherit; }
  #meshProducts { flex-basis: 100%; margin: 0; }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brandrow">
        <img class="brandmark" src="/sigil.png" width="40" height="40" alt="Everblooming sigil — Aziel Eliab" decoding="async">
        <p class="stamp">Everblooming sigil · Aziel Eliab</p>
      </div>
      <div class="appbar">
        <div>
          <h1>FragGate</h1>
          <p class="motto">One door — discover, route, refuse.</p>
        </div>
        <p class="pill" id="api-pill">API · checking</p>
      </div>
      <p class="lede">v${VERSION} software by <strong>${AUTHOR}</strong> only. Human buttons and MCP/OpenAPI share List / Describe / Call / Verify. The Python kernel stays FG-0.1. Forks are welcome and always allowed.</p>
      <nav class="toc" aria-label="Product sections">
        <a href="#workspace">Use UI</a>
        <a href="#meshStrip">Live Nodes</a>
        <a href="#install">Download / install</a>
        <a href="#matrix">Button matrix</a>
        <a href="#cite">Cite</a>
        <a href="/v1/skill">Skill</a>
        <a href="/openapi.json">OpenAPI</a>
        <a href="/mcp">MCP</a>
        <a href="${GITHUB_REPO}">GitHub</a>
      </nav>
      <p class="banner">${escapeHtml(HONEST)}</p>
    </header>

    <div id="meshStrip" aria-label="Suite Live Nodes">
      <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
      <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. Not an anonymity network.</div>
      <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
      <div>No Node Gate · No auto-heal · Aziel Eliab only</div>
      <div>
        <input id="meshBearer" type="text" maxlength="80" placeholder="bearer (required to enable)" aria-label="mesh bearer">
        <button id="meshEnable" type="button" title="Enable suite mesh. Declared bearer required. Default off.">Enable</button>
        <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
        <button id="meshJoin" type="button" title="Join as fraggate. Refused while mesh is OFF. No auto-join.">Join</button>
        <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
      </div>
      <div id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · not AnonBroadcast · not AZMail ring · not a Node Gate</div>
    </div>

    <section class="workspace" id="workspace">
      <h2><span class="kicker">Live software</span>FragGate door</h2>
      <p class="lede">Wired buttons — not chrome. They call this Worker’s <code>/v1/fraggate/*</code> (List / Describe / Call / Verify), which proxies the live catalog door <code>${DEFAULT_DOOR}/v1/fraggate/*</code>. OpenAPI and MCP share those same four ops. Suite mesh: <code>/v1/mesh/*</code> PROXY (default OFF; QNM live|locked|isolated; no Node Gate; no auto-heal; not anonymity). FragGate is the door. Canonical agent path: <code>POST ${DEFAULT_DOOR}/mcp</code>.</p>
      <div class="workgrid">
        <form id="ws-form" autocomplete="off">
          <label for="door"><span class="kicker">Door</span> Default is this Worker (same-origin <code>/v1/fraggate/*</code> proxy). “Catalog door” talks to aziel-runtime directly. Not AZBrowser.</label>
          <input id="door" type="url" placeholder="${escapeHtml(HOST)}" value="${escapeHtml(HOST)}">
          <div class="actions">
            <button type="button" class="ghost" id="btn-door-self">This Worker</button>
            <button type="button" class="ghost" id="btn-door-catalog">Catalog door</button>
          </div>
          <div class="row2">
            <div>
              <label for="slug"><span class="kicker">slug / name</span></label>
              <input id="slug" type="text" value="decisiongate" placeholder="decisiongate">
            </div>
            <div>
              <label for="op"><span class="kicker">op</span></label>
              <input id="op" type="text" value="health" placeholder="health">
            </div>
          </div>
          <label for="digest"><span class="kicker">digest</span> Optional. Used by Verify.</label>
          <input id="digest" type="text" placeholder="sha256 hex">
          <label for="args"><span class="kicker">JSON args / payload</span></label>
          <textarea id="args" spellcheck="false">{}</textarea>
          <label for="claim"><span class="kicker">claim (optional DecisionGATE)</span> JSON object or leave empty.</label>
          <textarea id="claim" spellcheck="false" placeholder='{"statement":"…","evidence":[],"impact_pos":[],"impact_neg":[],"values":[],"accountable":"Aziel Eliab"}'></textarea>
          <div class="actions">
            <button type="button" class="gold" id="btn-list">List registry</button>
            <button type="button" class="ink" id="btn-live">LIVE ops</button>
            <button type="button" class="ghost" id="btn-describe">Describe</button>
            <button type="button" class="ghost" id="btn-call">Call op</button>
            <button type="button" class="ghost" id="btn-verify">Verify</button>
            <a class="btn ghost" href="/openapi.json">OpenAPI</a>
            <a class="btn ghost" href="/mcp">MCP</a>
            <a class="btn ghost" href="${CATALOG_OPENAPI}">Catalog OpenAPI</a>
            <a class="btn ghost" href="${CATALOG_MCP}">Catalog MCP</a>
          </div>
        </form>
        <div>
          <div class="status" id="ws-status">No call yet. List walks the hashed registry. Call runs DecisionGATE. Unknown names refuse FG-HALLUC-TOOL.</div>
          <div class="metrics">
            <div class="metric"><b>Code</b><span id="last-code">—</span></div>
            <div class="metric"><b>Gate</b><span id="last-gate">—</span></div>
            <div class="metric"><b>Ledger tip</b><span id="last-tip">—</span></div>
            <div class="metric"><b>Registry digest</b><span id="last-digest">—</span></div>
          </div>
          <div class="gate" id="gate-box" hidden>
            <h3>DecisionGATE lineage</h3>
            <ol id="gate-lineage"></ol>
          </div>
          <div>
            <span class="kicker">LIVE ops</span>
            <div class="ops" id="ops-box"></div>
          </div>
          <details class="raw" open>
            <summary>Raw door result</summary>
            <pre id="raw-json">{}</pre>
          </details>
        </div>
      </div>
    </section>

    <section class="card" id="matrix">
      <h2><span class="kicker">Test matrix</span>Every button is a live op</h2>
      <table class="matrix">
        <thead><tr><th>Button</th><th>Hits</th><th>Expected</th></tr></thead>
        <tbody>
          <tr><td>List registry</td><td><code>GET /v1/fraggate/list</code></td><td>Hashed entries, registry digest, live/stub counts</td></tr>
          <tr><td>LIVE ops</td><td>same list, show <code>live_ops</code></td><td>Clickable <code>slug/op</code> chips; click fills the Call form</td></tr>
          <tr><td>Describe</td><td><code>GET /v1/fraggate/describe?name=</code></td><td>One catalog entry; unknown names stay unknown</td></tr>
          <tr><td>Call op</td><td><code>POST /v1/fraggate/call</code> <code>{slug, op, payload}</code></td><td>Result or typed refuse (FG-HALLUC-TOOL / FG-GATE / FG-STUB) + ledger tip</td></tr>
          <tr><td>Verify</td><td><code>POST /v1/fraggate/verify</code></td><td><code>matched</code> + digest + ledger tip when present</td></tr>
          <tr><td>OpenAPI</td><td><code>/openapi.json</code> and catalog OpenAPI</td><td>Same four paths documented</td></tr>
          <tr><td>MCP</td><td><code>POST /mcp</code> and catalog <code>POST /mcp</code></td><td>tools: fraggate_list, fraggate_describe, fraggate_verify, fraggate_call. Mesh pointer: catalog <code>mesh_*</code> + FragGate <code>slug=mesh</code></td></tr>
          <tr><td>Live Nodes</td><td><code>GET /v1/mesh</code> PROXY</td><td>Default OFF. QNM live|locked|isolated. GET never enables. No Node Gate</td></tr>
        </tbody>
      </table>
      <p class="meta">Default door = this Worker. Buttons call same-origin <code>/v1/fraggate/*</code>, which forwards to <code>${DEFAULT_DOOR}</code> (GET list / describe, POST verify / call). Suite mesh <code>/v1/mesh/*</code> PROXY (default OFF). Catalog door is the origin itself. Not AZBrowser. Not a Node Gate. Not UI-only.</p>
    </section>

    <section class="card" id="install">
      <h2><span class="kicker">Counted package</span>Download and one-click install</h2>
      <div class="nums">
        <p class="count">${v}<span>Views</span></p>
        <p class="count">${n}<span>Downloads</span></p>
      </div>
      <p>Download saves the gzip from this Worker (HTTP 200, counted). One-click install copies a Terminal command. After it finishes, run <code>python -m fraggate ping</code>. The kernel stays local FG-0.1.</p>
      <div class="btns">
        <a class="btn block primary" href="/download?asset=${DEFAULT_ASSET}">Download</a>
        <button type="button" class="btn block install" id="install-btn">One-click install</button>
      </div>
      <pre id="install-cmd">${INSTALL_LINE}</pre>
      <p class="meta">The download count ticks on the Download click. No 302 to GitHub. ${DEFAULT_ASSET} — ${n} counted.</p>
      <p class="iso">Isolated counter: Worker <code>fraggate-download-tracker</code>, project <code>fraggate</code>, KV <code>FRAGGATE_DOWNLOADS</code>. /v1, /mcp, and /v1/mesh/* do not increment downloads.</p>
      <p class="meta">GitHub: stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0} · release assets ${gh.release_download_count || 0}</p>
      <p class="meta">Door kin: <a href="${DEFAULT_DOOR}/">aziel-runtime</a> · <a href="https://decisiongate-download-tracker.vibelock.workers.dev/">DecisionGATE</a> · <a href="https://peacelock-download-tracker.vibelock.workers.dev/">PeaceLock</a> · <a href="https://www.azielcorpuslibrary.net/">library</a> · <a href="https://godlock.uk/">godlock.uk</a> · <a href="https://www.azieleliab.com/">www.azieleliab.com</a></p>
      <p class="meta"><a href="/stats">JSON stats</a> · <a href="/count">/count</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/mcp">MCP</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/v1/example">Example</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
      <h3>Per repo / branch / fork</h3>
      <ul>${breakdownList(stats)}</ul>
    </section>

    <section class="cite" id="cite">
      <h2>How to cite</h2>
      <p>${escapeHtml(HOW_TO_CITE)}</p>
      <p>Author: <strong>${AUTHOR}</strong> only · License: Apache-2.0 · Forks welcome and always allowed · Machine-readable: <a href="/cite.json">/cite.json</a></p>
      <p class="meta">No DOI is invented here. Software deposit still needed. Cite GitHub and this Worker.</p>
      <p><a href="${CATALOG}">Catalog</a> · <a href="${CATALOG_MCP}">Catalog MCP</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${HOST}/download">Download</a> · <a href="/llms.txt">llms.txt</a></p>
    </section>

    <footer>
      <p>Apache-2.0 · ${AUTHOR} · FragGate v${VERSION}</p>
      <p>Not a second kernel. Buttons, OpenAPI, and MCP share List / Describe / Call / Verify. Suite mesh default OFF.</p>
    </footer>
  </div>
  <script type="application/json" id="fg-boot">${boot}</script>
  <script>
    (function () {
      var boot = JSON.parse(document.getElementById("fg-boot").textContent);
      function $(id) { return document.getElementById(id); }
      function setStatus(kind, text) {
        var el = $("ws-status");
        el.className = "status" + (kind ? " " + kind : "");
        el.textContent = text;
      }
      function codeKind(code, ok) {
        if (ok === true || code === "FG-OK") return "ok";
        if (code === "FG-STUB") return "warn";
        if (code && String(code).indexOf("FG-") === 0) return "bad";
        if (ok === false) return "bad";
        return "";
      }
      function doorRoot() {
        var typed = ($("door").value || "").trim().replace(/\\/+$/, "");
        var self = boot.host || (typeof location !== "undefined" ? location.origin : "");
        if (!typed || typed === self || typed === "/") return "";
        return typed;
      }
      function fillForm(slug, op) {
        if (slug) $("slug").value = slug;
        if (op) $("op").value = op;
      }
      function renderOps(data) {
        var box = $("ops-box");
        box.textContent = "";
        var ops = (data && (data.live_ops || (data.result && data.result.live_ops))) || [];
        if (!ops.length && data && data.allowlist) {
          Object.keys(data.allowlist).forEach(function (slug) {
            (data.allowlist[slug] || []).forEach(function (op) { ops.push(slug + "/" + op); });
          });
        }
        if (!ops.length && data && data.result && data.result.allowlist) {
          Object.keys(data.result.allowlist).forEach(function (slug) {
            (data.result.allowlist[slug] || []).forEach(function (op) { ops.push(slug + "/" + op); });
          });
        }
        ops.slice(0, 80).forEach(function (item) {
          var parts = String(item).split("/");
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "ghost";
          btn.textContent = item;
          btn.onclick = function () { fillForm(parts[0], parts.slice(1).join("/") || "health"); };
          box.appendChild(btn);
        });
      }
      function renderGate(gate) {
        var box = $("gate-box");
        var ol = $("gate-lineage");
        ol.textContent = "";
        if (!gate) { box.hidden = true; return; }
        box.hidden = false;
        (gate.lineage || []).forEach(function (row) {
          var li = document.createElement("li");
          li.textContent = (row.name || "") + " · " + (row.state || "") + " — " + (row.feedback || "");
          ol.appendChild(li);
        });
      }
      function applyResult(data) {
        var inner = data && data.result && typeof data.result === "object" ? data.result : data;
        var code = (data && (data.code || data.error_code)) || (inner && inner.code) || "";
        var ok = data && data.ok;
        if (ok == null && data && data.status) ok = data.status === "ok";
        $("last-code").textContent = code || (ok === true ? "ok" : "—");
        var gate = data && data.gate;
        $("last-gate").textContent = (gate && (gate.final_state || gate.state)) || "—";
        var tip = data && data.ledger_tip;
        $("last-tip").textContent = (tip && (tip.tip || tip.hash)) || (data && data.ledger_hash) || "—";
        $("last-digest").textContent =
          (data && (data.registry_digest || (data.result && data.result.registry_digest))) || "—";
        renderGate(gate);
        renderOps(data);
        $("raw-json").textContent = JSON.stringify(data, null, 2);
        var title = data && data.display && data.display.title;
        var summary = data && data.display && data.display.summary;
        var msg = (data && (data.message || data.error_message)) || title || summary || (ok === false ? "Refuse." : "Done.");
        if (code) msg = code + " — " + msg;
        setStatus(codeKind(code, ok), msg);
      }
      function parseJsonField(id, fallback) {
        var raw = ($(id).value || "").trim();
        if (!raw) return fallback;
        return JSON.parse(raw);
      }
      async function hit(path, method, body) {
        var root = doorRoot();
        var url = root + path;
        var headers = { "Accept": "application/json", "User-Agent": "Mozilla/5.0" };
        var init = { method: method, headers: headers };
        if (body !== undefined) {
          headers["Content-Type"] = "application/json";
          init.body = JSON.stringify(body);
        }
        var res = await fetch(url, init);
        var data;
        try { data = await res.json(); }
        catch (e) { throw new Error("Non-JSON from " + url + " HTTP " + res.status); }
        applyResult(data);
        return data;
      }
      async function run(fn) {
        try { await fn(); }
        catch (err) { setStatus("bad", String(err.message || err)); }
      }
      $("btn-list").onclick = function () {
        run(function () { return hit("/v1/fraggate/list", "GET"); });
      };
      $("btn-live").onclick = function () {
        run(async function () {
          var data = await hit("/v1/fraggate/list", "GET");
          var ops = (data && (data.live_ops || (data.result && data.result.live_ops))) || [];
          setStatus("ok", "LIVE ops: " + ops.length + " (click a chip to fill slug/op)");
        });
      };
      $("btn-describe").onclick = function () {
        run(function () {
          var slug = ($("slug").value || "").trim();
          return hit("/v1/fraggate/describe?name=" + encodeURIComponent(slug) + "&slug=" + encodeURIComponent(slug), "GET");
        });
      };
      $("btn-verify").onclick = function () {
        run(function () {
          var slug = ($("slug").value || "").trim();
          var digest = ($("digest").value || "").trim();
          return hit("/v1/fraggate/verify", "POST", { name: slug, slug: slug, digest: digest || undefined });
        });
      };
      $("btn-call").onclick = function () {
        run(function () {
          var slug = ($("slug").value || "").trim();
          var op = ($("op").value || "").trim();
          var payload = parseJsonField("args", {});
          var claimRaw = ($("claim").value || "").trim();
          var body = { slug: slug, name: slug, op: op, payload: payload };
          if (claimRaw) body.claim = JSON.parse(claimRaw);
          return hit("/v1/fraggate/call", "POST", body);
        });
      };
      $("btn-door-self").onclick = function () { $("door").value = boot.host || (typeof location !== "undefined" ? location.origin : ""); };
      $("btn-door-catalog").onclick = function () { $("door").value = boot.catalog; };
      var installBtn = $("install-btn");
      var installPre = $("install-cmd");
      var installCmd = ${JSON.stringify(INSTALL_LINE)};
      if (installBtn) {
        installBtn.addEventListener("click", function () {
          function done(ok) {
            installBtn.textContent = ok ? "Copied! Paste in Terminal, then python -m fraggate ping" : "Select the command, copy it, then python -m fraggate ping";
            installBtn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(installCmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (installPre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(installPre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      }
      fetch("/v1/health").then(function (res) { return res.json(); }).then(function (data) {
        var pill = $("api-pill");
        if (!pill) return;
        if (data && data.ok) {
          pill.textContent = "API live · v" + (data.version || boot.version);
          pill.className = "pill ok";
        } else {
          pill.textContent = "API down";
          pill.className = "pill bad";
        }
      }).catch(function () {
        var pill = $("api-pill");
        if (pill) { pill.textContent = "API down"; pill.className = "pill bad"; }
      });
      function meshNum() {
        for (var i = 0; i < arguments.length; i++) {
          var raw = arguments[i];
          if (raw == null || raw === "") continue;
          var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
          if (Number.isFinite(n) && n >= 0) return Math.floor(n);
        }
        return 0;
      }
      function unwrapMesh(j) {
        if (!j || typeof j !== "object") return {};
        if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
        if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
        return j;
      }
      function paintMesh(raw) {
        var j = unwrapMesh(raw);
        var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
        var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
        var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
        var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
        var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
        $("meshLiveCount").textContent = String(live);
        $("qnmLive").textContent = String(live);
        $("qnmLocked").textContent = String(locked);
        $("qnmIsolated").textContent = String(isolated);
        var line = $("meshLine");
        if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". Not an anonymity network.";
        else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. Not an anonymity network.";
        else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. Not an anonymity network.";
        var products = j.products_present || j.products || [];
        var names = Array.isArray(products) ? products.map(function (p) { return typeof p === "string" ? p : (p && (p.product || p.slug)) || ""; }).filter(Boolean) : [];
        var nodes = Array.isArray(j.nodes) ? j.nodes : [];
        var extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
        $("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · not AnonBroadcast · not AZMail ring · not a Node Gate" + extra;
      }
      async function meshGet(path) {
        var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
        return r.json();
      }
      async function meshPost(path, payload) {
        var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
        return r.json();
      }
      async function refreshMesh() {
        try {
          var status = await meshGet("/v1/mesh");
          var merged = status;
          var inner = unwrapMesh(status);
          var on = inner.enabled === true;
          if (on) {
            try {
              var nodes = await meshGet("/v1/mesh/nodes");
              merged = Object.assign({}, inner, unwrapMesh(nodes));
            } catch (e) { /* status is enough */ }
          }
          paintMesh(merged);
          var nodeId = sessionStorage.getItem("fraggate_mesh_node");
          if (on && nodeId) {
            try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
          }
        } catch (e) {
          paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
        }
      }
      $("meshEnable").onclick = async function () {
        var bearer = ($("meshBearer").value || "").trim();
        paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
        refreshMesh();
      };
      $("meshDisable").onclick = async function () {
        sessionStorage.removeItem("fraggate_mesh_node");
        paintMesh(await meshPost("/v1/mesh/disable", {}));
        refreshMesh();
      };
      $("meshJoin").onclick = async function () {
        var j = await meshPost("/v1/mesh/join", { product: "fraggate", label: "FragGate Worker" });
        var inner = unwrapMesh(j);
        var id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
        if (id) sessionStorage.setItem("fraggate_mesh_node", String(id));
        paintMesh(j);
        refreshMesh();
      };
      $("meshLeave").onclick = async function () {
        var id = sessionStorage.getItem("fraggate_mesh_node");
        if (id) await meshPost("/v1/mesh/leave", { node_id: id });
        sessionStorage.removeItem("fraggate_mesh_node");
        refreshMesh();
      };
      window.addEventListener("pagehide", function () {
        var id = sessionStorage.getItem("fraggate_mesh_node");
        if (!id || typeof navigator.sendBeacon !== "function") return;
        try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
      });
      refreshMesh();
      setInterval(refreshMesh, 30000);
      document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshMesh(); });
    })();
  </script>
</body>
</html>`;
}
