# Demo Script — 5-minute live walkthrough

Target: ~5 minutes. 
Goal: Show a real CD workflow (brief, create, validate, fix) and prove the voices are genuinely distinct.

## Before you hit record

Run setup. Connect the MCP client. Confirm you see 4 tools with green status. Have a terminal open in the background just in case.

## 0. The hook — 15s

Open on the chat. Say:

"I don't want a smarter model. I want a model that knows the brand. That's what this server does."

## 1. The Lyrá session: brief → copy → self-critique — 120s

Paste this:

> "I'm working on Lyrá. Pull the brand guidelines and past campaigns, then give me 3 concepts for a winter season campaign."

Let the model call `get_brand_guidelines` and `get_campaign_examples`. Wait for the 3 concepts.

Then paste:

> "Write an OOH headline, an Instagram caption, and an email subject line for the first concept. Then run all three through validate_copy and fix anything that isn't on-brand."

Watch the loop. It generates, validates, gets dinged, rewrites.

Say: "It caught itself. No exclamation marks, no 'luxury', no hype. The validator enforces it deterministically, so the model fixes its own mistakes in the same turn."

## 2. The voice clash: Lyrá vs Kléos — 90s

Paste this:

> "Now do the same winter brief, but for Kléos. Give me an OOH headline and validate it."

Wait for the Kléos output. Notice the shift: bold, fiery, plus the responsibility line.

Now the payoff. Copy the Lyrá headline from step 1 and paste:

> "Validate this Lyrá headline against Kléos's rules: [paste Lyrá headline here]"

The Lyrá line scores low as Kléos. Same words, different brand, different score.

Say: "Same line, different verdict. The voices aren't just different prompts. They're enforced as different rule sets."

## 3. The guardrails: Anása — 45s

Paste this:

> "Validate this draft for Anása: 'Don't be crazy, just snap out of it and cheer up.'"

The validator returns off-brand. Low score. Flags stigma words. Flags missing helpline.

Say: "For a mental-health brand, this isn't about taste. It's about safety. A semantic retriever can't guarantee a banned word never ships. A hard rule check can."

## 4. Close — 10s

"Zero context reload. Three distinct voices. Self-correcting copy. And the original idea still comes from the human. That's the point."

### Backup (if a tool call misbehaves on camera)

Run the tests to prove the validator works, no MCP client needed:

```bash
.venv/bin/python tests/test_validator.py      # macOS/Linux
.venv\Scripts\python tests/test_validator.py  # Windows
```
```
