"""Tests that prove Brand Brain (a) loads, and (b) actually discriminates voice.

Run:  python scripts/setup.py   (or: python -m pytest -q)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brand_brain.knowledge import get_brand, list_brands
from brand_brain.validator import validate


def test_all_brands_load():
    brands = list_brands()
    ids = {b["brand_id"] for b in brands}
    assert {"lyra", "anasa", "kleos"} <= ids


def test_lyra_rejects_hype():
    lyra = get_brand("lyra")
    bad = "Book now! This is the most luxurious, world-class paradise. Amazing!"
    res = validate(lyra, bad)
    assert res["verdict"] == "off-brand"
    assert res["score"] < 60
    rules = {f["rule"] for f in res["findings"]}
    assert "banned_word" in rules
    assert "banned_pattern" in rules  # exclamation marks


def test_lyra_accepts_on_voice():
    lyra = get_brand("lyra")
    good = "The day starts when you decide it does. A swim before the island wakes. Bread still warm. The sea, unhurried."
    res = validate(lyra, good)
    assert res["verdict"] == "on-brand"
    assert res["score"] >= 85


def test_anasa_requires_helpline():
    anasa = get_brand("anasa")
    no_cta = "Sometimes things feel heavy and that is completely okay."
    res = validate(anasa, no_cta, is_campaign=True)
    rules = {f["rule"] for f in res["findings"]}
    assert any(r.startswith("missing:") for r in rules)


def test_anasa_flags_stigma():
    anasa = get_brand("anasa")
    bad = "Don't be crazy, just man up and snap out of it."
    res = validate(anasa, bad)
    assert res["verdict"] == "off-brand"
    banned = [f for f in res["findings"] if f["rule"] == "banned_word"]
    assert len(banned) >= 2


def test_anasa_no_substring_false_positive():
    """'recall' should not satisfy the 'call' CTA requirement."""
    anasa = get_brand("anasa")
    tricky = "Recall the feeling of a better day. You deserve it."
    res = validate(anasa, tricky, is_campaign=True)
    rules = {f["rule"] for f in res["findings"]}
    assert any(r.startswith("missing:") for r in rules)


def test_kleos_requires_responsibility_line():
    kleos = get_brand("kleos")
    no_resp = "Old soul. New fire. Slow-aged in Greek oak. Pour it like you mean it."
    res = validate(kleos, no_resp, is_campaign=True)
    rules = {f["rule"] for f in res["findings"]}
    assert "missing:responsibility" in rules


def test_kleos_flags_cliche():
    kleos = get_brand("kleos")
    bad = "A smooth finish, crafted to perfection. The perfect serve, like no other. Drink responsibly. 18+."
    res = validate(kleos, bad)
    banned = [f for f in res["findings"] if f["rule"] == "banned_word"]
    assert len(banned) >= 2


def test_voice_is_brand_specific():
    """The SAME line should score differently across brands — proof of distinct voices."""
    line = "Book now for the most amazing, luxurious escape!"
    lyra = validate(get_brand("lyra"), line)
    kleos = validate(get_brand("kleos"), line)
    # Lyrá bans 'luxurious'/'amazing'/'most'/'!'; Kléos doesn't ban these the same way.
    assert lyra["score"] < kleos["score"]


if __name__ == "__main__":
    import traceback
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in funcs:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(funcs)} tests passed")
    sys.exit(0 if passed == len(funcs) else 1)