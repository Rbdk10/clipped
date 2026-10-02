"""Frame drawing for the 1080x1920 video. Pure PIL; no footage required.

Layout respects TikTok's UI: nothing important above y=170 (tabs), right of
x=950 below y=700 (like/comment buttons) or below y=1480 (description).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")

NAVY = (8, 14, 32)
NAVY2 = (14, 30, 66)
SKY = (108, 171, 221)
WHITE = (255, 255, 255)
RED = (230, 46, 56)
GOLD = (255, 204, 0)
GREY = (170, 182, 204)

CARD_TOP, CARD_BOTTOM = 290, 1060
CAPTION_Y = 1250
SAFE_L, SAFE_R = 70, 950


def font(name, size):
    files = {"display": "Anton-Regular.ttf", "bold": "Montserrat-ExtraBold.ttf", "body": "Inter-SemiBold.ttf"}
    return ImageFont.truetype(os.path.join(FONT_DIR, files[name]), size)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def wrap(draw, text, fnt, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_text(text, kind, max_w, max_h, start, minimum=40, spacing=1.08):
    """Largest font size at which text wraps into the box."""
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    size = start
    while size >= minimum:
        f = font(kind, size)
        lines = wrap(probe, text, f, max_w)
        h = len(lines) * size * spacing
        if h <= max_h and all(probe.textlength(l, font=f) <= max_w for l in lines):
            return f, lines, size
        size -= 4
    f = font(kind, minimum)
    return f, wrap(probe, text, f, max_w), minimum


# --------------------------------------------------------------------------
# Background: drifting glows over navy. Pre-rendered oversize, panned per frame.

class Background:
    def __init__(self, seed=0, accent=SKY, base=NAVY, base2=NAVY2):
        import numpy as np
        rnd = random.Random(seed)
        bw, bh = W + 400, H + 400
        grad = Image.linear_gradient("L").resize((bw, bh))
        img = Image.composite(Image.new("RGB", (bw, bh), base2), Image.new("RGB", (bw, bh), base), grad)
        glow = Image.new("RGB", (bw, bh), (0, 0, 0))
        g = ImageDraw.Draw(glow)
        for _ in range(5):
            r = rnd.randint(260, 520)
            x, y = rnd.randint(0, bw), rnd.randint(0, bh)
            g.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(c * rnd.uniform(0.25, 0.45)) for c in accent))
        glow = glow.filter(ImageFilter.GaussianBlur(160))
        img = Image.fromarray(_add(img, glow))
        d = ImageDraw.Draw(img)
        for x in range(0, bw, 120):  # faint grid for texture
            d.line([(x, 0), (x, bh)], fill=tuple(min(c + 10, 255) for c in base2), width=1)
        for y in range(0, bh, 120):
            d.line([(0, y), (bw, y)], fill=tuple(min(c + 10, 255) for c in base2), width=1)
        self.img = img
        self.phase = rnd.uniform(0, 6.28)

    def frame(self, t):
        ox = 200 + 170 * math.sin(t * 0.21 + self.phase)
        oy = 200 + 170 * math.cos(t * 0.17 + self.phase)
        return self.img.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))


def _add(a, b):
    import numpy as np
    return np.clip(np.asarray(a, dtype=np.int16) + np.asarray(b, dtype=np.int16), 0, 255).astype("uint8")


# --------------------------------------------------------------------------
# Small shared pieces

def pill(text, fnt, fg, bg, pad=(26, 12)):
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    box = probe.textbbox((0, 0), text, font=fnt)
    w, h = box[2] - box[0] + pad[0] * 2, box[3] - box[1] + pad[1] * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=bg)
    d.text((pad[0] - box[0], pad[1] - box[1]), text, font=fnt, fill=fg)
    return im


def paste(dst, src, x, y, alpha=1.0):
    if alpha <= 0:
        return
    if alpha < 1:
        a = src.getchannel("A").point(lambda v: int(v * alpha))
        src = src.copy()
        src.putalpha(a)
    dst.paste(src, (int(x), int(y)), src)


def text_layer(lines, fnt, size, fill, spacing=1.08, align="left", width=None, stroke=0, stroke_fill=(0, 0, 0)):
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    width = width or int(max(probe.textlength(l, font=fnt) for l in lines)) + stroke * 2 + 4
    lh = int(size * spacing)
    im = Image.new("RGBA", (width, lh * len(lines) + int(size * 0.35) + stroke * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=fnt)
        x = {"left": stroke, "center": (width - lw) / 2, "right": width - lw - stroke}[align]
        d.text((x, i * lh + stroke), l, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


# --------------------------------------------------------------------------
# Scene types. Each returns a callable draw(frame, local_t, dur).

def scene_headline(v):
    kicker = pill(v.get("kicker", "LATEST").upper(), font("bold", 38), WHITE, RED if v.get("urgent", True) else NAVY2)
    width = v.get("width", SAFE_R - SAFE_L)
    f, lines, size = fit_text(v["text"].upper(), "display", width, 560, 150, spacing=1.04)
    body = text_layer(lines, f, size, WHITE, spacing=1.04)
    sub = None
    if v.get("sub"):
        sf, sl, ss = fit_text(v["sub"], "body", width, 150, 46)
        sub = text_layer(sl, sf, ss, GREY, spacing=1.2)
    total_h = kicker.height + 30 + body.height + (sub.height + 24 if sub else 0)
    top = CARD_TOP + (CARD_BOTTOM - CARD_TOP - total_h) // 2

    def draw(fr, t, dur):
        a = ease_out(t / 0.3)
        paste(fr, kicker, SAFE_L - 40 * (1 - a), top, a)
        b = ease_out((t - 0.08) / 0.35)
        paste(fr, body, SAFE_L, top + kicker.height + 30 + 50 * (1 - b), b)
        if sub:
            c = ease_out((t - 0.3) / 0.35)
            paste(fr, sub, SAFE_L, top + kicker.height + 30 + body.height + 24, c)
    return draw


def scene_stat(v):
    value = str(v["value"])
    pre, suf = v.get("prefix", ""), v.get("suffix", "")
    of = v.get("of")
    label = v.get("label", "")
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    of_txt = f"/{of}" if of else ""
    size = 330
    while size > 140:
        big, small = font("display", size), font("display", int(size * 0.45))
        need = probe.textlength(pre + value + suf, font=big) + (probe.textlength(of_txt, font=small) + 10 if of_txt else 0)
        if need <= SAFE_R - SAFE_L:
            break
        size -= 10
    lab_f, lab_lines, lab_s = fit_text(label.upper(), "bold", SAFE_R - SAFE_L, 200, 64)
    lab = text_layer(lab_lines, lab_f, lab_s, WHITE, align="center", width=SAFE_R - SAFE_L, spacing=1.15)
    numeric = value.replace(",", "").isdigit()
    target = int(value.replace(",", "")) if numeric else 0
    value_w = probe.textlength(pre + value + suf, font=big)
    full_w = value_w + (probe.textlength(of_txt, font=small) + 10 if of_txt else 0)

    def draw(fr, t, dur):
        d = ImageDraw.Draw(fr)
        p = ease_out(t / 0.9)
        shown = pre + (f"{int(round(target * p)):,}" if numeric else value) + suf
        x = (W - full_w) / 2
        y = CARD_TOP + 90
        s = ease_back(t / 0.35)
        col = GOLD if v.get("accent") == "gold" else SKY
        d.text((x, y + 40 * (1 - s)), shown, font=big, fill=col)
        if of_txt:
            d.text((x + value_w + 10, y + size * 0.5), of_txt, font=small, fill=GREY)
        a = ease_out((t - 0.4) / 0.4)
        paste(fr, lab, SAFE_L, y + size * 1.27, a)
    return draw


def scene_quote(v):
    f, lines, size = fit_text("“" + v["text"] + "”", "bold", SAFE_R - SAFE_L - 40, 520, 76, spacing=1.18)
    body = text_layer(lines, f, size, WHITE, spacing=1.18)
    who = pill("— " + v.get("who", ""), font("bold", 36), NAVY, SKY)
    total = body.height + 40 + who.height
    top = CARD_TOP + (CARD_BOTTOM - CARD_TOP - total) // 2

    def draw(fr, t, dur):
        d = ImageDraw.Draw(fr)
        a = ease_out(t / 0.3)
        d.rectangle([SAFE_L - 30, top, SAFE_L - 18, top + body.height * a], fill=SKY)
        paste(fr, body, SAFE_L + 10, top + 30 * (1 - a), a)
        b = ease_out((t - 0.35) / 0.3)
        paste(fr, who, SAFE_L + 10, top + body.height + 40, b)
    return draw


def scene_list(v):
    title = text_layer([v.get("title", "").upper()], font("display", 96), 96, SKY)
    items = []
    for it in v["items"][:5]:
        f, lines, size = fit_text(it, "bold", SAFE_R - SAFE_L - 90, 160, 58, minimum=36, spacing=1.12)
        items.append(text_layer(lines, f, size, WHITE, spacing=1.12))

    def draw(fr, t, dur):
        d = ImageDraw.Draw(fr)
        paste(fr, title, SAFE_L, CARD_TOP + 10, ease_out(t / 0.3))
        y = CARD_TOP + 10 + title.height + 30
        step = max(min((dur * 0.75) / max(len(items), 1), 2.5), 0.4)
        for i, im in enumerate(items):
            a = ease_out((t - 0.25 - i * step) / 0.3)
            if a > 0:
                cx, cy = SAFE_L + 22, y + 34
                r = 18 * ease_back((t - 0.25 - i * step) / 0.3)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD if v.get("numbered") is False else SKY)
                paste(fr, im, SAFE_L + 70 + 30 * (1 - a), y, a)
            y += im.height + 22
    return draw


def scene_timeline(v):
    items = v["items"][:6]
    hl = v.get("highlight", len(items) - 1)
    df = font("display", 56)
    rows = []
    for date, what in items:
        f, lines, size = fit_text(what, "bold", 560, 120, 46, minimum=32)
        rows.append((date.upper(), text_layer(lines, f, size, WHITE, spacing=1.12)))
    gap = (CARD_BOTTOM - CARD_TOP - 40) / max(len(rows), 1)

    def draw(fr, t, dur):
        d = ImageDraw.Draw(fr)
        x_line = SAFE_L + 250
        step = max(min(dur * 0.7 / len(rows), 1.6), 0.35)
        reach = ease_out(t / (step * len(rows) + 0.2))
        y0 = CARD_TOP + 40
        d.line([(x_line, y0), (x_line, y0 + (len(rows) - 1) * gap * reach + 1)], fill=GREY, width=6)
        for i, (date, im) in enumerate(rows):
            a = ease_out((t - i * step) / 0.3)
            y = y0 + i * gap
            if a <= 0:
                continue
            on = i == hl
            r = (22 if on else 14) * ease_back((t - i * step) / 0.3)
            d.ellipse([x_line - r, y - r, x_line + r, y + r], fill=GOLD if on else SKY)
            dl = d.textlength(date, font=df)
            d.text((x_line - 40 - dl, y - 34), date, font=df, fill=GOLD if on else SKY)
            paste(fr, im, x_line + 45, y - 30, a)
    return draw


def scene_versus(v):
    left, right = v["left"], v["right"]
    lf, ll, ls = fit_text(left["text"].upper(), "display", 400, 360, 92)
    rf, rl, rs = fit_text(right["text"].upper(), "display", 400, 360, 92)
    L = text_layer(ll, lf, ls, WHITE, align="center", width=410)
    R = text_layer(rl, rf, rs, WHITE, align="center", width=410)
    lh = pill(left.get("label", "").upper(), font("bold", 34), NAVY, SKY)
    rh = pill(right.get("label", "").upper(), font("bold", 34), WHITE, RED)
    vs = font("display", 120)

    def draw(fr, t, dur):
        d = ImageDraw.Draw(fr)
        a = ease_out(t / 0.35)
        b = ease_out((t - 0.2) / 0.35)
        y = CARD_TOP + 140
        paste(fr, lh, 70 + (410 - lh.width) / 2 - 60 * (1 - a), y - 90, a)
        paste(fr, L, 70 - 60 * (1 - a), y, a)
        paste(fr, rh, 600 + (410 - rh.width) / 2 + 60 * (1 - b), y - 90, b)
        paste(fr, R, 600 + 60 * (1 - b), y, b)
        if t > 0.35:
            s = ease_back((t - 0.35) / 0.3)
            d.text((540 - 55 * s, y + 380), "VS", font=vs, fill=GOLD)
    return draw


def scene_broll(v):
    # B-roll fills the frame (handled by the renderer); this just adds a label.
    label = v.get("text")
    if not label:
        return lambda fr, t, dur: None
    f, lines, size = fit_text(label.upper(), "display", SAFE_R - SAFE_L, 300, 120)
    im = text_layer(lines, f, size, WHITE, stroke=6)

    def draw(fr, t, dur):
        a = ease_out(t / 0.35)
        paste(fr, im, SAFE_L, CARD_BOTTOM - im.height - 30 * (1 - a), a)
    return draw


def scene_punch(v):
    f, lines, size = fit_text(v["text"].upper(), "display", SAFE_R - SAFE_L, 620, 260, spacing=1.0)
    col = {"gold": GOLD, "red": RED, "sky": SKY}.get(v.get("color"), WHITE)
    im = text_layer(lines, f, size, col, spacing=1.0, align="center", width=SAFE_R - SAFE_L)
    top = CARD_TOP + (CARD_BOTTOM - CARD_TOP - im.height) // 2

    def draw(fr, t, dur):
        s = ease_back(t / 0.25)
        if s <= 0.02:
            return
        layer = im.resize((max(int(im.width * s), 1), max(int(im.height * s), 1)), Image.BILINEAR) if abs(s - 1) > 0.01 else im
        paste(fr, layer, (W - layer.width) / 2 - (W - (SAFE_L + SAFE_R)) / 2, top + (im.height - layer.height) / 2)
    return draw


SCENES = {
    "punch": scene_punch,
    "headline": scene_headline,
    "stat": scene_stat,
    "quote": scene_quote,
    "list": scene_list,
    "timeline": scene_timeline,
    "versus": scene_versus,
    "broll": scene_broll,
}


# --------------------------------------------------------------------------
# Persistent overlays

class Chrome:
    """Series badge, progress bar, source tag."""

    def __init__(self, series, day):
        self.badge = pill(f"{series.upper()}  •  DAY {day}", font("bold", 34), NAVY, WHITE)
        self.src_font = font("body", 30)

    def draw(self, fr, t, total, source=None, credit=None):
        d = ImageDraw.Draw(fr)
        d.rectangle([0, 0, W, 10], fill=(255, 255, 255, 40))
        d.rectangle([0, 0, int(W * t / total), 10], fill=SKY)
        paste(fr, self.badge, (W - self.badge.width) // 2, 180)
        if source:
            txt = f"Source: {source}"
            d.text((SAFE_L, 1440), txt, font=self.src_font, fill=GREY)
        if credit:
            d.text((SAFE_L, 1480 if source else 1440), f"Photo: {credit}", font=self.src_font, fill=GREY)


class Captions:
    """Word-by-word captions in short chunks, active word highlighted."""

    def __init__(self, words, max_words=3, max_chars=18):
        self.f = font("bold", 92)
        self.chunks = []
        cur = []
        for w in words:
            cur.append(w)
            chars = sum(len(x.text) + 1 for x in cur)
            ends = w.text[-1:] in ".,!?;:"
            if len(cur) >= max_words or chars >= max_chars or ends:
                self.chunks.append(cur)
                cur = []
        if cur:
            self.chunks.append(cur)
        self.probe = ImageDraw.Draw(Image.new("L", (1, 1)))

    def draw(self, fr, t):
        chunk = None
        for c in self.chunks:
            if c[0].start <= t < c[-1].end + 0.05:
                chunk = c
                break
        if not chunk:
            return
        texts = [w.text.upper() for w in chunk]
        space = self.probe.textlength(" ", font=self.f)
        widths = [self.probe.textlength(x, font=self.f) for x in texts]
        total = sum(widths) + space * (len(texts) - 1)
        scale = 1.0
        if total > SAFE_R - SAFE_L:
            scale = (SAFE_R - SAFE_L) / total
        pop = 1 + 0.08 * (1 - ease_out((t - chunk[0].start) / 0.12))
        layer = Image.new("RGBA", (int(total) + 40, 150), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        x = 20
        for w, txt, wd in zip(chunk, texts, widths):
            active = w.start <= t < w.end + 0.03
            d.text((x, 20), txt, font=self.f, fill=GOLD if active else WHITE, stroke_width=9, stroke_fill=(0, 0, 0))
            x += wd + space
        s = scale * pop
        if abs(s - 1) > 0.01:
            layer = layer.resize((int(layer.width * s), int(layer.height * s)), Image.BILINEAR)
        cx = (SAFE_L + SAFE_R) / 2
        paste(fr, layer, cx - layer.width / 2, CAPTION_Y - layer.height / 2)
