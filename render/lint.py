"""Checks a script.json before rendering. Errors block the render; warnings don't.

    python -m render.lint episodes/2026-10-01/script.json
"""
import json
import re
import sys

from .scenes import SCENES

BANNED = [
    (r"\bcheat(s|ed|ing|ers?)?\b", "say 'found to have broken the rules'"),
    (r"\bfrauds?\b|\bfraudulent\b", "say 'the commission found …'"),
    (r"\bliars?\b|\blied\b", "attribute, don't characterise"),
    (r"\bcorrupt(ion)?\b", "not established by the decision"),
    (r"\bwill be relegated\b|\bare getting relegated\b", "punishment isn't decided: say 'could' and attribute"),
    (r"\bwill be stripped\b", "punishment isn't decided"),
    (r"\bfinal verdict\b", "City are appealing"),
    (r"\bsources say\b", "name the outlet"),
]


def lint(script):
    errors, warnings = [], []
    segs = script.get("segments", [])
    for key in ("date", "day", "segments", "caption", "hashtags", "sources"):
        if key not in script:
            errors.append(f"missing '{key}'")
    words = sum(len(s.get("say", "").split()) for s in segs)
    if words < 155:
        errors.append(f"{words} words: too short for 61s+ (aim 165-195)")
    elif words > 215:
        errors.append(f"{words} words: too long (aim 165-195)")
    if not 8 <= len(segs) <= 14:
        warnings.append(f"{len(segs)} segments (aim 9-13)")
    types = []
    for i, s in enumerate(segs, 1):
        v = s.get("visual", {})
        t = v.get("type")
        types.append(t)
        if t not in SCENES:
            errors.append(f"segment {i}: unknown visual type {t!r}")
        n = len(s.get("say", "").split())
        if n > 30:
            warnings.append(f"segment {i}: {n} words, so one graphic sits too long; split it")
        for pat, why in BANNED:
            for field in (s.get("say", ""), json.dumps(v)):
                if re.search(pat, field, re.I):
                    errors.append(f"segment {i}: banned wording /{pat}/ ({why})")
        if re.search(r"\bguilty\b", s.get("say", ""), re.I) and not re.search(
                r"\b(premier league|commission|panel|found|says|ruled|according)\b", s.get("say", ""), re.I):
            errors.append(f"segment {i}: 'guilty' must be attributed")
    if segs and len(segs[0].get("say", "").split()) > 18:
        warnings.append("hook is over 18 words")
    for need in ("stat", "punch"):
        if need not in types:
            warnings.append(f"no '{need}' visual")
    tags = script.get("hashtags", [])
    if len(tags) > 5:
        errors.append(f"{len(tags)} hashtags (TikTok max 5)")
    if len(script.get("sources", [])) < 1:
        errors.append("no sources")
    text = " ".join(s.get("say", "") for s in segs).lower()
    if not re.search(r"deny|denies|innocent|appeal", text):
        warnings.append("doesn't mention City's denial/appeal")
    return errors, warnings


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        e, w = lint(json.load(f))
    for x in w:
        print("warning:", x)
    for x in e:
        print("ERROR:", x)
    sys.exit(1 if e else 0)
