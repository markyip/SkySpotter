"""Optional PoC: exercise the in-app MilitaryAircraftClassifier (gallery path).

For verifying a checkpoint you just trained, use batch_test_classifier.py or
scripts/launchers/verify_model.* instead (tests customized_model/ on testing_data/).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "testing_data" / "test_images"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "testing_data" / "poc_gallery_output"
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _iter_images(root: Path) -> Iterable[Path]:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".arw", ".dng", ".nef", ".cr2", ".cr3", ".raf", ".orf", ".rw2"}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def _topk(labels: list[str], probs: np.ndarray, k: int = 3) -> list[tuple[str, float]]:
    arr = np.asarray(probs, dtype=np.float32).reshape(-1)
    if arr.size == 0:
        return []
    k = max(1, min(k, arr.size))
    idxs = np.argsort(arr)[::-1][:k]
    out: list[tuple[str, float]] = []
    for idx in idxs:
        label = labels[int(idx)] if int(idx) < len(labels) else f"class_{int(idx)}"
        out.append((label, float(arr[int(idx)])))
    return out


def _safe_name(p: Path) -> str:
    # Keep deterministic file names for outputs.
    return p.name.replace(" ", "_")


def _ensure_classifier_session(classifier) -> None:
    if getattr(classifier, "_session", None) is not None:
        return
    import onnxruntime as ort

    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    preferred = [
        "CoreMLExecutionProvider",
        "CUDAExecutionProvider",
        "TensorrtExecutionProvider",
        "DmlExecutionProvider",
        "AzureExecutionProvider",
        "CPUExecutionProvider",
    ]
    available = ort.get_available_providers()
    selected = [p for p in preferred if p in available] or ["CPUExecutionProvider"]
    classifier._session = ort.InferenceSession(
        classifier.onnx_path, sess_options=so, providers=selected
    )
    try:
        shape = list(classifier._session.get_inputs()[0].shape)
        h_dim = shape[2] if len(shape) > 2 else None
        w_dim = shape[3] if len(shape) > 3 else None
        if isinstance(h_dim, int) and isinstance(w_dim, int) and h_dim == w_dim:
            classifier._input_size = int(h_dim)
        else:
            classifier._input_size = 384
    except Exception:
        classifier._input_size = 384


def run(input_dir: Path, output_dir: Path, max_images: int = 0) -> None:
    from semantic_search import MilitaryAircraftClassifier, _load_index_source_image
    from exif_subject_area import pixmap_ltwh_focus_hint
    from background_removal import get_background_remover

    output_dir.mkdir(parents=True, exist_ok=True)
    pipeline_dir = output_dir / "pipeline_images"
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "top3_detection_scores.csv"

    classifier = MilitaryAircraftClassifier()
    classifier._ensure_model()
    _ensure_classifier_session(classifier)
    remover = get_background_remover()

    rows: list[dict[str, object]] = []
    files = list(_iter_images(input_dir))
    if max_images and max_images > 0:
        files = files[:max_images]
    if not files:
        print(f"No supported images found in {input_dir}")
        return

    for i, fp in enumerate(files, start=1):
        print(f"[{i}/{len(files)}] Processing {fp.name}")
        src_im = _load_index_source_image(str(fp), max_size=2048).convert("RGB")

        # Step 1: background removal (same component used by classifier flow).
        try:
            bg_removed = remover.remove_background(src_im)
        except Exception:
            # Keep PoC robust when background remover is unavailable.
            bg_removed = src_im

        # Step 2: global prediction.
        global_label, global_conf, global_probs = classifier._predict_im(bg_removed)
        chosen_label, chosen_conf, chosen_probs = global_label, global_conf, global_probs
        chosen_crop = bg_removed
        stage = "global"

        # Step 3: focus-aware crop path (same decision rule as semantic_search.classify()).
        try:
            focus_hint = pixmap_ltwh_focus_hint(str(fp), bg_removed.width, bg_removed.height)
            if focus_hint:
                ltwh, _source = focus_hint
                cx = ltwh[0] + ltwh[2] // 2
                cy = ltwh[1] + ltwh[3] // 2
                crop_size = int(min(bg_removed.width, bg_removed.height) * 0.7)
                crop_size = max(int(getattr(classifier, "_input_size", 384) or 384), crop_size)
                left = max(0, cx - crop_size // 2)
                top = max(0, cy - crop_size // 2)
                right = min(bg_removed.width, left + crop_size)
                bottom = min(bg_removed.height, top + crop_size)
                if right - left < crop_size:
                    left = max(0, right - crop_size)
                if bottom - top < crop_size:
                    top = max(0, bottom - crop_size)
                crop_im = bg_removed.crop((left, top, right, bottom))
                crop_label, crop_conf, crop_probs = classifier._predict_im(crop_im)
                if (crop_conf > chosen_conf) or (chosen_conf < 0.45 and crop_conf > 0.35):
                    chosen_label, chosen_conf, chosen_probs = crop_label, crop_conf, crop_probs
                    chosen_crop = crop_im
                    stage = "focus_crop"
        except Exception:
            pass

        # Output pipeline image: background-removed and cropped image actually used.
        out_img = pipeline_dir / f"{fp.stem}.pipeline.png"
        chosen_crop.save(out_img)

        top3 = _topk(classifier.LABELS, chosen_probs, k=3)
        row = {
            "file_path": str(fp),
            "pipeline_image": str(out_img),
            "stage": stage,
            "top1_label": top3[0][0] if len(top3) > 0 else "",
            "top1_score": top3[0][1] if len(top3) > 0 else 0.0,
            "top2_label": top3[1][0] if len(top3) > 1 else "",
            "top2_score": top3[1][1] if len(top3) > 1 else 0.0,
            "top3_label": top3[2][0] if len(top3) > 2 else "",
            "top3_score": top3[2][1] if len(top3) > 2 else 0.0,
            "chosen_label": chosen_label,
            "chosen_conf": float(chosen_conf),
        }
        rows.append(row)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file_path",
                "pipeline_image",
                "stage",
                "top1_label",
                "top1_score",
                "top2_label",
                "top2_score",
                "top3_label",
                "top3_score",
                "chosen_label",
                "chosen_conf",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Pipeline images: {pipeline_dir}")
    print(f"Done. CSV: {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "PoC: run gallery MilitaryAircraftClassifier on a folder "
            "(app_model / in-app DirectML path). "
            "To verify customized_model/ after training, use scripts/launchers/verify_model.bat or verify_model.sh."
        )
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
        help=f"Folder of images to process (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Folder for pipeline images and CSV (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=0,
        help="Optional cap for quick PoC runs (0 = all images).",
    )
    args = parser.parse_args()

    run(Path(args.input_dir), Path(args.output_dir), max_images=args.max_images)


if __name__ == "__main__":
    main()
