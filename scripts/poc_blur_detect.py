#!/usr/bin/env python3
"""POC: Laplacian blur scores (EXIF ROI / center / full — no rembg)."""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic", ".heif"}


def iter_images(folder: str):
    for dirpath, _dirnames, filenames in os.walk(folder):
        for name in sorted(filenames):
            ext = os.path.splitext(name)[1].lower()
            if ext in IMAGE_EXTS:
                yield os.path.join(dirpath, name)


def main() -> int:
    parser = argparse.ArgumentParser(description="POC Laplacian blur scores for a folder")
    parser.add_argument("folder", help="Root folder to scan (recursive)")
    parser.add_argument(
        "--csv",
        metavar="PATH",
        help="Write CSV (default: <folder>/blur_scores.csv)",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max files (0 = all)")
    args = parser.parse_args()
    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1

    from blur_score import (
        blur_blurry_fraction,
        blur_index_max_size,
        blur_rank_blurry_count,
        compute_blur_score_for_index,
    )
    from semantic_search import _load_index_source_image

    blurry_frac = blur_blurry_fraction()
    max_size = blur_index_max_size()

    rows: list[tuple[float | None, str, str, str]] = []
    paths = list(iter_images(folder))
    if args.limit > 0:
        paths = paths[: args.limit]

    print(f"Scanning {len(paths)} images under:\n  {folder}\n")
    print(f"Rating: bottom {blurry_frac * 100:.0f}% of folder = blurry (relative rank)")
    print(f"Mode: Laplacian on EXIF focus ROI, else center crop (max side {max_size}, no rembg)\n")

    t0 = time.perf_counter()
    for i, path in enumerate(paths, 1):
        rel = os.path.relpath(path, folder)
        score = None
        region = ""
        note = ""
        try:
            rgb = _load_index_source_image(path, max_size=max_size)
            score, region = compute_blur_score_for_index(path, rgb)
        except Exception as exc:
            note = f"err:{exc.__class__.__name__}"

        rows.append((score if score is not None else -1.0, rel, "", region or note))
        if i <= 3 or i % 25 == 0 or i == len(paths):
            print(f"  [{i}/{len(paths)}] {rel[:70]}", flush=True)

    elapsed = time.perf_counter() - t0
    rows.sort(key=lambda r: r[0])

    scored_idx = [i for i, row in enumerate(rows) if row[0] >= 0]
    n_blurry = blur_rank_blurry_count(len(scored_idx))
    blurry_idx = set(scored_idx[:n_blurry]) if n_blurry else set()
    relabeled: list[tuple[float, str, str, str]] = []
    for i, (score, rel, _lb, region) in enumerate(rows):
        if score < 0:
            relabeled.append((score, rel, "", region))
        else:
            lb = "blurry" if i in blurry_idx else "sharp"
            relabeled.append((score, rel, lb, region))
    rows = relabeled

    csv_path = args.csv or os.path.join(folder, "blur_scores.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["blur_score", "rating", "region", "path"])
        for score, rel, lb, region in rows:
            w.writerow(
                [
                    f"{score:.1f}" if score >= 0 else "",
                    lb,
                    region,
                    rel,
                ]
            )
    print(f"\nWrote {len(rows)} rows to {csv_path}")
    print(f"Total time: {elapsed:.1f}s ({elapsed / max(len(paths), 1):.2f}s per image)")

    sharp_n = sum(1 for _, _, lb, _ in rows if lb == "sharp")
    blurry_n = sum(1 for _, _, lb, _ in rows if lb == "blurry")
    by_region: dict[str, int] = {}
    for _, _, _, reg in rows:
        if reg in ("exif", "center", "full"):
            by_region[reg] = by_region.get(reg, 0) + 1
    print(f"\n--- Summary ---\n  sharp:  {sharp_n}\n  blurry: {blurry_n}")
    print(f"  regions: {by_region}")

    print("\n--- Lowest 10 scores ---")
    for score, rel, lb, region in rows[:10]:
        sc = f"{score:8.1f}" if score >= 0 else "     n/a"
        print(f"  {sc}  {lb:6s}  {region:8s}  {rel}")

    print("\n--- Highest 10 scores ---")
    for score, rel, lb, region in [r for r in rows if r[0] >= 0][-10:]:
        print(f"  {score:8.1f}  {lb:6s}  {region:8s}  {rel}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
