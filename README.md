# Brand Brain

A multi-brand MCP server that lets any creative team chat with a client's brand voice and instantly generate on-brand work. Concepts, copy, and self-critique, without re-loading the brand book from scratch every time.

Built as a Creative AI Technologist practical exercise (Track A).

## The problem (from the brief)

> Every time a Creative Director, copywriter, or strategist starts work for a brand, they spend significant time re-loading themselves with the brand's tone, prior campaigns, do's and don'ts, and strategic positioning. With 50+ clients, this knowledge is fragmented across decks, brand books, briefs, and people's heads.

Brand Brain turns that fragmented knowledge into a callable, model-agnostic layer: three MCP tools that any AI client (Cursor, Claude Desktop, and others) can use to ground itself in a specific brand before it writes a single line.

## Why an MCP server (the strategic bet)

The brief asks for an approach that scales to 100+ clients. A Claude Project or a custom Gem is locked to one vendor and one UI. An MCP server is the reusable brand-context layer. Write it once, plug it into whatever model the agency (or the client's data-residency rules) requires.

## What it exposes

| Tool | What it does | Brief requirement |
|---|---|---|
| `list_brands` | Catalogue of brands, industry, and voice | helper |
| `get_brand_guidelines` | Story, mission, values, positioning, tone, do's/don'ts, lexicon | Tool 1 |
| `get_campaign_examples` | Past work with channel, audience, format, and outcome | Tool 2 |
| `validate_copy` | Deterministic, rules-based tone critique: verdict, 0-100 score, per-issue findings and fixes | Tool 3 |

### Three deliberately distinct brands (across 3 industries)

| Brand | Industry | Voice | The point it proves |
|---|---|---|---|
| **Lyrá** | Travel & Hospitality | serene, sensory, assured | Understated luxury. Bans hype, exclamation marks, and the word "luxury". |
| **Anása** | Public Sector / Social | warm, plain, steady | Plain, safe public-health voice. Requires a helpline, blocks stigma. |
| **Kléos** | Food, Drinks & Beverages | bold, witty, proud | Heritage swagger. Bans spirits clichés, requires a responsibility line. |

A tagline written for Lyrá will not pass as a Kléos line, and the validator proves it numerically (see `tests/`).

## Quick start

You need [Python 3.10+](https://www.python.org/downloads/) and any MCP-compatible AI client.

### 1. Run setup (one time)

| | How |
|---|---|
| **Windows** | Double-click **`setup.bat`** |
| **Mac** | Double-click **`setup.command`** (if macOS blocks it: right-click, then Open) |
| **Terminal** | `python scripts/setup.py` |

Setup creates a local environment, installs dependencies, runs a quick check, and writes MCP config files. When you see **Done - Brand Brain is ready**, continue.

### 2. Connect an MCP client

**Cursor**

1. Open this folder as your workspace.
2. **Settings -> MCP** -> enable **brand-brain**.
3. Confirm you see **4 tools** with a green status.

Setup writes `.cursor/mcp.json`.

**Claude Desktop**

1. Open `mcp-config/claude_desktop.json` (created by setup).
2. Copy the `brand-brain` block into your Claude config:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Restart Claude Desktop. Confirm **brand-brain** shows 4 tools.

**Other clients**

Use the same `command`, `args`, and `cwd` as in `mcp-config/claude_desktop.json`, adapted to your client's config format.

### 3. Try a Creative-Director session

Open chat with the tools enabled and paste something like:

> "Use brand-brain. I'm working on Lyrá. Pull the guidelines and past campaigns, then give me 3 launch concepts for the new winter season, write an OOH headline, an Instagram caption and an email subject line, then validate each with validate_copy and rewrite anything that isn't on-brand."

A full walkthrough lives in [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md).

**Something not working?** Re-run setup, then restart your MCP client.

## Repo layout

```
├── brand_brain/
│   ├── server.py        # MCP server: 3 required tools + list_brands
│   ├── knowledge.py     # loads the file-based knowledge base
│   └── validator.py     # deterministic, no-LLM tone validator
├── knowledge_base/
│   ├── lyra/            # guidelines.md + voice_rules.json + campaigns.json
│   ├── anasa/
│   └── kleos/
├── tests/test_validator.py
├── setup.bat            # Windows one-click setup
├── setup.command        # macOS one-click setup
├── scripts/
│   ├── setup.py         # setup (also: python scripts/setup.py)
│   └── launch_mcp.py    # cross-platform MCP launcher
├── mcp-config/
│   └── claude_desktop.example.json   # template; setup writes claude_desktop.json locally
├── docs/
│   ├── STRATEGY.md      # Part 1: strategy write-up
│   ├── BUILD.md         # Part 2: stack, prompt design, drift, productionizing
│   ├── REFLECTION.md    # Part 3: surprises, next build, push-back
│   └── DEMO_SCRIPT.md   # live 5-min walkthrough
├── pyproject.toml
└── .cursor/mcp.json
```

## The division of labour (why this is honest about limits)

- The connected AI client does the creative generation.
- The server does the adjudication. Deterministic, reviewable, no black box.
- The human Creative Director owns taste, strategy, and the final call.

See [`docs/STRATEGY.md`](docs/STRATEGY.md) section 4 and [`docs/REFLECTION.md`](docs/REFLECTION.md).
