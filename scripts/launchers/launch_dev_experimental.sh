#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export PYTHONUTF8=1
export SkySpotter_PREFER_DIRECTML=1
export SkySpotter_FEATURES_FILE=config/skyspotter_features.json
export SkySpotter_ENABLE_BLUR_SCORE=1
export RAWVIEWER_USE_PROCESS_POOL=0
export RAWVIEWER_VERBOSE_INFO_LOGS=0
export RAWVIEWER_VERBOSE_CONSOLE=0
export RAWVIEWER_FOCUS_GALLERY_SWITCH=1
export RAWVIEWER_FILE_LOG=1
export RAWVIEWER_VERBOSE_ORIENTATION_LOGS=1
export RAWVIEWER_DEBUG=1

echo "[SkySpotter] Launching with EXPERIMENTAL features (blur scoring)..."
if command -v pixi >/dev/null 2>&1; then
  exec pixi run -e experimental start "$@"
else
  export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
  exec python3 -u src/main.py "$@"
fi
