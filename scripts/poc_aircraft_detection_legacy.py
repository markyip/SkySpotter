from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from skimage.measure import label, regionprops
from transformers import ViTForImageClassification, ViTImageProcessor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from exif_subject_area import pixmap_ltwh_focus_hint  # noqa: E402
from semantic_search import _load_index_source_image  # noqa: E402


def _numpy_version_tuple() -> tuple[int, int, int]:
    raw = np.__version__.split(".")
    nums: list[int] = []
    for part in raw[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        nums.append(int(digits) if digits else 0)
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2])


def _iter_images(root: Path):
    exts = {".arw", ".jpg", ".jpeg", ".png", ".dng", ".nef", ".cr2", ".cr3", ".raf", ".orf", ".rw2", ".tif", ".tiff", ".bmp", ".webp"}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


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
    allow_fallback_bg: bool = False,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    pipeline_dir = output_dir / "pipeline_images"
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "top3_detection_scores.csv"

    print(f"Loading legacy checkpoint model from {model_dir}...")
    processor = ViTImageProcessor.from_pretrained(str(model_dir))
    model = ViTForImageClassification.from_pretrained(str(model_dir))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f"Device: {device}")

    use_legacy_rembg = True
    session = None
    rembg_remove = None
    remover_fallback = None

    np_ver = _numpy_version_tuple()
    if np_ver >= (2, 4, 0) and not allow_fallback_bg:
        raise RuntimeError(
            "NumPy >= 2.4 detected; rembg dependency (numba) is incompatible in this env. "
            "Please run inside a pixi environment with numpy<2.4, e.g.:\n"
            "  pixi install\n"
            "  pixi run python scripts/poc_aircraft_detection_legacy.py "
            '--input-dir "D:\\Development\\F-35" --output-dir "D:\\Development\\SkySpotter\\poc_f35_output_legacy_pixi"'
        )

    try:
        from rembg import new_session, remove as _rembg_remove

        print("Initializing rembg session: isnet-general-use")
        session = new_session("isnet-general-use")
        rembg_remove = _rembg_remove
    except Exception as e:
        if not allow_fallback_bg:
            raise RuntimeError(
                "rembg(isnet-general-use) initialization failed and fallback is disabled.\n"
                f"Original error: {e}\n"
                "Please ensure pixi env is synced (`pixi install`) and rerun with `pixi run ...`.\n"
                "If you intentionally want fallback, add --allow-fallback-bg."
            ) from e
        use_legacy_rembg = False
        print(f"[WARN] rembg(isnet-general-use) unavailable: {e}")
        from background_removal import get_background_remover

        remover_fallback = get_background_remover()
        print("[WARN] Falling back to background_removal.py pipeline")

    files = list(_iter_images(input_dir))
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
                # Load
                img = _load_index_source_image(str(fp), max_size=4096).convert("RGB")
                focus = _focus_point(fp, img.width, img.height)

                # BG removal (legacy rembg path, fallback if unavailable in env)
                if use_legacy_rembg and rembg_remove is not None and session is not None:
                    img_nobg = rembg_remove(img, session=session, alpha_matting=False)
                else:
                    bg = remover_fallback.remove_background(img)
                    # Convert fallback RGB output to RGBA mask-compatible image.
                    alpha_full = Image.new("L", bg.size, 255)
                    img_nobg = bg.convert("RGBA")
                    img_nobg.putalpha(alpha_full)

                # Connected components on alpha
                alpha = np.array(img_nobg.split()[-1])
                binary = alpha > 20
                labeled = label(binary)
                props = regionprops(labeled)
                if not props:
                    row[1] = "empty_mask"
                    row[-1] = "No object detected after background removal"
                    writer.writerow(row)
                    f.flush()
                    continue

                target_label = None
                if focus:
                    cx, cy = focus
                    for p in props:
                        minr, minc, maxr, maxc = p.bbox
                        if minc <= cx <= maxc and minr <= cy <= maxr:
                            target_label = p.label
                            break
                if target_label is None:
                    target_label = max(props, key=lambda p: p.area).label

                # Isolate selected blob
                blob_mask = labeled == target_label
                new_alpha = np.where(blob_mask, alpha, 0).astype(np.uint8)
                final_img = img_nobg.copy()
                final_img.putalpha(Image.fromarray(new_alpha))

                bbox = Image.fromarray(new_alpha).getbbox()
                if not bbox:
                    row[1] = "empty_blob"
                    writer.writerow(row)
                    f.flush()
                    continue

                cropped = final_img.crop(bbox)
                w, h = cropped.size
                cropped.save(out_img)

                if w < min_width or h < min_height:
                    row[1] = f"too_small({w}x{h})"
                    writer.writerow(row)
                    f.flush()
                    continue

                # White background composite
                bg = Image.new("RGB", cropped.size, (255, 255, 255))
                bg.paste(cropped, mask=cropped.split()[-1])

                inputs = processor(images=bg, return_tensors="pt").to(device)
                with torch.no_grad():
                    outputs = model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
                top3_prob, top3_idx = torch.topk(probs, 3)

                row[1] = "focused_blob" if focus else "largest_blob"
                if not use_legacy_rembg:
                    row[1] += "_fallback_bg"
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
    parser = argparse.ArgumentParser(description="Legacy PoC aircraft detection (isnet focus-blob pipeline).")
    parser.add_argument("--input-dir", default=r"D:\Development\F-35")
    parser.add_argument("--output-dir", default=r"D:\Development\SkySpotter\poc_f35_output_legacy")
    parser.add_argument("--model-dir", default=r"D:\Development\SkySpotter\aviation_model_processed")
    parser.add_argument("--min-width", type=int, default=350)
    parser.add_argument("--min-height", type=int, default=350)
    parser.add_argument("--max-images", type=int, default=0)
    parser.add_argument(
        "--allow-fallback-bg",
        action="store_true",
        help="Allow fallback to background_removal.py if rembg is unavailable (disabled by default).",
    )
    args = parser.parse_args()

    run(
        Path(args.input_dir),
        Path(args.output_dir),
        Path(args.model_dir),
        min_width=args.min_width,
        min_height=args.min_height,
        max_images=args.max_images,
        allow_fallback_bg=args.allow_fallback_bg,
    )


if __name__ == "__main__":
    main()
