"""Narration with per-word timings for captions.

Two engines:
- ElevenLabs (default when ELEVENLABS_API_KEY is set): /with-timestamps gives
  character-level timings, so captions are exact. Audio is cached per segment in
  the episode's voice/ folder so re-renders don't spend credits.
- Kokoro (offline, Apache-2.0) fallback. It has no timestamps, so each sentence
  is synthesised alone and words are spread inside it by a length-based weight.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass

import numpy as np

MODEL_DIR = os.environ.get("CLIPPED_MODELS", os.path.join(os.path.dirname(__file__), "..", "models"))
SR = 24000
_kokoro = None


@dataclass
class Word:
    text: str
    start: float
    end: float


def _engine():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"),
                         os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    return _kokoro


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


# Things the voice gets wrong if read literally. Captions keep the original.
_SPOKEN = [
    (r"£(\d+(?:\.\d+)?)\s?m\b", r"\1 million pounds"),
    (r"£(\d+(?:\.\d+)?)\s?bn\b", r"\1 billion pounds"),
    (r"£(\d+(?:\.\d+)?)", r"\1 pounds"),
    (r"\bvs\.?\b", "versus"),
    (r"\bPL\b", "Premier League"),
    (r"\bFFP\b", "F F P"),
    (r"\bCAS\b", "C A S"),
    (r"\bAPT\b", "A P T"),
]


def spoken_form(text):
    # Token by token, so each caption word maps to a known run of spoken words.
    return " ".join(_spoken_token(t) for t in text.split())


def _spoken_token(tok):
    for pat, rep in _SPOKEN:
        tok = re.sub(pat, rep, tok)
    return tok


def _weight(word):
    core = re.sub(r"[^\w£%]", "", word)
    w = max(len(core), 2) + 1.5
    if re.search(r"[,;:]$", word):
        w += 2.5
    if re.match(r"^[\d£]", core):
        w += 3 * len(core)  # numbers take longer to say than to write
    return w


def synthesize(segments, voice="bm_george", speed=1.12, gap=0.12, seg_gap=0.22):
    """segments: list of narration strings.

    Returns (audio float32 mono @SR, words, seg_bounds) where seg_bounds is a
    list of (start, end) seconds per segment.
    """
    k = _engine()
    chunks, words, bounds = [], [], []
    t = 0.0
    for si, seg in enumerate(segments):
        seg_start = t
        for sent in split_sentences(seg):
            audio, sr = k.create(spoken_form(sent), voice=voice, speed=speed, lang="en-gb")
            assert sr == SR
            dur = len(audio) / SR
            toks = sent.split()
            weights = [_weight(w) for w in toks]
            total = sum(weights)
            lead, tail = 0.03, 0.06
            usable = max(dur - lead - tail, 0.1)
            cur = t + lead
            for tok, w in zip(toks, weights):
                d = usable * w / total
                words.append(Word(tok, cur, cur + d))
                cur += d
            chunks.append(audio.astype(np.float32))
            t += dur
            chunks.append(np.zeros(int(gap * SR), np.float32))
            t += gap
        if si < len(segments) - 1:
            chunks.append(np.zeros(int(seg_gap * SR), np.float32))
            t += seg_gap
        bounds.append((seg_start, t))
    audio = np.concatenate(chunks) if chunks else np.zeros(SR, np.float32)
    return audio, words, bounds


# --------------------------------------------------------------------------
# ElevenLabs

ELEVEN_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128"
ELEVEN_DEFAULTS = {
    "voice_id": "fhWgCDAdAXgPVl5ls9uP",   # "Matthew": British news/sport reader; fastest and least monotone of 8 tested (2026-10-01)
    "model_id": "eleven_multilingual_v2",
    "stability": 0.45,
    "similarity_boost": 0.8,
    "style": 0.25,
    "speed": 1.0,   # Matthew is quick; at 1.08 Day 4 ran 58.7 s, under TikTok's 61 s Creator Rewards line
}


def eleven_available():
    return bool(os.environ.get("ELEVENLABS_API_KEY"))


def _eleven_call(text, prev_text, next_text, cfg):
    body = {
        "text": text,
        "model_id": cfg["model_id"],
        "voice_settings": {k: cfg[k] for k in ("stability", "similarity_boost", "style", "speed")}
                          | {"use_speaker_boost": True},
    }
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
    req = urllib.request.Request(ELEVEN_URL.format(voice=cfg["voice_id"]), data=json.dumps(body).encode(),
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def _decode_mp3(data):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", "-", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         input=data, capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def _spoken_words(chars, starts, ends):
    """Group character timings into (word, start, end) for the spoken text."""
    out, cur, cs = [], "", None
    for c, a, b in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                out.append((cur, cs, last))
            cur, cs = "", None
            continue
        if cs is None:
            cs = a
        cur += c
        last = b
    if cur:
        out.append((cur, cs, last))
    return out


def synthesize_eleven(segments, cache_dir, cfg=None, seg_gap=0.22):
    cfg = {**ELEVEN_DEFAULTS, **(cfg or {})}
    os.makedirs(cache_dir, exist_ok=True)
    chunks, words, bounds = [], [], []
    t = 0.0
    spoken = [spoken_form(s) for s in segments]
    for si, seg in enumerate(segments):
        text = spoken[si]
        key = hashlib.sha1(json.dumps([text, cfg], sort_keys=True).encode()).hexdigest()[:16]
        mp3, meta = os.path.join(cache_dir, key + ".mp3"), os.path.join(cache_dir, key + ".json")
        if not (os.path.exists(mp3) and os.path.exists(meta)):
            res = _eleven_call(text, spoken[si - 1] if si else None,
                               spoken[si + 1] if si + 1 < len(spoken) else None, cfg)
            with open(mp3, "wb") as f:
                f.write(base64.b64decode(res["audio_base64"]))
            with open(meta, "w") as f:
                json.dump(res["alignment"], f)
            print(f"elevenlabs: segment {si + 1} ({len(text)} chars)", file=sys.stderr)
        with open(mp3, "rb") as f:
            audio = _decode_mp3(f.read())
        with open(meta) as f:
            al = json.load(f)
        sw = _spoken_words(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"])
        # map caption tokens onto spoken words (one token can be several spoken words, e.g. £830m)
        j = 0
        for tok in seg.split():
            n = max(len(_spoken_token(tok).split()), 1)
            run = sw[j:j + n] or sw[-1:]
            words.append(Word(tok, t + run[0][1], t + run[-1][2]))
            j += n
        bounds.append((t, t + len(audio) / SR + (seg_gap if si < len(segments) - 1 else 0)))
        chunks.append(audio)
        t += len(audio) / SR
        if si < len(segments) - 1:
            chunks.append(np.zeros(int(seg_gap * SR), np.float32))
            t += seg_gap
    return np.concatenate(chunks), words, bounds
