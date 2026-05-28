#!/bin/bash

set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "SkySpotter macOS Build Script"
echo "============================="
echo ""

if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "[ERROR] This script is designed for macOS only."
    echo "Current OS: $OSTYPE"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH"
    exit 1
fi

if [ ! -f "icons/appicon.icns" ]; then
    echo "[WARNING] Icon file not found: icons/appicon.icns"
fi

VENV_DIR="$ROOT/rawviewer_env"
PYTHON_BIN="$VENV_DIR/bin/python3"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

if [ ! -x "$PYTHON_BIN" ]; then
    echo "[ERROR] Missing venv interpreter: $PYTHON_BIN"
    exit 1
fi

echo "Using virtual environment: $VENV_DIR"

if command -v brew >/dev/null 2>&1; then
    echo "Checking Homebrew dependencies for pyexiv2 (inih, gettext)..."
    brew list inih &>/dev/null || brew install inih
    brew list gettext &>/dev/null || brew install gettext
fi

echo "Upgrading pip..."
"$PYTHON_BIN" -m pip install --upgrade pip

echo "Installing dependencies..."
"$PYTHON_BIN" -m pip install --upgrade PyQt6 rawpy send2trash pyinstaller natsort exifread pyexiv2 Pillow psutil numpy qtawesome pyqtgraph reverse-geocoder pycountry huggingface-hub pyobjc-framework-Cocoa pyobjc-framework-CoreML pyobjc-framework-Quartz pyobjc-framework-Vision onnxruntime tokenizers sentencepiece protobuf onnxscript torchvision

"$PYTHON_BIN" -m pip uninstall -y sentence-transformers torch torchvision transformers scikit-learn scipy safetensors coremltools >/dev/null 2>&1 || true

echo "Cleaning previous builds..."
chmod -R u+w build dist 2>/dev/null || true
rm -rf build || true
chmod -R u+w dist 2>/dev/null || true
rm -rf dist || true
rm -f *.spec

echo "Building SkySpotter..."
if "$PYTHON_BIN" build.py; then
    echo ""
    echo "[SUCCESS] Build completed!"
    if [ -d "dist/SkySpotter.app" ]; then
        echo "  dist/SkySpotter.app"
    elif [ -d "dist/RAWviewer.app" ]; then
        echo "  dist/RAWviewer.app"
    fi
else
    echo "[ERROR] Build failed."
    exit 1
fi
