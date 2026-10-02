# How to write an episode

The audience is UK football fans scrolling TikTok. They give you about 2 seconds. Write like a sharp Sky Sports News presenter talking to a mate: punchy and clear, never shouty.

## Length
- **170–200 words → 62–72 seconds** with the Matthew voice (~2.8 words/s; 160 words came out at 59 s). The video must be **over 61 s**, because TikTok's Creator Rewards Program only pays on videos over 1 minute. Don't go over 80 s.
- **9–13 segments.** Each segment is 1–2 sentences and gets its own graphic, so the picture changes every 3–7 s. A segment over ~25 words means one graphic sits too long; split it.
- Sentences of 6–14 words, one fact per sentence. Use contractions.

## Structure
1. **Hook (segment 1, ≤ 15 words).** Lead with today's stakes or the surprise, never a warm-up. Good patterns:
   - "Manchester City have until Friday to …"
   - "The Premier League just …"
   - "Everyone's asking if City get relegated. Here's what the rules actually say."
   - "One line in today's ruling changes everything."
   Only use a pattern if it's true today.
2. **Open loop (segment 2).** Promise a payoff: "And today we found out how they plan to fight it."
3. **Quick recap (1 segment).** One line for new viewers: "Quick recap. On 29 September an independent commission found City broke the rules on 114 of 115 charges."
4. **Today's news (3–6 segments).** Name the source aloud ("Sky Sports reports …"). Use a `punch` card ("THE TWIST", "BUT…") before the key turn.
5. **What it means / what's next (1–2 segments).**
6. **Engagement + CTA (last segment).** Ask an opinion question with real options ("A fine, a points deduction, or something bigger?"), then "follow for tomorrow's update."

**Quiet day (no real new development):** never invent news. Make it an explainer from the backlog in `case/case-file.md`. Open with "No ruling today, so here's the one thing you need to understand about …". Still give it a Day number.

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
- Across each week, the viewer must hear that City deny wrongdoing and that the punishment is still pending. Include both in every episode until either changes.
- Opinion must be labelled ("Pundits argue …", "Kieran Maguire thinks …"). The narrator has no opinion of their own.
- A new fact needs **two independent outlets**, or it gets attributed to the one outlet that reported it ("The Times reports …").
- Never voice-clone or imitate a real person.

## Visuals: pick the graphic that SHOWS the sentence
| Type | Use for |
|---|---|
| `headline` | hook, statements, "why it matters" |
| `punch` | 1–3 word pattern interrupt: "THE TWIST", "BUT…", "FRIDAY" |
| `stat` | any number: charges, £, points, days |
| `versus` | two sides: City vs Premier League, commission vs appeal |
| `quote` | on-record quotes, re-typed, never screenshots |
| `list` | next steps, possible punishments (≤ 4 items) |
| `timeline` | how we got here, upcoming dates |
| `broll` | licensed footage from `library/broll/`; falls back to a headline if there's none |

Rules:
- Use at least one `stat` and one `punch` per episode.
- Don't open with the same visual type two days running (check yesterday's script).
- No club crests, logos, Premier League footage, screenshots of articles, or photos of people. The graphics are ours, and that's what keeps the account "original" in TikTok's eyes.
- On-screen text should not just repeat the voiceover. Make it the headline version: 2–6 words.
- Every factual segment gets a short `source` ("Sky Sports, 1 Oct").

## Caption and hashtags (`post.md`)
- First line, under 100 characters, keyword-rich: "Man City 115 charges update, Day N: …".
- Then 2–3 factual sentences, then "Sources: …", then "AI voiceover."
- **Hashtags: max 5.** Always use `#mancity #115charges #premierleague`, plus 2 rotating tags (`#footballnews`, `#appeal`, `#ffp`, `#pl`, `#football`).
