# clipped

A daily TikTok news agent for the Man City "115 charges" case. See README.md.

- For a daily run, follow `agent/DAILY.md` exactly.
- Python 3.11, no package layout beyond `render/`. Run modules with `python3 -m render.<name>` from the repo root.
- The renderer is pure PIL frames piped to ffmpeg. There is no browser or Remotion. Keep it that way: the cloud environment only reaches GitHub and the package registries.
- `models/` is gitignored. `scripts/setup.sh` fetches the model.
- Never put PL footage, crests or article screenshots in the repo.
