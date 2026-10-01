"""Narration: Kokoro (offline, Apache-2.0) with per-word timings for captions.

Kokoro doesn't return word timestamps, so each sentence is synthesised on its
own (exact sentence boundaries) and words inside a sentence are spread by a
length-based weight. Good enough for 1-3 word caption chunks.
"""
import os
import re
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
    for pat, rep in _SPOKEN:
        text = re.sub(pat, rep, text)
    return text


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
