#!/usr/bin/env python3
"""
Build script for RAW Image Viewer Windows/macOS executable
Handles dependency installation and executable creation.
"""

VERSION = "1.0.0"

import os
import subprocess
import platform
import shutil
import time
import sys
import json
from pathlib import Path

# Repository root (directory containing this script)
REPO_ROOT = Path(__file__).resolve().parent


def _project_venv_python() -> Path:
    if platform.system() == "Windows":
        return REPO_ROOT / "SkySpotter_env" / "Scripts" / "python.exe"
    return REPO_ROOT / "SkySpotter_env" / "bin" / "python3"


def _running_inside_project_venv() -> bool:
    try:
        return Path(sys.executable).resolve() == _project_venv_python().resolve()
    except OSError:
        return False


def _is_externally_managed_python() -> bool:
    """True for Homebrew / Debian PEP 668 installs where ``pip install`` to system is blocked."""
    return (Path(sys.prefix) / "EXTERNALLY-MANAGED").is_file()


def _should_use_project_venv_for_build() -> bool:
    """
    Prefer ./SkySpotter_env so ``pip install`` / PyInstaller do not hit system Python limits.

    - macOS: always (matches ``scripts/launchers/build_macos.sh``; Homebrew 3.14 may block pip without an
      ``EXTERNALLY-MANAGED`` file under ``sys.prefix``).
    - Linux: when PEP 668 marker is present.
    Set ``SkySpotter_USE_SYSTEM_PYTHON_BUILD=1`` to skip and use the current interpreter.
    """
    if os.environ.get("SkySpotter_USE_SYSTEM_PYTHON_BUILD", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    if _running_inside_project_venv():
        return False
    if platform.system() == "Darwin":
        return True
    if _is_externally_managed_python():
        return True
    return False


def ensure_project_venv_and_reexec() -> None:
    """
    Create ./SkySpotter_env if needed and re-exec this script with that interpreter.

    Skips when already using ./SkySpotter_env (e.g. ``scripts/launchers/build_macos.sh``) or when
    ``SkySpotter_USE_SYSTEM_PYTHON_BUILD=1``.
    """
    if not _should_use_project_venv_for_build():
        return
    vpy = _project_venv_python()
    venv_dir = REPO_ROOT / "SkySpotter_env"
    if not vpy.is_file():
        if platform.system() == "Darwin":
            venv_msg = (
                "[INFO] Creating ./SkySpotter_env ??macOS builds default to an isolated venv "
                "(reliable pip/PyInstaller vs Homebrew Python). "
                "Set SkySpotter_USE_SYSTEM_PYTHON_BUILD=1 to opt out."
            )
        else:
            venv_msg = (
                "[INFO] Creating ./SkySpotter_env ??system Python is PEP 668 externally managed; "
                "pip cannot install into it."
            )
        print(venv_msg)
        rc = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=False,
        ).returncode
        if rc != 0 or not vpy.is_file():
            print(
                "[ERROR] Could not create ./SkySpotter_env. From the repo root try:\n"
                "  ./scripts/launchers/build_macos.sh\n"
                "or:  python3 -m venv SkySpotter_env && ./SkySpotter_env/bin/python3 -m pip install -U pip && "
                "./SkySpotter_env/bin/python3 build.py"
            )
            sys.exit(1)
    script = Path(__file__).resolve()
    argv = [str(vpy), str(script), *sys.argv[1:]]
    print(f"[INFO] Re-running build with project venv: {vpy}")
    os.execv(str(vpy), argv)


