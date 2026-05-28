"""Shared background removal and subject crop for classifier training and batch tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Optional, Tuple

import numpy as np
from PIL import Image
from skimage.measure import label, regionprops

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".arw",
    ".dng",
    ".nef",
    ".cr2",
    ".cr3",
    ".raf",
    ".orf",
    ".rw2",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
}


def iter_image_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def isolate_subject_rgba(
    img: Image.Image,
    *,
    rembg_remove,
    session,
    focus_point: Optional[Tuple[float, float]] = None,
    remover_fallback=None,
) -> Tuple[Optional[Image.Image], str]:
    """Return RGBA crop of main subject, or (None, status) on failure."""
    if rembg_remove is not None and session is not None:
        img_nobg = rembg_remove(img, session=session, alpha_matting=False)
    elif remover_fallback is not None:
        bg = remover_fallback.remove_background(img)
        alpha_full = Image.new("L", bg.size, 255)
        img_nobg = bg.convert("RGBA")
        img_nobg.putalpha(alpha_full)
    else:
        return None, "no_bg_remover"

    alpha = np.array(img_nobg.split()[-1])
    binary = alpha > 20
    labeled = label(binary)
    props = regionprops(labeled)
    if not props:
        return None, "empty_mask"

    target_label = None
    if focus_point:
        cx, cy = focus_point
        for prop in props:
            minr, minc, maxr, maxc = prop.bbox
            if minc <= cx <= maxc and minr <= cy <= maxr:
                target_label = prop.label
                break
    if target_label is None:
        target_label = max(props, key=lambda p: p.area).label

    blob_mask = labeled == target_label
    new_alpha = np.where(blob_mask, alpha, 0).astype(np.uint8)
    final_img = img_nobg.copy()
    final_img.putalpha(Image.fromarray(new_alpha))

    bbox = Image.fromarray(new_alpha).getbbox()
    if not bbox:
        return None, "empty_blob"

    cropped = final_img.crop(bbox)
    status = "focused_blob" if focus_point else "largest_blob"
    return cropped, status


def composite_white_background(cropped_rgba: Image.Image) -> Image.Image:
    bg = Image.new("RGB", cropped_rgba.size, (255, 255, 255))
    bg.paste(cropped_rgba, mask=cropped_rgba.split()[-1])
    return bg


def init_rembg_session():
    from rembg import new_session, remove as rembg_remove

    session = new_session("isnet-general-use")
    return session, rembg_remove


def init_fallback_remover():
    src_dir = Path(__file__).resolve().parents[1] / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from background_removal import get_background_remover

    return get_background_remover()


def build_processed_dataset(
    source_dir: Path,
    dest_dir: Path,
    *,
    min_width: int = 400,
    min_height: int = 400,
    load_image: Callable[[Path], Image.Image],
    focus_point_fn: Optional[Callable[[Path, int, int], Optional[Tuple[float, float]]]] = None,
    progress_callback=None,
) -> Tuple[int, int]:
    """
    Mirror class subfolders from source_dir into dest_dir with rembg + crop PNGs.
    Returns (saved_count, skipped_count).
    """
    session = None
    rembg_remove = None
    remover_fallback = None
    try:
        session, rembg_remove = init_rembg_session()
    except Exception:
        remover_fallback = init_fallback_remover()

    saved = 0
    skipped = 0
    class_dirs = sorted(
        d for d in source_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    )
    for class_dir in class_dirs:
        out_class = dest_dir / class_dir.name
        out_class.mkdir(parents=True, exist_ok=True)
        for src_path in iter_image_files(class_dir):
            rel = src_path.relative_to(class_dir)
            out_path = out_class / f"{rel.stem}.png"
            if out_path.exists() and out_path.stat().st_mtime >= src_path.stat().st_mtime:
                saved += 1
                continue
            try:
                img = load_image(src_path).convert("RGB")
                focus = None
                if focus_point_fn:
                    focus = focus_point_fn(src_path, img.width, img.height)
                cropped, status = isolate_subject_rgba(
                    img,
                    rembg_remove=rembg_remove,
                    session=session,
                    focus_point=focus,
                    remover_fallback=remover_fallback,
                )
                if cropped is None:
                    skipped += 1
                    if progress_callback:
                        progress_callback(src_path, status)
                    continue
                w, h = cropped.size
                if w < min_width and h < min_height:
                    skipped += 1
                    if progress_callback:
                        progress_callback(src_path, f"too_small({w}x{h})")
                    continue
                rgb = composite_white_background(cropped)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                rgb.save(out_path, format="PNG")
                saved += 1
                if progress_callback:
                    progress_callback(src_path, status)
            except Exception as exc:
                skipped += 1
                if progress_callback:
                    progress_callback(src_path, f"error:{exc}")

    return saved, skipped
