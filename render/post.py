"""Writes post.md next to the script: the news paragraph, a paste-ready caption, and a checklist."""
import json
import os


def write_post(script_path, meta=None):
    with open(script_path) as f:
        s = json.load(f)
    paragraph = " ".join(seg["say"] for seg in s["segments"])
    caption = s["caption"] + "\n\n" + " ".join(s["hashtags"])
    lines = [
        f"# Day {s['day']}: {s.get('title', '')}",
        "",
        f"_{s['date']}" + (f" · {meta['duration']:.0f}s video_" if meta else "_"),
        "",
        "## Today's update",
        "",
        paragraph,
        "",
        "## Caption (paste into TikTok)",
        "",
        "```",
        caption,
        "```",
        "",
        "## Before you post",
        "- Turn on **AI-generated content** (Settings → More options), because the voice is AI.",
        "- Optional: add a trending sound at 5–10% volume under the voice.",
        "- Add it to the **The City Case** playlist.",
        "",
        "## Sources",
        "",
    ]
    lines += [f"- [{x['name']}]({x['url']})" for x in s["sources"]]
    out = os.path.join(os.path.dirname(script_path), "post.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    return out