def run_command(cmd):
    # Support both string commands and lists
    if isinstance(cmd, list):
        result = subprocess.run(cmd)
    else:
        result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def update_macos_plist(app_path):
    """Update Info.plist in macOS app bundle to add file associations"""
    plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
    if not os.path.exists(plist_path):
        print(f"[WARNING] Info.plist not found at {plist_path}")
        return False
        
    try:
        import plistlib
        with open(plist_path, 'rb') as f:
            plist = plistlib.load(f)
            
        # Define supported extensions
        image_extensions = [
            'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'tif', 'tiff', 'heic',
            'cr2', 'cr3', 'nef', 'arw', 'dng', 'raf', 'orf', 'rw2', 'pef', 'srw', 'crw', 'mef', 'mrw'
        ]
        
        # Add CFBundleDocumentTypes if not present
        if 'CFBundleDocumentTypes' not in plist:
            plist['CFBundleDocumentTypes'] = []
            
        # Check if our document type is already defined
        doc_type_exists = any(
            doc.get('CFBundleTypeName') == 'Image File' for doc in plist['CFBundleDocumentTypes']
        )
        
        if not doc_type_exists:
            doc_type = {
                'CFBundleTypeName': 'Image File',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': [
                    'public.image',
                    'public.camera-raw-image'
                ],
                'CFBundleTypeExtensions': image_extensions
            }
            plist['CFBundleDocumentTypes'].append(doc_type)
            
        # Set a unique Bundle Identifier
        plist['CFBundleIdentifier'] = 'com.markyip.skyspotter'
        plist['CFBundleName'] = 'SkySpotter'
        plist['CFBundleDisplayName'] = 'SkySpotter Aviation Specialist'
        plist['CFBundleExecutable'] = 'SkySpotter'
        plist['CFBundlePackageType'] = 'APPL'
        plist['CFBundleShortVersionString'] = VERSION
        
        # Add macOS permission usage descriptions
        plist['NSDesktopFolderUsageDescription'] = 'SkySpotter needs access to your Desktop to display images.'
        plist['NSDocumentsFolderUsageDescription'] = 'SkySpotter needs access to your Documents folder to display images.'
        plist['NSDownloadsFolderUsageDescription'] = 'SkySpotter needs access to your Downloads folder to display images.'
        plist['NSRemovableVolumesUsageDescription'] = 'SkySpotter needs access to external volumes to display images from cameras or cards.'
        plist['NSPhotoLibraryUsageDescription'] = 'SkySpotter needs access to your photo library to display images.'
        plist['NSAppleEventsUsageDescription'] = 'SkySpotter needs to receive file open events from the system.'
        
        # macOS specific flags
        plist['LSMinimumSystemVersion'] = '10.15.0'
        plist['NSHighResolutionCapable'] = True
        plist['LSSupportsOpeningDocumentsInPlace'] = True
        plist['LSApplicationCategoryType'] = 'public.app-category.photography'

        with open(plist_path, 'wb') as f:
            plistlib.dump(plist, f)
        print("[SUCCESS] Updated Info.plist with Bundle ID, file associations and usage descriptions")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to update Info.plist: {e}")
        return False


def install_dependencies():
    """Install required dependencies"""
    print("Installing/upgrading dependencies...")
    system_name = platform.system()
    dependencies = [
        'PyQt6',
        'rawpy',
        'send2trash',
        'pyinstaller',
        'natsort',
        'exifread',
        'Pillow',  # Added for NEF thumbnail fallback
        'psutil',  # Added for system memory info in image_cache
        'numpy',   # Required for image processing (used in all modules)
        'qtawesome', # Required for icons in main.py
        'pyqtgraph',
        'reverse-geocoder',  # Offline city/country lookup from GPS EXIF
        'pycountry',         # ISO country code -> full country name
        'tokenizers',        # Lightweight tokenizer for SigLIP (Aviation Specialist)
        'sentencepiece',     # SigLIP tokenizer dependency
        'protobuf',          # ONNX/Transformers dependency
        'torchvision',       # Optimized image processing for ViT
        'onnxscript',        # Required for ONNX model export
    ]

    if system_name == "Windows":
        # Windows semantic backend will move to ONNX
        dependencies.append('onnxruntime-directml')
        dependencies.append('mediapipe')
        dependencies.append('opencv-contrib-python')
    elif system_name == "Darwin":
        dependencies.append('onnxruntime-silicon')
        dependencies.append('huggingface-hub')
        dependencies.append('pyobjc-framework-CoreML')
        dependencies.append('pyobjc-framework-Quartz')
        dependencies.append('pyobjc-framework-Vision')
    if system_name in ("Darwin", "Windows"):
        dependencies.append("pyexiv2")

    for dep in dependencies:
        print(f"Installing {dep}...")
        if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", dep]):
            print(f"[ERROR] Failed to install {dep}")
            return False

    if system_name == "Darwin":
        print("Installing pyobjc-framework-Cocoa (macOS share sheet)...")
        if not run_command(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pyobjc-framework-Cocoa"]
        ):
            print("[WARNING] pyobjc-framework-Cocoa install failed; Share may not work in the built app.")
    elif system_name == "Windows":
        print("Installing pywin32 (Windows Share verb)...")
        if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pywin32"]):
            print("[WARNING] pywin32 install failed; Share may not work in the built app.")

    print("Dependencies installed successfully!")
    return True


