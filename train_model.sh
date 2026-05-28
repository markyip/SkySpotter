#!/usr/bin/env bash
set -euo pipefail

# Optional override:
# export SkySpotter_TRAIN_DATA_PATH="/path/to/SkySpotter/training_data/classified_images"

echo "[SkySpotter] Installing/updating pixi environment..."
pixi install

echo "[SkySpotter] Starting model training..."
pixi run python scripts/train_processed_aircraft.py

echo "[SkySpotter] Training completed successfully."
