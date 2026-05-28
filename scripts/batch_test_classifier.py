"""Verify a user-trained ViT checkpoint on sample images (PoC / batch test).

Default layout:
  - Input:  testing_data/test_images/
  - Model:  customized_model/  (after scripts/launchers/train_model.*)
  - Output: testing_data/test_output/

Run: scripts/launchers/verify_model.bat (Windows) or scripts/launchers/verify_model.sh (macOS).
Same rembg-style preprocessing as training. Works for any subject classes you trained.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import torch
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classifier_preprocess import (
    composite_white_background,
    init_fallback_remover,
    init_rembg_session,
    isolate_subject_rgba,
    iter_image_files,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "testing_data" / "test_images"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "testing_data" / "test_output"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "customized_model"
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from exif_subject_area import pixmap_ltwh_focus_hint  # noqa: E402
from semantic_search import _load_index_source_image  # noqa: E402


def _focus_point(path: Path, width: int, height: int):
    hint = pixmap_ltwh_focus_hint(str(path), width, height)
    if not hint:
        return None
    ltwh, _ = hint
    l, t, w, h = ltwh
    return (l + w / 2.0, t + h / 2.0)


def run(
    input_dir: Path,
    output_dir: Path,
    model_dir: Path,
    min_width: int = 350,
    min_height: int = 350,
    max_images: int = 0,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    pipeline_dir = output_dir / "pipeline_images"
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "top3_detection_scores.csv"

    if not model_dir.is_dir() or not (model_dir / "model.safetensors").is_file():
        raise FileNotFoundError(
            f"Checkpoint not found at {model_dir}. "
            "Train a model first (outputs default to customized_model/) or pass --model-dir."
        )

    print(f"Loading checkpoint from {model_dir}...")
    processor = ViTImageProcessor.from_pretrained(str(model_dir))
    model = ViTForImageClassification.from_pretrained(str(model_dir))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f"Device: {device}")

    session = None
    rembg_remove = None
    remover_fallback = None
    try:
        print("Initializing rembg session: isnet-general-use")
        session, rembg_remove = init_rembg_session()
    except Exception as e:
        print(f"[WARN] rembg unavailable ({e}); using fallback background removal.")
        remover_fallback = init_fallback_remover()

    files = list(iter_image_files(input_dir))
    if max_images and max_images > 0:
        files = files[:max_images]
    print(f"Found {len(files)} files in {input_dir}")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "file_path",
                "status",
                "pipeline_image",
                "top1_label",
                "top1_score",
                "top2_label",
                "top2_score",
                "top3_label",
                "top3_score",
                "error",
            ]
        )

        for idx, fp in enumerate(files, start=1):
            print(f"[{idx}/{len(files)}] Processing {fp.name}")
            out_img = pipeline_dir / f"{fp.stem}.pipeline.png"
            row = [str(fp), "", str(out_img), "", "", "", "", "", "", ""]
            try:
                img = _load_index_source_image(str(fp), max_size=4096).convert("RGB")
                focus = _focus_point(fp, img.width, img.height)

                cropped, status = isolate_subject_rgba(
                    img,
                    rembg_remove=rembg_remove,
                    session=session,
                    focus_point=focus,
                    remover_fallback=remover_fallback,
                )
                if cropped is None:
                    row[1] = status
                    row[-1] = "No usable subject after background removal"
                    writer.writerow(row)
                    f.flush()
                    continue

                w, h = cropped.size
                cropped.save(out_img)
                if w < min_width or h < min_height:
                    row[1] = f"too_small({w}x{h})"
                    writer.writerow(row)
                    f.flush()
                    continue

                bg = composite_white_background(cropped)
                inputs = processor(images=bg, return_tensors="pt").to(device)
                with torch.no_grad():
                    outputs = model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
                top3_prob, top3_idx = torch.topk(probs, 3)

                row[1] = status
                for i in range(3):
                    cls_idx = int(top3_idx[i].item())
                    label_name = model.config.id2label[cls_idx]
                    conf = float(top3_prob[i].item())
                    base = 3 + i * 2
                    row[base] = label_name
                    row[base + 1] = f"{conf:.6f}"
            except Exception as e:
                row[1] = "error"
                row[-1] = str(e)

            writer.writerow(row)
            f.flush()

    print(f"Done. Pipeline images: {pipeline_dir}")
    print(f"Done. CSV: {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Batch-test a trained ViT classifier: rembg subject crop, then top-3 labels. "
            "Use any classes (birds, animals, aircraft, etc.)."
        )
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
        help=f"Folder of test images (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Results folder (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--model-dir",
        default=str(DEFAULT_MODEL_DIR),
        help=f"Checkpoint directory (default: {DEFAULT_MODEL_DIR})",
    )
    parser.add_argument("--min-width", type=int, default=350)
    parser.add_argument("--min-height", type=int, default=350)
    parser.add_argument("--max-images", type=int, default=0)
    args = parser.parse_args()

    run(
        Path(args.input_dir),
        Path(args.output_dir),
        Path(args.model_dir),
        min_width=args.min_width,
        min_height=args.min_height,
        max_images=args.max_images,
    )


if __name__ == "__main__":
    main()
