"""
Experimental sharpness score for gallery filters (sharp / blurry).

**Disabled by default** — set ``SkySpotter_ENABLE_BLUR_SCORE=1`` to index scores and
use search tokens. See README (Experimental features).

Laplacian variance on a downscaled ``subject_rect`` crop (original RGB + rembg bbox).
"""

from __future__ import annotations

import logging
import math
import os
from typing import Callable, Literal, Optional, Sequence, Tuple, TypeVar

from PIL import Image

logger = logging.getLogger(__name__)

T = TypeVar("T")


def blur_score_enabled() -> bool:
    """See ``skyspotter_features.blur_score_enabled()``."""
    from skyspotter_features import blur_score_enabled as _enabled

    return _enabled()


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
        return max(128, int(os.environ.get("SkySpotter_BLUR_MAX_SIZE", "1920")))
    except (TypeError, ValueError):
        return 1920


def center_crop_fraction() -> float:
    try:
        return max(0.3, min(1.0, float(os.environ.get("SkySpotter_BLUR_CENTER_FRACTION", "0.7"))))
    except (TypeError, ValueError):
        return 0.7


def subject_bbox_pad_fraction() -> float:
    try:
        return max(0.0, min(0.5, float(os.environ.get("SkySpotter_BLUR_SUBJECT_BBOX_PAD", "0.08"))))
    except (TypeError, ValueError):
        return 0.08


def bbox_from_rgba_alpha(
    rgba_image: Image.Image, threshold: int = 20
) -> Optional[Tuple[int, int, int, int]]:
    """Return (left, top, right, bottom) from rembg alpha; right/bottom are exclusive."""
    import numpy as np

    if rgba_image is None or rgba_image.mode != "RGBA":
        return None
    alpha = np.asarray(rgba_image.split()[-1], dtype=np.uint8)
    ys, xs = np.where(alpha > threshold)
    if ys.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def crop_rgb_by_bbox(
    rgb_image: Image.Image,
    bbox: Tuple[int, int, int, int],
    pad_fraction: Optional[float] = None,
) -> Optional[Image.Image]:
    """Pad bbox and crop original RGB (no background removal)."""
    if rgb_image is None or bbox is None:
        return None
    left, top, right, bottom = bbox
    w, h = rgb_image.size
    bw = max(1, right - left)
    bh = max(1, bottom - top)
    frac = subject_bbox_pad_fraction() if pad_fraction is None else float(pad_fraction)
    pad_l = int(round(bw * frac))
    pad_t = int(round(bh * frac))
    pad_r = pad_l
    pad_b = pad_t
    left = max(0, left - pad_l)
    top = max(0, top - pad_t)
    right = min(w, right + pad_r)
    bottom = min(h, bottom + pad_b)
    if right - left < 32 or bottom - top < 32:
        return None
    return rgb_image.crop((left, top, right, bottom))


def subject_rect_crop_rgb(
    src_rgb: Image.Image, rgba_for_bbox: Image.Image
) -> Optional[Image.Image]:
    """Crop ``src_rgb`` to rembg alpha bbox; keeps natural background inside the rect."""
    if src_rgb is None or rgba_for_bbox is None:
        return None
    if src_rgb.size != rgba_for_bbox.size:
        return None
    bbox = bbox_from_rgba_alpha(rgba_for_bbox)
    if bbox is None:
        return None
    return crop_rgb_by_bbox(src_rgb, bbox)


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
    file_path: str,
    rgb_image: Image.Image,
    *,
    rgba_for_bbox: Optional[Image.Image] = None,
) -> Tuple[Optional[float], str]:
    """
    Laplacian sharpness on a ``subject_rect`` crop of original RGB (no white compositing).

    Requires ``rgba_for_bbox`` from ``prepare_subject_pipeline``. Returns (None, \"\") when
    the subject bbox cannot be derived.
    """
    if rgb_image is None or rgba_for_bbox is None:
        return None, ""
    w, h = rgb_image.size
    if w < 8 or h < 8:
        return None, ""

    subject_crop = subject_rect_crop_rgb(rgb_image, rgba_for_bbox)
    if subject_crop is None or min(subject_crop.size) < 32:
        logger.debug(
            "[BLUR] no subject_rect for %s",
            os.path.basename(file_path or ""),
        )
        return None, ""

    score = laplacian_sharpness_from_rgb(subject_crop)
    logger.debug(
        "[BLUR] score=%.1f region=subject_rect file=%s",
        score,
        os.path.basename(file_path or ""),
    )
    return score, "subject_rect"
