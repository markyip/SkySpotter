# SkySpotter v1.0.0 (Aviation Specialist Edition)

<p align="center">
  <img src="icons/appicon.ico" alt="SkySpotter Icon" width="256">
</p>

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✈️ Meet SkySpotter AI

You're an aviation photographer who just returned from RIAT or spent a day at the Mach Loop. You took thousands of shots of fast jets, helicopters, and flybys — and now you're facing the real challenge: **sorting through them.**

**SkySpotter** (forked from RAWviewer) is a specialized AI-powered image viewer built specifically for aviation photographers. It features an onboard **Military Aircraft Classifier** that uses advanced computer vision to identify, categorize, and organize your aircraft photos with a single click.

## ✨ Core AI Features

<<<<<<< HEAD
- Instant file previewing: No import steps — just drag & drop.
- Zoom in with a single key to check sharpness immediately.
- Stay in zoomed mode while browsing with arrow keys.
- Quickly remove blurry photos from the queue with `↓` (moves them to a discard folder).
- No complex controls to memorize — just the essential keys to move fast.

This is a **pre-filtering tool**, letting you go through hundreds of RAW files efficiently **before** committing to editing them in Lightroom or Photoshop.

## 🔍 What is RAWviewer?
**RAWviewer** is a fast, modern, cross-platform image viewer for Windows and macOS, built with PyQt6. It supports advanced zooming, panning, and direct file association, allowing RAW files to be opened with a double-click.

## ✨ Features

- **Cross-platform support**: Windows and macOS
- **Ultra-Fast Performance**: Instant folder loading (scans thousands of images in milliseconds) using optimized algorithms
- **High-Fidelity Thumbnails**: Uses high-quality **LANCZOS resampling** and **2x oversampling** for crystal-clear previews on Retina and 4K displays.
- **Smart Prefetching**: Predictively loads relevant images in the background for zero-latency navigation
- **Memory-First Cache (Default)**: Uses fast in-memory caching by default with no disk/SQLite writes
- **Optional Persistent Cache**: Set `RAWVIEWER_PERSISTENT_CACHE=1` to re-enable disk/SQLite cache persistence
- **Gallery View**: Justified grid layout with virtualized rendering, EXIF-aware ordering, and current-image positioning
- **Gallery search (macOS + Core ML bundle)**: Free-text semantic ranking plus structured metadata filters (`camera:`, ISO, GPS, **`format:`** / **`ext:`**, and more — see README table below)
- **Wide RAW format support**: Canon (CR2, CR3), Nikon (NEF), Sony (ARW), Adobe DNG, and many more
- **Robust Orientation Handling**: Definitive fixes for Sony ARW and other RAW formats, ensuring images are always displayed upright
- **Pillarbox-Free Gallery**: Accurately calculates aspect ratios to prevent black bars in the gallery view
- **macOS File Association**: Fully integrated with macOS Finder; can be set as the default viewer and supports double-click to open
- **Intuitive navigation**: Keyboard shortcuts, mouse controls, and scroll wheel support
- **Zoom functionality**: Fit-to-window and 100% zoom modes with smooth panning, including native Mac trackpad pinch-to-zoom
- **File management**: Move images to discard folder or delete permanently
- **EXIF data display**: View camera settings, focal length, ISO, aperture, and capture information with robust metadata extraction
- **Session persistence**: Remembers your last opened folder, image, and view mode
- **Single-image histogram**: Press `H` to show or hide the strip while viewing one image
- **Modern Installer**: Lightweight executable that automatically provisions a self-contained Python environment and downloads AI models on first launch
- **Professional Startup**: Synchronized native and Qt splash screens for a flicker-free, premium launch experience.
- **Modern UI**: Material Design 3 aesthetics with Font Awesome icons (via qtawesome) and non-intrusive loading indicators
- **Platform-specific chrome**: On Windows, the bottom bar omits Share (no stable system share without WinRT interop); **Share** remains on macOS.
- **Non-destructive visual rotate**: Rotate in viewer by 90° steps without modifying original files (including RAW), with gallery-visible tiles refreshed immediately.
- **Precision Focus Area Detection**: Overlays the camera's focus point(s) using manufacturer-specific MakerNote data (Canon, Nikon, Sony) plus EXIF SubjectArea/SubjectLocation with orientation-aware mapping and robust coordinate scaling.
=======
- **Automated Aircraft Classification**: Our custom Vision Transformer (ViT) model recognizes over 100+ military aircraft types (e.g., F-35, AH-64, B-2, Eurofighter Typhoon).
- **One-Click Auto-Sort**: Simply click the **Magic Wand** icon in the gallery toolbar. SkySpotter will analyze every image in your folder and automatically sort them into dedicated subfolders based on the aircraft model detected!
- **AI Background Removal**: To maximize identification accuracy, SkySpotter features an integrated U-2-Net model that strips away complex backgrounds (like skies and trees) so the classifier can focus purely on the aircraft's silhouette.
- **Attention-Adjusted Cropping**: The AI reads your camera's EXIF focus points to crop tightly around the subject before classification, ensuring it doesn't get confused by tiny aircraft in large frames.
- **Hardware Acceleration**:
  - **macOS**: Built-in Apple Neural Engine / Metal support via the `CoreMLExecutionProvider`.
  - **Windows**: Full GPU acceleration support via `TensorrtExecutionProvider` and DirectML.
