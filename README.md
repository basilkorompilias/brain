# Brand Brain

A multi-brand MCP server that lets any INTERWEAVE creative chat with a client's brand voice and instantly generate on-brand work. Concepts, copy, and self-critique, without re-loading the brand book from scratch every time.

Built for the INTERWEAVE Creative AI Technologist practical exercise (Track A).

## The problem (from the brief)

> Every time a Creative Director, copywriter, or strategist starts work for a brand, they spend significant time re-loading themselves with the brand's tone, prior campaigns, do's and don'ts, and strategic positioning. With 50+ clients, this knowledge is fragmented across decks, brand books, briefs, and people's heads.

Brand Brain turns that fragmented knowledge into a callable, model-agnostic layer: three MCP tools that any AI client (Cursor, Claude Desktop, etc.) can use to ground itself in a specific brand before it writes a single line.

## Why an MCP server (the strategic bet)

The brief asks for a demo that scales to 100+ clients. A Claude Project or a custom Gem is locked to one vendor and one UI. An MCP server is the reusable brand-context layer. Write it once, plug it into whatever model the agency (or the client's data-residency rules) requires this quarter. This repo demos it in Cursor. No Claude account needed.

## What it exposes

| Tool | What it does | Brief requirement |
|---|---|---|
| `list_brands` | Catalogue of brands, industry, and voice | helper |
| `get_brand_guidelines` | Story, mission, values, positioning, tone, do's/don'ts, lexicon | Tool 1 |
| `get_campaign_examples` | Past work with channel, audience, format, and outcome | Tool 2 |
| `validate_copy` | Deterministic, rules-based tone critique: verdict, 0-100 score, per-issue findings and fixes | Tool 3 |

### Three deliberately distinct brands (across 3 of Interweave's industries)

| Brand | Industry | Voice | The point it proves |
|---|---|---|---|
| **Lyrá** | Travel & Hospitality | serene, sensory, assured | Understated luxury. Bans hype, exclamation marks, and the word "luxury". |
| **Anása** | Public Sector / Social | warm, plain, steady | Plain, safe public-health voice. Requires a helpline, blocks stigma. |
| **Kléos** | Food, Drinks & Beverages | bold, witty, proud | Heritage swagger. Bans spirits clichés, requires a responsibility line. |

A tagline written for Lyrá will not pass as a Kléos line, and the validator proves it numerically (see `tests/`).

## Quick start (Cursor)

```bash
# 1. install
cd brand-brain
pip install -e .

# 2. confirm it runs
python tests/test_validator.py          # 8/8 tests should pass

# 3. point Cursor at it
#    .cursor/mcp.json is already in this repo. Open the brand-brain
#    folder in Cursor, go to Settings -> MCP, and enable "brand-brain".
```

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "brand-brain": {
      "command": "python",
      "args": ["-m", "brand_brain.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Claude Desktop? Same server. Drop the block above (with an absolute `cwd`) into `claude_desktop_config.json` under `mcpServers`. It's the same MCP server. That portability is the whole point.

### Run a Creative-Director session

Open Cursor's chat with the tools enabled and try the flow in [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md):

> "Use brand-brain. I'm working on Lyrá. Pull the guidelines and past campaigns, then give me 3 launch concepts for the new winter season, write an OOH headline, an Instagram caption and an email subject line, then validate each with validate_copy and rewrite anything that isn't on-brand."

## Repo layout

```
brand-brain/
├── brand_brain/
│   ├── server.py        # MCP server — 3 required tools + list_brands
│   ├── knowledge.py     # loads the file-based knowledge base
│   └── validator.py     # deterministic, no-LLM tone validator
├── knowledge_base/
│   ├── lyra/            # guidelines.md + voice_rules.json + campaigns.json
│   ├── anasa/
│   └── kleos/
├── tests/test_validator.py
├── docs/
│   ├── STRATEGY.md      # Part 1 — strategy write-up
│   ├── BUILD.md         # Part 2 — stack, prompt design, drift, productionizing
│   ├── REFLECTION.md    # Part 3 — surprises, next build, push-back
│   └── DEMO_SCRIPT.md   # the live 5-min walkthrough
└── .cursor/mcp.json
```

## The division of labour (why this is honest about limits)

- The model (Cursor's LLM) does the creative generation.
- The server does the adjudication. Deterministic, reviewable, no black box.
- The human Creative Director owns taste, strategy, and the final call.

See [`docs/STRATEGY.md`](docs/STRATEGY.md) section 4 and [`docs/REFLECTION.md`](docs/REFLECTION.md).