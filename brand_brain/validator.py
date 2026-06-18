"""Deterministic, rules-based copy validator.

Why rules-based and not an LLM call?
  1. Plug-anywhere: the MCP server needs no API key and no network, so it runs
     identically in Cursor, Claude Desktop, or CI.
  2. Reviewable: a Creative Director (and an evaluator) can read exactly *why* a
     line passed or failed. No black box.
  3. Deterministic: the same copy always gets the same critique — essential for a
     live demo and for trust.

The LLM (the MCP *client* — Cursor's model) still does the creative generation
and can read this structured feedback to self-critique and rewrite. That is the
right division of labour: the model creates, the server adjudicates.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .knowledge import Brand


# ---------------------------------------------------------------------------
# Small, dependency-free text metrics
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[A-Za-z']+")
_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")
_VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_RE.findall(text) if s.strip()]


def _count_syllables(word: str) -> int:
    word = word.lower().strip("'")
    if not word:
        return 0
    groups = _VOWEL_GROUPS.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_kincaid_grade(text: str) -> float:
    """Estimate US reading grade level (Flesch-Kincaid). Lower = simpler."""
    words = _words(text)
    sentences = _sentences(text)
    if not words or not sentences:
        return 0.0
    syllables = sum(_count_syllables(w) for w in words)
    wps = len(words) / len(sentences)
    spw = syllables / len(words)
    grade = 0.39 * wps + 11.8 * spw - 15.59
    return round(max(0.0, grade), 1)


def avg_sentence_length(text: str) -> float:
    sentences = _sentences(text)
    if not sentences:
        return 0.0
    return round(len(_words(text)) / len(sentences), 1)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    severity: str            # "high" | "medium" | "low" | "good"
    rule: str                # short rule id / label
    message: str             # human-readable explanation
    evidence: str = ""       # the offending snippet, if any
    suggestion: str = ""     # concrete fix

    def as_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v != ""}


_SEVERITY_PENALTY = {"high": 25, "medium": 12, "low": 5, "good": 0}


# ---------------------------------------------------------------------------
# The validator
# ---------------------------------------------------------------------------

def validate(brand: Brand, copy: str, *, is_campaign: bool = True) -> dict:
    """Validate `copy` against `brand`'s voice rules. Returns structured feedback.

    `is_campaign` toggles checks for required campaign elements (e.g. helpline,
    responsibility line) that don't apply to, say, an internal note.
    """
    rules = brand.voice_rules
    findings: list[Finding] = []
    text = copy.strip()
    lower = text.lower()

    if not text:
        return {
            "brand": brand.name,
            "brand_id": brand.brand_id,
            "verdict": "empty",
            "score": 0,
            "summary": "No copy provided to validate.",
            "findings": [],
        }

    # --- 1. Banned words -------------------------------------------------
    for word in rules.get("banned_words", []):
        if re.search(rf"\b{re.escape(word.lower())}\b", lower):
            findings.append(
                Finding(
                    severity="high",
                    rule="banned_word",
                    message=f"Off-voice word for {brand.name}: \u201c{word}\u201d.",
                    evidence=word,
                    suggestion=_suggest_alternative(rules, word),
                )
            )

    # --- 2. Banned regex patterns ---------------------------------------
    for pat in rules.get("banned_patterns", []):
        pattern = pat["pattern"]
        flags = re.IGNORECASE
        try:
            if pat.get("is_regex"):
                match = re.search(pattern, text, flags)
            else:
                match = re.search(re.escape(pattern), text, flags)
        except re.error:
            continue
        if match:
            findings.append(
                Finding(
                    severity="high",
                    rule="banned_pattern",
                    message=pat.get("reason", "Off-voice pattern detected."),
                    evidence=match.group(0)[:60],
                )
            )

    # --- 3. Reading grade ----------------------------------------------
    grade = flesch_kincaid_grade(text)
    grade_target = rules.get("reading_grade_target")
    if grade_target:
        lo, hi = grade_target["min"], grade_target["max"]
        if grade > hi:
            findings.append(
                Finding(
                    severity="medium",
                    rule="reading_grade",
                    message=(
                        f"Reading grade {grade} is above {brand.name}'s target "
                        f"({lo}-{hi}). Use shorter words and sentences."
                    ),
                )
            )
        elif grade < lo:
            findings.append(
                Finding(
                    severity="low",
                    rule="reading_grade",
                    message=(
                        f"Reading grade {grade} is below target ({lo}-{hi}); "
                        "fine for a headline, watch it for body copy."
                    ),
                )
            )

    # --- 4. Sentence length --------------------------------------------
    asl = avg_sentence_length(text)
    sl_target = rules.get("sentence_length_target", {})
    max_avg = sl_target.get("max_avg_words")
    if max_avg and asl > max_avg:
        findings.append(
            Finding(
                severity="medium",
                rule="sentence_length",
                message=(
                    f"Average sentence length {asl} words exceeds {brand.name}'s "
                    f"target of ~{max_avg}. Break sentences up."
                ),
            )
        )

    # --- 5. Required elements (campaign copy only) ---------------------
    if is_campaign:
        for req in rules.get("required_elements", []):
            options = [o.lower() for o in req.get("any_of", [])]
            if options and not any(o in lower for o in options):
                findings.append(
                    Finding(
                        severity="high",
                        rule=f"missing:{req['id']}",
                        message=f"Missing required element: {req['label']}.",
                        suggestion=f"Add one of: {', '.join(req['any_of'])}.",
                    )
                )

    # --- 6. Positive signal: preferred lexicon -------------------------
    preferred = [w.lower() for w in rules.get("preferred_words", [])]
    hits = sorted({w for w in preferred if re.search(rf"\b{re.escape(w)}\b", lower)})
    if hits:
        findings.append(
            Finding(
                severity="good",
                rule="on_lexicon",
                message=(
                    f"On-voice language for {brand.name}: "
                    f"{', '.join(hits[:6])}."
                ),
            )
        )
    elif preferred:
        findings.append(
            Finding(
                severity="low",
                rule="lexicon",
                message=(
                    f"None of {brand.name}'s signature words appear. Consider "
                    f"reaching for: {', '.join(preferred[:6])}."
                ),
            )
        )

    # --- Score & verdict ----------------------------------------------
    penalty = sum(_SEVERITY_PENALTY[f.severity] for f in findings)
    score = max(0, 100 - penalty)
    if score >= 85:
        verdict = "on-brand"
    elif score >= 60:
        verdict = "needs-work"
    else:
        verdict = "off-brand"

    return {
        "brand": brand.name,
        "brand_id": brand.brand_id,
        "verdict": verdict,
        "score": score,
        "voice": rules.get("voice_words", []),
        "metrics": {
            "reading_grade": grade,
            "avg_sentence_length": asl,
            "word_count": len(_words(text)),
        },
        "summary": _summarise(brand, verdict, findings),
        "findings": [f.as_dict() for f in findings],
    }


def _suggest_alternative(rules: dict, banned: str) -> str:
    preferred = rules.get("preferred_words", [])
    if preferred:
        return f"Try on-voice language instead, e.g. {', '.join(preferred[:4])}."
    return "Rephrase to avoid this term."


def _summarise(brand: Brand, verdict: str, findings: list[Finding]) -> str:
    highs = [f for f in findings if f.severity == "high"]
    voice = " / ".join(brand.voice_rules.get("voice_words", [])) or "the brand"
    if verdict == "on-brand":
        return f"Reads as {brand.name} ({voice}). No blocking issues."
    if verdict == "needs-work":
        return (
            f"Close to {brand.name}'s voice but not there yet — "
            f"{len(findings)} note(s) to address."
        )
    return (
        f"Off-voice for {brand.name}. {len(highs)} high-severity issue(s) "
        f"break the {voice} tone and need fixing before this ships."
    )
