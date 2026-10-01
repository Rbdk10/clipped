# clipped: The City Case

An agent that makes a daily TikTok news update on the Premier League v Manchester City "115 charges" case. It runs every morning as a Claude Code routine. Each run:

1. **Researches** the last 36 hours of news and checks it against `case/case-file.md`.
2. **Writes** a ~65 s script in a TikTok format: a hook, a one-line recap, today's news, what's next, and a comment question. The legal-wording rules are in `agent/STYLE.md`.
3. **Renders** a 1080×1920 video: animated news graphics, a British AI voice, and word-by-word captions.
4. **Commits** `episodes/<date>/`: `video.mp4`, `post.md` (the paragraph plus a paste-ready caption and hashtags), `frames.jpg` and `script.json`.

You review the video and post it.

## Why graphics and not gameplay or footage
I researched this before building (sources in the session notes):
- **Animated graphics** (headline cards, counting numbers, versus cards, timelines, re-typed quotes) are made fresh for every video. TikTok's For You feed and Creator Rewards favour original content and down-rank reused clips.
- **Gameplay backgrounds** (Subway Surfers, Minecraft parkour) still hold attention. But they undercut credibility on a legal story, and stock gameplay packs get flagged as unoriginal.
- **Premier League footage** gets taken down; the league removed about 1M clips in 2023/24.
- **Club crests** count as third-party logos, which hurts For You feed eligibility.
- **AI-generated video** of real places gets auto-labelled, and viewers can now turn AI content down in their feeds.
- **Licensed stock footage** is supported as an optional layer. See `library/README.md`.
- **Videos run over 61 s,** because TikTok's Creator Rewards only pay on videos longer than a minute.

## Voice
[Kokoro](https://github.com/thewh1teagle/kokoro-onnx) runs locally. It's free, Apache-2.0 licensed (fine for monetised videos) and needs no API key. The default voice is `bm_george`, a British male; `bm_lewis`, `bm_daniel` and `bm_fable` are alternatives. Set `"voice"` in a script to change it. Because the voice is AI, **turn on TikTok's AI-generated label** when you post.

## Run it by hand
```bash
bash scripts/setup.sh                                   # deps + voice model (once per machine)
python3 -m render.lint   episodes/2026-10-01/script.json
python3 -m render.render episodes/2026-10-01/script.json   # add --preview for a fast encode
```

## Layout
- `agent/DAILY.md`: the agent's daily procedure (what the routine runs)
- `agent/STYLE.md`: hooks, structure, legal wording, visual rules
- `case/`: running case file with sources, plus a daily log
- `render/`: TTS, scenes, captions, lint, renderer
- `episodes/<date>/`: one folder per day
- `library/broll/`: optional licensed footage
