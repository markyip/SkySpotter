"""Gallery ViT classifier version, fingerprint, and update protection."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from gallery_model_paths import (
    GALLERY_CLASSIFIER_ID,
    GALLERY_CLASSIFIER_VERSION,
    REQUIRED_CHECKPOINT_FILES,
    checkpoint_dir_candidates,
    default_release_url,
    gallery_classifier_dir,
    is_valid_checkpoint_dir,
    load_manifest,
)

SOURCE_BUNDLE = "bundle"
SOURCE_CUSTOM = "custom"
SOURCE_DOWNLOAD = "download"
SOURCE_EXISTING = "existing"

ClassifierProgressCallback = Callable[[int, int, str], None]

logger = logging.getLogger(__name__)

_PROTECTED_SOURCES = frozenset({SOURCE_CUSTOM})
_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


@dataclass(frozen=True)
class ClassifierUpdateStatus:
    state: str  # up_to_date | update_available | missing | custom_protected | modified_locally
    local_version: str
    remote_version: str
    checkpoint_dir: str
    message: str


def project_root_from_module() -> Path:
    return Path(__file__).resolve().parents[1]


def classifier_env_override() -> str:
    return (
        os.environ.get("SkySpotter_GALLERY_CLASSIFIER_DIR", "").strip()
        or os.environ.get("SkySpotter_APP_MODEL_DIR", "").strip()
        or os.environ.get("SkySpotter_AIRCRAFT_CHECKPOINT_DIR", "").strip()
    )


def resolve_active_checkpoint_dir(project_root: str | Path | None = None) -> Path | None:
    root = Path(project_root) if project_root is not None else project_root_from_module()
    for candidate in checkpoint_dir_candidates(root):
        if is_valid_checkpoint_dir(candidate):
            return Path(candidate).resolve()
    return None


def compute_checkpoint_fingerprint(checkpoint_dir: str | Path) -> str:
    """Stable hash of model weights + label list (detects any replacement)."""
    root = Path(checkpoint_dir)
    if not is_valid_checkpoint_dir(root):
        return ""
    h = hashlib.sha256()
    for name in ("model.safetensors", "labels.txt"):
        path = root / name
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    return h.hexdigest()


def parse_version(version: str) -> tuple[int, int, int]:
    text = (version or "").strip()
    match = _VERSION_RE.search(text)
    if not match:
        return (0, 0, 0)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def version_is_newer(remote: str, local: str) -> bool:
    return parse_version(remote) > parse_version(local)


def read_model_version(checkpoint_dir: str | Path) -> dict[str, Any] | None:
    path = Path(checkpoint_dir) / "model_version.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def write_model_version(
    checkpoint_dir: str | Path,
    *,
    version: str,
    source: str,
    fingerprint: str | None = None,
) -> None:
    root = Path(checkpoint_dir)
    fp = fingerprint or compute_checkpoint_fingerprint(root)
    payload = {
        "id": GALLERY_CLASSIFIER_ID,
        "version": (version or GALLERY_CLASSIFIER_VERSION).strip(),
        "source": source,
        "fingerprint": fp,
    }
    (root / "model_version.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def mark_checkpoint_custom(checkpoint_dir: str | Path, version: str | None = None) -> None:
    root = Path(checkpoint_dir)
    if not is_valid_checkpoint_dir(root):
        raise ValueError(f"Not a valid classifier checkpoint: {root}")
    info = read_model_version(root) or {}
    write_model_version(
        root,
        version=(version or str(info.get("version") or "custom")).strip(),
        source=SOURCE_CUSTOM,
    )


def is_using_env_override(project_root: str | Path | None = None) -> bool:
    override = classifier_env_override()
    if not override:
        return False
    active = resolve_active_checkpoint_dir(project_root)
    if active is None:
        return False
    try:
        return Path(override).resolve() == active
    except OSError:
        return True


def is_modified_locally(checkpoint_dir: str | Path) -> bool:
    root = Path(checkpoint_dir)
    if not is_valid_checkpoint_dir(root):
        return False
    live = compute_checkpoint_fingerprint(root)
    info = read_model_version(root)
    if not info:
        return False
    recorded = str(info.get("fingerprint") or "").strip()
    return bool(recorded and live and recorded != live)


def is_protected_from_auto_update(
    checkpoint_dir: str | Path,
    project_root: str | Path | None = None,
) -> bool:
    root = Path(checkpoint_dir)
    if is_using_env_override(project_root):
        return True
    info = read_model_version(root) or {}
    source = str(info.get("source") or SOURCE_EXISTING).strip().lower()
    if source in _PROTECTED_SOURCES:
        return True
    if is_modified_locally(root):
        return True
    return False


def backfill_model_version_if_needed(
    checkpoint_dir: str | Path,
    project_root: str | Path | None = None,
) -> None:
    root = Path(checkpoint_dir)
    if not is_valid_checkpoint_dir(root):
        return
    manifest = load_manifest(project_root)
    remote_version = str(manifest.get("version") or GALLERY_CLASSIFIER_VERSION).strip()
    info = read_model_version(root)
    if info is None:
        write_model_version(root, version=remote_version, source=SOURCE_EXISTING)
        return
    if not str(info.get("fingerprint") or "").strip():
        write_model_version(
            root,
            version=str(info.get("version") or remote_version).strip(),
            source=str(info.get("source") or SOURCE_EXISTING).strip(),
        )


def check_official_update_status(
    project_root: str | Path | None = None,
) -> ClassifierUpdateStatus:
    root = Path(project_root) if project_root is not None else project_root_from_module()
    manifest = load_manifest(root)
    remote_version = str(manifest.get("version") or GALLERY_CLASSIFIER_VERSION).strip()
    default_dir = gallery_classifier_dir(root)

    if is_using_env_override(root):
        active = resolve_active_checkpoint_dir(root)
        cp = str(active or classifier_env_override())
        return ClassifierUpdateStatus(
            state="custom_protected",
            local_version=str((read_model_version(cp) or {}).get("version") or "unknown"),
            remote_version=remote_version,
            checkpoint_dir=cp,
            message="Using SkySpotter_GALLERY_CLASSIFIER_DIR; official auto-update is disabled.",
        )

    if not is_valid_checkpoint_dir(default_dir):
        return ClassifierUpdateStatus(
            state="missing",
            local_version="",
            remote_version=remote_version,
            checkpoint_dir=str(default_dir),
            message="Gallery classifier is not installed.",
        )

    backfill_model_version_if_needed(default_dir, root)
    info = read_model_version(default_dir) or {}
    local_version = str(info.get("version") or GALLERY_CLASSIFIER_VERSION).strip()

    if is_protected_from_auto_update(default_dir, root):
        state = "modified_locally" if is_modified_locally(default_dir) else "custom_protected"
        if str(info.get("source") or "").strip().lower() == SOURCE_CUSTOM:
            state = "custom_protected"
        return ClassifierUpdateStatus(
            state=state,
            local_version=local_version,
            remote_version=remote_version,
            checkpoint_dir=str(default_dir),
            message=(
                "Local classifier is custom or modified; it will not be replaced automatically."
            ),
        )

    if version_is_newer(remote_version, local_version):
        return ClassifierUpdateStatus(
            state="update_available",
            local_version=local_version,
            remote_version=remote_version,
            checkpoint_dir=str(default_dir),
            message=(
                f"Official gallery classifier {remote_version} is available "
                f"(installed: {local_version})."
            ),
        )

    return ClassifierUpdateStatus(
        state="up_to_date",
        local_version=local_version,
        remote_version=remote_version,
        checkpoint_dir=str(default_dir),
        message=f"Gallery classifier is up to date ({local_version}).",
    )


def release_download_params(project_root: str | Path | None = None) -> tuple[str, str, str]:
    root = Path(project_root) if project_root is not None else project_root_from_module()
    manifest = load_manifest(root)
    release = manifest.get("release") or {}
    version = str(manifest.get("version") or GALLERY_CLASSIFIER_VERSION).strip()
    url = (
        os.environ.get("SkySpotter_APP_MODEL_URL", "").strip()
        or str(release.get("url") or "").strip()
        or default_release_url(root)
    )
    sha256 = (
        os.environ.get("SkySpotter_APP_MODEL_SHA256", "").strip()
        or str(release.get("sha256") or "").strip()
    )
    return version, url, sha256


def _emit_progress(
    callback: ClassifierProgressCallback | None,
    done: int,
    total: int,
    phase: str,
) -> None:
    if callback is not None:
        callback(int(done), int(total), phase)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_checkpoint(
    src: Path,
    dest: Path,
    version: str,
    source: str,
    *,
    progress_callback: ClassifierProgressCallback | None = None,
) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    _emit_progress(progress_callback, 0, 0, "install")
    shutil.copytree(src, dest)
    write_model_version(dest, version=version, source=source)
    _emit_progress(progress_callback, 100, 100, "install")


def _download_zip(
    url: str,
    dest_zip: Path,
    progress_callback: ClassifierProgressCallback | None = None,
) -> None:
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    last_pct = -1

    def _report(block_num: int, block_size: int, total_size: int) -> None:
        nonlocal last_pct
        done = block_num * block_size
        total = total_size if total_size > 0 else 0
        if total > 0:
            pct = min(100, int(done * 100 / total))
            if pct != last_pct:
                last_pct = pct
                _emit_progress(progress_callback, done, total, "download")
        else:
            _emit_progress(progress_callback, done, 0, "download")

    urllib.request.urlretrieve(url, dest_zip, reporthook=_report)


def _install_from_zip(
    zip_path: Path,
    dest: Path,
    version: str,
    *,
    progress_callback: ClassifierProgressCallback | None = None,
) -> None:
    staging = Path(tempfile.mkdtemp(prefix="skyspotter_gallery_model_"))
    try:
        _emit_progress(progress_callback, 0, 0, "install")
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
        _copy_checkpoint(
            picked, dest, version, SOURCE_DOWNLOAD, progress_callback=progress_callback
        )
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _download_and_install(
    dest: Path,
    version: str,
    url: str,
    expected_sha256: str,
    *,
    progress_callback: ClassifierProgressCallback | None = None,
) -> int:
    if not url:
        return 1

    with tempfile.TemporaryDirectory(prefix="skyspotter_model_dl_") as tmp:
        zip_path = Path(tmp) / f"{GALLERY_CLASSIFIER_ID}.zip"
        try:
            _download_zip(url, zip_path, progress_callback)
        except Exception:
            return 1
        if expected_sha256:
            _emit_progress(progress_callback, 0, 0, "verify")
            digest = _sha256_file(zip_path)
            if digest.lower() != expected_sha256.lower():
                logger.error(
                    "[MODEL] Gallery classifier zip SHA256 mismatch (got %s, expected %s)",
                    digest,
                    expected_sha256,
                )
                return 1
        else:
            logger.info(
                "[MODEL] No SHA256 configured for gallery classifier release; "
                "skipping zip checksum (checkpoint files validated after extract)."
            )
        try:
            _install_from_zip(
                zip_path, dest, version, progress_callback=progress_callback
            )
        except Exception:
            return 1
    _emit_progress(progress_callback, 100, 100, "complete")
    return 0


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


def install_gallery_classifier(
    install_dir: str | Path,
    bundle_dir: str | Path | None = None,
    *,
    version: str | None = None,
    url: str | None = None,
    expected_sha256: str | None = None,
    force: bool = False,
    update_if_older: bool = False,
    mark_custom: bool = False,
    check_only: bool = False,
    progress_callback: ClassifierProgressCallback | None = None,
) -> int:
    """Install or update the default gallery classifier. Returns 0 on success."""
    root = Path(install_dir).resolve()
    module_root = project_root_from_module()
    manifest = load_manifest(root if (root / "models").is_dir() else module_root)
    manifest_version = (version or manifest.get("version") or GALLERY_CLASSIFIER_VERSION).strip()
    dest = gallery_classifier_dir(root)

    if mark_custom:
        if not is_valid_checkpoint_dir(dest):
            return 1
        mark_checkpoint_custom(dest, version=manifest_version)
        return 0

    if check_only:
        status = check_official_update_status(root)
        if status.state == "update_available":
            return 2
        if status.state == "missing":
            return 1
        return 0

    release = manifest.get("release") or {}
    download_url = (url or os.environ.get("SkySpotter_APP_MODEL_URL", "") or "").strip()
    if not download_url:
        _, download_url, _ = release_download_params(root)
    sha256_expected = (
        expected_sha256
        or os.environ.get("SkySpotter_APP_MODEL_SHA256", "")
        or (release.get("sha256") or "")
    ).strip()

    bundle_path = Path(bundle_dir).resolve() if bundle_dir is not None else None

    if is_valid_checkpoint_dir(dest):
        backfill_model_version_if_needed(dest, root)
        info = read_model_version(dest) or {}
        local_version = str(info.get("version") or manifest_version).strip()

        if is_protected_from_auto_update(dest, root) and not force:
            return 0

        if not force and not update_if_older:
            if not (dest / "model_version.json").is_file():
                write_model_version(dest, version=local_version, source=SOURCE_EXISTING)
            return 0

        if not force and update_if_older and not version_is_newer(manifest_version, local_version):
            return 0

        if force or update_if_older:
            return _download_and_install(
                dest,
                manifest_version,
                download_url,
                sha256_expected,
                progress_callback=progress_callback,
            )

    if bundle_path is not None:
        for src in _bundle_checkpoint_dirs(bundle_path):
            _copy_checkpoint(
                src,
                dest,
                manifest_version,
                SOURCE_BUNDLE,
                progress_callback=progress_callback,
            )
            _emit_progress(progress_callback, 100, 100, "complete")
            return 0

    return _download_and_install(
        dest,
        manifest_version,
        download_url,
        sha256_expected,
        progress_callback=progress_callback,
    )
