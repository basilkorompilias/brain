# Brand Brain

An MCP server that helps Creative Agencies generate and evaluate material consistent with inhouse standards and brand guidelines. Brand Brain has three tools: one to get brand rules, one to get past work, and one to check if the generated material follows the rules. It saves you from re-reading the brand book every time you start a task.

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
| **Lyra** | Travel & Hospitality | serene, sensory, assured | Understated luxury. Bans hype, exclamation marks, and the word "luxury". |
| **Anása** | Public Sector / Social | warm, plain, steady | Plain, safe public-health voice. Requires a helpline, blocks stigma. |
| **Kléos** | Food, Drinks & Beverages | bold, witty, proud | Heritage swagger. Bans spirits clichés, requires a responsibility line. |

A tagline written for Lyra will not pass as a Kléos line, and the validator proves it numerically (see `tests/`).

## Quick start

You need [Python 3.10+](https://www.python.org/downloads/) and any MCP-compatible AI client.

### 1. Get the repo

Clone **once** in Terminal:

```bash
git clone https://github.com/basilkorompilias/brain.git
```

Do not run `git clone` again inside the `brain` folder.

### 2. Run setup (one time)

**Mac:** Open your home folder in Finder and search for **`brain`**. Open that folder and double-click **`setup.command`**.

To open it from Terminal after cloning:

```bash
open ~/brain
```

Then double-click **`setup.command`**. If macOS blocks it, right-click and choose Open.

| | How |
|---|---|
| **Mac** | Finder: search for `brain`, double-click **`setup.command`** |
| **Windows** | In File Explorer, open the cloned **`brain`** folder and double-click **`setup.bat`** |
| **Terminal** | `cd ~/brain && ./setup.command` |

Setup creates a local environment, installs dependencies, runs a quick check, and writes MCP config files. When you see **Done - Brand Brain is ready**, continue.

### 3. Connect an MCP client

Use the same **`brain`** folder you opened in step 2.

**Cursor**

1. **File -> Open Folder** and select that **`brain`** folder.
2. **Settings -> MCP** -> enable **brand-brain**.
3. Confirm you see **4 tools** with a green status.

**Claude Desktop**

1. **Settings -> Extensions -> Advanced settings -> Install Extension**
2. Select **`mcp-config/brand-brain.mcpb`** inside that folder
3. Set **Repository root** to that same **`brain`** folder
4. Confirm **brand-brain** shows 4 tools

### 4. Try a Creative-Director session

Open chat with the tools enabled and paste something like:

> "Use brand-brain. I'm working on Lyra. Pull the guidelines and past campaigns, then give me 3 launch concepts for the new winter season, write an OOH headline, an Instagram caption and an email subject line, then validate each with validate_copy and rewrite anything that isn't on-brand."

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
│   └── brand-brain.mcpb    # Claude Desktop extension
├── mcp-extension/          # source for brand-brain.mcpb
├── docs/
│   ├── 1_STRATEGY.md      # Part 1: strategy write-up
│   ├── 2_BUILD.md         # Part 2: stack, prompt design, drift, productionizing
│   └── 3_REFLECTION.md    # Part 3: surprises, next build, push-back
├── pyproject.toml
└── .cursor/mcp.json
```

## The division of labour (why this is honest about limits)

- The connected AI client does the creative generation.
- The server does the adjudication. Deterministic, reviewable, no black box.
- The human Creative Director owns taste, strategy, and the final call.

See [`docs/1_STRATEGY.md`](docs/1_STRATEGY.md) section 4 and [`docs/3_REFLECTION.md`](docs/3_REFLECTION.md).
