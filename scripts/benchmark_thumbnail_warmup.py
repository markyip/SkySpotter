"""Compare aircraft indexing with and without thumbnail warm-up.

Measures whether warm-up reduces total wall time or only front-loads RAW decode.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from raw_file_extensions import RAW_FILE_EXTENSIONS  # noqa: E402

IMAGE_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    *{f".{ext}" for ext in RAW_FILE_EXTENSIONS},
}


def iter_images(folder: Path) -> list[Path]:
    files = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name.startswith("._"):
            continue
        if p.suffix.lower() in IMAGE_EXTS:
            files.append(p)
    return files


def invalidate_thumbnails(paths: list[str]) -> None:
    from image_cache import get_image_cache

    cache = get_image_cache()
    for p in paths:
        try:
            cache.invalidate_file(p)
        except Exception:
            pass


def count_cached(paths: list[str]) -> int:
    from image_cache import get_image_cache

    cache = get_image_cache()
    return sum(1 for p in paths if cache.get_thumbnail(p) is not None)


def bench_load_only(paths: list[str], max_size: int) -> dict:
    from semantic_search import _load_index_source_image

    per: list[float] = []
    t0 = time.perf_counter()
    for p in paths:
        t1 = time.perf_counter()
        _load_index_source_image(p, max_size=max_size)
        per.append(time.perf_counter() - t1)
    return {
        "total_s": time.perf_counter() - t0,
        "mean_s": statistics.mean(per) if per else 0.0,
        "median_s": statistics.median(per) if per else 0.0,
    }


def bench_warm(paths: list[str]) -> dict:
    from semantic_search import SemanticImageIndex

    index = SemanticImageIndex()
    t0 = time.perf_counter()
    warmed = index._warm_thumbnail_cache_for_aircraft(paths, None)
    return {
        "total_s": time.perf_counter() - t0,
        "warmed": warmed,
        "cached_after": count_cached(paths),
    }


def bench_classify_parallel(paths: list[str], max_size: int, workers: int) -> dict:
    from semantic_search import MilitaryAircraftClassifier, _thread_local_aircraft_classifier

    per: list[float] = []

    def _one(fp: str) -> None:
        t1 = time.perf_counter()
        clf = _thread_local_aircraft_classifier()
        clf.classify(fp, max_source_size=max_size)
        per.append(time.perf_counter() - t1)

    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(_one, paths))
    return {
        "total_s": time.perf_counter() - t0,
        "mean_s": statistics.mean(per) if per else 0.0,
        "median_s": statistics.median(per) if per else 0.0,
        "workers": workers,
    }


def run_scenario(
    name: str,
    paths: list[str],
    *,
    max_size: int,
    workers: int,
    use_warm: bool,
    clear_cache: bool,
) -> dict:
    if clear_cache:
        invalidate_thumbnails(paths)

    cached_before = count_cached(paths)
    warm_stats = None
    t0 = time.perf_counter()
    if use_warm:
        warm_stats = bench_warm(paths)
    classify_stats = bench_classify_parallel(paths, max_size, workers)
    total = time.perf_counter() - t0
    return {
        "scenario": name,
        "use_warm": use_warm,
        "cached_before": cached_before,
        "cached_after_warm": count_cached(paths) if use_warm else cached_before,
        "warm": warm_stats,
        "classify": classify_stats,
        "wall_total_s": total,
    }


def main() -> int:
    os.environ.setdefault("PYTHONUTF8", "1")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_dir",
        type=Path,
        nargs="?",
        default=Path(r"K:\Photos\23092025 Mach Loop"),
    )
    parser.add_argument("--max-images", type=int, default=40)
    parser.add_argument(
        "--max-source-size",
        type=int,
        default=0,
        help="0 = use _classifier_index_max_size()",
    )
    parser.add_argument("--workers", type=int, default=0, help="0 = auto")
    parser.add_argument(
        "--skip-classify",
        action="store_true",
        help="Only compare load-only cold vs warm+cached load",
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        print(f"Not a directory: {args.input_dir}", file=sys.stderr)
        return 1

    files = iter_images(args.input_dir)
    if args.max_images > 0:
        files = files[: args.max_images]
    if not files:
        print(f"No images in {args.input_dir}", file=sys.stderr)
        return 1

    paths = [str(p) for p in files]

    from semantic_search import SemanticImageIndex, _classifier_index_max_size

    max_size = args.max_source_size or _classifier_index_max_size()
    workers = args.workers or SemanticImageIndex._aircraft_classify_worker_count()

    print(f"Dataset: {args.input_dir} ({len(paths)} images)")
    print(f"max_source_size={max_size} workers={workers}")
    print()

    if args.skip_classify:
        invalidate_thumbnails(paths)
        cold = bench_load_only(paths, max_size)
        warm = bench_warm(paths)
        hot = bench_load_only(paths, max_size)
        print("=== Load-only (thumbnail decode path) ===")
        print(f"cold cache:  total={cold['total_s']:.2f}s mean={cold['mean_s']:.3f}s")
        print(f"warm pass:   total={warm['total_s']:.2f}s warmed={warm['warmed']}")
        print(f"hot cache:   total={hot['total_s']:.2f}s mean={hot['mean_s']:.3f}s")
        print(
            f"net vs cold: warm+hot={warm['total_s'] + hot['total_s']:.2f}s "
            f"(delta {(warm['total_s'] + hot['total_s']) - cold['total_s']:+.2f}s)"
        )
        return 0

    no_warm = run_scenario(
        "no-warm",
        paths,
        max_size=max_size,
        workers=workers,
        use_warm=False,
        clear_cache=True,
    )
    with_warm = run_scenario(
        "with-warm",
        paths,
        max_size=max_size,
        workers=workers,
        use_warm=True,
        clear_cache=True,
    )

    def _print_row(r: dict) -> None:
        c = r["classify"]
        w = r["warm"]
        warm_s = w["total_s"] if w else 0.0
        print(
            f"{r['scenario']:10}  wall={r['wall_total_s']:7.2f}s  "
            f"warm={warm_s:6.2f}s  classify={c['total_s']:7.2f}s  "
            f"mean/img={c['mean_s']:.3f}s  cached={r['cached_after_warm']}/{len(paths)}"
        )

    print("=== Full classify pipeline (parallel, cache cleared each run) ===")
    _print_row(no_warm)
    _print_row(with_warm)
    delta = with_warm["wall_total_s"] - no_warm["wall_total_s"]
    pct = (delta / no_warm["wall_total_s"] * 100.0) if no_warm["wall_total_s"] else 0.0
    print()
    print(f"with-warm vs no-warm: {delta:+.2f}s ({pct:+.1f}%)")
    if delta > 1.0:
        print("→ Warm-up likely front-loads work (similar total, slower to finish).")
    elif delta < -1.0:
        print("→ Warm-up reduces total time (cache + parallel I/O helps).")
    else:
        print("→ Roughly neutral; warm mainly batches decode before classify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
