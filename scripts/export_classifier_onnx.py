#!/usr/bin/env python3
"""Export the gallery ViT checkpoint to ONNX for DirectML (default runtime env)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("SkySpotter_PREFER_DIRECTML", "0")


def main() -> int:
    from semantic_search import MilitaryAircraftClassifier

    clf = MilitaryAircraftClassifier()

    def progress(msg: str) -> None:
        print(msg, flush=True)

    ok = clf.export_onnx_for_directml(progress_callback=progress)
    if not ok:
        print(
            "Export failed. Use the dev-ml pixi env (pixi run -e dev-ml export-classifier-onnx) "
            "and ensure models/gallery-classifier/.../model.safetensors exists.",
            file=sys.stderr,
        )
        return 1
    print(f"ONNX ready: {clf.onnx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