>>>>>>> origin/main

## 🚀 Quick Start

### Download Executable

#### Windows
<<<<<<< HEAD
1. Download the latest release from the [Releases Page](https://github.com/markyip/RAWviewer/releases/latest)
2. Download `RAWviewer.exe` directly (no zip extraction needed)
3. Double-click `RAWviewer.exe` to initiate the installation process. It will automatically download the necessary dependencies and AI models to a destination of your choice.
4. Launch RAWviewer from the Desktop shortcut created during installation! (You can safely delete the original `RAWviewer.exe` installer afterwards).
=======

1. Download the latest release from the [Releases Page](https://github.com/markyip/SkySpotter/releases/latest)
2. Double-click `SkySpotter.exe` to launch
>>>>>>> origin/main

#### macOS

1. Download and extract the latest macOS `.zip` release.
2. Drag `SkySpotter.app` to your **Applications** folder.
3. **CRITICAL FIRST STEP:** You must run this command in your Terminal once to remove the quarantine flag:
   ```bash
   xattr -cr /Applications/SkySpotter.app
   ```

## ⌨️ Keyboard Shortcuts

- **Space**: Toggle between fit-to-window and 100% zoom
- **`Esc`**: Return to Gallery View (from Single View)
- **`←`/`→` arrows**: Navigate between images
- **`↓`**: Move current image to Discard folder
- **Delete**: Delete current image (with confirmation)
- **`H`**: Show or hide the single-image histogram strip
- **`F`**: Toggle dashed focus/subject indicator overlay (amber = maker AF, lime = EXIF subject area)

## 🏗️ Building from Source

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Windows

**Option 1: Using batch script (recommended)**

```batch
# Run the automated build script
build_windows.bat
```

**Option 2: Manual build**

```bash
# Activate virtual environment (if using one)
skyspotter_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build executable
python build.py
```

### macOS

```bash
# Run the automated build script
./build_macos.sh
```

### Dependencies

All dependencies are listed in `requirements.txt`:

- PyQt6 >= 6.6.0
- rawpy >= 0.25.0
- numpy >= 2.0.0
- Pillow >= 10.0.0
- send2trash >= 1.8.0
- pyinstaller >= 6.0.0
- natsort >= 8.4.0
- exifread >= 3.0.0
- psutil >= 5.9.0
- pyqtgraph >= 0.13.0
- qtawesome >= 1.2.0

## 🐛 Troubleshooting

### Windows

- **"Windows protected your PC"**: Click "More info" → "Run anyway"
- **Antivirus warnings**: Add SkySpotter to your antivirus exclusions
- **Performance issues**: Try running as administrator
- **AttributeError with stdout**: This is normal for windowed builds - the application runs without a console window

### macOS

- **"App is damaged and should be moved to the Trash" / "Apple could not verify SkySpotter is free of malware"**:
  - **Why it happens**: Apple heavily restricts apps downloaded outside the App Store that aren't signed with a paid developer certificate. On newer macOS versions (especially Apple Silicon M1/M2/M3), macOS breaks the app's ad-hoc signature and aggressively blocks opening it.
  - **The Fix (Fastest)**: Open your **Terminal** app and run the following command to remove the quarantine flag:
    ```bash
    xattr -cr /Applications/SkySpotter.app
    ```
    _(Note: If you placed the app somewhere other than the Applications folder, update the path accordingly)._

- **"Symbol not found: (\_mkfifoat)" or App crashes instantly on macOS 12 (Monterey) or older**:
  - **Why it happens**: The pre-built release is compiled using a newer macOS 13+ SDK. Older macOS versions do not have the required system files to run it.
  - **The Fix**: You must build the app locally (see the "Ultimate Fix" below).

#### 🛠️ The Ultimate Fix: Build Locally (Solves Both Issues Above)

If you are on macOS 12 or older, OR if you simply want to permanently bypass all Gatekeeper/Quarantine warnings forever, you can build the app directly on your own machine. It takes about 2 minutes:

1. **Install Python 3.10, 3.11, or 3.12** (We recommend the official installer from [python.org](https://www.python.org/downloads/macos/)).
2. **Open Terminal** and run these commands to download and build:
   ```bash
   git clone https://github.com/markyip/SkySpotter.git
   cd SkySpotter
   ./build_macos.sh
   ```
   This will automatically create a perfectly compatible, warning-free `SkySpotter.app` inside the `dist/` folder!

#### 🔧 Local Build Troubleshooting

- **Error: "No matching distribution found for pyexiv2"**
  - **Why it happens**: You are using an older version of Python (like macOS Monterey's default Python 3.9) on an Apple Silicon (M1/M2) Mac. `pyexiv2` does not provide pre-compiled packages for that specific combination.
  - **The Fix**:
    1. Install a newer version of Python (e.g., Python 3.11).
    2. **CRITICAL:** If you previously ran the build script, it created a virtual environment stuck on the old Python version. Delete it by running `rm -rf skyspotter_env`.
    3. Re-run `./build_macos.sh` (If it still uses 3.9, explicitly point to your new Python, e.g., `/usr/local/bin/python3 ./build_macos.sh`).

- **Error: Massive C++ compilation failures / PyQt6 missing wheels**
  - **Why it happens**: You are using a bleeding-edge version of Python (like Python 3.14). It takes the open-source community several months to build pre-compiled packages for brand-new Python versions. Without a wheel, the installer attempts to compile massive UI frameworks like PyQt6 from raw C++ source code, which usually fails.
  - **The Fix**: Roll back to a widely supported "sweet spot" version like **Python 3.11** or **3.12**, where every single required library has highly stable, pre-compiled macOS packages ready to download instantly. Remember to delete your old `skyspotter_env` folder before rebuilding!

- **Homebrew delays on macOS 12 Monterey or older**:
  - Homebrew has officially dropped "binary bottle" support for Monterey. However, **it still works**. When the build script attempts to `brew install inih gettext`, Homebrew will simply compile them from source on your machine. This is completely normal but may take 2-3 extra minutes.

- **Permission Denied / Cannot Read Folder**: Modern macOS requires explicit permission for apps to access the Desktop or Documents.
  1. Go to **System Settings** > **Privacy & Security** > **Full Disk Access**.
  2. Click the **+** button and add `SkySpotter.app`.
  3. Toggle it to **ON**.

- **"Semantic search unavailable" / asks to download models even in packaged app**:
  1. Open `SkySpotter.app/Contents/Resources/models/mobileclip2_coreml/`.
  2. Confirm either **S2** pair (`mobileclip_s2_*`) or **S0 app-export** pair (`mobileclip2_s0_*`) exists, plus `bpe_simple_vocab_16e6.txt.gz`.
  3. If missing, rebuild with `models/mobileclip2_coreml/` present before running `python build.py`.

## 🧠 Customizing the Classifier

SkySpotter is equipped with scripts that make it incredibly easy to train a custom image classifier on your own datasets (e.g., classifying bird species or cars).

1. **Organize Your Data**: Create a folder (e.g., `./CustomDataSet/Eagle/`, `./CustomDataSet/Sparrow/`).
2. **Background Removal**: Use `scripts/batch_bg_pipeline.py` to strip the backgrounds and tightly crop your images before training.
3. **Train the Model**: Run `python scripts/train_aviation_specialist.py`.
4. **Export to ONNX**: Run `python scripts/export_to_onnx.py`. Replace the default `.onnx` model in `src/models/` with your new one!

## 📁 Supported Image Formats

- **RAW**: Canon (CR2, CR3), Nikon (NEF), Sony (ARW), Adobe DNG, Olympus, Panasonic, Fujifilm, and more.
- **Standard**: JPG, JPEG, TIFF, HEIF

## 🏛️ Architecture & Dependencies

SkySpotter uses a multi-threaded `QThreadPool` for AI inference, allowing up to 4 images to be processed and sorted concurrently.

Required hardware acceleration packages (install via pip depending on your system):

- macOS: `onnxruntime-silicon`
- Windows: `onnxruntime-directml` or `onnxruntime-gpu`

## ☕ Support

If you find SkySpotter useful and it's become part of your workflow, feel free to chip in to help fund my **RIAT tickets for next year**. Enjoy organizing your airshow shots! 📸
