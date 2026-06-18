# Part 1 — Strategy
*Brand Brain — Creative AI Technologist exercise*

## 1. Which 2–3 client archetypes to target first, and why

I would not start with the brands that are easiest to automate. I'd start with the ones where the voice is distinctive enough to prove the system works, and the cost of being off-voice is high enough that the CD actually wants the help.

That gives three archetypes, which are the three brands in this prototype:

1. **Luxury hospitality (Lyra).** Voice is the product. A luxury resort sells a feeling, and the failure mode (sounding like a hype-y travel ad) is instantly recognisable. It's the cleanest proof that the system can hold a restrained voice, which is the hardest thing for an LLM to do. Models default to enthusiastic and over-adjectived. 

2. **Public-sector / social cause (Anása).** The opposite voice: plain, warm, accessible. It also has the highest stakes. A mental-health campaign has safe-messaging rules, mandatory helpline signposting, and stigma language that must never ship. This archetype proves Brand Brain can enforce hard compliance rules, not just stylistic preferences. It's also where campaigns-for-good positioning lives.

3. **Fast-Moving Consumer Goods (FMCG) / premium drinks (Kléos).** The commercial workhorse. High creative throughput across many channels, plus its own regulatory floor (alcohol marketing: no under-25s, no "drink equals success", mandatory responsibility line). Proves the system handles a bold voice and a third, different rule set.

Why these three together: they are maximally far apart on the voice spectrum (restrained, plain, and bold) and they each carry a different kind of rule (stylistic taste, safety compliance, or legal compliance). If Brand Brain keeps these three distinct and on-side, the middle of the portfolio is easy.

## 2. The right model + tooling stack, and why

My choice: an MCP server as the brand-context layer, model-agnostic, with a deterministic local validator. Reasoning, as a real comparison:

| Option | Strengths | Why it's not the core |
|---|---|---|
| **Claude (Projects)** | Excellent instruction-following and tone control. Projects give per-client context. MCP-native. | Vendor-locked UI. Context lives in one product. Doesn't answer "how do we reuse this across 100 clients and across tools." |
| **Claude API + Vertex AI (for RAG + MCP)** | Best-in-class for nuanced voice. MCP is a first-class citizen. Strong tool use. | Per-token cost at portfolio scale. Vertex or other EU Cloud services are required for GDPR handling. |
| **Gemini (Gems / Vertex)** | Huge context window (cheap to stuff a whole brand book in). Vertex offers EU data residency and Google-Cloud governance. Strong multimodality for the Art-Director half. | Gems are consumer-grade and locked. Vertex is the serious path but heavier to stand up. |
| **Hybrid (my pick)** | Put the brand knowledge and rules behind MCP. Let the model be a swappable backend. | Slightly more upfront engineering, but it's the only option that survives a vendor, price, or regulation change. |

Why MCP-first wins for a multi-brand agency specifically:

- **Reusability across 100+ clients.** The brand layer is written once and works from any MCP client. That directly answers "an approach we can scale."
- **Tool use.** The CD flow (retrieve, generate, validate, rewrite) needs real tool calls, not just a long prompt. MCP is built for exactly this.
- **Cost at scale.** The expensive part (validation) is deterministic and runs locally with zero token cost. Only generation hits a paid model.
- **EU data residency.** Brand IP stays in your infrastructure (the server), not pasted into a third-party chat. You choose the generation model per client. A privacy-sensitive public-sector client can route to an EU-resident Vertex endpoint while a low-risk FMCG uses whatever is cheapest and best.
- **Multimodality.** Out of scope for this exercise (the Art-Director half), but MCP doesn't block it. An image/asset tool can be added to the same server.

Concrete recommendation for production: MCP server (this repo) plus Claude as default generation model for its tone control, with Gemini on Vertex as the EU-resident or cost-optimised alternative routed per-client.

## 3. MCP vs. simple RAG vs. system-prompt-only

These aren't competitors. They're a maturity ladder, and the right rung depends on the client tier.

| Approach | What it is | Best for | Breaks down when |
|---|---|---|---|
| **System-prompt-only** | Paste the brand voice into the prompt | A new/small client, a one-off, a pitch | Knowledge grows past a clean prompt. No past-campaign recall. Every user re-pastes. No validation. |
| **Simple RAG** | Embed brand docs, retrieve relevant chunks at query time | Clients with lots of unstructured material (decks, transcripts, old briefs) | Retrieval is fuzzy for rules (ex. "never say luxury"). You can't trust a semantic match to enforce a hard don't. No actions, just text-in/text-out. |
| **MCP (this build)** | Typed tools over a curated knowledge base + deterministic checks | The portfolio standard. Any client where voice must be enforced, not just suggested | More upfront structuring of each brand's knowledge |

How I'd deploy across a full client portfolio:

- **System-prompt-only** goes to the long tail: tiny clients, pitches, experiments. Zero setup, good enough.
- **RAG** goes to clients with deep archives of messy material. Bolt it inside an MCP tool (`search_brand_archive`) so retrieval feeds the same interface.
- **MCP** is the default for any retained client. The killer feature isn't retrieval, it's the deterministic `validate_copy` rule enforcement. Safety- or compliance-heavy brands (Anása, Kléos) cannot rely on a semantic retriever to guarantee a banned word never ships. They need a hard rule check. MCP also lets RAG and prompt-context coexist as tools behind one interface.

A system prompt is a sticky note. RAG is a librarian. MCP is the brand's operating system. Most clients eventually want the OS.

## 4. What Brand Brain deliberately does NOT do

Brand Brain does not:

- **Decide strategy.** It encodes the positioning strategists set. It won't tell you what the brand should stand for or which audience to chase (even if it can provide feedback).
- **Approve or ship anything.** `validate_copy` returns a verdict and a score, not a green light. It's an advisor, not an approver.
- **Invent the leap.** It's excellent at on-voice, competent output and at catching what's off-voice. It does not originate the genuinely surprising, category-breaking idea. That is breakthrough-creative territory. It raises the floor. It does not raise the ceiling.
- **Generate the brand's first voice.** It needs a real brand book behind it. Put bad input in, get confident bad output.
- **Replace human judgment on sensitive work.** For Anása, a machine can flag stigma words. It cannot judge whether a piece is kind in context. A human signs off on anything that touches mental health.

Where the human Creative Director stays essential:

- **Taste and the final call.** Knowing when breaking a rule is the right move. The validator flags a rule break. The CD decides if it's brilliant or wrong.
- **Strategy and the brief behind the brief.** An agency's value is challenging the brief, not just executing it. A model takes the brief literally. A CD interrogates it.
- **The original idea.** The concept worth building a campaign around.
- **Accountability.** When work ships, a person owns it. The system is on the hook for nothing.

Brand Brain's honest pitch: it removes the 30-minute context-reload tax and the off-voice first draft, so the CD spends their time on judgment, strategy, and the leap. The parts that are actually the job.

# A note on the brands and IP

All three brands in this prototype (Lyra, Anása, and Kléos) are fictional, created for this exercise. Their guidelines, voice rules, and "past campaigns" are synthesized to be realistic and to cover three very different voice and compliance profiles across three industries (Travel & Hospitality, Public Sector / Social Causes, Food & Drinks).

They are archetype-inspired by common agency work (resort branding, public-good campaigns, premium drinks), but no real client data, confidential material, or proprietary brand book was used. The "campaign outcomes" are illustrative, not real metrics.

This is intentional, per the brief: "you can synthesize these from publicly available material" and "one fictional or real brand archetype of your choice."

For a real deployment, each brand directory would be populated from the client's actual brand book and campaign history, with strategist sign-off.