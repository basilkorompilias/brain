"""Brand Brain MCP server.

Run with:  python -m brand_brain.server      (stdio transport)
Or via the console script:  brand-brain

Exposes four tools to any MCP client (Cursor, Claude Desktop, etc.):
  - list_brands           : catalogue of available brands
  - get_brand_guidelines  : tone, voice, do's/don'ts, positioning (REQUIRED)
  - get_campaign_examples : past work with metadata                (REQUIRED)
  - validate_copy         : structured, rules-based tone critique  (REQUIRED)
"""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .knowledge import get_brand, list_brands as _list_brands
from .validator import validate

mcp = FastMCP("brand-brain")


# ---------------------------------------------------------------------------
# Tool 0 (helper): list available brands
# ---------------------------------------------------------------------------
@mcp.tool()
def list_brands() -> str:
    """List every brand Brand Brain knows about, with industry and voice.

    Call this first to discover valid `brand_id` values for the other tools.
    """
    return json.dumps({"brands": _list_brands()}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool 1 (REQUIRED): brand guidelines
# ---------------------------------------------------------------------------
@mcp.tool()
def get_brand_guidelines(brand_id: str) -> str:
    """Retrieve a brand's full guidelines: story, mission, values, strategic
    positioning, tone of voice, do's/don'ts, and lexicon.

    Use this at the START of any creative task so the work is grounded in the
    brand's actual voice rather than generic AI tone.

    Args:
        brand_id: e.g. "lyra", "anasa", "kleos". Use list_brands to discover.
    """
    brand = get_brand(brand_id)
    header = (
        f"# {brand.name}  \n"
        f"*Industry: {brand.industry} — Voice: "
        f"{', '.join(brand.voice_rules.get('voice_words', []))}*\n\n"
    )
    return header + brand.guidelines_md


# ---------------------------------------------------------------------------
# Tool 2 (REQUIRED): campaign examples
# ---------------------------------------------------------------------------
@mcp.tool()
def get_campaign_examples(brand_id: str, channel: str = "", limit: int = 5) -> str:
    """Retrieve past campaign examples for a brand, with metadata: channel,
    audience, format, outcome, and why each worked.

    Use this to ground new concepts in what has actually performed for the brand.

    Args:
        brand_id: e.g. "lyra", "anasa", "kleos".
        channel:  optional case-insensitive filter, e.g. "email", "OOH", "social".
        limit:    max number of campaigns to return (default 5).
    """
    brand = get_brand(brand_id)
    campaigns = brand.campaigns
    if channel:
        c = channel.lower()
        campaigns = [x for x in campaigns if c in x.get("channel", "").lower()]
    campaigns = campaigns[: max(1, limit)]
    payload = {
        "brand": brand.name,
        "brand_id": brand.brand_id,
        "count": len(campaigns),
        "filter_channel": channel or None,
        "campaigns": campaigns,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool 3 (REQUIRED): validate copy
# ---------------------------------------------------------------------------
@mcp.tool()
def validate_copy(brand_id: str, copy: str, is_campaign: bool = True) -> str:
    """Validate a draft piece of copy against a brand's tone rules and return
    STRUCTURED feedback: an overall verdict (on-brand / needs-work / off-brand),
    a 0-100 score, per-issue findings with severity, evidence and concrete
    suggestions, plus readability metrics.

    This check is deterministic and rules-based (no LLM), so the same copy always
    gets the same critique. Use it to self-critique and then rewrite.

    Args:
        brand_id:    e.g. "lyra", "anasa", "kleos".
        copy:        the draft text to check.
        is_campaign: if True (default), also checks brand-required elements such
                     as a helpline (Anása) or responsibility line (Kléos).
    """
    brand = get_brand(brand_id)
    result = validate(brand, copy, is_campaign=is_campaign)
    return json.dumps(result, ensure_ascii=False, indent=2)


def main() -> None:
    """Entry point — runs the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
