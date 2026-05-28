"""Compare PyTorch vs DirectML ONNX aircraft classifier throughput on a folder."""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def iter_images(folder: Path) -> list[Path]:
    files = []
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            files.append(p)
    return files


def run_mode(
    mode: str,
    files: list[Path],
    *,
    prefer_dml: bool,
    max_source_size: int,
) -> dict:
    os.environ["SkySpotter_PREFER_DIRECTML"] = "1" if prefer_dml else "0"
    os.environ.pop("SkySpotter_CLASSIFIER_DEVICE", None)
    os.environ["SkySpotter_INDEX_MAX_SIZE"] = str(max_source_size)

    # Reload provider helpers so env is picked up cleanly.
    for mod in ("onnxruntime_providers", "semantic_search"):
        if mod in sys.modules:
            del sys.modules[mod]

    from onnxruntime_providers import dml_available, prefer_directml_classifier
    from semantic_search import MilitaryAircraftClassifier

    assert prefer_directml_classifier() == prefer_dml or (
        prefer_dml and not dml_available()
    ), f"mode={mode} prefer_dml={prefer_dml} actual={prefer_directml_classifier()}"

    clf = MilitaryAircraftClassifier()
    per_image: list[float] = []
    labels: list[str] = []
    t0 = time.perf_counter()
    for i, fp in enumerate(files, 1):
        t_img = time.perf_counter()
        label = clf.classify(str(fp), max_source_size=max_source_size)
        elapsed = time.perf_counter() - t_img
        per_image.append(elapsed)
        labels.append(label or "")
        print(f"  [{mode}] {i}/{len(files)} {fp.name}: {elapsed:.2f}s -> {label or '(none)'}")
    total = time.perf_counter() - t0
    return {
        "mode": mode,
        "prefer_dml": prefer_dml,
        "dml_available": dml_available(),
        "n": len(files),
        "total_s": total,
        "mean_s": statistics.mean(per_image) if per_image else 0.0,
        "median_s": statistics.median(per_image) if per_image else 0.0,
        "first_s": per_image[0] if per_image else 0.0,
        "rest_mean_s": statistics.mean(per_image[1:]) if len(per_image) > 1 else 0.0,
        "labels_non_empty": sum(1 for x in labels if x),
    }


def main() -> int:
    # Avoid cp950 console errors during torch.onnx export on Windows.
    os.environ.setdefault("PYTHONUTF8", "1")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_dir",
        type=Path,
        nargs="?",
        default=Path(r"D:\Development\Test Image set"),
    )
    parser.add_argument("--max-images", type=int, default=0)
    parser.add_argument(
        "--max-source-size",
        type=int,
        default=int(os.environ.get("SkySpotter_INDEX_MAX_SIZE", "1280")),
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

    print(f"Dataset: {args.input_dir} ({len(files)} images)")
    print(f"max_source_size={args.max_source_size}")
    print()

    print("=== PyTorch path (SkySpotter_PREFER_DIRECTML=0) ===")
    pytorch = run_mode(
        "pytorch",
        files,
        prefer_dml=False,
        max_source_size=args.max_source_size,
    )
    print()

    print("=== DirectML ONNX path (SkySpotter_PREFER_DIRECTML=1) ===")
    dml = run_mode(
        "directml",
        files,
        prefer_dml=True,
        max_source_size=args.max_source_size,
    )
    print()

    speedup = pytorch["total_s"] / dml["total_s"] if dml["total_s"] > 0 else 0.0
    print("=== Summary ===")
    for r in (pytorch, dml):
        print(
            f"{r['mode']:10} total={r['total_s']:.1f}s  "
            f"mean={r['mean_s']:.2f}s/img  median={r['median_s']:.2f}s  "
            f"first={r['first_s']:.2f}s  rest_mean={r['rest_mean_s']:.2f}s  "
            f"labeled={r['labels_non_empty']}/{r['n']}"
        )
    print(f"DirectML speedup (total time): {speedup:.2f}x")
    if pytorch["labels_non_empty"] != dml["labels_non_empty"]:
        print(
            "NOTE: label counts differ between paths — compare timings only if labels match."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
