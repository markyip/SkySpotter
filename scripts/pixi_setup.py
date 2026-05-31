#!/usr/bin/env python3
"""Post-install setup: OpenCV repair + PyTorch GPU/CPU selection."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pixi_fix_opencv import repair_opencv  # noqa: E402
from pixi_setup_classifier_torch import configure_classifier_torch  # noqa: E402


def main() -> int:
    ok_cv = repair_opencv()
    if not ok_cv:
        print("OpenCV repair failed.", file=sys.stderr)
        return 1

    backend = configure_classifier_torch()
    print(f"Classifier backend after setup: {backend}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
