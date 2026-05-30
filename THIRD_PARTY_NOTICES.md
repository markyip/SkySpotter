# Third-Party Notices

SkySpotter is distributed under the [MIT License](LICENSE) (Copyright © 2025 Mark Yip).

This file lists **third-party software, libraries, and model weights** that SkySpotter uses or may download at runtime. When you clone, build, or redistribute SkySpotter (including installers that bundle model weights), you must comply with the licenses below in addition to the MIT License.

**Not legal advice.** If you ship a product based on this repository, have counsel review your distribution (especially PyQt6 and bundled ONNX weights).

---

## Summary

| Component | Used for | License | When it applies |
| --- | --- | --- | --- |
| [SkySpotter gallery ViT](#1-default-gallery-classifier-skyspotter-military-aircraft-vit) | Aircraft labels, Magic Wand, indexing | Apache-2.0 | Default; bundled under `models/gallery-classifier/` or installer |
| [Google ViT base](#2-google-vit-base-checkpoints) | Pretrained backbone for gallery / training | Apache-2.0 | Derived checkpoints & training |
| [dima806 military aircraft ViT](#3-fallback-classifier-dima806military_aircraft_image_detection) | ONNX export / HF fallback | Apache-2.0 | If bundled checkpoint missing |
| [rembg](#4-rembg-daniel-gatis) | Background removal (classification pipeline) | MIT | Runtime dependency; downloads ONNX weights |
| [IS-Net / isnet-general-use](#5-is-net--isnet-general-use-weights) | rembg default segmentation model | Apache-2.0 | Downloaded with rembg |
| [U²-Net (u2net.onnx)](#6-u-net-u2netonnx-fallback) | Fallback background removal | Apache-2.0 (typical for U²-Net weights via rembg) | If `BackgroundRemover` fallback path runs |
| [Blur scoring](#7-blur-scoring-no-third-party-model) | `sharp` / `blurry` gallery filters | — | Laplacian heuristic only |
| [MobileCLIP2 ONNX](#8-optional-semantic-search--mobileclip) | Optional CLIP-style search | Apple AMLR (see model card) | Only if `SkySpotter_ENABLE_SEMANTIC_SEARCH=1` |
| [SigLIP ONNX](#9-optional-siglip-semantic-backend) | Optional semantic embeddings | Apache-2.0 (typical) | Legacy/opt-in semantic backend |
| [PyQt6](#10-pyqt6-gui-framework) | Application UI | GPL-3.0 | Always (GUI) |
| [ONNX Runtime](#11-onnx-runtime) | Model inference | MIT | Classifier / rembg / optional CLIP |

---

## Machine learning models

### 1. Default gallery classifier (`skyspotter-military-aircraft-vit`)

- **Location:** `models/gallery-classifier/skyspotter-military-aircraft-vit/` (or installed via `scripts/download_app_model.py`)
- **Purpose:** Military/civil aircraft type labels, Magic Wand folder sorting, `aircraft:` gallery search
- **License:** Apache License 2.0 (Hugging Face–style ViT checkpoint)
- **Provenance:** Fine-tuned by the SkySpotter project from **[`google/vit-base-patch16-384`](https://huggingface.co/google/vit-base-patch16-384)** (Apache-2.0). Input resolution 384×384; label set in `labels.txt`.
- **Redistribution:** Include a copy of the [Apache-2.0 license](https://www.apache.org/licenses/LICENSE-2.0.txt) and state that the checkpoint was modified / retrained for SkySpotter if you redistribute weights.

### 2. Google ViT base checkpoints

Used as pretraining bases for the default gallery model and training scripts:

| Model | URL | License |
| --- | --- | --- |
| `google/vit-base-patch16-384` | https://huggingface.co/google/vit-base-patch16-384 | Apache-2.0 |
| `google/vit-base-patch16-224-in21k` | https://huggingface.co/google/vit-base-patch16-224-in21k | Apache-2.0 |

**Copyright:** Google LLC (see each model’s Hugging Face model card and `config.json`).

Training entry point: `scripts/train_processed_aircraft.py` (`MODEL_ID = "google/vit-base-patch16-384"`).

### 3. Fallback classifier (`dima806/military_aircraft_image_detection`)

- **URL:** https://huggingface.co/dima806/military_aircraft_image_detection
- **Purpose:** Hugging Face fallback when exporting or downloading ONNX if no local gallery checkpoint is available (`MilitaryAircraftClassifier.HUB_REPO_ID` in `src/semantic_search.py`)
- **License:** Apache-2.0 (per model card)
- **Base model:** [`google/vit-base-patch16-224-in21k`](https://huggingface.co/google/vit-base-patch16-224-in21k)
- **Notice:** Upstream reports ~76% accuracy on its benchmark; labels and performance differ from the SkySpotter gallery checkpoint.

**Suggested attribution line:**

> Aircraft classification fallback model: [dima806/military_aircraft_image_detection](https://huggingface.co/dima806/military_aircraft_image_detection) (Apache-2.0), fine-tuned from Google ViT.

### 4. rembg (Daniel Gatis)

- **Project:** https://github.com/danielgatis/rembg  
- **PyPI:** `rembg` (see `pixi.toml`)
- **Purpose:** Removes image backgrounds before ViT subject crop (`isnet-general-use` session in `MilitaryAircraftClassifier`)
- **License:** MIT

```
MIT License

Copyright (c) 2020-present Daniel Gatis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### 5. IS-Net / `isnet-general-use` weights

- **Source:** [Dichotomous Image Segmentation (DIS)](https://github.com/xuebinqin/DIS) — IS-Net, general-use weights
- **Distribution:** Downloaded by rembg (e.g. `isnet-general-use.onnx` from rembg releases)
- **License:** Apache-2.0 (see [DIS LICENSE.md](https://github.com/xuebinqin/DIS/blob/main/LICENSE.md))
- **Redistribution:** Retain Apache-2.0 copyright and license notices if you ship these ONNX files.

### 6. U²-Net (`u2net.onnx`) fallback

- **Source:** rembg release assets — https://github.com/danielgatis/rembg/releases  
- **Code path:** `src/background_removal.py` when the rembg session is unavailable
- **License:** Weights are commonly distributed under the same terms as the [U²-Net / DIS](https://github.com/xuebinqin/DIS) project (Apache-2.0). Confirm the license on the specific release you mirror if you redistribute the file.

### 7. Blur scoring (no third-party model)

Gallery filters **`sharp`** and **`blurry`** use a **Laplacian variance** heuristic on downscaled pixels (EXIF focus ROI, central crop, or full frame). See `src/blur_score.py`. **No separate blur-detection model weights** are bundled or downloaded.

---

## Optional features (off by default)

### 8. Optional semantic search — MobileCLIP

Enabled only when `SkySpotter_ENABLE_SEMANTIC_SEARCH=1` (not the default aviation workflow).

| Asset | URL | License (per HF) |
| --- | --- | --- |
| ONNX export | [`plhery/mobileclip2-onnx`](https://huggingface.co/plhery/mobileclip2-onnx) | `apple-amlr` |
| Base | [`apple/MobileCLIP2-S2`](https://huggingface.co/apple/MobileCLIP2-S2) | See Apple model card |

Read the **Apple Machine Learning Research License** on the model card before enabling or redistributing these files.

### 9. Optional SigLIP semantic backend

| Asset | URL | License (per HF) |
| --- | --- | --- |
| ONNX | [`Xenova/siglip-base-patch16-512`](https://huggingface.co/Xenova/siglip-base-patch16-512) | Apache-2.0 (typical) |

Used only when semantic embeddings are enabled and this backend is selected in code paths that reference `SiglipSemanticSearch`.

---

## Runtime libraries (selected)

SkySpotter depends on many open-source packages via Pixi/conda-forge and PyPI. The following have **distinct license implications** for redistribution:

### 10. PyQt6 (GUI framework)

- **Package:** `PyQt6` (`pixi.toml`)
- **License:** **GNU General Public License v3.0** (GPL-3.0)
- **Vendor:** Riverbank Computing — https://www.riverbankcomputing.com/software/pyqt/
- **Note:** Distributing a **binary** of SkySpotter that links against PyQt6 may require you to comply with GPL-3.0 (source offer, license text, etc.) unless you have a **commercial PyQt license** from Riverbank. This is separate from SkySpotter’s MIT license.

### 11. ONNX Runtime

- **Packages:** `onnxruntime-directml` (Windows), ONNX Runtime used by rembg
- **License:** MIT — https://github.com/microsoft/onnxruntime/blob/main/LICENSE

### Other dependencies

A non-exhaustive list of runtime dependencies appears in `pixi.toml` (e.g. `torch`, `transformers`, `huggingface_hub`, `opencv-python-headless`, `mediapipe`, `Pillow`, `numpy`). Each package ships its own license metadata on PyPI or conda-forge. Use your environment’s license report tools (e.g. `pip-licenses`, `conda list --license`) for a complete bill of materials when preparing a release.

---

## Apache License 2.0 (reference)

Model weights marked **Apache-2.0** above are licensed under the Apache License, Version 2.0.

- Full text: https://www.apache.org/licenses/LICENSE-2.0.txt  
- How to apply: https://www.apache.org/licenses/LICENSE-2.0#apply

When redistributing Apache-2.0 weights or derivative checkpoints:

1. Include a copy of the Apache-2.0 license.  
2. Retain copyright, patent, trademark, and attribution notices from the source distribution.  
3. Include a **NOTICE** file if the upstream provides one.  
4. State **significant changes** if you modified the weights (e.g. SkySpotter fine-tune).

---

## Updates

This file is maintained for the SkySpotter open-source repository on GitHub. For release-specific changes to bundled models, see [RELEASE_NOTES.md](RELEASE_NOTES.md).

If you believe a notice is missing or incorrect, please open an issue or pull request.
