"""Licensed photos in library/photos/, each with a licence record and an on-screen credit."""
import functools
import json
import os

PHOTO_DIR = os.path.join(os.path.dirname(__file__), "..", "library", "photos")


@functools.lru_cache(maxsize=None)
def photo_records():
    path = os.path.join(PHOTO_DIR, "index.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return {r["file"]: r for r in json.load(f)}


def photo_record(image):
    """Licensed photo for an "image" of the form "photos/<file>", else None."""
    if not image or not image.startswith("photos/"):
        return None
    return photo_records().get(image.split("/", 1)[1])
