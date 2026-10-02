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
**ElevenLabs** is the main voice. The default is "Matthew", a British voice from the ElevenLabs library made for news reading and sports commentary, using `eleven_multilingual_v2`. Of the 8 British male voices tested on 2026-10-01, he read the fastest (~190 wpm, which suits short-form) and had the most pitch variation, so he sounds least monotone. Christopher (`G17SuINrv2H9FC6nvetn`) is the runner-up.
- Its timestamp endpoint gives exact word timings, so the captions sync perfectly.
- Each segment's audio is cached in `episodes/<date>/voice/`, so re-renders don't spend credits.
- Each episode uses about 1,000 characters. Daily, that's about 30k a month: right at the Starter plan's limit, so use Creator (100k) for headroom.
- ElevenLabs needs `ELEVENLABS_API_KEY` set and `api.elevenlabs.io` allowed in the environment's network settings.
- To change the voice per episode, add `"elevenlabs": {"voice_id": "...", "speed": 1.1}` to the script.

When there's no key, it falls back to **Kokoro** "George" (offline, free, Apache-2.0). Set `CLIPPED_TTS=kokoro` to force it.

Because the voice is AI, **turn on TikTok's AI-generated label** when you post.

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
