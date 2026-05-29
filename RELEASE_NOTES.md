# SkySpotter Release Notes

## Unreleased (main)

Work in progress on the **SkySpotter** aviation specialist viewer—not yet tagged as a release.

### Aircraft gallery & indexing

- All AI (ViT labels, indexing, Magic Wand) runs **locally**—photos are not sent to the cloud for detection.
- ViT aircraft classifier with gallery labels, Magic Wand auto-sort, and `aircraft:` / model-name gallery search (EXIF + detected labels).
- Fixes for aircraft filter queries, Magic Wand moves when a type folder already exists, and reading indexed labels from the database.
- Minimum crop size for classification uses a fraction of the source image (default 20% per axis) instead of a fixed pixel floor.
- Faster open when launching on a single file: show that image first while the rest of the folder scans in the background.

### Models & installer

- Default checkpoint lives under `models/gallery-classifier/skyspotter-military-aircraft-vit/` (Git LFS); legacy `app_model/` path still supported.
- Windows installer: SkySpotter branding, `pixi.lock` + `pixi install --locked`, gallery classifier install step (`scripts/download_app_model.py`).
- Installer entry uses `src/bootstrap.py` (replaces missing legacy installer script).

### Documentation

- README rewritten for aviation workflows (focus overlay, aircraft search, formats, Pixi-only builds).
- Removed RAWviewer-era release history from this file; future versions will be listed here as SkySpotter ships.
