#!/usr/bin/env python3
"""
Install or update the gallery ViT checkpoint under models/gallery-classifier/<id>/.

CLI wrapper around gallery_classifier_version.install_gallery_classifier().
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gallery_classifier_version import (  # noqa: E402
    check_official_update_status,
    install_gallery_classifier,
)


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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing official checkpoint (never overwrites custom/modified)",
    )
    parser.add_argument(
        "--update-if-older",
        action="store_true",
        help="Download only when manifest version is newer than model_version.json",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Report update status; exit 2 if an official update is available",
    )
    parser.add_argument(
        "--mark-custom",
        action="store_true",
        help="Mark the default checkpoint as custom (disables automatic official updates)",
    )
    args = parser.parse_args()

    install_dir = Path(args.install_dir)
    if args.check_only:
        status = check_official_update_status(install_dir)
        print(f"[INFO] {status.message}")
        return install_gallery_classifier(
            install_dir,
            check_only=True,
        )

    bundle = Path(args.bundle_dir) if args.bundle_dir else None

    def _cli_progress(done: int, total: int, phase: str) -> None:
        if phase == "download" and total > 0:
            pct = min(100, int(done * 100 / total))
            if pct % 10 == 0 or done >= total:
                print(f"  ... {pct}%", flush=True)
        elif phase == "verify":
            print("[INFO] Verifying download...", flush=True)
        elif phase == "install":
            print("[INFO] Installing gallery classifier...", flush=True)

    code = install_gallery_classifier(
        install_dir,
        bundle,
        version=args.version or None,
        url=args.url or None,
        expected_sha256=args.sha256 or None,
        force=args.force,
        update_if_older=args.update_if_older,
        mark_custom=args.mark_custom,
        progress_callback=_cli_progress if not args.mark_custom else None,
    )
    if code == 0 and not args.mark_custom:
        from gallery_model_paths import gallery_classifier_dir

        print(f"[SUCCESS] Gallery classifier ready: {gallery_classifier_dir(install_dir)}")
    elif code == 1 and args.mark_custom:
        print("[ERROR] No classifier found to mark as custom.")
    return code


if __name__ == "__main__":
    sys.exit(main())
