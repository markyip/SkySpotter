#!/usr/bin/env python3
"""Compare blur POC: baseline (no bbox) vs subject_rect on original RGB."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from poc_blur_detect import iter_images  # noqa: E402
from poc_cv2 import ensure_cv2  # noqa: E402


@dataclass
class ModeResult:
    name: str
    elapsed: float
    n_images: int
    scores: dict[str, float] = field(default_factory=dict)
    ratings: dict[str, str] = field(default_factory=dict)
    regions: dict[str, str] = field(default_factory=dict)


def _rate_scores(scores: dict[str, float]) -> dict[str, str]:
    from blur_score import blur_rank_blurry_count

    ordered = sorted(scores.items(), key=lambda x: x[1])
    n_blurry = blur_rank_blurry_count(len(ordered))
    blurry_set = {rel for rel, _ in ordered[:n_blurry]}
    return {rel: ("blurry" if rel in blurry_set else "sharp") for rel in scores}


def run_baseline(folder: str, paths: list[str], max_size: int) -> ModeResult:
    os.environ["SkySpotter_BLUR_MAX_SIZE"] = str(max_size)
    from blur_score import compute_blur_score_for_index
    from semantic_search import _load_index_source_image

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
    return ModeResult(
        name=f"baseline@{max_size}",
        elapsed=elapsed,
        n_images=len(paths),
        scores=scores,
        ratings=_rate_scores(scores),
        regions=regions,
    )


def run_subject_rect(folder: str, paths: list[str], max_size: int) -> ModeResult:
    os.environ["SkySpotter_BLUR_MAX_SIZE"] = str(max_size)
    from blur_score import compute_blur_score_for_index
    from semantic_search import MilitaryAircraftClassifier

    clf = MilitaryAircraftClassifier()
    scores: dict[str, float] = {}
    regions: dict[str, str] = {}
    t0 = time.perf_counter()
    for path in paths:
        rel = os.path.relpath(path, folder)
        try:
            src, rgba, _crop = clf.prepare_subject_pipeline(path, max_size)
            if src is None:
                continue
            score, region = compute_blur_score_for_index(
                path, src, rgba_for_bbox=rgba
            )
            if score is not None:
                scores[rel] = float(score)
                regions[rel] = region
        except Exception:
            pass
    elapsed = time.perf_counter() - t0
    return ModeResult(
        name=f"subject_rect@{max_size}",
        elapsed=elapsed,
        n_images=len(paths),
        scores=scores,
        ratings=_rate_scores(scores),
        regions=regions,
    )


def print_comparison(a: ModeResult, b: ModeResult) -> None:
    common = sorted(set(a.scores) & set(b.scores))
    print("=" * 60)
    print("TIMING")
    print("=" * 60)
    for r in (a, b):
        print(
            f"  {r.name}: {r.elapsed:.2f}s total, "
            f"{r.elapsed / max(r.n_images, 1):.3f}s/image, scored={len(r.scores)}"
        )
    if a.elapsed > 0:
        print(f"  time ratio ({b.name} / {a.name}): {b.elapsed / a.elapsed:.2f}x")

    by_reg_a: dict[str, int] = {}
    by_reg_b: dict[str, int] = {}
    for reg in a.regions.values():
        by_reg_a[reg] = by_reg_a.get(reg, 0) + 1
    for reg in b.regions.values():
        by_reg_b[reg] = by_reg_b.get(reg, 0) + 1

    print("\n" + "=" * 60)
    print("REGIONS USED")
    print("=" * 60)
    print(f"  {a.name}: {by_reg_a}")
    print(f"  {b.name}: {by_reg_b}")

    print("\n" + "=" * 60)
    print("LABELS (bottom 20% = blurry)")
    print("=" * 60)
    for r in (a, b):
        sharp = sum(1 for v in r.ratings.values() if v == "sharp")
        blurry = sum(1 for v in r.ratings.values() if v == "blurry")
        print(f"  {r.name}: sharp={sharp}, blurry={blurry}")

    if not common:
        return

    flips = [rel for rel in common if a.ratings[rel] != b.ratings[rel]]
    print(f"  rating flips: {len(flips)} / {len(common)}")

    import statistics

    deltas = [b.scores[rel] - a.scores[rel] for rel in common]
    print("\n" + "=" * 60)
    print("SCORE DELTA (subject_rect - baseline)")
    print("=" * 60)
    print(f"  mean: {statistics.mean(deltas):+.1f}")
    print(f"  median: {statistics.median(deltas):+.1f}")
    print(f"  max |delta|: {max(abs(d) for d in deltas):.1f}")

    if flips:
        print("\n--- Rating flips ---")
        for rel in sorted(flips):
            print(
                f"  {a.ratings[rel]:6s} {a.scores[rel]:7.1f} [{a.regions.get(rel,'?')}] -> "
                f"{b.ratings[rel]:6s} {b.scores[rel]:7.1f} [{b.regions.get(rel,'?')}]  {rel}"
            )

    score_deltas = sorted(
        [(rel, b.scores[rel] - a.scores[rel]) for rel in common],
        key=lambda x: abs(x[1]),
        reverse=True,
    )
    print("\n--- Largest |score delta| (top 12) ---")
    for rel, d in score_deltas[:12]:
        print(
            f"  {d:+8.1f}  {a.scores[rel]:8.1f} -> {b.scores[rel]:8.1f}  "
            f"{a.ratings[rel]}/{b.ratings[rel]}  {rel}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline vs subject_rect blur POC")
    parser.add_argument("folder", help="Image folder")
    parser.add_argument("--max-size", type=int, default=1280, help="Thumbnail max side")
    parser.add_argument("--limit", type=int, default=0, help="Max files (0=all)")
    args = parser.parse_args()
    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1

    paths = list(iter_images(folder))
    if args.limit > 0:
        paths = paths[: args.limit]

    print(f"Folder: {folder} ({len(paths)} images, max_side={args.max_size})\n")
    ensure_cv2()

    print("Running baseline (EXIF -> center -> full, no subject bbox)...", flush=True)
    baseline = run_baseline(folder, paths, args.max_size)
    reg_a: dict[str, int] = {}
    for reg in baseline.regions.values():
        reg_a[reg] = reg_a.get(reg, 0) + 1
    print(f"  done: {baseline.elapsed:.1f}s, regions={reg_a}\n", flush=True)

    print("Running subject_rect (EXIF -> rembg bbox on original RGB -> center -> full)...", flush=True)
    subject = run_subject_rect(folder, paths, args.max_size)
    reg_b: dict[str, int] = {}
    for reg in subject.regions.values():
        reg_b[reg] = reg_b.get(reg, 0) + 1
    print(f"  done: {subject.elapsed:.1f}s, regions={reg_b}\n", flush=True)

    print_comparison(baseline, subject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
