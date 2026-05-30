# SkySpotter Release Notes

## Unreleased (main)

Work in progress on the **SkySpotter** aviation specialist viewer—not yet tagged as a release.

### Aircraft gallery & indexing

- All AI (ViT labels, indexing, Magic Wand) runs **locally**—photos are not sent to the cloud for detection.
- ViT aircraft classifier with gallery labels, Magic Wand auto-sort, and `aircraft:` / model-name gallery search (EXIF + detected labels).
- Fixes for aircraft filter queries, Magic Wand moves when a type folder already exists, and reading indexed labels from the database.
- Minimum crop size for classification uses a fraction of the source image (default 20% per axis) instead of a fixed pixel floor.
- Faster open when launching on a single file: show that image first while the rest of the folder scans in the background.

### Blur detection — sharp / blurry gallery filters (experimental)

> **Experimental — reference only.** These features are under active tuning. Outputs are **not** guaranteed to match how sharp a photo looks to you; use them as a starting point for culling, not as ground truth.

- **`sharp` / `blurry` search tokens** filter the current gallery folder (or the current filter result) using an indexed **Laplacian sharpness score** on a downscaled frame—**no** separate blur ML model and **no** rembg for this step.
- **ROI priority:** EXIF / maker focus area when available → else central crop (default 70%) → else full thumbnail (`SkySpotter_BLUR_MAX_SIZE`, default 1280 px).
- **Folder-relative ranking:** the lowest-scoring fraction of indexed images in the active set is treated as **blurry** (default **20%**, `SkySpotter_BLUR_BLURRY_FRACTION=0.2`); the rest with scores count as **sharp**. Absolute cutoffs remain available via `blur>=N` / `blur<N` tokens (`SkySpotter_BLUR_SHARP_THRESHOLD` for legacy numeric filters only).
- **Re-index** after upgrading blur logic so `blur_score` values in the semantic index match the new pipeline.
- **POC:** `scripts/poc_blur_detect.py` writes `blur_scores.csv` for batch validation on a folder.

Aircraft **type** labels still come from the ViT classifier (below); blur scoring is independent of that model.

### Models & installer

- Default checkpoint lives under `models/gallery-classifier/skyspotter-military-aircraft-vit/` (Git LFS); legacy `app_model/` path still supported.
- Windows installer: SkySpotter branding, `pixi.lock` + `pixi install --locked`, gallery classifier install step (`scripts/download_app_model.py`).
- Installer entry uses `src/bootstrap.py` (replaces missing legacy installer script).

### Documentation

- README rewritten for aviation workflows (focus overlay, aircraft search, formats, Pixi-only builds).
- Removed RAWviewer-era release history from this file; future versions will be listed here as SkySpotter ships.

### Third-party models & attribution

See **[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)** for copyrights, full license references (Apache-2.0, MIT, GPL-3.0 for PyQt6), and redistribution requirements for bundled or downloaded model weights (gallery ViT, rembg / IS-Net, optional CLIP backends).
