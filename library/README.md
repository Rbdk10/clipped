# Footage library (optional)

The videos are fully animated graphics by default. To mix in real footage, add licensed clips here and list them in `broll/index.json`:

```json
[
  {"file": "manchester-skyline-night.mp4", "tags": ["manchester", "city"], "license": "Pexels", "source": "https://www.pexels.com/video/…"},
  {"file": "empty-stadium-floodlights.mp4", "tags": ["stadium"], "license": "Mixkit free", "source": "https://mixkit.co/…"}
]
```

Then use `{"type": "broll", "tags": ["stadium"], "text": "Short label"}` in a script. The renderer picks a clip with a matching tag, starts at a random point, crops it to 9:16 and darkens it so the text reads.

## What's safe to add
- **Pexels, Pixabay, Mixkit, Coverr:** free for commercial use. Record the source URL anyway.
- Generic stadiums, Manchester skyline, courts, gavels, documents, money, a football on grass.
- Your own footage.

## What NOT to add
- Premier League match footage or broadcast clips. The league takes these down and they get accounts struck.
- Club crests or logos as the main subject.
- Identifiable people next to narration about rule-breaking (Pexels' licence forbids showing people in a negative light).
- Gameplay packs from "no-copyright" sites. Thousands of accounts reuse them, and TikTok flags them as unoriginal.
- Photoreal AI video of real people or places. It gets auto-labelled, and viewers can turn AI content down in their feed.

Keep each clip under ~20 MB (1080p, ≤ 30 s) so the repo stays small. The cloud environment can't download from stock sites, so clips have to be committed here.
