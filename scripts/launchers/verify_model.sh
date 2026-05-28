#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Optional overrides:
# export SkySpotter_VERIFY_INPUT_DIR=".../testing_data/test_images"
# export SkySpotter_VERIFY_MODEL_DIR=".../customized_model"
# export SkySpotter_VERIFY_OUTPUT_DIR=".../testing_data/test_output"

echo "[SkySpotter] Installing/updating pixi environment..."
pixi install

echo "[SkySpotter] Verifying trained model on testing_data/test_images..."
echo "[SkySpotter] Checkpoint: customized_model/  (override with SkySpotter_VERIFY_MODEL_DIR)"
echo "[SkySpotter] Results: testing_data/test_output/"

args=()
if [[ -n "${SkySpotter_VERIFY_INPUT_DIR:-}" ]]; then
  args+=(--input-dir "$SkySpotter_VERIFY_INPUT_DIR")
fi
if [[ -n "${SkySpotter_VERIFY_MODEL_DIR:-}" ]]; then
  args+=(--model-dir "$SkySpotter_VERIFY_MODEL_DIR")
fi
if [[ -n "${SkySpotter_VERIFY_OUTPUT_DIR:-}" ]]; then
  args+=(--output-dir "$SkySpotter_VERIFY_OUTPUT_DIR")
fi

pixi run python scripts/batch_test_classifier.py "${args[@]}"

echo "[SkySpotter] Verification completed. See testing_data/test_output/top3_detection_scores.csv"