def _darwin_ensure_homebrew_pyexiv2_libs() -> None:
    """
    pyexiv2's bundled libexiv2.dylib expects Homebrew libinih / gettext on the build machine
    (see https://github.com/LeoHsiao1/pyexiv2/blob/master/docs/Tutorial.md FAQ).
    """
    if platform.system() != "Darwin":
        return
    brew = shutil.which("brew")
    if not brew:
        print(
            "[INFO] Homebrew (`brew`) not on PATH. If `import pyexiv2` fails, install "
            "https://brew.sh then run: brew install inih gettext"
        )
        return
    for formula in ("inih", "gettext"):
        listed = subprocess.run(
            [brew, "list", formula],
            capture_output=True,
        )
        if listed.returncode != 0:
            print(
                f"[INFO] Installing Homebrew `{formula}` (native dependency for pyexiv2 / Exiv2)..."
            )
            subprocess.run([brew, "install", formula], check=False)


def _darwin_preflight_pyexiv2_import() -> None:
    """Fail fast with a clear message before PyInstaller touches pyexiv2."""
    if platform.system() != "Darwin":
        return
    try:
        import pyexiv2  # noqa: F401
    except Exception as e:
        print(
            "[ERROR] pyexiv2 failed to import (required for this macOS build).\n"
            "  Install native libraries, then re-run:\n"
            "    brew install inih gettext\n"
            f"  Underlying error: {e}"
        )
        sys.exit(1)


def apply_build_feature_flags(*, enable_blur_score: bool | None = None) -> None:
    """Write config/skyspotter_features.json before packaging."""
    script = REPO_ROOT / "scripts" / "set_features.py"
    if not script.is_file():
        print(f"[WARNING] Missing {script}; skipping feature flag update")
        return
    if enable_blur_score is True:
        cmd = [sys.executable, str(script), "--copy-experimental"]
        label = "experimental (blur_score on)"
    elif enable_blur_score is False:
        cmd = [sys.executable, str(script), "--blur-score", "off"]
        label = "default (blur_score off)"
    else:
        env = os.environ.get("SkySpotter_BUILD_ENABLE_BLUR_SCORE", "").strip().lower()
        if env in ("1", "true", "yes", "on"):
            cmd = [sys.executable, str(script), "--copy-experimental"]
            label = "experimental (blur_score on, from env)"
        elif env in ("0", "false", "no", "off"):
            cmd = [sys.executable, str(script), "--blur-score", "off"]
            label = "default (blur_score off, from env)"
        else:
            return
    print(f"[INFO] Applying build feature flags: {label}")
    if not run_command(cmd):
        print("[WARNING] Feature flag update failed; continuing with existing config")


