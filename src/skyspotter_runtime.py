"""
SkySpotter runtime paths, settings, and environment variable names.

Prefer SkySpotter_* env vars and ~/.skyspotter_cache; accept RAWVIEWER_* /
~/.skyspotter_cache as legacy fallbacks. One-time migration moves legacy cache
and QSettings into SkySpotter locations when the new store is empty.
"""

from __future__ import annotations

import os
import shutil
from typing import Optional

SETTINGS_ORG = "SkySpotter"
SETTINGS_APP = "SkySpotter"
LEGACY_SETTINGS_ORG = "SkySpotter"
LEGACY_SETTINGS_APP = "SkySpotter"

CACHE_DIRNAME = ".skyspotter_cache"
LEGACY_CACHE_DIRNAME = ".skyspotter_cache"

_cache_migrated = False
_settings_migrated = False


def legacy_cache_root() -> str:
    return os.path.expanduser(f"~/{LEGACY_CACHE_DIRNAME}")


def cache_root() -> str:
    """Primary on-disk cache directory (created if missing)."""
    override = (
        os.environ.get("SkySpotter_CACHE_DIR", "").strip()
        or os.environ.get("RAWVIEWER_CACHE_DIR", "").strip()
    )
    if override:
        path = os.path.expanduser(override)
    else:
        path = os.path.expanduser(f"~/{CACHE_DIRNAME}")
    os.makedirs(path, exist_ok=True)
    ensure_cache_migrated(path)
    return path


def ensure_cache_migrated(target_root: Optional[str] = None) -> None:
    """Move top-level legacy cache entries into SkySpotter cache when new store is empty."""
    global _cache_migrated
    if _cache_migrated:
        return
    _cache_migrated = True

    new_root = target_root or os.path.expanduser(f"~/{CACHE_DIRNAME}")
    legacy = legacy_cache_root()
    if os.path.normcase(os.path.abspath(legacy)) == os.path.normcase(
        os.path.abspath(new_root)
    ):
        return
    if not os.path.isdir(legacy):
        return

    try:
        new_entries = os.listdir(new_root) if os.path.isdir(new_root) else []
    except OSError:
        new_entries = []
    if new_entries:
        return

    os.makedirs(new_root, exist_ok=True)
    for name in os.listdir(legacy):
        src = os.path.join(legacy, name)
        dst = os.path.join(new_root, name)
        if os.path.exists(dst):
            continue
        try:
            shutil.move(src, dst)
        except OSError:
            try:
                if os.path.isdir(src) and not os.path.islink(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except OSError:
                pass


def env_get(name: str, default: str = "") -> str:
    """Read SkySpotter_{name}, then RAWVIEWER_{name}, else default."""
    for prefix in ("SkySpotter_", "RAWVIEWER_"):
        val = os.environ.get(f"{prefix}{name}")
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return default


def env_flag(name: str, *, default: bool = False) -> bool:
    raw = env_get(name, "")
    if not raw:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


def env_int(name: str, default: int, *, minimum: Optional[int] = None) -> int:
    try:
        value = int(env_get(name, str(default)).strip())
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        return max(minimum, value)
    return value


def app_settings():
    """QSettings for SkySpotter with one-time copy from legacy SkySpotter registry."""
    from PyQt6.QtCore import QSettings

    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    _migrate_settings_from_legacy_once(settings)
    return settings


def _migrate_settings_from_legacy_once(new_settings) -> None:
    global _settings_migrated
    if _settings_migrated:
        return
    _settings_migrated = True

    from PyQt6.QtCore import QSettings

    legacy = QSettings(LEGACY_SETTINGS_ORG, LEGACY_SETTINGS_APP)
    for key in legacy.allKeys():
        if not new_settings.contains(key):
            new_settings.setValue(key, legacy.value(key))
    try:
        new_settings.sync()
    except Exception:
        pass
