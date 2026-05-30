#!/usr/bin/env python3
"""Read or write config/skyspotter_features.json for dev builds and installers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "config" / "skyspotter_features.json"


def _load(path: Path) -> dict:
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"blur_score": False}


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage SkySpotter feature flags JSON")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_PATH,
        help=f"Features JSON path (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--blur-score",
        choices=("on", "off"),
        help="Enable or disable experimental blur scoring",
    )
    parser.add_argument(
        "--copy-experimental",
        action="store_true",
        help="Copy config/skyspotter_features.experimental.json to the target file",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print current flags and exit",
    )
    args = parser.parse_args()
    path: Path = args.file
    if not path.is_absolute():
        path = ROOT / path

    if args.copy_experimental:
        src = ROOT / "config" / "skyspotter_features.experimental.json"
        if not src.is_file():
            print(f"Missing template: {src}", file=sys.stderr)
            return 1
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Wrote experimental flags to {path}")
        return 0

    data = _load(path)
    if args.blur_score == "on":
        data["blur_score"] = True
    elif args.blur_score == "off":
        data["blur_score"] = False

    if args.show and args.blur_score is None and not args.copy_experimental:
        print(json.dumps(data, indent=2))
        return 0

    if args.blur_score is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {path}")
        print(json.dumps(data, indent=2))

    if args.blur_score is None and not args.show and not args.copy_experimental:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
