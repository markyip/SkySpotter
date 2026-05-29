"""Canonical paths for the gallery ViT classifier (GitHub: models/gallery-classifier/)."""

from __future__ import annotations

import json
import os
from pathlib import Path

GALLERY_CLASSIFIER_ID = "skyspotter-military-aircraft-vit"
GALLERY_CLASSIFIER_VERSION = "1.0.0"
GALLERY_CLASSIFIER_REL = Path("models") / "gallery-classifier" / GALLERY_CLASSIFIER_ID
MANIFEST_REL = Path("models") / "gallery-classifier" / "manifest.json"

REQUIRED_CHECKPOINT_FILES = (
    "config.json",
    "model.safetensors",
    "preprocessor_config.json",
    "labels.txt",
)

DEFAULT_GITHUB_REPO = "markyip/SkySpotter"
DEFAULT_RELEASE_TAG = f"gallery-classifier-v{GALLERY_CLASSIFIER_VERSION}"
DEFAULT_RELEASE_ZIP = (
    f"https://github.com/{DEFAULT_GITHUB_REPO}/releases/download/"
    f"{DEFAULT_RELEASE_TAG}/{GALLERY_CLASSIFIER_ID}-v{GALLERY_CLASSIFIER_VERSION}.zip"
)


def gallery_classifier_dir(project_root: str | Path) -> Path:
    return Path(project_root) / GALLERY_CLASSIFIER_REL


def legacy_app_model_dir(project_root: str | Path) -> Path:
    return Path(project_root) / "app_model"


def is_valid_checkpoint_dir(path: str | Path) -> bool:
    root = Path(path)
    return all((root / name).is_file() for name in REQUIRED_CHECKPOINT_FILES)


def load_manifest(project_root: str | Path | None = None) -> dict:
    roots: list[Path] = []
    if project_root is not None:
        roots.append(Path(project_root))
    roots.append(Path(__file__).resolve().parents[1])
    for root in roots:
        manifest_path = root / MANIFEST_REL
        if manifest_path.is_file():
            return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "id": GALLERY_CLASSIFIER_ID,
        "version": GALLERY_CLASSIFIER_VERSION,
        "github": {"repo": DEFAULT_GITHUB_REPO, "path": str(GALLERY_CLASSIFIER_REL).replace("\\", "/")},
        "release": {"url": DEFAULT_RELEASE_ZIP, "sha256": ""},
    }


def default_release_url(project_root: str | Path | None = None) -> str:
    manifest = load_manifest(project_root)
    release = manifest.get("release") or {}
    url = (release.get("url") or "").strip()
    if url:
        return url
    env_url = os.environ.get("SkySpotter_APP_MODEL_URL", "").strip()
    return env_url or DEFAULT_RELEASE_ZIP


def checkpoint_dir_candidates(project_root: str | Path) -> list[str]:
    """Search order for gallery ViT weights (first valid wins)."""
    override = (
        os.environ.get("SkySpotter_APP_MODEL_DIR", "").strip()
        or os.environ.get("SkySpotter_GALLERY_CLASSIFIER_DIR", "").strip()
        or os.environ.get("SkySpotter_AIRCRAFT_CHECKPOINT_DIR", "").strip()
    )
    root = Path(project_root)
    candidates: list[str] = []
    if override:
        candidates.append(override)
    candidates.extend(
        [
            str(gallery_classifier_dir(root)),
            str(legacy_app_model_dir(root)),
            str(root / "aviation_model_processed"),
            str(root / "aviation_model_v3"),
        ]
    )
    return candidates
