#!/usr/bin/env python3
"""Compare Laplacian blur POC at two max thumbnail sizes (timing + labels)."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from poc_blur_detect import IMAGE_EXTS, iter_images  # noqa: E402
from poc_cv2 import ensure_cv2  # noqa: E402


@dataclass
class RunResult:
    max_size: int
    elapsed: float
    n_images: int
    scores: dict[str, float]  # rel path -> score
    ratings: dict[str, str]  # rel path -> sharp|blurry
    regions: dict[str, str]


def run_folder(folder: str, max_size: int, limit: int = 0) -> RunResult:
    os.environ["SkySpotter_BLUR_MAX_SIZE"] = str(max_size)

    from blur_score import (
        blur_rank_blurry_count,
        compute_blur_score_for_index,
    )
    from semantic_search import _load_index_source_image

    paths = list(iter_images(folder))
    if limit > 0:
        paths = paths[:limit]

    scores: dict[str, float] = {}
    regions: dict[str, str] = {}
    t0 = time.perf_counter()
    for path in paths:
        rel = os.path.relpath(path, folder)
        try:
            rgb = _load_index_source_image(path, max_size=max_size)
            score, region = compute_blur_score_for_index(path, rgb)
            if score is not None:
                scores[rel] = float(score)
                regions[rel] = region
        except Exception:
            pass
    elapsed = time.perf_counter() - t0

    ordered = sorted(scores.items(), key=lambda x: x[1])
    n_blurry = blur_rank_blurry_count(len(ordered))
    blurry_set = {rel for rel, _ in ordered[:n_blurry]}
    ratings = {
        rel: ("blurry" if rel in blurry_set else "sharp") for rel in scores
    }
    return RunResult(
        max_size=max_size,
        elapsed=elapsed,
        n_images=len(paths),
        scores=scores,
        ratings=ratings,
        regions=regions,
    )


def spearman_like_rank_delta(a: dict[str, float], b: dict[str, float]) -> int:
    """Count pairs where relative order differs (simple disagreement count)."""
    common = sorted(set(a) & set(b))
    disagreements = 0
    for i, p1 in enumerate(common):
        for p2 in common[i + 1 :]:
            s1 = a[p1] - a[p2]
            s2 = b[p1] - b[p2]
            if s1 == 0 and s2 == 0:
                continue
            if (s1 > 0) != (s2 > 0):
                disagreements += 1
    return disagreements


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare blur POC at two max sizes")
    parser.add_argument("folder", help="Image folder (recursive)")
    parser.add_argument(
        "--sizes",
        default="1280,1920",
        help="Comma-separated max side lengths (default: 1280,1920)",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max files (0=all)")
    args = parser.parse_args()
    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1

    sizes = [int(s.strip()) for s in args.sizes.split(",") if s.strip()]
    if len(sizes) != 2:
        print("Provide exactly two sizes, e.g. --sizes 1280,1920", file=sys.stderr)
        return 1

    print(f"Folder: {folder}\n")
    ensure_cv2()
    results: list[RunResult] = []
    for sz in sizes:
        print(f"Running max_size={sz} ...", flush=True)
        r = run_folder(folder, sz, limit=args.limit)
        results.append(r)
        per = r.elapsed / max(r.n_images, 1)
        print(f"  done: {r.elapsed:.2f}s total, {per:.3f}s/image, scored={len(r.scores)}\n")

    a, b = results[0], results[1]
    common = sorted(set(a.scores) & set(b.scores))
    if not common:
        print("No common scored images.")
        return 1

    label_flip = [rel for rel in common if a.ratings[rel] != b.ratings[rel]]
    score_deltas = [(rel, b.scores[rel] - a.scores[rel]) for rel in common]
    score_deltas.sort(key=lambda x: abs(x[1]), reverse=True)

    import statistics

    deltas = [b.scores[rel] - a.scores[rel] for rel in common]
    ratios = [
        b.scores[rel] / a.scores[rel] if a.scores[rel] > 1e-6 else float("nan")
        for rel in common
    ]
    ratios = [r for r in ratios if r == r]

    print("=" * 60)
    print("TIMING")
    print("=" * 60)
    for r in results:
        print(
            f"  max_side {r.max_size}: {r.elapsed:.2f}s total, "
            f"{r.elapsed / max(r.n_images, 1):.3f}s/image"
        )
    if a.elapsed > 0:
        print(f"  ratio ({b.max_size}/{a.max_size} time): {b.elapsed / a.elapsed:.2f}x")

    print("\n" + "=" * 60)
    print("LABELS (bottom 20% = blurry)")
    print("=" * 60)
    for r in results:
        sharp = sum(1 for v in r.ratings.values() if v == "sharp")
        blurry = sum(1 for v in r.ratings.values() if v == "blurry")
        print(f"  max_side {r.max_size}: sharp={sharp}, blurry={blurry}")
    print(f"  rating flips ({a.max_size} vs {b.max_size}): {len(label_flip)} / {len(common)}")

    print("\n" + "=" * 60)
    print("SCORES")
    print("=" * 60)
    print(f"  images compared: {len(common)}")
    print(f"  mean delta ({b.max_size}-{a.max_size}): {statistics.mean(deltas):+.1f}")
    print(f"  median delta: {statistics.median(deltas):+.1f}")
    if ratios:
        print(f"  median score ratio ({b.max_size}/{a.max_size}): {statistics.median(ratios):.3f}")
    print(f"  max |delta|: {max(abs(d) for d in deltas):.1f}")
    print(f"  pairwise rank disagreements: {spearman_like_rank_delta(a.scores, b.scores)}")

    if label_flip:
        print("\n--- Rating flips (sharp <-> blurry) ---")
        for rel in sorted(label_flip):
            print(
                f"  {a.ratings[rel]:6s}@{a.max_size} -> {b.ratings[rel]:6s}@{b.max_size}  "
                f"scores {a.scores[rel]:.1f} -> {b.scores[rel]:.1f}  {rel}"
            )

    print(f"\n--- Largest |score delta| (top 15) ---")
    for rel, d in score_deltas[:15]:
        print(
            f"  delta {d:+8.1f}  {a.scores[rel]:8.1f} -> {b.scores[rel]:8.1f}  "
            f"{a.ratings[rel]:6s}/{b.ratings[rel]:6s}  {rel}"
        )

    blurry_a = {rel for rel, lb in a.ratings.items() if lb == "blurry"}
    blurry_b = {rel for rel, lb in b.ratings.items() if lb == "blurry"}
    only_a = sorted(blurry_a - blurry_b)
    only_b = sorted(blurry_b - blurry_a)
    if only_a or only_b:
        print(f"\n--- Blurry set diff (20% rank) ---")
        if only_a:
            print(f"  blurry only @ {a.max_size} ({len(only_a)}):")
            for rel in only_a[:10]:
                print(f"    {a.scores[rel]:.1f}  {rel}")
        if only_b:
            print(f"  blurry only @ {b.max_size} ({len(only_b)}):")
            for rel in only_b[:10]:
                print(f"    {b.scores[rel]:.1f}  {rel}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
