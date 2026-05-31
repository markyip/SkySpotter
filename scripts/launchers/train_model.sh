#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Optional override:
# export SkySpotter_TRAIN_DATA_PATH="/path/to/SkySpotter/training_data/classified_images"

echo "[SkySpotter] Installing/updating pixi environments (default + dev-ml)..."
pixi install
pixi install -e dev-ml

echo "[SkySpotter] Starting model training..."
pixi run -e dev-ml train-model

echo "[SkySpotter] Training completed successfully."
