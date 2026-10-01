"""Render an episode: script.json -> video.mp4 (1080x1920, 30fps, -14 LUFS).

    python -m render.render episodes/2026-10-01/script.json

See render/SCRIPT_FORMAT.md for the script schema.
"""
import json
import os
import random
import subprocess
import sys
import tempfile
import time
import wave

import numpy as np
from PIL import Image, ImageDraw

from . import lint, post, scenes, tts
from .scenes import H, W

FPS = 30
ROOT = os.path.join(os.path.dirname(__file__), "..")
BROLL_DIR = os.path.join(ROOT, "library", "broll")

THEMES = [
    dict(base=(8, 14, 32), base2=(14, 30, 66), accent=(108, 171, 221)),   # night navy, sky glow
    dict(base=(6, 10, 14), base2=(20, 28, 40), accent=(255, 204, 0)),     # graphite, gold glow
    dict(base=(4, 22, 38), base2=(10, 48, 70), accent=(90, 200, 230)),    # deep teal
]


# --------------------------------------------------------------------------
# Optional footage: library/broll/index.json lists licensed clips with tags.

def load_broll():
    path = os.path.join(BROLL_DIR, "index.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        clips = json.load(f)
    return [c for c in clips if os.path.exists(os.path.join(BROLL_DIR, c["file"]))]


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


class BrollReader:
    """Streams frames of a clip, cropped to 9:16, darkened, with a slow push-in."""

    def __init__(self, path, dur, rnd):
        length = probe_duration(path)
        start = rnd.uniform(0, max(length - dur - 0.5, 0))
        zoom = rnd.choice(["1.0+0.04*t/%f" % dur, "1.04-0.04*t/%f" % dur])
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"fps={FPS},eq=brightness=-0.12:saturation=0.85")
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", f"{start:.2f}", "-stream_loop", "-1", "-i", path,
             "-t", f"{dur + 1:.2f}", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE)
        self.last = None

    def frame(self):
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombytes("RGB", (W, H), buf)
        return self.last

    def close(self):
        self.proc.kill()


