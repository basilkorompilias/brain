# Part 2 — Build Documentation
*Track A — MCP Server for a Brand (extended to 3 brands)*

## Stack chosen

| Layer | Choice | Why |
|---|---|---|
| Protocol | **MCP** via the official `mcp` Python SDK (`FastMCP`) | Vendor-neutral tool layer. The reusable asset that scales across the portfolio. |
| Language | **Python 3.10+** | Fast to read, zero ceremony. The SDK is first-class. |
| Transport | **stdio** | What MCP clients launch locally. No ports, no hosted server. |
| Knowledge base | **Flat files** (`guidelines.md` + `voice_rules.json` + `campaigns.json` per brand) | Reviewable by a CD without a DB. Mirrors how brand books already live. Trivially diffable in git. |
| Validator | **Pure Python, deterministic, no LLM** | Reviewable, reproducible, free to run, works offline and anywhere. |
| Client | **MCP host** | Cursor, Claude Desktop, and other stdio MCP clients. |

Why I extended Track A to 3 brands: Track A asks for one brand. Track B's superpower is distinct voices across brands. By making `brand_id` an argument on every tool, one MCP server delivers Track A's technical depth and Track B's voice-differentiation proof, at almost no extra cost. The tests prove the voices are actually distinct (`test_voice_is_brand_specific`).

## Prompt / system design

The design philosophy is "thin model, thick tools." Instead of one giant system prompt, the intelligence lives in three places the model calls:

1. `get_brand_guidelines` returns the brand book as structured markdown (Story, Mission, Values, Positioning, Tone, Do's, Don'ts, Lexicon). This functions as the system prompt, but fetched on demand, per brand, so it never goes stale and never has to be re-pasted.
2. `get_campaign_examples` grounds new work in what has actually performed, with metadata (channel, audience, format, outcome, why it worked). This is few-shot prompting sourced from real brand history instead of invented examples.
3. `validate_copy` closes the loop. The model generates, then submits its own draft for a deterministic critique and rewrites. This retrieve-generate-validate-rewrite loop is the core interaction, and it's what makes the output on-brand instead of just plausible-sounding.

Tool descriptions are themselves prompt engineering. Each tool's docstring tells the model when to call it (e.g. "Use this at the START of any creative task"), which steers the agent toward the right workflow without a long system prompt.

### The `voice_rules.json` schema (the heart of it)

```jsonc
{
  "voice_words": ["serene", "sensory", "assured"],
  "reading_grade_target": { "min": 4, "max": 9 },
  "sentence_length_target": { "max_avg_words": 16 },
  "banned_words": ["luxury", "exclusive", "stunning"],
  "banned_patterns": [ {"pattern": "!", "reason": "Lyrá never uses '!'"} ],
  "preferred_words": ["light", "salt", "stone"],
  "required_elements": [ {"id": "helpline", "any_of": ["1to1","call","text"]} ],
  "rules": [ {"id": "no_hype", "severity": "high"} ]
}
```

This separates human-readable guidance (the `.md`) from machine-enforceable rules (the `.json`). A strategist edits the markdown. A technologist tunes the JSON. Both live in git.

## How I handle brand-voice drift

Drift means the model slowly reverts to generic, enthusiastic AI tone over a long session. Four layered defences:

1. Per-brand banned/preferred lexicons. Each brand has explicit off-voice words (Lyrá: "luxury"; Anása: "crazy"; Kléos: "smooth") that get caught deterministically regardless of how the model is feeling.
2. The deterministic validator as a tripwire. Because it's rules-based, it cannot drift. It scores every draft the same way every time, so drift is caught the moment it appears, not after it ships.
3. Required-element enforcement. Compliance items (Anása's helpline, Kléos's responsibility line) are hard-required for campaign copy. They can't be forgotten.
4. Readability and sentence-length guards. These catch the most common drift signal: sentences quietly getting longer and more adjective-laden over a session.

The validator returns evidence and suggestions, so the model can self-correct in the same turn rather than the human having to notice and re-steer.

## What I'd need to productionize this for 100+ clients

**Knowledge and authoring**
- A simple brand-onboarding pipeline: ingest existing brand books and decks, draft `guidelines.md` + `voice_rules.json` (LLM-assisted), then require strategist review and sign-off. The human gate is the quality bar.
- Move flat files to a versioned store (still git-backed, or a DB with audit history) so every change to a brand's rules is tracked and reversible.
- Add a `search_brand_archive` RAG tool for clients with large messy archives, inside the same MCP interface.

**Serving and access**
- Offer HTTP/SSE transport (the SDK supports it) so it's a hosted service, not a local process. Put auth and per-client access control in front (a creative only sees the brands they're assigned).
- Per-client model routing for cost and EU data residency (see STRATEGY section 2). For example, Vertex EU endpoint for public-sector clients, cheapest-good model for FMCG.

**Quality and trust**
- A golden-set evaluation harness. For each brand, a labelled set of on- and off-voice lines the validator must score correctly. The `tests/` here are the seed.
- Validator tuning loop. When a CD overrides a verdict, log it and feed it back into the rules. The system learns each brand's edge cases.
- Telemetry. Track time-to-first-draft and override rate per brand to prove ROI.

**Governance**
- Clear "human-in-the-loop required" flags on sensitive brands (Anása).
- Audit log of every generation for client transparency.

## File map

```
brand_brain/server.py      # 4 tools (3 required + list_brands)
brand_brain/knowledge.py   # cached file-based KB loader, get_brand/list_brands
brand_brain/validator.py   # FK grade, sentence metrics, rule engine, scoring
knowledge_base/<brand>/    # guidelines.md, voice_rules.json, campaigns.json
tests/test_validator.py    # 9 tests incl. cross-brand voice discrimination
```

## Run it

```bash
python scripts/setup.py
# then connect via .cursor/mcp.json or mcp-config/claude_desktop.json
```