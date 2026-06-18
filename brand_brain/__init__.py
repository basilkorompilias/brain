"""Brand Brain — a multi-brand MCP server for agency creatives.

Exposes three tools over the Model Context Protocol:
- get_brand_guidelines : tone, voice, do's/don'ts, positioning
- get_campaign_examples: past work with channel/audience/outcome metadata
- validate_copy        : deterministic, rules-based tone critique

The knowledge base lives in ../knowledge_base and is loaded on first access.
"""
__version__ = "0.1.0"