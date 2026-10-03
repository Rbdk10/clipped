# script.json format

```jsonc
{
  "date": "2026-10-01",          // UK date
  "day": 3,                      // days since 28 Sep 2026
  "series": "The City Case",     // badge text (optional)
  "title": "City's appeal plan revealed",
  "rumour": {"claim": "Pep could return if the appeal fails", "outlet": "Metro", "rating": 2},  // segment 2's rumour, paid off at the end
  "elevenlabs": {"voice_id": "fhWgCDAdAXgPVl5ls9uP", "speed": 1.0},  // optional overrides (default voice: Matthew)
  "voice": "bm_george",          // Kokoro fallback voice: bm_george | bm_lewis | bm_daniel | bm_fable …
  "speed": 1.22,                 // Kokoro speed; 1.15–1.3 sounds natural
  "segments": [
    {
      "say": "Narration for this beat. Written the way it should appear in captions.",
      "visual": { "type": "headline", ... },
      "image": "stadium.jpg",          // optional still background in the episode folder (slow pan, darkened)
      "source": "Sky Sports, 1 Oct"   // optional on-screen source line
    }
  ],
  "caption": "Man City 115 charges update, Day 3: …  Sources: … AI voiceover.",
  "hashtags": ["#mancity", "#115charges", "#premierleague", "#footballnews", "#appeal"],
  "sources": [{ "name": "Sky Sports: …", "url": "https://…" }]
}
```

The voice reads `£830m` as "830 million pounds", and `PL` as "Premier League". Captions show the text exactly as written. Write numbers as digits.

## Visual types

| type | fields | example |
|---|---|---|
| `rumour` | `text` (the claim, ≤ 10 words), `outlet`, `stamp`? (default "UNCONFIRMED") | `{"type":"rumour","text":"Pep back if the appeal fails?","outlet":"Metro"}` |
| `verdict` | `text` (short claim), `rating` 0–10, `word`: confirmed / developing / shaky / denied | `{"type":"verdict","text":"Pep return","rating":2,"word":"shaky"}` |
| `headline` | `text`, `kicker`, `sub`?, `urgent` (red kicker, default true) | `{"type":"headline","kicker":"Appeal deadline","text":"City have until Friday"}` |
| `punch` | `text` (1–3 words), `color`: white/gold/red/sky | `{"type":"punch","text":"The twist","color":"gold"}` |
| `stat` | `value`, `prefix`?, `suffix`?, `of`?, `label`, `accent`: "gold"? | `{"type":"stat","value":"114","of":"115","label":"charges upheld"}` |
| `versus` | `left`/`right`: `{label, text}` | `{"type":"versus","left":{"label":"Commission","text":"Owner's money"},"right":{"label":"City","text":"Government money"}}` |
| `quote` | `text`, `who` | `{"type":"quote","text":"Clear material errors","who":"Manchester City statement"}` |
| `list` | `title`, `items` (≤ 4, short), `step`? (seconds between items; ~1.3 for the intro) | `{"type":"list","title":"What happens next","items":["Appeal by Friday","New appeal board"]}` |
| `timeline` | `items` [[date, event]…] (≤ 6), `highlight` (index) | `{"type":"timeline","items":[["Feb 2023","Charged"],["29 Sep 2026","Verdict"]],"highlight":1}` |
| `broll` | `tags`, `text`? | Uses a clip from `library/broll/index.json`. With no clips it falls back to a headline using `text`. |

Numbers in a `stat` count up from 0 when they're plain digits. Keep `value` to digits and put "£"/"M" in `prefix`/`suffix`.
