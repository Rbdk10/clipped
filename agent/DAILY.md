# Daily run: The City Case

You are the producer of a daily TikTok news series on the Premier League v Manchester City "115 charges" case. Each run makes one ~65-second episode: research → script → render → publish files to the repo.

Read `agent/STYLE.md` before writing. It holds the writing and legal-wording rules.

## 1. Set up (start it first; it takes ~1 min)
```bash
bash scripts/setup.sh
```
It installs Python deps and the Kokoro voice model into `models/`. ffmpeg is already in the container.

## 2. Catch up
- `case/case-file.md`: where the case stands, with sources.
- The top ~7 lines of `case/log.md`: what recent episodes covered.
- The last 3 episodes' `script.json`: note every fact they already covered. Those facts don't get their own segment again (see "No recaps" in STYLE.md), and don't reuse a rumour they already checked unless it has moved on.
- **Day number** = days since 28 Sep 2026 (29 Sep 2026 = Day 1). Use UK date.

## 3. Research the last ~36 hours
Run several WebSearch queries in parallel with `mode: "extended"`. For example:
- `Man City 115 charges latest`
- `Manchester City appeal Premier League`
- `Man City sanction points deduction`
- `Premier League Manchester City statement`
- Plus a query for each open question in the case file.

WebFetch is blocked for most news sites in this environment, so work from search summaries and cross-check them. A fact needs **two independent outlets**, or it gets attributed to the one that reported it. Prefer: BBC, Sky Sports, The Athletic, The Guardian, The Times, ESPN, Reuters, PA, official PL or City statements. Treat fan sites and aggregators (CaughtOffside, Football365, readmancity) as leads, not sources.

While researching, collect **today's rumours** too: tabloid scoops, X "EXCL"s, single-outlet claims (Mirror, Sun, Daily Mail, Metro, Football Insider, talkSPORT, X). Pick the one viewers will most want resolved for the `rumour` hook, then research it properly (who else carries it, any denial) for the rumour check at the end. Pepstein's daily brief at `~/Dev/pepstein/reports/<date>.md` has a ready-made "Rumour mill" section when it's available locally.

Decide which kind of day it is:
- **News day:** something new and verified happened. Build the episode around it.
- **Quiet day:** nothing new. Make an explainer from the case-file backlog. Never pad, inflate or invent.

## 4. Write `episodes/<YYYY-MM-DD>/script.json`
Follow `render/SCRIPT_FORMAT.md` and `agent/STYLE.md`. Then:
```bash
python3 -m render.lint episodes/<date>/script.json
```
Fix every ERROR. Fix warnings unless there's a reason not to.

## 5. Render and check
```bash
python3 -m render.render episodes/<date>/script.json
```
This writes `video.mp4`, `frames.jpg` (one frame per segment) and `post.md`. It prints the duration.

- **Voice:** the output's `"voice"` field says `elevenlabs` or `kokoro`. If it fell back to Kokoro, say so in your report.
- **Duration under 61 s:** add a sentence, then re-render. **Over 80 s:** trim.
- **Look at `frames.jpg` with the Read tool:** check for text cut off, overlapping, or off-screen. Fix the script (shorter on-screen text) and re-render if anything is wrong.

## 6. Update the case file
- Edit `case/case-file.md`: update "Last updated", "Where it stands now", the timeline and the open questions. Only add facts with sources, and mark single-source items.
- Add one line to the top of `case/log.md`.

## 7. Commit and push
```bash
git add episodes/<date> case/   # includes episodes/<date>/voice/ (cached ElevenLabs audio)
git commit -m "Day N: <title>"
git push -u origin HEAD
```
Retry the push on network errors (2s, 4s, 8s, 16s).

## 8. Report
Finish with a short message:
- the Day number and title
- the news paragraph (from `post.md`)
- the video duration
- anything uncertain that the user should check before posting.

## Rules
- Never publish a claim you couldn't source. If something big is only rumoured, say "reports suggest" and name the outlet, or leave it out.
- Don't edit `render/` code during a daily run unless rendering is broken. If you do fix it, say so in the report.
- Don't post to TikTok or anywhere else. The user posts manually.
