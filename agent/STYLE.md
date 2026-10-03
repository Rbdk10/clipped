# How to write an episode

The audience is UK football fans scrolling TikTok. They give you about 2 seconds. Write like a sharp Sky Sports News presenter talking to a mate: punchy and clear, never shouty.

## Length
- **170–200 words → 62–72 seconds** with the Matthew voice (~2.8 words/s; 160 words came out at 59 s). The video must be **over 61 s**, because TikTok's Creator Rewards Program only pays on videos over 1 minute. Don't go over 80 s.
- **9–13 segments.** Each segment is 1–2 sentences and gets its own graphic, so the picture changes every 3–7 s. A segment over ~25 words means one graphic sits too long; split it.
- Sentences of 6–14 words, one fact per sentence. Use contractions.

## Structure: rumour hook → new news → rumour payoff
Every episode is built to keep viewers to the end: open on a rumour, deliver today's news, and only settle the rumour in the last 15 seconds.

1. **Rumour hook (segment 1, ≤ 15 words, visual `rumour`).** The juiciest *unconfirmed* claim from the last 36 hours: a tabloid scoop, an X "EXCL", a single-outlet report. Name who's saying it, out loud and on the card: "The Mirror claims Pep could walk back into City if the appeal fails." A question works too: "Is Haaland really leaving over the verdict?"
   - It must be a real, published claim. Never invent or exaggerate one.
   - The narrator never endorses it. Attribute it ("X claims", "reports suggest") and keep the legal wording below.
2. **Open loop (segment 2).** Promise the payoff: "We'll tell you how much of that holds up at the end. First, what actually happened today."
3. **Today's news (5–8 segments).** Only things that are **new since yesterday's episode**. Name the source aloud ("Sky Sports reports …"). Use a `punch` card ("THE TWIST", "BUT…") before the key turn.
4. **What's next (1 segment).** The next date or decision to watch.
5. **Rumour check (1–2 segments, visual `verdict`).** Come back to the opening rumour with the details: who else is reporting it, what's confirmed, what's been denied, and a 0–10 credibility rating with a one-word verdict (`confirmed` / `developing` / `shaky` / `denied`). "Rumour check: only Metro and an X account have it. Nobody at City has commented. Two out of ten."
6. **Engagement + CTA (last segment).** Ask an opinion question about today's news or the rumour ("Would you want Pep back? Comment below."), then "follow for tomorrow's update."

**No recaps.** Don't spend a segment re-explaining the case: no "Quick recap…", no re-listing the verdict, the 115 charges or the £-figures that earlier episodes covered. Regular viewers have seen it, and it's the part they scroll past. If a new fact needs context, give it as a half-sentence inside the news line ("…City, who are appealing the commission's ruling, …"). Check the last 3 episodes' scripts; a fact they already led with can only appear as that kind of half-sentence.

**No rumour worth using?** Open with the most surprising new detail of the day as a question ("Why is Man United suddenly counting its losses?") and answer it in the closing segments instead. Same shape, still no recap.

**Quiet day (nothing new and verified):** never invent news. Lead with the best rumour of the day if there is one, then make the middle an explainer on one open question from `case/case-file.md` that previous episodes haven't covered. Still give it a Day number.

## Legal wording: non-negotiable
The case is under appeal. Write every claim so it would survive a lawyer reading it.

| Never | Write instead |
|---|---|
| "City cheated / are frauds / lied / corrupt" | "an independent commission found City broke Premier League rules" |
| "City will be relegated / stripped of titles" | "the punishment hasn't been decided. Options include …" |
| "Final verdict", "it's over" | "City say they'll appeal" |
| "Sources say …" (unnamed) | "The Athletic reports …" |
| Claims about named executives' personal conduct | Only what the published decision or an on-record statement says |
| "Breaking" when it isn't | Use `"urgent": false` on the kicker |

- "Guilty" is fine only when attributed: "the Premier League says City were found guilty …".
- Every episode must still say, once and briefly, that City deny wrongdoing / are appealing and that the punishment is still pending. Do it as a half-sentence inside a news line, not as a recap segment.
- Opinion must be labelled ("Pundits argue …", "Kieran Maguire thinks …"). The narrator has no opinion of their own.
- A new fact needs **two independent outlets**, or it gets attributed to the one outlet that reported it ("The Times reports …").
- Never voice-clone or imitate a real person.

## Visuals: pick the graphic that SHOWS the sentence
| Type | Use for |
|---|---|
| `rumour` | segment 1 only: the claim, `outlet`, and an UNCONFIRMED stamp |
| `verdict` | the rumour check near the end: claim, `rating` 0–10, `word` |
| `headline` | statements, "why it matters" |
| `punch` | 1–3 word pattern interrupt: "THE TWIST", "BUT…", "FRIDAY" |
| `stat` | any number: charges, £, points, days |
| `versus` | two sides: City vs Premier League, commission vs appeal |
| `quote` | on-record quotes, re-typed, never screenshots |
| `list` | next steps, possible punishments (≤ 4 items) |
| `timeline` | how we got here, upcoming dates |
| `broll` | licensed footage from `library/broll/`; falls back to a headline if there's none |

Rules:
- Use one `rumour` (segment 1), one `verdict` (in the last 3 segments), and at least one `stat` and one `punch` per episode.
- Every episode opens on the `rumour` card, so vary the *second* segment's visual from yesterday's instead.
- No club crests, logos, Premier League footage or screenshots of articles. The graphics are ours, and that's what keeps the account "original" in TikTok's eyes.
- **Photos of real people only from `library/photos/`** (public domain or CC licences that allow commercial use, each with a licence record). Use `"image": "photos/<file>"`; the renderer adds the "Photo: …" credit and puts the face beside the headline.
  - A person appears only while the narration names them or is about them. Never put someone behind a line about breaches they aren't personally accused of (no Pep behind "114 of 115 charges").
  - Never use press-agency photos (Getty, PA, Reuters, AP) or AI-generated images of real people.
  - When you use a library photo, list its credit in the caption: "Photos: …".
- On-screen text should not just repeat the voiceover. Make it the headline version: 2–6 words.
- Every factual segment gets a short `source` ("Sky Sports, 1 Oct").

## Caption and hashtags (`post.md`)
- First line, under 100 characters, keyword-rich: "Man City 115 charges update, Day N: …".
- Then 2–3 factual sentences, then "Sources: …", then "AI voiceover."
- **Hashtags: max 5.** Always use `#mancity #115charges #premierleague`, plus 2 rotating tags (`#footballnews`, `#appeal`, `#ffp`, `#pl`, `#football`).
