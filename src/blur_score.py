"""
Sharpness score for gallery filters (sharp / blurry).

Laplacian variance on a downscaled frame **without** rembg: EXIF / maker focus ROI when
available, else a central crop, else the full thumbnail. ViT classification still uses
rembg separately. Higher score = sharper.
"""

from __future__ import annotations

import logging
import math
import os
from typing import Callable, Literal, Optional, Sequence, Tuple, TypeVar

from PIL import Image

logger = logging.getLogger(__name__)

T = TypeVar("T")


def blur_blurry_fraction() -> float:
    """Fraction of scored images treated as blurry (bottom rank). Default 20%."""
    try:
        f = float(os.environ.get("SkySpotter_BLUR_BLURRY_FRACTION", "0.2"))
        return max(0.01, min(0.99, f))
    except (TypeError, ValueError):
        return 0.2


def blur_sharp_threshold() -> float:
    """Legacy absolute Laplacian cutoff (``blur>=N`` filters only; not ``sharp``/``blurry``)."""
    try:
        return float(os.environ.get("SkySpotter_BLUR_SHARP_THRESHOLD", "100"))
    except (TypeError, ValueError):
        return 100.0


def blur_rank_blurry_count(n_scored: int, blurry_fraction: Optional[float] = None) -> int:
    """How many lowest-scoring images count as blurry (at least one sharp remains when n ≥ 2)."""
    if n_scored <= 0:
        return 0
    if n_scored == 1:
        return 0
    frac = blur_blurry_fraction() if blurry_fraction is None else max(0.01, min(0.99, blurry_fraction))
    return max(1, min(n_scored - 1, math.ceil(n_scored * frac)))


def filter_rows_by_blur_rank(
    rows: Sequence[T],
    score_fn: Callable[[T], Optional[float]],
    want: Literal["sharp", "blurry"],
    blurry_fraction: Optional[float] = None,
) -> list[T]:
    """
    Rank ``blur_score`` within the current row set (gallery folder / filter pipeline).

    Bottom ``blur_blurry_fraction()`` → blurry; the rest with scores → sharp.
    Rows without a score are excluded from both.
    """
    scored: list[tuple[T, float]] = []
    for row in rows:
        s = score_fn(row)
        if s is not None:
            scored.append((row, s))
    n = len(scored)
    if n == 0:
        return []
    scored.sort(key=lambda pair: pair[1])
    n_blurry = blur_rank_blurry_count(n, blurry_fraction)
    blurry_set = {id(r) for r, _ in scored[:n_blurry]}
    if want == "blurry":
        return [r for r, _ in scored if id(r) in blurry_set]
    return [r for r, _ in scored if id(r) not in blurry_set]


def blur_index_max_size() -> int:
    try:
        return max(128, int(os.environ.get("SkySpotter_BLUR_MAX_SIZE", "1280")))
    except (TypeError, ValueError):
        return 1280


def center_crop_fraction() -> float:
    try:
        return max(0.3, min(1.0, float(os.environ.get("SkySpotter_BLUR_CENTER_FRACTION", "0.7"))))
    except (TypeError, ValueError):
        return 0.7


def _orientation_for_path(file_path: str) -> int:
    try:
        from image_cache import get_image_cache

        meta = get_image_cache().get_exif(file_path) or {}
        return int(meta.get("orientation", 1) or 1)
    except Exception:
        return 1


def _laplacian_variance(gray_u8: "np.ndarray") -> float:
    """4-connected Laplacian variance (higher = sharper). Pure NumPy."""
    import numpy as np

    g = np.asarray(gray_u8, dtype=np.float64)
    if g.size == 0 or g.ndim != 2:
        return 0.0
    if g.shape[0] < 3 or g.shape[1] < 3:
        return 0.0
    lap = (
        -4.0 * g[1:-1, 1:-1]
        + g[:-2, 1:-1]
        + g[2:, 1:-1]
        + g[1:-1, :-2]
        + g[1:-1, 2:]
    )
    return float(lap.var())


def laplacian_sharpness_from_rgb(rgb_image: Image.Image) -> float:
    """Return Laplacian variance (higher = sharper)."""
    import numpy as np

    gray = np.asarray(rgb_image.convert("L"), dtype=np.uint8)
    if gray.size == 0:
        return 0.0
    max_side = blur_index_max_size()
    h, w = gray.shape[:2]
    longest = max(h, w)
    if longest > max_side:
        scale = max_side / float(longest)
        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))
        gray = np.asarray(
            rgb_image.convert("L").resize((new_w, new_h), Image.Resampling.LANCZOS),
            dtype=np.uint8,
        )
    return _laplacian_variance(gray)


def exif_focus_crop_rgb(
    file_path: str, rgb_image: Image.Image
) -> Optional[Image.Image]:
    """Crop to EXIF / maker focus subject region in ``rgb_image`` coordinates."""
    if not file_path or rgb_image is None:
        return None
    w, h = rgb_image.size
    if w < 8 or h < 8:
        return None
    try:
        from exif_subject_area import pixmap_ltwh_focus_hint

        hint = pixmap_ltwh_focus_hint(
            file_path, w, h, _orientation_for_path(file_path)
        )
        if not hint:
            return None
        left, top, cw, ch = hint[0]
        left = max(0, min(int(left), w - 1))
        top = max(0, min(int(top), h - 1))
        cw = max(1, min(int(cw), w - left))
        ch = max(1, min(int(ch), h - top))
        if cw < 16 or ch < 16:
            return None
        return rgb_image.crop((left, top, left + cw, top + ch))
    except Exception as exc:
        logger.debug("[BLUR] EXIF focus crop failed for %s: %s", file_path, exc)
        return None


def center_crop_rgb(rgb_image: Image.Image, fraction: Optional[float] = None) -> Image.Image:
    """Central ``fraction`` of width/height (default 0.7)."""
    frac = center_crop_fraction() if fraction is None else float(fraction)
    w, h = rgb_image.size
    cw = max(1, int(round(w * frac)))
    ch = max(1, int(round(h * frac)))
    left = (w - cw) // 2
    top = (h - ch) // 2
    return rgb_image.crop((left, top, left + cw, top + ch))


def compute_blur_score_for_index(
    file_path: str, rgb_image: Image.Image
) -> Tuple[Optional[float], str]:
    """
    Laplacian sharpness without rembg.

    Returns (score, region tag): ``exif``, ``center``, or ``full``.
    """
    if rgb_image is None:
        return None, ""
    w, h = rgb_image.size
    if w < 8 or h < 8:
        return None, ""

    exif_crop = exif_focus_crop_rgb(file_path, rgb_image)
    if exif_crop is not None:
        score = laplacian_sharpness_from_rgb(exif_crop)
        logger.debug(
            "[BLUR] score=%.1f region=exif file=%s",
            score,
            os.path.basename(file_path),
        )
        return score, "exif"

    center = center_crop_rgb(rgb_image)
    if min(center.size) >= 32:
        score = laplacian_sharpness_from_rgb(center)
        logger.debug(
            "[BLUR] score=%.1f region=center file=%s",
            score,
            os.path.basename(file_path),
        )
        return score, "center"

    score = laplacian_sharpness_from_rgb(rgb_image)
    logger.debug(
        "[BLUR] score=%.1f region=full file=%s",
        score,
        os.path.basename(file_path),
    )
    return score, "full"
