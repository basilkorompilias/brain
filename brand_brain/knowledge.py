"""Knowledge-base loader for Brand Brain.

Reads the per-brand documents from the knowledge_base/ directory. Keeping this
as plain files on disk (markdown + JSON) is deliberate: it is the simplest thing
that demonstrably works, it is reviewable by a Creative Director without a
database, and it maps cleanly onto how agencies typically store brand books and
campaign decks. See docs/2_BUILD.md for how this scales to 100+ clients.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parent.parent / "knowledge_base"


@dataclass
class Brand:
    """Everything Brand Brain knows about a single client."""

    brand_id: str
    guidelines_md: str
    voice_rules: dict
    campaigns: list[dict] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.voice_rules.get("name", self.brand_id.title())

    @property
    def industry(self) -> str:
        return self.voice_rules.get("industry", "Unknown")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_brands() -> dict[str, Brand]:
    """Load every brand directory under knowledge_base/ into memory.

    A brand directory must contain: guidelines.md, voice_rules.json,
    campaigns.json. Cached so repeated tool calls are cheap.
    """
    brands: dict[str, Brand] = {}
    if not KB_ROOT.exists():
        raise FileNotFoundError(f"Knowledge base not found at {KB_ROOT}")

    for brand_dir in sorted(p for p in KB_ROOT.iterdir() if p.is_dir()):
        guidelines = brand_dir / "guidelines.md"
        voice = brand_dir / "voice_rules.json"
        campaigns = brand_dir / "campaigns.json"
        if not (guidelines.exists() and voice.exists()):
            continue
        voice_rules = _read_json(voice)
        campaign_data = _read_json(campaigns).get("campaigns", []) if campaigns.exists() else []
        brand = Brand(
            brand_id=brand_dir.name,
            guidelines_md=_read_text(guidelines),
            voice_rules=voice_rules,
            campaigns=campaign_data,
        )
        brands[brand.brand_id] = brand
    return brands


def get_brand(brand_id: str) -> Brand:
    """Fetch one brand by id, with a helpful error listing valid ids."""
    brands = load_brands()
    key = brand_id.strip().lower()
    if key not in brands:
        valid = ", ".join(sorted(brands)) or "(none loaded)"
        raise KeyError(f"Unknown brand '{brand_id}'. Available brands: {valid}")
    return brands[key]


def list_brands() -> list[dict]:
    """Lightweight catalogue for the picker / first call in a session."""
    out = []
    for b in load_brands().values():
        out.append(
            {
                "brand_id": b.brand_id,
                "name": b.name,
                "industry": b.industry,
                "voice": b.voice_rules.get("voice_words", []),
                "campaign_count": len(b.campaigns),
            }
        )
    return out
