# SkySpotter Release Notes

## Unreleased (main)

Work in progress on the **SkySpotter** aviation specialist viewer—not yet tagged as a release.

### Aircraft gallery & indexing

- All AI (ViT labels, indexing, Magic Wand) runs **locally**—photos are not sent to the cloud for detection.
- ViT aircraft classifier with gallery labels, Magic Wand auto-sort, and `aircraft:` / model-name gallery search (EXIF + detected labels).
- Fixes for aircraft filter queries, Magic Wand moves when a type folder already exists, and reading indexed labels from the database.
- Minimum crop size for classification uses a fraction of the source image (default 20% per axis) instead of a fixed pixel floor.
- Faster open when launching on a single file: show that image first while the rest of the folder scans in the background.

### Blur detection — sharp / blurry gallery filters (experimental, **disabled by default**)

> **Experimental — reference only.** Not enabled in the default app build. Laplacian + subject-rect scoring did not match visual culling well enough in our tests. Enable with `SkySpotter_ENABLE_BLUR_SCORE=1` and re-index; see README **Experimental features**.

- **`sharp` / `blurry` search tokens** (when enabled) use indexed `blur_score` on a **`subject_rect`** crop of original RGB (rembg bbox).
- **Folder-relative ranking:** lowest fraction = blurry (default **20%**, `SkySpotter_BLUR_BLURRY_FRACTION`).
- **POC:** `scripts/poc_blur_detect.py` (requires `pixi run fix-opencv` for rembg).

### Models & installer

- Default checkpoint lives under `models/gallery-classifier/skyspotter-military-aircraft-vit/` (Git LFS); legacy `app_model/` path still supported.
- Windows installer: SkySpotter branding, `pixi.lock` + `pixi install --locked`, gallery classifier install step (`scripts/download_app_model.py`).
- Installer entry uses `src/bootstrap.py` (replaces missing legacy installer script).

### Documentation

- README rewritten for aviation workflows (focus overlay, aircraft search, formats, Pixi-only builds).
- Removed RAWviewer-era release history from this file; future versions will be listed here as SkySpotter ships.

### Third-party models & attribution

See **[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)** for copyrights, full license references (Apache-2.0, MIT, GPL-3.0 for PyQt6), and redistribution requirements for bundled or downloaded model weights (gallery ViT, rembg / IS-Net, optional CLIP backends).
