# GitHub SEO — FragGate

GitHub-side SEO / ecosystem cross-links only. Does **not** change Worker UI or `workers/*/src`. No `wrangler deploy`.

Public identity: **Aziel Eliab** only. Aka / `alternateName` only: **Aziel Elroi Eliab** (Elroi).

**FragGate is THE single door (FG-0.1).** Host: [Aziel Runtime](https://github.com/AzielEliab/aziel-runtime) **2.0.0-rc1**.

Coordinator applies the live About box (`gh repo edit`). This file is the source of truth; PRs cannot patch About via git. Do not rely on `PATCH` if it 403s.

## Description (≤350 characters)

```text
FragGate FG-0.1 — THE single door for Aziel Runtime (MCP / OpenAPI). Hashed registry, DecisionGATE, ledger. Hosted on aziel-runtime 2.0.0-rc1. Author: Aziel Eliab.
```

## Homepage

Runtime door (execution / OpenAPI):

`https://aziel-runtime.vibelock.workers.dev/`

**[Try on Glama](https://glama.ai/mcp/servers/AzielEliab/aziel-runtime)** is the primary Install Server / MCP distribution door (README + this lock). Worker origin stays secondary.

## Topics (≤20)

`fraggate`, `mcp`, `openapi`, `aziel-eliab`, `aziel-runtime`, `digital-forensics`, `kernel`, `model-context-protocol`, `decisiongate`, `cloudflare-workers`, `glama`, `ai-agents`, `apache-2-0`

Required discovery terms: **fraggate**, **mcp**, **openapi**, **aziel-runtime**.

## Entity graph (locked)

| Entity | `@id` |
|--------|-------|
| Person | `https://www.azieleliab.com/#aziel` |
| Runtime SoftwareApplication | `https://www.azieleliab.com/runtime#runtime` |

Do **not** use `https://github.com/AzielEliab#person`. Worker origin is `relatedLink` / execution URL, not the identity hub.

## Official Aziel ecosystem (README + this lock)

- Official site → https://www.azieleliab.com/ (Person `@id` https://www.azieleliab.com/#aziel)
- Runtime hub → https://www.azieleliab.com/runtime#runtime
- Aziel Corpus Library → https://www.azielcorpuslibrary.net/
- GodLock.uk → https://godlock.uk/
- Aziel Runtime (host, 2.0.0-rc1) → https://github.com/AzielEliab/aziel-runtime
- **Try on Glama** (primary MCP) → https://glama.ai/mcp/servers/AzielEliab/aziel-runtime
- Runtime Worker (secondary) → https://aziel-runtime.vibelock.workers.dev/
- Human Worker UI (this repo) → https://fraggate-download-tracker.vibelock.workers.dev/

## Compatible AI clients

Keep the **full** set already in the README. Do **not** shrink to a Grok / ChatGPT / Venice triad.

ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic Desktop / custom tools), Cursor (MCP), Glama (Install Server / MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex AI, Mistral, Meta AI, Apple Intelligence / Applebot surfaces, Amazon Q / Amazonbot tooling, DuckAssist / DuckDuckGo AI, You.com, Cohere, plus other MCP/OpenAPI-capable assistants.

## Apply (coordinator; 403 is OK)

```bash
gh repo edit AzielEliab/fraggate \
  --description "FragGate FG-0.1 — THE single door for Aziel Runtime (MCP / OpenAPI). Hashed registry, DecisionGATE, ledger. Hosted on aziel-runtime 2.0.0-rc1. Author: Aziel Eliab." \
  --homepage "https://aziel-runtime.vibelock.workers.dev/" \
  --add-topic fraggate --add-topic mcp --add-topic openapi \
  --add-topic aziel-eliab --add-topic aziel-runtime --add-topic digital-forensics \
  --add-topic kernel --add-topic model-context-protocol --add-topic decisiongate \
  --add-topic cloudflare-workers --add-topic glama --add-topic ai-agents \
  --add-topic apache-2-0
```

Existing topics stay. Do not invent a second author.
