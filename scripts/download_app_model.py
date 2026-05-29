#!/usr/bin/env python3
"""
Install the gallery ViT checkpoint under models/gallery-classifier/<id>/.

Used by the Windows installer after pixi install. Order:
  1. Copy from PyInstaller bundle (models/gallery-classifier/... or legacy app_model/)
  2. Download release zip from manifest / SkySpotter_APP_MODEL_URL (optional SHA256)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gallery_model_paths import (  # noqa: E402
    GALLERY_CLASSIFIER_ID,
    GALLERY_CLASSIFIER_VERSION,
    REQUIRED_CHECKPOINT_FILES,
    default_release_url,
    gallery_classifier_dir,
    is_valid_checkpoint_dir,
    legacy_app_model_dir,
    load_manifest,
)


def _bundle_checkpoint_dirs(bundle_dir: Path) -> list[Path]:
    rel = Path("models") / "gallery-classifier" / GALLERY_CLASSIFIER_ID
    candidates = [
        bundle_dir / rel,
        bundle_dir / "SkySpotter" / rel,
        bundle_dir / "app_model",
        bundle_dir / "SkySpotter" / "app_model",
    ]
    out: list[Path] = []
    for p in candidates:
        if is_valid_checkpoint_dir(p):
            out.append(p)
    return out


def _write_version_file(model_dir: Path, version: str, source: str) -> None:
    payload = {"id": GALLERY_CLASSIFIER_ID, "version": version, "source": source}
    (model_dir / "model_version.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _copy_checkpoint(src: Path, dest: Path, version: str, source: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest)
    _write_version_file(dest, version, source)
    print(f"[SUCCESS] Gallery classifier installed: {dest}")


def _download_zip(url: str, dest_zip: Path) -> None:
    print("[INFO] Downloading gallery classifier archive...")
    print(f"       {url}")
    dest_zip.parent.mkdir(parents=True, exist_ok=True)

    def _report(block_num: int, block_size: int, total_size: int) -> None:
        if total_size <= 0:
            return
        done = block_num * block_size
        pct = min(100, int(done * 100 / total_size))
        if block_num % 50 == 0:
            print(f"  ... {pct}%", flush=True)

    urllib.request.urlretrieve(url, dest_zip, reporthook=_report)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _install_from_zip(zip_path: Path, dest: Path, version: str) -> None:
    staging = Path(tempfile.mkdtemp(prefix="skyspotter_gallery_model_"))
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(staging)
        roots = [staging]
        for child in staging.iterdir():
            if child.is_dir():
                roots.append(child)
        picked: Path | None = None
        for root in roots:
            if is_valid_checkpoint_dir(root):
                picked = root
                break
        if picked is None:
            raise RuntimeError(
                "Archive does not contain a valid gallery classifier "
                f"(need {', '.join(REQUIRED_CHECKPOINT_FILES)})"
            )
        _copy_checkpoint(picked, dest, version, "download")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def install_gallery_classifier(
    install_dir: Path,
    bundle_dir: Path | None = None,
    *,
    version: str | None = None,
    url: str | None = None,
    expected_sha256: str | None = None,
) -> int:
    install_dir = install_dir.resolve()
    manifest = load_manifest(install_dir if (install_dir / "models").is_dir() else ROOT)
    version = (version or manifest.get("version") or GALLERY_CLASSIFIER_VERSION).strip()
    dest = gallery_classifier_dir(install_dir)

    if is_valid_checkpoint_dir(dest):
        print(f"[INFO] Gallery classifier already present: {dest}")
        if not (dest / "model_version.json").is_file():
            _write_version_file(dest, version, "existing")
        return 0

    if bundle_dir is not None:
        for src in _bundle_checkpoint_dirs(bundle_dir.resolve()):
            _copy_checkpoint(src, dest, version, "bundle")
            return 0

    release = manifest.get("release") or {}
    download_url = (url or os.environ.get("SkySpotter_APP_MODEL_URL", "") or default_release_url(ROOT)).strip()
    expected_sha256 = (
        expected_sha256
        or os.environ.get("SkySpotter_APP_MODEL_SHA256", "")
        or (release.get("sha256") or "")
    ).strip()

    if not download_url:
        print(
            "[ERROR] No classifier in installer bundle. Clone the repo with Git LFS or set "
            "SkySpotter_APP_MODEL_URL to a release zip."
        )
        return 1

    with tempfile.TemporaryDirectory(prefix="skyspotter_model_dl_") as tmp:
        zip_path = Path(tmp) / f"{GALLERY_CLASSIFIER_ID}.zip"
        try:
            _download_zip(download_url, zip_path)
        except Exception as exc:
            print(f"[ERROR] Download failed: {exc}")
            print(
                "[HINT] Publish a GitHub release or clone the repo:\n"
                "  git clone https://github.com/markyip/SkySpotter.git\n"
                "  cd SkySpotter && git lfs pull"
            )
            return 1
        if expected_sha256:
            digest = _sha256_file(zip_path)
            if digest.lower() != expected_sha256.lower():
                print(f"[ERROR] SHA256 mismatch (got {digest}, expected {expected_sha256})")
                return 1
        _install_from_zip(zip_path, dest, version)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install SkySpotter gallery ViT classifier")
    parser.add_argument(
        "--install-dir",
        required=True,
        help="SkySpotter root (contains src/, pixi.toml)",
    )
    parser.add_argument("--bundle-dir", default="", help="PyInstaller bundle directory")
    parser.add_argument("--url", default="", help="Override release zip URL")
    parser.add_argument("--version", default="")
    parser.add_argument("--sha256", default="", help="Expected SHA256 of zip")
    args = parser.parse_args()

    bundle = Path(args.bundle_dir) if args.bundle_dir else None
    return install_gallery_classifier(
        Path(args.install_dir),
        bundle,
        version=args.version or None,
        url=args.url or None,
        expected_sha256=args.sha256 or None,
    )


if __name__ == "__main__":
    sys.exit(main())
