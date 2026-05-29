# Gallery classifier models

Published ViT checkpoints used by SkySpotter for aircraft labels, indexing, and Magic Wand.

## Default model: `skyspotter-military-aircraft-vit`

| File | Purpose |
|------|---------|
| `config.json` | Hugging Face ViT config |
| `model.safetensors` | Weights (~330 MB, **Git LFS**) |
| `preprocessor_config.json` | Image preprocessing |
| `labels.txt` | One class name per line |

Metadata: `manifest.json` (version, GitHub path, optional release zip URL).

## Get the weights from GitHub

```bash
git clone https://github.com/markyip/SkySpotter.git
cd SkySpotter
git lfs install
git lfs pull
```

Weights live at `models/gallery-classifier/skyspotter-military-aircraft-vit/`.

Optional release zip (installer / offline): see `manifest.json` → `release.url`.

## Override at runtime

Set `SkySpotter_GALLERY_CLASSIFIER_DIR` or legacy `SkySpotter_APP_MODEL_DIR` to any folder containing the four required files.

## Train your own

Train into `customized_model/`, verify with `scripts/batch_test_classifier.py`, then copy the four files into a new folder under `models/gallery-classifier/<your-model-id>/` and update `manifest.json` or point the env var at your folder.