class StillPan:
    """Ken Burns for a still image: cover-crop oversize, then pan a 9:16 window across it."""

    def __init__(self, path, dur, rnd):
        im = Image.open(path).convert("RGB")
        scale = max(W * 1.18 / im.width, H * 1.18 / im.height)
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        from PIL import ImageEnhance
        self.im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.9)).enhance(0.8)
        self.dur = max(dur, 0.1)
        mx, my = self.im.width - W, self.im.height - H
        pts = [(0, 0), (mx, 0), (0, my), (mx, my), (mx // 2, 0), (mx // 2, my)]
        self.a = rnd.choice(pts)
        self.b = rnd.choice([p for p in pts if p != self.a])
        self.t = 0

    def frame(self):
        k = min(max(self.t / self.dur, 0), 1)
        k = k * k * (3 - 2 * k)  # smoothstep
        x = self.a[0] + (self.b[0] - self.a[0]) * k
        y = self.a[1] + (self.b[1] - self.a[1]) * k
        self.t += 1 / FPS
        return self.im.crop((int(x), int(y), int(x) + W, int(y) + H))

    def close(self):
        pass


def pick_broll(clips, tags, used, rnd):
    tags = set(tags or [])
    pool = [c for c in clips if tags & set(c.get("tags", []))] or clips
    fresh = [c for c in pool if c["file"] not in used] or pool
    return rnd.choice(fresh) if fresh else None


# --------------------------------------------------------------------------
# Audio

def whoosh(sr, dur=0.35, rnd=None):
    rnd = rnd or np.random.default_rng(0)
    n = int(sr * dur)
    noise = rnd.standard_normal(n).astype(np.float32)
    # crude band-sweep: running mean with shrinking window + fade envelope
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    out = np.convolve(noise, np.ones(24) / 24, mode="same") * env
    return out / (np.abs(out).max() + 1e-6)


def write_wav(path, audio, sr):
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# --------------------------------------------------------------------------

def render(script_path, out_path=None, voice=None, preview=False):
    t0 = time.time()
    with open(script_path) as f:
        script = json.load(f)
    out_path = out_path or os.path.join(os.path.dirname(script_path), "video.mp4")
    segs = script["segments"]
    day = script.get("day", 1)
    rnd = random.Random(script.get("date", "") + str(day))
    theme = THEMES[day % len(THEMES)]

    audio, words, bounds = tts.synthesize([s["say"] for s in segs],
                                          voice=voice or script.get("voice", "bm_george"),
                                          speed=script.get("speed", 1.12))
    sr = tts.SR
    tail = 0.6
    total = len(audio) / sr + tail
    audio = np.concatenate([audio, np.zeros(int(tail * sr), np.float32)])
    sfx_rng = np.random.default_rng(day)
    for (start, _end) in bounds[1:]:
        w = whoosh(sr, rnd=sfx_rng) * 0.06
        i = max(int((start - 0.12) * sr), 0)
        audio[i:i + len(w)] += w[:len(audio) - i]

    bg = scenes.Background(seed=day, accent=theme["accent"], base=theme["base"], base2=theme["base2"])
    chrome = scenes.Chrome(script.get("series", "The City Case"), day)
    captions = scenes.Captions(words)
    clips = load_broll()
    used = set()
    # darkens footage behind the card and caption band so text stays legible
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        a = int(150 * max(0.0, 1 - abs(y - 900) / 900) + 40)
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, a))

    draws = []
    for s in segs:
        v = dict(s.get("visual") or {"type": "headline", "text": s["say"][:60]})
        if v["type"] == "broll" and not clips:
            v = {"type": "headline", "text": v.get("text") or v.get("fallback") or "", "kicker": v.get("kicker", "LATEST")}
        draws.append((v, scenes.SCENES[v["type"]](v)))

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        write_wav(wav, audio, sr)
        n_frames = int(total * FPS)
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-i", wav,
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
               "-c:v", "libx264", "-preset", "ultrafast" if preview else "medium", "-crf", "21",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
               "-movflags", "+faststart", "-shortest", out_path]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        seg_i, reader = -1, None
        for fi in range(n_frames):
            t = fi / FPS
            i = 0
            while i + 1 < len(bounds) and t >= bounds[i + 1][0] - 0.12:
                i += 1
            start = bounds[i][0] - (0.12 if i else 0)
            end = bounds[i + 1][0] - 0.12 if i + 1 < len(bounds) else total
            if i != seg_i:
                seg_i = i
                if reader:
                    reader.close()
                    reader = None
                v = draws[i][0]
                img = segs[i].get("image")
                img = img and os.path.join(os.path.dirname(script_path), img)
                if img and not os.path.exists(img):
                    print(f"warning: missing image {img}, using animated background", file=sys.stderr)
                    img = None
                if img:
                    reader = StillPan(img, end - start, rnd)
                elif v["type"] == "broll" and clips:
                    c = pick_broll(clips, v.get("tags"), used, rnd)
                    used.add(c["file"])
                    reader = BrollReader(os.path.join(BROLL_DIR, c["file"]), end - start, rnd)
            frame = reader.frame() if reader else None
            if frame is None:
                frame = bg.frame(t)
            frame = frame.convert("RGBA") if frame.mode != "RGBA" else frame.copy()
            if reader:
                frame.alpha_composite(shade)
            v, draw = draws[i]
            draw(frame, t - start, end - start)
            chrome.draw(frame, t, total, segs[i].get("source"))
            captions.draw(frame, t)
            if i and t - start < 0.07:  # cut flash
                frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.35)
            enc.stdin.write(frame.convert("RGB").tobytes())
        if reader:
            reader.close()
        enc.stdin.close()
        enc.wait()
    if enc.returncode:
        raise SystemExit(f"ffmpeg failed ({enc.returncode})")

    meta = {"duration": round(total, 2), "words": len(words), "render_seconds": round(time.time() - t0, 1),
            "segments": [[round(a, 2), round(b, 2)] for a, b in bounds]}
    print(json.dumps(meta))
    return meta


def contact_sheet(video, bounds, out):
    """One frame from the middle of each segment, tiled, for a quick visual check."""
    with tempfile.TemporaryDirectory() as tmp:
        tiles = []
        for i, (a, b) in enumerate(bounds):
            p = os.path.join(tmp, f"{i}.png")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a + (b - a) * 0.6:.2f}", "-i", video,
                            "-frames:v", "1", "-vf", "scale=270:480", p], check=True)
            tiles.append(Image.open(p).copy())
    cols = min(len(tiles), 5)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 280, rows * 490), "white")
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 280, (i // cols) * 490))
    sheet.save(out, quality=80)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--out")
    ap.add_argument("--voice")
    ap.add_argument("--preview", action="store_true", help="fast encode")
    ap.add_argument("--force", action="store_true", help="render despite lint errors")
    a = ap.parse_args()
    with open(a.script) as f:
        errs, warns = lint.lint(json.load(f))
    for w in warns:
        print("lint warning:", w, file=sys.stderr)
    for e in errs:
        print("lint ERROR:", e, file=sys.stderr)
    if errs and not a.force:
        sys.exit("fix the lint errors (or pass --force)")
    meta = render(a.script, a.out, a.voice, a.preview)
    video = a.out or os.path.join(os.path.dirname(a.script), "video.mp4")
    contact_sheet(video, meta["segments"], os.path.join(os.path.dirname(video), "frames.jpg"))
    print("wrote", post.write_post(a.script, meta))
