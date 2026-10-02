# Handoff from the cloud session (2 Oct 2026)

Branch: `claude/serene-hamilton-1nrysy`. Read README.md, agent/DAILY.md and agent/STYLE.md for how the agent works.

## Done
- Daily agent built: research → script → lint → render (animated graphics, captions, voice) → commit.
- Routine **"The City Case: daily TikTok episode"** runs daily at 06:47 UK in the cloud. It pushes to this branch.
- Day 3 (1 Oct) and Day 4 (2 Oct) episodes are in `episodes/`.
- Day 4 was also rendered with 3 Higgsfield background images (stadium, gavel, hourglass). That version is in the user's Higgsfield library as `city-case-day4.mp4`.
  - Segments can now set `"image"`; the renderer pans across it.
- ElevenLabs narration is implemented (`render/tts.py`, exact word timings, audio cached in `episodes/<date>/voice/`). The default voice is now **Matthew** (see README), and the word target is 170–200.
- Done locally (1 Oct): Day 4 re-rendered with ElevenLabs/Matthew, 66.5 s, still without the Higgsfield images. The key is in the local vault as `ELEVENLABS_API_KEY` (`secret run ELEVENLABS_API_KEY -- python3 -m render.render ...`).
  - It isn't active yet: there's no key and no network access in the cloud environment.

## To do now: send this to FRIDAY
Use the `send_friday_task` tool:

> Use Chrome on the **anthoniedeklerk** profile only.
> 1. On elevenlabs.io → Developers → API Keys, create a key named "clipped" with Text to Speech access. Copy it with the site's Copy button; never read it or show it.
> 2. On claude.ai/code, open the session for Rbdk10/clipped → cloud environment menu in the title bar → Edit. Add the environment variable `ELEVENLABS_API_KEY` with the key as its value. Clear the clipboard afterwards.
> 3. In the same screen, add `api.elevenlabs.io` and `d8j0ntlcm91z4.cloudfront.net` to the allowed network domains. Save.
> 4. On claude.ai → Routines → "The City Case: daily TikTok episode", add the **Higgsfield** connector. Save.
> 5. Show an approval card before every Save and before creating the key.

## After FRIDAY is done
- Locally: `bash scripts/setup.sh`, then re-render Day 4 with ElevenLabs:
  - `export ELEVENLABS_API_KEY=...` (from the user's own keychain/vault, never pasted in chat)
  - `python3 -m render.render episodes/2026-10-02/script.json`
- To use the Higgsfield images locally, download the 3 images into `episodes/2026-10-02/` as `stadium.jpg`, `gavel.jpg` and `hourglass.jpg` from the user's Higgsfield generations (1 Oct ~23:49 UTC).
- Rule from the user: **max 3 Higgsfield images per video, images only, no video generations.**
- Then update the routine prompt / agent/DAILY.md so daily runs generate up to 3 images with Higgsfield.
