#!/usr/bin/env python3
"""Repair OpenCV: drop headless conflict and reinstall opencv-contrib-python if needed."""

from __future__ import annotations

import importlib
import subprocess
import sys


def _pip(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pip", *args],
        text=True,
        capture_output=True,
    )


def _cv2_ok() -> bool:
    sys.modules.pop("cv2", None)
    try:
        cv2 = importlib.import_module("cv2")
    except Exception:
        return False
    return bool(getattr(cv2, "__file__", None)) and hasattr(cv2, "Laplacian") and hasattr(
        cv2, "BORDER_DEFAULT"
    )


def repair_opencv(*, quiet: bool = False) -> bool:
    """
    Remove opencv-python-headless when it conflicts with opencv-contrib-python.
    Reinstall opencv-contrib-python when the cv2 extension is missing.
    """
    import importlib.metadata as md

    try:
        contrib_ver = md.version("opencv-contrib-python")
    except md.PackageNotFoundError:
        if not quiet:
            print("opencv-contrib-python missing — run: pixi install", file=sys.stderr)
        return False

    try:
        md.version("opencv-python-headless")
        if not quiet:
            print(
                "Removing opencv-python-headless (conflicts with opencv-contrib-python) …",
                flush=True,
            )
        r = _pip("uninstall", "-y", "opencv-python-headless")
        if r.returncode != 0 and not quiet:
            print(r.stderr or r.stdout, file=sys.stderr)
    except md.PackageNotFoundError:
        pass

    if _cv2_ok():
        return True

    if not quiet:
        print(
            f"Reinstalling opencv-contrib-python=={contrib_ver} (cv2 binary missing) …",
            flush=True,
        )
    r = _pip(
        "install",
        "--force-reinstall",
        "--no-deps",
        f"opencv-contrib-python=={contrib_ver}",
    )
    if r.returncode != 0:
        if not quiet:
            print(r.stderr or r.stdout, file=sys.stderr)
        return False
    if r.stdout.strip() and not quiet:
        print(r.stdout.strip(), flush=True)

    return _cv2_ok()


def main() -> int:
    if not repair_opencv():
        print("OpenCV repair failed.", file=sys.stderr)
        return 1
    cv2 = importlib.import_module("cv2")
    print(f"OpenCV OK: {cv2.__version__} ({cv2.__file__})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
