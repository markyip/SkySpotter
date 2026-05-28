# SkySpotter v1.0.0 (Aviation Specialist Edition)



Version
License

## ✈️ Meet SkySpotter AI

You're an aviation photographer who just returned from RIAT or spent a day at the Mach Loop. You took thousands of shots of fast jets, helicopters, and flybys — and now you're facing the real challenge: **sorting through them.**

**SkySpotter** is a specialized AI-powered image viewer built specifically for aviation photographers. It features an onboard **Military Aircraft Classifier** that uses advanced computer vision to identify, categorize, and organize your aircraft photos with a single click.

## ✨ Core AI Features

- Instant file previewing: No import steps — just drag & drop.
- Zoom in with a single key to check sharpness immediately.
- Stay in zoomed mode while browsing with arrow keys.
- Quickly remove blurry photos from the queue with `↓` (moves them to a discard folder).
- No complex controls to memorize — just the essential keys to move fast.

This is a **pre-filtering tool**, letting you go through hundreds of RAW files efficiently **before** committing to editing them in Lightroom or Photoshop.

## 🔍 What is SkySpotter?

**SkySpotter** is a fast, modern, cross-platform image viewer for Windows and macOS, built with PyQt6. It supports advanced zooming, panning, and direct file association, allowing RAW files to be opened with a double-click.

## ✨ Features

- **Automated Aircraft Classification**: Our custom Vision Transformer (ViT) model recognizes over 100+ military aircraft types (e.g., F-35, AH-64, B-2, Eurofighter Typhoon).
- **One-Click Auto-Sort**: Click the **Magic Wand** in the gallery toolbar to move images into subfolders by detected aircraft type. After sorting, the gallery still shows those files (see folder scope below).
- **GPU acceleration**: On **Windows**, aircraft detection uses **DirectML** so folder indexing can use your graphics card without extra setup. On **Mac**, Apple Silicon Macs use the built-in GPU when available.
- **Cross-platform support**: Windows and macOS
- **Ultra-Fast Performance**: Instant folder loading (scans thousands of images in milliseconds) using optimized algorithms
- **Smart Prefetching**: Predictively loads relevant images in the background for zero-latency navigation
- **Memory-First Cache (Default)**: Uses fast in-memory caching by default with no disk/SQLite writes
- **Gallery View**: Justified grid layout with virtualized rendering, EXIF-aware ordering, and current-image positioning. When you open a folder, the gallery lists images in that folder **and one level of child subfolders** (e.g. `F-35/`, `Typhoon/`) — not deeper nested trees. Hidden folders (names starting with `.`) and a `Discard` subfolder are skipped.
- **Gallery filters**: EXIF/metadata filters plus **aircraft label** search (`aircraft:`, or type a model name after indexing); optional neural semantic search is off by default (see below)
- **Wide RAW format support**: Canon (CR2, CR3), Nikon (NEF), Sony (ARW), Adobe DNG, and many more
- **macOS File Association**: Fully integrated with macOS Finder; can be set as the default viewer and supports double-click to open
- **Intuitive navigation**: Keyboard shortcuts, mouse controls, and scroll wheel support
- **File management**: Move images to discard folder or delete permanently
- **EXIF data display**: View camera settings, focal length, ISO, aperture, and capture information with robust metadata extraction
- **Single-image histogram**: Press `H` to show or hide the strip while viewing one image
- **Non-destructive visual rotate**: Rotate in viewer by 90° steps without modifying original files (including RAW), with gallery-visible tiles refreshed immediately.
- **Precision Focus Area Detection**: Overlays the camera's focus point(s) using manufacturer-specific MakerNote data (Canon, Nikon, Sony) plus EXIF SubjectArea/SubjectLocation with orientation-aware mapping and robust coordinate scaling.

## 🚀 Quick Start

### Download Executable

#### Windows

