# Demo Script: 5-minute live walkthrough
*Brand Brain MCP server. Target: ~5 minutes.*

Goal: show a Creative-Director session (brief, on-brand concepts, copy, self-critique) and prove the brands have distinct voices.

## 0. Setup (before recording): 20s

- Double-click `setup.bat` (Windows) or `setup.command` (Mac), or run `python scripts/setup.py`.
- Connect brand-brain in your MCP client (see README).
- Confirm brand-brain shows 4 tools (green).

One line to say: "The intelligence isn't in a giant prompt. It's in three tools any model can call."

## 1. Discover the brands: 30s

Prompt:
> "Use the brand-brain tools. What brands are available?"

Model calls `list_brands`. Shows Lyrá (hospitality), Anása (public sector), Kléos (drinks) with their voices.

## 2. The CD session: Lyrá (restrained luxury): 90s

Prompt:
> "I'm working on Lyrá. Pull the brand guidelines and past campaigns, then give me 3 launch concepts for a winter season, plus an OOH headline, an Instagram caption, and an email subject line. Then run each through `validate_copy` and rewrite anything that isn't on-brand."

Watch for the loop:
- `get_brand_guidelines("lyra")` + `get_campaign_examples("lyra")`
- 3 concepts grounded in subtraction/stillness
- 3 channel copy variants (no "!", no "luxury", sensory nouns)
- `validate_copy` on each, verdicts + scores
- model rewrites anything below "on-brand"

Say: "Notice it never says 'luxury' or uses an exclamation mark. Those are banned in Lyrá's rules, and the validator enforces it deterministically."

## 3. Prove distinct voices: same brief, different brand: 90s

Prompt:
> "Now switch to Kléos. Same task, a winter-season OOH headline. Then validate it. After that, paste the Lyrá headline from before into `validate_copy` for Kléos, and vice-versa."

Kléos copy is bold, fiery, has the responsibility line. The cross-checks show a Lyrá line scores low as a Kléos line and vice-versa. Numerical proof the voices are distinct.

## 4. Show the safety teeth: Anása: 45s

Prompt:
> "For Anása, validate this draft: 'Don't be crazy, just snap out of it and cheer up.'"

`validate_copy` returns off-brand, low score, flags stigma words and missing helpline.

Say: "For a mental-health brand the rules aren't taste, they're safety. The server hard-requires a helpline and blocks stigma language. A semantic retriever couldn't guarantee that."

## 5. Close: 25s

"It cut the context-reload to zero, generated on-brand copy across three very different voices, caught its own off-brand lines, and enforced compliance, all behind a model-agnostic MCP layer that scales to 100+ clients. What it doesn't do is have the original idea or sign off the work. That stays with the Creative Director. Details in the strategy and reflection docs."

### Backup (if a tool call misbehaves on camera)

Run the tests to prove the validator works, no MCP client needed:

```bash
.venv/bin/python tests/test_validator.py      # macOS/Linux
.venv\Scripts\python tests/test_validator.py  # Windows
```