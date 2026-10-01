#!/usr/bin/env bash
# One-time setup per container: Python deps + Kokoro voice model (~350MB, from GitHub releases).
set -euo pipefail
cd "$(dirname "$0")/.."
pip3 install -q -r requirements.txt 2>&1 | grep -v "Running pip as the 'root' user" || true
mkdir -p models
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [ ! -s "models/$f" ]; then
    echo "downloading $f"
    curl -fsSL --retry 4 -o "models/$f.part" "$base/$f" && mv "models/$f.part" "models/$f"
  fi
done
command -v ffmpeg >/dev/null || { echo "ffmpeg missing: apt-get install -y ffmpeg"; exit 1; }
echo "setup ok"
