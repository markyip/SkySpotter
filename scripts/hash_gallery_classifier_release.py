#!/usr/bin/env python3
"""
Compute SHA256 for a gallery-classifier release zip and update manifest.json.

Typical release flow:
  1. pixi run python scripts/hash_gallery_classifier_release.py --from-checkpoint
  2. Upload dist/<id>-v<version>.zip to GitHub release gallery-classifier-v<version>
  3. Commit the updated manifest.json
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gallery_classifier_version import _sha256_file  # noqa: E402
from gallery_model_paths import (  # noqa: E402
    DEFAULT_GITHUB_REPO,
    GALLERY_CLASSIFIER_ID,
    GALLERY_CLASSIFIER_VERSION,
    MANIFEST_REL,
    REQUIRED_CHECKPOINT_FILES,
    gallery_classifier_dir,
    is_valid_checkpoint_dir,
    load_manifest,
)


def _manifest_path(project_root: Path, override: Path | None) -> Path:
    if override is not None:
        return override.resolve()
    return project_root / MANIFEST_REL


def _release_zip_name(version: str) -> str:
    return f"{GALLERY_CLASSIFIER_ID}-v{version}.zip"


def _release_tag(version: str) -> str:
    return f"gallery-classifier-v{version}"


def _release_url(version: str, repo: str = DEFAULT_GITHUB_REPO) -> str:
    tag = _release_tag(version)
    return (
        f"https://github.com/{repo}/releases/download/"
        f"{tag}/{_release_zip_name(version)}"
    )


def create_release_zip(checkpoint_dir: Path, dest_zip: Path) -> None:
    if not is_valid_checkpoint_dir(checkpoint_dir):
        missing = [n for n in REQUIRED_CHECKPOINT_FILES if not (checkpoint_dir / n).is_file()]
        raise RuntimeError(
            f"Invalid checkpoint at {checkpoint_dir} (missing: {', '.join(missing)})"
        )
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    if dest_zip.exists():
        dest_zip.unlink()
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in REQUIRED_CHECKPOINT_FILES:
            zf.write(checkpoint_dir / name, arcname=name)


def update_manifest(
    manifest_path: Path,
    project_root: Path,
    sha256: str,
    *,
    version: str | None = None,
    repo: str = DEFAULT_GITHUB_REPO,
) -> dict:
    if manifest_path.is_file():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = load_manifest(project_root)

    ver = (version or data.get("version") or GALLERY_CLASSIFIER_VERSION).strip()
    release = data.setdefault("release", {})
    release["sha256"] = sha256.lower()
    if version:
        data["version"] = ver
        github = data.setdefault("github", {})
        github["tag"] = _release_tag(ver)
        release["url"] = _release_url(ver, repo=repo)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hash gallery classifier release zip and update manifest.json"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=ROOT,
        help="SkySpotter repo root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=f"Manifest path (default: {MANIFEST_REL})",
    )
    parser.add_argument(
        "--zip",
        type=Path,
        default=None,
        help="Release zip to hash (default with --from-checkpoint: dist/<id>-v<version>.zip)",
    )
    parser.add_argument(
        "--from-checkpoint",
        action="store_true",
        help="Build release zip from models/gallery-classifier/<id>/ before hashing",
    )
    parser.add_argument(
        "--version",
        default="",
        help="Set manifest version, github tag, and release URL (e.g. 1.1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print SHA256 only; do not write manifest",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Compare --zip SHA256 to manifest release.sha256 (exit 1 on mismatch)",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    manifest_path = _manifest_path(project_root, args.manifest)
    version = (args.version or "").strip() or None

    zip_path = args.zip
    if args.from_checkpoint:
        ver = version or str(load_manifest(project_root).get("version") or GALLERY_CLASSIFIER_VERSION)
        if zip_path is None:
            zip_path = project_root / "dist" / _release_zip_name(ver)
        checkpoint = gallery_classifier_dir(project_root)
        print(f"[INFO] Packing checkpoint: {checkpoint}")
        print(f"[INFO] Output zip: {zip_path}")
        create_release_zip(checkpoint, zip_path.resolve())
    elif zip_path is None:
        parser.error("Provide --zip PATH or use --from-checkpoint")

    zip_path = zip_path.resolve()
    if not zip_path.is_file():
        print(f"[ERROR] Zip not found: {zip_path}", file=sys.stderr)
        return 1

    digest = _sha256_file(zip_path)
    print(f"[INFO] File: {zip_path}")
    print(f"[INFO] SHA256: {digest}")

    if args.verify:
        expected = str((load_manifest(project_root).get("release") or {}).get("sha256") or "").strip()
        if not expected:
            print("[ERROR] manifest release.sha256 is empty", file=sys.stderr)
            return 1
        if digest.lower() != expected.lower():
            print(f"[ERROR] SHA256 mismatch (manifest expects {expected})", file=sys.stderr)
            return 1
        print("[SUCCESS] Zip matches manifest release.sha256")
        return 0

    if args.dry_run:
        print("[INFO] Dry run — manifest not modified")
        return 0

    data = update_manifest(manifest_path, project_root, digest, version=version)
    print(f"[SUCCESS] Updated {manifest_path}")
    print(f"         version={data.get('version')} sha256={digest[:16]}…")
    url = (data.get("release") or {}).get("url") or ""
    if url:
        print(f"         url={url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
