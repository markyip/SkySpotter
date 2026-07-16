#!/usr/bin/env bash
# Launch SkySpotter from source (debug / development).
# Repo root: scripts/launchers -> ../..

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COLD_START_FLAG="${ROOT}/.skyspotter_cold_start"
if [ -f "$COLD_START_FLAG" ] || [ -f "${ROOT}/.skyspotter_cold_start" ]; then
    export SkySpotter_DISABLE_SESSION_RESTORE=1
    export RAWVIEWER_DISABLE_SESSION_RESTORE=1
    rm -f "$COLD_START_FLAG" "${ROOT}/.skyspotter_cold_start"
    echo "[SkySpotter] Cold start: session restore disabled for this launch (after clear_cache.sh)."
fi

export PYTHONUTF8=1
export SkySpotter_FEATURES_FILE=config/skyspotter_features.json
export SkySpotter_USE_PROCESS_POOL=1
export SkySpotter_PROGRESSIVE_RAW_LOAD=1
export SkySpotter_NAV_PRELOAD_DISPLAY=1
export RAWVIEWER_VERBOSE_ORIENTATION_LOGS=1
export RAWVIEWER_DEBUG=1
# Gallery: EXIF + aircraft labels only (semantic/face off in skyspotter_features.json).
export RAWVIEWER_ENABLE_SEMANTIC_SEARCH="${RAWVIEWER_ENABLE_SEMANTIC_SEARCH:-0}"
export RAWVIEWER_AUTO_METADATA_INDEX="${RAWVIEWER_AUTO_METADATA_INDEX:-1}"
export RAWVIEWER_TEST_PYEXIV2="${RAWVIEWER_TEST_PYEXIV2:-1}"
export RAWVIEWER_TEST_SEMANTIC="${RAWVIEWER_TEST_SEMANTIC:-0}"
export RAWVIEWER_GPU_VIEW="${RAWVIEWER_GPU_VIEW:-1}"
export RAWVIEWER_VERBOSE_INFO_LOGS=0
export RAWVIEWER_VERBOSE_CONSOLE=0
export RAWVIEWER_FOCUS_GALLERY_SWITCH=1
export RAWVIEWER_FILE_LOG=1
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"

if [ -f "${ROOT}/SkySpotter_env/bin/activate" ]; then
    # shellcheck source=/dev/null
    source "${ROOT}/SkySpotter_env/bin/activate"
fi

if [ "${RAWVIEWER_TEST_PYEXIV2}" = "1" ]; then
    echo "[SkySpotter] Testing pyexiv2 import..."
    python3 - <<'PY' || { echo "[ERROR] pyexiv2 import failed."; exit 1; }
import pyexiv2
print("pyexiv2 OK:", pyexiv2.__file__)
PY
fi

echo "[SkySpotter] Launching in development mode..."
if command -v pixi >/dev/null 2>&1; then
    exec pixi run python -u src/main.py "$@"
fi
exec python3 -u src/main.py "$@"
