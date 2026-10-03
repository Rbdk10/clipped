"""Checks a script.json before rendering. Errors block the render; warnings don't.

    python -m render.lint episodes/2026-10-01/script.json
"""
import json
import os
import re
import sys

from .scenes import SCENES
from .photos import photo_records

PHOTOS = photo_records()

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


RECAP = r"\b(quick )?recap\b|\bto recap\b|\bas a reminder\b|\bin case you missed\b|\bif you'?re new\b"


def _words(text):
    return {w for w in re.findall(r"[a-z0-9£']+", text.lower()) if len(w) > 3}


def previous_lines(path, n=3):
    """Narration lines from the last n episodes before this one (by folder name)."""
    if not path:
        return []
    here = os.path.dirname(os.path.abspath(path))
    root, me = os.path.dirname(here), os.path.basename(here)
    older = sorted(d for d in os.listdir(root) if d < me and os.path.isfile(os.path.join(root, d, "script.json")))
    out = []
    for d in older[-n:]:
        with open(os.path.join(root, d, "script.json")) as f:
            out += [(d, s.get("say", "")) for s in json.load(f).get("segments", [])]
    return out


def lint(script, path=None):
    errors, warnings = [], []
    segs = script.get("segments", [])
    for key in ("date", "day", "segments", "caption", "hashtags", "sources"):
        if key not in script:
            errors.append(f"missing '{key}'")
    words = sum(len(s.get("say", "").split()) for s in segs)
    if words < 165:
        errors.append(f"{words} words: too short for 61s+ (aim 170-200)")
    elif words > 215:
        errors.append(f"{words} words: too long (aim 170-200)")
    if not 8 <= len(segs) <= 14:
        warnings.append(f"{len(segs)} segments (aim 9-13)")
    types = []
    for i, s in enumerate(segs, 1):
        v = s.get("visual", {})
        t = v.get("type")
        types.append(t)
        if t not in SCENES:
            errors.append(f"segment {i}: unknown visual type {t!r}")
        img = s.get("image") or ""
        if img.startswith("photos/"):
            rec = PHOTOS.get(img.split("/", 1)[1])
            if not rec:
                errors.append(f"segment {i}: {img} has no licence record in library/photos/index.json")
            elif not rec.get("credit"):
                errors.append(f"segment {i}: {img} has no credit line")
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

    # Shape: rumour hook -> new news -> rumour check. No recap segments.
    rumour = script.get("rumour")
    if segs:
        intro = segs[0]
        n = len(intro.get("say", "").split())
        if intro.get("visual", {}).get("type") != "list" or len(intro.get("visual", {}).get("items", [])) < 3:
            errors.append("segment 1 must be the intro: a 'list' visual ('In this video') with 3+ headlines")
        if not 12 <= n <= 28:
            warnings.append(f"intro is {n} words (aim 15-25)")
        if not re.search(r"all in this video|in this video", intro.get("say", ""), re.I):
            warnings.append("intro should end with 'and more. It's all in this video.'")
    if rumour:
        if types[1:2] != ["rumour"]:
            errors.append("segment 2 must be the 'rumour' visual")
        say2 = segs[1].get("say", "") if len(segs) > 1 else ""
        if not re.search(r"\b(might|could|may|reportedly|rumou?r)\b", say2, re.I):
            errors.append("the rumour must be hedged ('might', 'could'); the narrator never states it as fact")
        if re.search(r"\b(claims?|according to|reports say)\b", say2, re.I):
            errors.append("keep outlets and 'claims' out of the rumour line; they go on the card and in the rumour check")
        if not (segs[1].get("visual", {}).get("outlet") if len(segs) > 1 else None):
            errors.append("the rumour card needs an 'outlet'")
        if "verdict" not in types[-3:]:
            errors.append("the rumour check ('verdict' visual) must be in the last 3 segments")
    else:
        warnings.append("no 'rumour' in the script: open on a rumour unless there genuinely isn't one today")
        if segs and "?" not in segs[0].get("say", ""):
            warnings.append("without a rumour, open on a question the ending answers")
    for i, s in enumerate(segs, 1):
        if re.search(RECAP, s.get("say", ""), re.I):
            errors.append(f"segment {i}: recap segment; regulars have seen it, so give context as a half-sentence instead")
    for i, s in enumerate(segs[2:], 3):  # intro and rumour may echo a running story
        mine = _words(s.get("say", ""))
        if len(mine) < 4:
            continue
        for ep, line in previous_lines(path):
            theirs = _words(line)
            if theirs and len(mine & theirs) / len(mine | theirs) >= 0.5:
                warnings.append(f"segment {i} repeats {ep}: \"{line[:60]}...\"; only new news gets a segment")
                break
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
        e, w = lint(json.load(f), sys.argv[1])
    for x in w:
        print("warning:", x)
    for x in e:
        print("ERROR:", x)
    sys.exit(1 if e else 0)