def main():
    ensure_project_venv_and_reexec()

    import argparse

    parser = argparse.ArgumentParser(description="Build SkySpotter installer / executable")
    parser.add_argument(
        "--enable-blur-score",
        action="store_true",
        help="Bake experimental blur scoring into config/skyspotter_features.json for this build",
    )
    parser.add_argument(
        "--disable-blur-score",
        action="store_true",
        help="Ensure blur scoring is off in config/skyspotter_features.json (default release)",
    )
    args, _unknown = parser.parse_known_args()
    if args.enable_blur_score and args.disable_blur_score:
        print("[ERROR] Use only one of --enable-blur-score / --disable-blur-score")
        sys.exit(1)
    if args.enable_blur_score:
        apply_build_feature_flags(enable_blur_score=True)
    elif args.disable_blur_score:
        apply_build_feature_flags(enable_blur_score=False)
    else:
        apply_build_feature_flags(enable_blur_score=None)

    system_name = platform.system()
    if system_name == 'Windows':
        print("SkySpotter Windows Build Script")
    elif system_name == 'Darwin':
        print(f"SkySpotter macOS Build Script v{VERSION}")
    else:
        print(f"SkySpotter Build Script v{VERSION} ({system_name})")
    print("==============================")
    print("")

    # Install dependencies first
    if not install_dependencies():
        print("[ERROR] Dependency installation failed.")
        sys.exit(1)

    if platform.system() == "Darwin":
        _darwin_ensure_homebrew_pyexiv2_libs()
        _darwin_preflight_pyexiv2_import()

    print("")
    print("Building SkySpotter executable...")

    # Import PyQt6 after installation
    try:
        import PyQt6
    except ImportError:
        print("[ERROR] PyQt6 not available after installation")
        sys.exit(1)

    # Clean previous builds
    print("Cleaning previous builds...")
    
    # Try to kill any running SkySpotter.exe processes on Windows
    if platform.system() == 'Windows':
        try:
            result = subprocess.run(
                ['taskkill', '/F', '/IM', 'SkySpotter.exe', '/T'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("Closed running SkySpotter.exe instances")
                time.sleep(1)  # Wait a moment for file handles to release
        except Exception as e:
            print(f"[WARNING] Could not close running instances: {e}")
    
    # Clean build directory
    if os.path.exists('build'):
        try:
            print("Cleaning build directory...")
            shutil.rmtree('build')
        except PermissionError as e:
            print(f"[WARNING] Could not delete build directory: {e}")
            print("  Continuing anyway...")
        except Exception as e:
            print(f"[WARNING] Error cleaning build directory: {e}")
    
    # Clean dist directory (try to delete specific files first)
    if os.path.exists('dist'):
        try:
            print("Cleaning dist directory...")
            # Try to delete the exe file specifically first
            exe_name = 'SkySpotter.exe' if platform.system() == 'Windows' else 'SkySpotter'
            exe_path = os.path.join('dist', exe_name)
            if os.path.exists(exe_path):
                try:
                    os.remove(exe_path)
                    print(f"  Removed {exe_name}")
                except PermissionError:
                    print("[ERROR] Cannot delete {exe_name} - it may be running.")
                    print("  Please close SkySpotter and try again.")
                    sys.exit(1)
                except Exception as e:
                    print(f"[WARNING] Could not delete {exe_name}: {e}")
            
            # Try to remove the entire dist directory
            try:
                shutil.rmtree('dist')
            except PermissionError:
                print("[WARNING] Some files in dist directory are locked, but continuing...")
            except Exception as e:
                print(f"[WARNING] Could not fully clean dist directory: {e}")
        except Exception as e:
            print(f"[WARNING] Error cleaning dist directory: {e}")

    # Prevent stale local logs from being packed into installer payload ("src;src").
    logs_dir = Path("src") / "logs"
    if logs_dir.exists():
        try:
            print("Cleaning src/logs before packaging...")
            shutil.rmtree(logs_dir)
        except Exception as e:
            print(f"[WARNING] Could not clean src/logs: {e}")

    # Platform-agnostic icon
    is_aviation = os.environ.get("SkySpotter_AVIATION_BUILD", "").strip().lower() in ("1", "true", "yes")
    
    if platform.system() == 'Windows':
        icon_file = os.path.join('icons', 'appicon_aviation.ico' if is_aviation else 'appicon.ico')
    elif platform.system() == 'Darwin':
        icon_file = os.path.join('icons', 'appicon_aviation.icns' if is_aviation else 'appicon.icns')
    else:
        icon_file = os.path.join('icons', 'appicon_aviation.ico' if is_aviation else 'appicon.ico')  # fallback
    icon_path = os.path.abspath(icon_file)
    if not os.path.exists(icon_path):
        print(f"[WARNING] Icon file not found: {icon_path}")
        icon_arg = ''
    else:
        icon_arg = f'--icon "{icon_path}"'
    # Find PyQt6 imageformats plugin path
    pyqt_path = os.path.dirname(PyQt6.__file__)
    if platform.system() == 'Windows':
        imageformats_src = os.path.join(
            pyqt_path, 'Qt6', 'plugins', 'imageformats')
        add_data_sep = ';'
    elif platform.system() == 'Darwin':
        imageformats_src = os.path.join(
            pyqt_path, 'Qt6', 'plugins', 'imageformats')
        add_data_sep = ':'
    else:
        imageformats_src = os.path.join(
            pyqt_path, 'Qt6', 'plugins', 'imageformats')
        add_data_sep = ':'
    # Add --add-data for imageformats and icons directory
    add_data_args = [
        f'--add-data "{imageformats_src}{add_data_sep}imageformats"',
        f'--add-data "icons{add_data_sep}icons"',
        f'--add-data "config{add_data_sep}config"',
    ]
    if platform.system() == "Darwin":
        m2 = Path("models/mobileclip2_coreml")
        if m2.is_dir() and list(m2.glob("*_image.mlpackage")):
            add_data_args.append(
                f'--add-data "{m2.resolve()}{add_data_sep}models/mobileclip2_coreml"'
            )
            print("[INFO] Bundling MobileCLIP2 Core ML from models/mobileclip2_coreml/")
    elif platform.system() == "Windows":
        add_data_args.append('--add-data "uninstall.bat;."')
        add_data_args.append('--add-data "scripts;scripts"')
    add_data_arg_str = " ".join(add_data_args)

    src_path = os.path.abspath('src')
    
    cmd_base = [
        sys.executable, "-m", "PyInstaller",
        "--windowed",
        "--paths", src_path,
        "--hidden-import", "SkySpotter_ui.gallery_view",
        "--hidden-import", "SkySpotter_ui.widgets",
        "--hidden-import", "natsort",
        "--hidden-import", "send2trash",
        "--hidden-import", "metadata_backend",
        "--name", "SkySpotter"
    ]
    try:
        import pyexiv2  # noqa: F401

        if platform.system() in ("Darwin", "Windows"):
            cmd_base.extend(["--hidden-import", "pyexiv2", "--collect-all", "pyexiv2"])
            print("[INFO] PyInstaller: bundling pyexiv2 with --collect-all (native Exiv2 libs).")
    except ImportError:
        print(
            "[WARNING] pyexiv2 not importable; build continues without pyexiv2 bundling. "
            "Install pyexiv2 before packaging for EXIF read/write in the app."
        )
    
    # Bundling ONNX Runtime for lightweight specialist models (cross-platform)
    try:
        import onnxruntime
        cmd_base.extend(["--hidden-import", "onnxruntime", "--collect-all", "onnxruntime"])
        print("[INFO] PyInstaller: bundling onnxruntime with --collect-all.")
    except ImportError:
        print("[WARNING] onnxruntime not found; specialist models may be disabled.")

    # Bundling HuggingFace Hub and Tokenizers for on-demand model acquisition
    try:
        import huggingface_hub
        cmd_base.extend(["--hidden-import", "huggingface_hub", "--collect-all", "huggingface_hub"])
        print("[INFO] PyInstaller: bundling huggingface_hub with --collect-all.")
    except ImportError:
        print("[WARNING] huggingface_hub not found; model download will fail.")

    try:
        import tokenizers
        cmd_base.extend(["--hidden-import", "tokenizers", "--collect-all", "tokenizers"])
        print("[INFO] PyInstaller: bundling tokenizers with --collect-all.")
    except ImportError:
        print("[WARNING] tokenizers not found; specialist search will fail.")

    if platform.system() == "Darwin":
        cmd_base.extend([
            "--hidden-import", "objc",
            "--hidden-import", "AppKit",
            "--hidden-import", "Foundation",
            "--hidden-import", "CoreML",
            "--hidden-import", "Quartz",
            "--hidden-import", "Vision",
            "--exclude-module", "coremltools",
            "--exclude-module", "torch",
            "--exclude-module", "torchvision",
            "--exclude-module", "sentence_transformers",
            "--exclude-module", "transformers",
            "--exclude-module", "sklearn",
            "--exclude-module", "scipy",
            "--exclude-module", "safetensors",
        ])
    elif platform.system() == "Windows":
        cmd_base.extend([
            "--hidden-import", "win32com.client",
            "--hidden-import", "pythoncom",
            "--hidden-import", "pywintypes",
        ])
        # Windows uses Pixi bootstrap. Exclude everything except PyQt6 and standard libs
        cmd_base.extend([
            "--exclude-module", "torch",
            "--exclude-module", "torchvision",
            "--exclude-module", "tensorboard",
            "--exclude-module", "sentence_transformers",
            "--exclude-module", "transformers",
            "--exclude-module", "scipy",
            "--exclude-module", "matplotlib",
            "--exclude-module", "onnxruntime",
            "--exclude-module", "rawpy",
            "--exclude-module", "numpy",
            "--exclude-module", "PIL",
            "--exclude-module", "pyexiv2",
            "--exclude-module", "pyqtgraph",
            "--exclude-module", "natsort",
            "--exclude-module", "send2trash",
            "--exclude-module", "exifread",
        ])
        
        add_data_args.append('--add-data "pixi.toml;."')
        add_data_args.append('--add-data "pixi.lock;."')
        add_data_args.append('--add-data "src;src"')
    
    if platform.system() == 'Darwin':
        cmd_base.append("--onedir")
        cmd_base.extend(["--osx-bundle-identifier", "com.markyip.skyspotter"])
    else:
        cmd_base.append("--onefile")
        
    if icon_arg:
        if platform.system() == 'Windows':
            cmd_base.extend(["--icon", icon_path])
        else:
            cmd_base.extend(["--icon", icon_path])
            
    # Add data
    for arg in add_data_args:
        cmd_base.extend(["--add-data", arg.split('--add-data ')[-1].strip('"')])
        
    if platform.system() == 'Windows':
        cmd_base.append("src/bootstrap.py")
    else:
        cmd_base.append("src/main.py")

    print(f"Running: {' '.join(cmd_base)}")
    if not run_command(cmd_base):
        print("[ERROR] Build failed.")
        sys.exit(1)
    if platform.system() == 'Windows':
        exe_path = Path('dist/SkySpotter/SkySpotter.exe')
    else:
        exe_path = Path('dist/SkySpotter.app')
    if exe_path.exists():
        print(f"[SUCCESS] Executable created: {exe_path}")
        
        # Windows-specific post-build steps: Uninstall script and Installer
        if platform.system() == 'Windows':
            print("Preparing Windows distribution extras...")
            dist_dir = REPO_ROOT / "dist" / "SkySpotter"
            
            # 1. Copy uninstall.bat to dist folder
            uninst_src = REPO_ROOT / "uninstall.bat"
            if uninst_src.exists():
                shutil.copy2(uninst_src, dist_dir / "uninstall.bat")
                print(f"  Copied uninstall.bat to {dist_dir}")
            
            # 2. Bundle gallery classifier for the installer
            classifier_src = (
                REPO_ROOT / "models" / "gallery-classifier" / "skyspotter-military-aircraft-vit"
            )
            classifier_dst = dist_dir / "models" / "gallery-classifier" / "skyspotter-military-aircraft-vit"
            checkpoint = classifier_src / "model.safetensors"
            if checkpoint.is_file():
                if classifier_dst.exists():
                    shutil.rmtree(classifier_dst.parent.parent)
                classifier_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(classifier_src, classifier_dst)
                manifest_src = REPO_ROOT / "models" / "gallery-classifier" / "manifest.json"
                if manifest_src.is_file():
                    shutil.copy2(manifest_src, classifier_dst.parent / "manifest.json")
                print(f"  Copied gallery classifier to {classifier_dst}")
            else:
                print(
                    "  [WARNING] gallery classifier weights missing — run: git lfs pull\n"
                    "  Installer will try SkySpotter_APP_MODEL_URL or GitHub release zip."
                )

            # 3. Build Installer EXE
            build_installer()

        if platform.system() == 'Darwin':
            print("Patching macOS Info.plist...")
            update_macos_plist(str(exe_path))
            print("Re-signing macOS app bundle (ad-hoc)...")
            run_command(['codesign', '--force', '--deep', '-s', '-', str(exe_path)])
            print("Clearing macOS quarantine attribute...")
            run_command(['xattr', '-cr', str(exe_path)])
    else:
        print("[ERROR] Executable was not created!")
        
    if platform.system() == 'Windows' and exe_path.exists():
        print("Build completed successfully.")

def build_installer():
    """Build the standalone installer EXE on Windows"""
    print("")
    print("Building SkySpotter Installer...")
    
    if platform.system() != 'Windows':
        print("[SKIP] Installer build only supported on Windows.")
        return

    bootstrap_script = REPO_ROOT / "src" / "bootstrap.py"
    if not bootstrap_script.exists():
        print(f"[ERROR] Installer entry not found: {bootstrap_script}")
        return

    icon_path = REPO_ROOT / "icons" / "appicon.ico"

    installer_add_data = [
        f"src{os.pathsep}src",
        f"scripts{os.pathsep}scripts",
        f"icons{os.pathsep}icons",
        f"config{os.pathsep}config",
        f"pixi.toml{os.pathsep}.",
        f"pixi.lock{os.pathsep}.",
        f"uninstall.bat{os.pathsep}.",
    ]
    classifier_dir = REPO_ROOT / "models" / "gallery-classifier"
    if (classifier_dir / "skyspotter-military-aircraft-vit" / "model.safetensors").is_file():
        installer_add_data.append(f"models{os.pathsep}models")
        print("[INFO] Bundling models/gallery-classifier/ into SkySpotter_Setup.exe")
    else:
        print(
            "[WARNING] Gallery classifier not bundled — run git lfs pull or set "
            "SkySpotter_APP_MODEL_URL before building the installer"
        )

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SkySpotter_Setup",
        "--clean",
        str(bootstrap_script),
    ]
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    for spec in installer_add_data:
        cmd.extend(["--add-data", spec])
    
    # Remove empty strings from cmd (like if icon_path didn't exist)
    cmd = [c for c in cmd if c]
    
    print(f"Running: {' '.join(cmd)}")
    if run_command(cmd):
        print("[SUCCESS] Installer created: dist/SkySpotter_Setup.exe")
    else:
        print("[ERROR] Installer build failed.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[CRITICAL ERROR] Build script crashed: {e}")
        sys.exit(1)
    
    # If main() returns None/0 but we want to check if it really succeeded
    # Actually main() doesn't return anything, so we should check for failures inside main()