1. Download the latest release from the [Releases Page](https://github.com/markyip/SkySpotter/releases/latest)
2. Download `SkySpotter.exe` directly (no zip extraction needed)
3. Double-click `SkySpotter.exe` to initiate the installation process. It will automatically download the necessary dependencies and AI models to a destination of your choice.
4. Launch SkySpotter from the Desktop shortcut created during installation! (You can safely delete the original `SkySpotter.exe` installer afterwards).

#### macOS

1. Download the latest release from the [Releases Page](https://github.com/markyip/SkySpotter/releases/latest)
2. Download and extract the latest macOS `.zip` release.
3. Drag `SkySpotter.app` to your **Applications** folder.
4. **CRITICAL FIRST STEP:** Because this app is not signed with a paid Apple Developer certificate, macOS Gatekeeper may block it. Run this once in Terminal to remove the quarantine flag:
  ```bash
   xattr -cr /Applications/SkySpotter.app
  ```
5. You can then launch from Applications or Launchpad.

## ⌨️ Keyboard Shortcuts

- **Space**: Toggle between fit-to-window and 100% zoom
- `**G`**: Toggle between Gallery View and Single Image View
- `**Esc**`: Return to Gallery View (from Single View)
- `**←`/`→` arrows**: Navigate between images
- `**↓`**: Move current image to Discard folder
- **Delete**: Delete current image (with confirmation)
- `**H`**: Show or hide the single-image histogram strip
- `**F**`: Toggle dashed focus/subject indicator overlay (amber = maker AF, lime = EXIF subject area)

## 🔎 Gallery search (Gallery view)

Open the bottom search panel. SkySpotter focuses on **aircraft identification**; the search bar filters the gallery by **EXIF/metadata** and **detected aircraft labels** (after folder indexing).

- **Default (no extra download):** `camera:sony`, `iso<800`, `aircraft:typhoon`, or type `F-35` to match indexed labels.
- **Optional neural semantic search** (~800 MB SigLIP ONNX): set `SkySpotter_ENABLE_SEMANTIC_SEARCH=1` before launch if you want free-text description search (e.g. `jet takeoff`). Not required for Magic Wand or aircraft tooltips.

- **Important:** Words like `**face`**, `**faces**`, `**people**`, `**person**`, and `**human**` are **not** sent to the neural search: they filter by the **Vision face-detection count** stored at index time (same as `has:face`). If no faces were detected (distant subjects, backs to camera, silhouettes), those photos are excluded—try free-text phrases instead, e.g. `crowd`, `pedestrians`, `spectators`.
- **Formats:** Prefer `**format:jpeg`** · `**format:raw**` (`type jpeg` / `ext raw` with a space also normalize). Loose phrases `**file jpeg**` / `**file raw**` map to `**format:**` so `**.jpg**` matches **JPEG** synonyms and `**raw`** covers typical camera RAW extensions (not only filenames containing the substring `raw`).
- You can combine a description with structured filters on one line (see examples).
- **Clear** the field or use the **×** control to restore the full folder.

### Gallery search syntax examples

Separate tokens with spaces. Filters use `key:value` or comparison forms.


| Kind               | Example                                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Aircraft label     | `aircraft:F-35` or `Typhoon` (matches indexed `detected_aircraft`)                                                               |
| Filter combo       | `camera:sony iso<800 aircraft:viper`                                                                                               |
| Camera / lens      | `camera:canon` · `lens:70-200`                                                                                                     |
| ISO / year         | `iso<=800` · `year>=2024`                                                                                                          |
| Place              | `city:tokyo` · `country:jp` · `admin:california`                                                                                   |
| File name          | `filename:_dsc` or `name:img_`                                                                                                     |
| File format        | `format:cr3` · `type:jpeg` · `ext:jpg,png` · `format:raw` (same set as `[src/raw_file_extensions.py](src/raw_file_extensions.py)`) |
| Date prefix        | `date:2024-05`                                                                                                                     |
| GPS / faces        | `has:gps` · `no:gps` · `has:face` · `people` · `person` · `no:face`                                                                |


## 🖱️ Mouse Controls

- **Double-click**: Zoom in to the clicked point (from fit), or zoom out to fit
- **Pinch (Mac/Windows Trackpad) or Ctrl+Scroll**: Smoothly zoom in/out with smart cursor anchoring
- **Click and drag**: Pan image when zoomed in
- **Drag and drop**: Open images or folders
- **Scroll Wheel (fit-to-window)**: Navigate images - Scroll down = previous, Scroll up = next
- **Scroll Wheel (zoom mode)**: Pan image vertically
- **Horizontal Wheel (zoom mode)**: Pan image horizontally (left/right)
- **Scroll Wheel (Gallery View)**: Scroll through the image grid

When focus/subject indicator is enabled (`F`):

- **Space** from fit-to-window zooms to the focus/subject box center.
- **Double-click** still zooms to your clicked point (same as normal mode).

## 🏗️ Building from Source

### Prerequisites

- [Pixi](https://pixi.sh/latest/) (recommended package manager for development and reproducible builds)
- Alternatively: Python 3.10–3.12 and pip for legacy manual builds

### Recommended dev environment (pixi)

For consistent model tooling, aircraft classification, and `rembg` behavior:

```bash
pixi install
pixi run start
```

**Local testing from source** (console logs, same on both platforms):

| Platform | Command |
|----------|---------|
| **Windows** | `scripts\launchers\launch_dev.bat` |
| **macOS** | `./scripts/launchers/launch_dev.sh` |

Train, verify, and build scripts are in the same folder — see `scripts/launchers/README.md`.

### macOS: MPS + STRICT_REMBG

On Apple Silicon Macs, SkySpotter can use PyTorch MPS acceleration for aircraft
checkpoint inference.

Set strict rembg mode to avoid silent fallback behavior during aircraft
identification:

```bash
export SkySpotter_STRICT_REMBG=1
pixi run start
```

What this does:

- Prefers Torch device order: `mps` -> `cuda` -> `cpu`.
- Forces `rembg` (`isnet-general-use`) for the legacy aircraft preprocessing path.
- If `rembg` initialization fails in strict mode, that classification attempt is skipped instead of silently falling back to the alternate background removal pipeline.

How to verify in logs:

- Model device line includes `device='mps'` when MPS is active.
- rembg init line appears as `rembg session initialized: isnet-general-use`.
- strict mode is shown as `strict_rembg=True` in classifier backend logs.

### Aircraft classification speed & GPU paths

Folder indexing runs **one image at a time**: **rembg** (subject isolation), then the **ViT** checkpoint in `app_model/`.

#### Windows — DirectML (default)

Pixi ships **`onnxruntime-directml`** and **`onnxscript`**. With default settings, both stages use your **DirectX 12 GPU**:

| Stage | Runtime | Provider |
|-------|---------|----------|
| rembg (`isnet-general-use`) | ONNX Runtime | `DmlExecutionProvider` |
| ViT classifier | ONNX Runtime (one-time export from checkpoint) | `DmlExecutionProvider` |

You do **not** need a CUDA build of PyTorch for GPU acceleration on Windows.

**Verify in the log** after opening a folder:

- `rembg session initialized: ... providers=['DmlExecutionProvider', ...]`
- `Aircraft classifier (ONNX): ... active_provider=DmlExecutionProvider`

The first run may pause on **“Exporting aircraft model for DirectML (one-time)…”** (~25 s on a typical PC) while the ViT is converted to ONNX; the file is cached under your SkySpotter cache folder for later runs.

**Rough throughput** (60 JPEGs, 1280 px indexing — dev machine, CPU PyTorch vs DirectML ViT): about **2.5× faster** end-to-end than `SkySpotter_PREFER_DIRECTML=0` (PyTorch ViT on CPU). Re-run: `pixi run python scripts/benchmark_classifier_paths.py "<your folder>"`.

**Environment variables:**

| Variable | Effect |
|----------|--------|
| `SkySpotter_PREFER_DIRECTML=1` | Default on Windows — ONNX + DirectML for ViT when available |
| `SkySpotter_PREFER_DIRECTML=0` | Force PyTorch ViT (usually **CPU** with default pixi `torch`) |
| `SkySpotter_CLASSIFIER_DEVICE=dml` | Force ONNX + DirectML for ViT |
| `SkySpotter_CLASSIFIER_DEVICE=cuda` | PyTorch ViT on NVIDIA (requires CUDA `torch`) |
| `SkySpotter_CLASSIFIER_DEVICE=cpu` | PyTorch ViT on CPU only |
| `SkySpotter_INDEX_MAX_SIZE=1280` | Smaller decode size during folder indexing (faster) |
| `SkySpotter_CLASSIFIER_MIN_CROP_SIZE=400` | Skip ViT only if **both** crop width and height are below this; either side ≥ 400 runs classification |
| `SkySpotter_ORT_PROVIDERS` | Optional provider order, e.g. `DmlExecutionProvider,CPUExecutionProvider` |

Set `PYTHONUTF8=1` if ONNX export fails on Windows with a console encoding error (cp950).

#### macOS — MPS + CoreML

See **macOS: MPS + STRICT_REMBG** above. ViT inference uses PyTorch **MPS** on Apple Silicon; rembg/ONNX may use **CoreML** when the provider is available.

### Windows

**Option 1: Using batch script (recommended)**

```batch
scripts\launchers\build_windows.bat
```

**Option 2: Manual build with Pixi**

```bash
pixi install
pixi run start
pixi run python build.py
```

### macOS

**Option 1: Using shell script (recommended)**

```bash
./scripts/launchers/build_macos.sh
```

**Option 2: Manual build with Pixi**

```bash
pixi install
pixi run start
pixi run python build.py
```

### Dependencies

Project dependencies are managed via **`pixi.toml`** (`pixi install`). Build scripts in `scripts/launchers/` install pip packages into a local virtual environment when not using Pixi alone.

**Packaging note:** `build.py` removes `src/logs/` before PyInstaller runs so development log files are not copied into the installer payload (`--add-data "src;src"`).

## 🐛 Troubleshooting

### Crash logs (Windows and macOS)

SkySpotter writes crash-related files to the **first writable folder** below. Look for:

- `crash_report_YYYYMMDD_HHMMSS.txt` — uncaught Python exceptions
- `fatal_dump_YYYYMMDD_HHMMSS.log` — low-level fatal crashes (access violation / segfault)

| How you run SkySpotter | Where to look |
|------------------------|---------------|
| **From source (development)** | `<project>/src/logs/` first, then `<project>/logs/` |
| **Windows installed app** | `%LOCALAPPDATA%\SkySpotter\logs\` (e.g. `C:\Users\<you>\AppData\Local\SkySpotter\logs\`) |
| **macOS installed app** | `~/Library/Application Support/SkySpotter/logs/` |

Optional: set `RAWVIEWER_FILE_LOG=1` when developing to enable extra file logging under `src/logs/`.

### Windows

- **"Windows protected your PC"**: Click "More info" → "Run anyway"
- **Antivirus warnings**: Add SkySpotter to your antivirus exclusions
- **Performance issues**: Try running as administrator
- **AttributeError with stdout**: This is normal for windowed builds - the application runs without a console window
- **Crash code `-1073741819` / `0xC0000005` (access violation)**:
  - This is a native crash (Qt/LibRaw/ONNX/driver layer), not always a Python exception.
  - Check **`%LOCALAPPDATA%\SkySpotter\logs\`** for `fatal_dump_*.log` and `crash_report_*.txt` (see **Crash logs** above). If you run from a git checkout, also check `<project>\src\logs\`.

### macOS

- **"App is damaged and should be moved to the Trash" / "Apple could not verify SkySpotter is free of malware"**:
  - **Why it happens**: Apple heavily restricts apps downloaded outside the App Store that aren't signed with a paid developer certificate. On newer macOS versions (especially Apple Silicon M1/M2/M3), macOS breaks the app's ad-hoc signature and aggressively blocks opening it.
  - **The Fix (Fastest)**: Open your **Terminal** app and run the following command to remove the quarantine flag:
    ```bash
    xattr -cr /Applications/SkySpotter.app
    ```
    _(Note: If you placed the app somewhere other than the Applications folder, update the path accordingly)._
- **"Symbol not found: (mkfifoat)" or App crashes instantly on macOS 12 (Monterey) or older**:
  - **Why it happens**: The pre-built release is compiled using a newer macOS 13+ SDK. Older macOS versions do not have the required system files to run it.
  - **The Fix**: You must build the app locally (see the "Ultimate Fix" below).

#### 🛠️ The Ultimate Fix: Build Locally (Solves Both Issues Above)

If you are on macOS 12 or older, OR if you simply want to permanently bypass all Gatekeeper/Quarantine warnings forever, you can build the app directly on your own machine. Pixi pins a supported Python version for you:

1. **Install Pixi** (Terminal: `curl -fsSL https://pixi.sh/install.sh | bash`).
2. **Clone and build:**
  ```bash
   git clone https://github.com/markyip/SkySpotter.git
   cd SkySpotter
   pixi run python build.py
  ```
   This creates a compatible `SkySpotter.app` in `dist/`. You can also run `./scripts/launchers/build_macos.sh` if you prefer the shell wrapper.

#### 🔧 Local Build Troubleshooting

- **Error: "No matching distribution found for pyexiv2" or massive C++ / PyQt6 compile failures**
  - **Why it happens**: Unsupported Python (too old or too bleeding-edge).
  - **The Fix**: Use **Pixi** (`pixi install` / `pixi run python build.py`) so Python and wheels stay pinned. Delete any stale `skyspotter_env` folder before rebuilding with the batch/shell scripts.
- **Homebrew delays on macOS 12 Monterey or older**:
  - Homebrew has officially dropped "binary bottle" support for Monterey. However, **it still works**. When the build script attempts to `brew install inih gettext`, Homebrew will simply compile them from source on your machine. This is completely normal but may take 2-3 extra minutes.
- **Permission Denied / Cannot Read Folder**: Modern macOS requires explicit permission for apps to access the Desktop or Documents.
  1. Go to **System Settings** > **Privacy & Security** > **Full Disk Access**.
  2. Click the **+** button and add `SkySpotter.app`.
  3. Toggle it to **ON**.
- **Gallery search only filters EXIF / aircraft labels:** This is expected. SkySpotter does not download SigLIP models unless you set `SkySpotter_ENABLE_SEMANTIC_SEARCH=1`.
- **Magic Wand hidden:** Wait until aircraft indexing finishes (labels written to the index). The wand appears only when at least one image has a detected aircraft label.

## 🧠 Customizing the Classifier

Train a **custom ViT classifier** on your own labeled folders—birds, animals, vehicles, military aircraft, or any other subjects. SkySpotter ships a default model in `app_model/` for gallery inference; **your trained checkpoint does not replace it until you copy files there yourself.**

### Workflow overview

| Step | Folder / action | Purpose |
|------|-----------------|--------|
| 1. Label training photos | `training_data/classified_images/<class>/` | One subfolder per class |
| 2. Train | `scripts/launchers/train_model.*` → `customized_model/` | Fine-tune ViT; rembg runs automatically |
| 3. Test | `testing_data/test_images/` → `scripts/launchers/verify_model.*` | Confirm the checkpoint before gallery use |
| 4. Promote | Copy into **`app_model/`** | **Active model** the app loads for labels and Magic Wand |
| — | `training_data/processed_images/` | Cached training PNGs (generated at step 2; do not edit) |

### 1. Prepare labeled images

Add images under `training_data/classified_images/`, one subfolder per class (see `training_data/classified_images/README.md`).

### 2. Train (background removal is automatic)

Training **always** runs `rembg` background removal and subject cropping on your source images before fine-tuning. You do not run a separate preprocessing step.

Use the pixi environment (includes `rembg` and pinned `numpy` for numba):

- **Windows:** `scripts\launchers\train_model.bat`
- **macOS:** `./scripts/launchers/train_model.sh`

Or directly:

```bash
pixi install
pixi run python scripts/train_processed_aircraft.py
```

The checkpoint is written to **`customized_model/`** by default (`config.json`, `model.safetensors`, `preprocessor_config.json`, `labels.txt`).

Optional environment variables:

- `SkySpotter_TRAIN_DATA_PATH` — source labeled folders (default: `training_data/classified_images`)
- `SkySpotter_TRAIN_OUTPUT_DIR` — checkpoint output (default: `customized_model`)
- `SkySpotter_TRAIN_PROCESSED_PATH` — cached processed PNGs (default: `training_data/processed_images`)

**Training acceleration:** Windows/NVIDIA uses CUDA when available; Apple Silicon uses MPS; otherwise CPU. The trainer prints the device at startup.

### 3. Test your model (before using the gallery)

Use held-out photos that were **not** in your training folders when possible, so you are checking generalization—not memorization.

**3a. Add test images**

1. Copy sample photos into `testing_data/test_images/` (any mix of classes you trained).
2. See `testing_data/test_images/README.md` for a short checklist.

**3b. Run verification**

From the project root:

| Platform | Command |
|----------|---------|
| **Windows** | `scripts\launchers\verify_model.bat` |
| **macOS** | `./scripts/launchers/verify_model.sh` |
| **Either** | `pixi run verify-model` |

The script runs `scripts/batch_test_classifier.py` on **`customized_model/`** with the same rembg-style preprocessing as training.

Optional overrides (set before running the `.bat` / `.sh`):

- `SkySpotter_VERIFY_INPUT_DIR` — test image folder (default: `testing_data/test_images`)
- `SkySpotter_VERIFY_MODEL_DIR` — checkpoint folder (default: `customized_model`)
- `SkySpotter_VERIFY_OUTPUT_DIR` — results folder (default: `testing_data/test_output`)

**3c. Review results**

After a successful run, open:

| Output | What to check |
|--------|----------------|
| `testing_data/test_output/pipeline_images/` | Subject crop looks correct (aircraft centered, background removed) |
| `testing_data/test_output/top3_detection_scores.csv` | `top1_label` / `top1_score` match what you expect; compare `top2`/`top3` when unsure |

In the CSV:

- **`status`** — preprocessing outcome (e.g. crop too small, rembg issue).
- **`top1_score`** — confidence for the best label (higher is stronger; very low scores may mean a bad crop or a class the model has not seen enough).
- **`error`** — non-empty if that file failed entirely.

If labels are wrong, add more training images for those classes and re-run **step 2**, then verify again. Repeat until you are happy with the CSV and pipeline images.

**3d. Optional: test the gallery path**

`scripts/poc_aircraft_detection.py` exercises the **in-app** classifier (`app_model` / DirectML). Use this only **after** you copy your checkpoint to step 4—not for the first check on `customized_model/`.

### 4. Promote to the gallery when ready

When verification looks good, **copy** these four files from `customized_model/` into `app_model/`:

- `config.json`
- `model.safetensors`
- `preprocessor_config.json`
- `labels.txt`

Restart SkySpotter (or reload the folder) so indexing picks up your model. Open a folder with aircraft photos and confirm labels or Magic Wand behavior in the app.

### 5. Runtime behavior

Gallery classification uses the checkpoint in **`app_model/`** only (see `app_model/README.md`). If that folder is missing or invalid, labels are not applied.

To use a different folder without renaming: set `SkySpotter_APP_MODEL_DIR` to its path before launching.

## 📁 Supported Image Formats

### RAW formats

- **Canon**: CR2, CR3
- **Nikon**: NEF
- **Sony**: ARW
- **Adobe**: DNG
- **Olympus**: ORF
- **Panasonic**: RW2
- **Fujifilm**: RAF
- **Hasselblad**: 3FR
- **Pentax**: PEF
- **Samsung**: SRW
- **Sigma**: X3F
- **And many more supported by LibRaw**

### Standard formats

- **JPEG**: JPG, JPEG
- **TIFF**: TIF, TIFF
- **HEIF**: HEIF

## ⚠️ Known Issues

### Camera compatibility

- **Newer camera models**: Support for the latest camera releases may be limited until LibRaw catches up.
- **Proprietary RAW formats**: Some manufacturers' newest RAW formats may not be fully supported immediately after camera release.
- **Firmware updates**: Camera firmware updates may change RAW formats and require LibRaw updates.

## 🏛️ Architecture & Dependencies

SkySpotter combines RAWviewer's viewer architecture with aviation-specific inference:

- **ImageLoadManager**: Thread pool and priority queue for loading
- **UnifiedImageProcessor**: Single path for RAW, JPEG, TIFF, and more
- **Cache**: Memory-first by default; optional disk/SQLite via `SkySpotter_PERSISTENT_CACHE=1`
- **Aircraft classifier**: Multi-threaded `QThreadPool` (up to 4 concurrent classification jobs in the gallery workflow)

Optional gallery **semantic search** (~800 MB download) is off by default; it does not affect aircraft classification or Magic Wand. See **Aircraft classification speed & GPU paths** under Building from Source for technical details.

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

## 🤝 Contributing

Contributions are welcome. Please open a Pull Request with a clear description of the change.

## 📞 Support

If you encounter issues:

1. Attach crash logs from the folder that matches how you run the app:
   - **Windows (installer):** `%LOCALAPPDATA%\SkySpotter\logs\`
   - **macOS (`.app`):** `~/Library/Application Support/SkySpotter/logs/`
   - **From source:** `<project>/src/logs/` or `<project>/logs/`
   
   Files: `crash_report_*.txt`, `fatal_dump_*.log` (see **Crash logs** under Troubleshooting).
2. Search existing GitHub issues.
3. Open a new issue with OS version, steps to reproduce, and relevant log excerpts.

## ☕ Thank you

If you find SkySpotter useful and it's become part of your workflow, feel free to chip in to help fund my **RIAT tickets for next year**. Enjoy organizing your airshow shots! 📸