"""
SkySpotter feature flags (build + dev + runtime).

Resolution order for each flag:
  1. Environment override (``SkySpotter_ENABLE_<FLAG>``), if set
  2. JSON file (``SkySpotter_FEATURES_FILE`` or ``config/skyspotter_features.json``)
  3. Built-in default (off for experimental features)

Use ``scripts/set_features.py``, ``SkySpotter_ENABLE_BLUR_SCORE=1``, or ``pixi run start-experimental`` for dev.
Pass ``--enable-blur-score`` to ``build.py`` when packaging an installer.
"""

from __future__ import annotations

import json
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _repo_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _parse_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in _TRUTHY:
        return True
    if text in {"0", "false", "no", "off", ""}:
        return False
    return None


def features_file_path() -> Path:
    """Path to the active features JSON (may not exist yet)."""
    raw = os.environ.get("SkySpotter_FEATURES_FILE", "").strip()
    if raw:
        p = Path(raw)
        if not p.is_absolute():
            p = _repo_root() / p
        return p
    return _repo_root() / "config" / "skyspotter_features.json"


@lru_cache(maxsize=1)
def load_feature_config() -> dict[str, Any]:
    path = features_file_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _flag_from_env(env_name: str) -> bool | None:
    raw = os.environ.get(env_name)
    if raw is None or str(raw).strip() == "":
        return None
    return str(raw).strip().lower() in _TRUTHY


def blur_score_enabled() -> bool:
    """Experimental Laplacian ``sharp`` / ``blurry`` gallery filters."""
    env = _flag_from_env("SkySpotter_ENABLE_BLUR_SCORE")
    if env is not None:
        return env
    file_val = _parse_bool(load_feature_config().get("blur_score"))
    if file_val is not None:
        return file_val
    return False


def face_scan_enabled() -> bool:
    """RAWviewer-style face-count indexing for ``people`` / ``portrait`` gallery filters."""
    env = _flag_from_env("SkySpotter_ENABLE_FACE_SCAN")
    if env is not None:
        return env
    file_val = _parse_bool(load_feature_config().get("face_scan"))
    if file_val is not None:
        return file_val
    return False


def feature_flags_summary() -> dict[str, bool]:
    return {
        "blur_score": blur_score_enabled(),
        "face_scan": face_scan_enabled(),
    }
