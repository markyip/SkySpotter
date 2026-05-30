"""
Ensure a working OpenCV (cv2) build before blur POC scripts run rembg.

Pixi envs must not keep ``opencv-python-headless`` alongside ``opencv-contrib-python``.
Run ``pixi run fix-opencv`` after ``pixi install``, or let POC scripts auto-repair.
"""

from __future__ import annotations

import os
import sys


def ensure_cv2(*, auto_fix: bool = True) -> None:
    """
    Verify cv2 has native bindings (Laplacian, BORDER_DEFAULT). Optionally repair env.

    Set ``POC_CV2_NO_FIX=1`` to check only (no pip changes).
    """
    if os.environ.get("POC_CV2_NO_FIX", "").strip().lower() in ("1", "true", "yes"):
        auto_fix = False

    sys.modules.pop("cv2", None)
    try:
        import cv2

        if (
            getattr(cv2, "__file__", None)
            and hasattr(cv2, "Laplacian")
            and hasattr(cv2, "BORDER_DEFAULT")
        ):
            print(
                f"[poc_cv2] OpenCV {cv2.__version__} OK ({cv2.__file__})",
                flush=True,
            )
            return
    except Exception as first_err:
        if not auto_fix:
            raise SystemExit(
                f"OpenCV (cv2) is broken.\nRun: pixi run fix-opencv\n\n{first_err}"
            ) from first_err
    else:
        first_err = None

    if auto_fix:
        from pixi_fix_opencv import repair_opencv

        if repair_opencv(quiet=False):
            import cv2

            print(
                f"[poc_cv2] OpenCV {cv2.__version__} OK after repair ({cv2.__file__})",
                flush=True,
            )
            return

    msg = (
        "OpenCV (cv2) is missing or broken (rembg needs a full cv2 build).\n"
        "Fix:\n"
        "  pixi install\n"
        "  pixi run fix-opencv\n"
        "  pixi run python -c \"import cv2; print(cv2.__version__, cv2.__file__)\"\n"
        "SkySpotter uses opencv-contrib-python only (see pixi.toml).\n"
    )
    if first_err:
        msg += f"\nImport error: {first_err}\n"
    raise SystemExit(msg)
