# SkySpotter

<p align="center">
  <img src="icons/appicon.ico" alt="SkySpotter Icon" width="256"><br>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <a href="https://www.buymeacoffee.com/markyip"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-orange?logo=buy-me-a-coffee" alt="Buy Me a Coffee"></a>
</p>

## ✈️ Meet SkySpotter

You’re an aviation photographer who just returned from an airshow, a base visit, or a day at the Mach Loop. You’ve come home with a full memory card and thousands of shots of fast jets, helicopters, and flybys—and now you’re facing the real challenge: **sorting through them all**.

SkySpotter is a smart image viewer for Windows and Mac that helps you quickly sort, clean up, and organize massive folders of airplane photos before you start editing.

Best of all, it’s built entirely around your privacy. All of the AI features—like recognizing aircraft types and auto-sorting them into folders—run 100% locally on your computer. Your photos are never uploaded to the cloud, meaning your files stay completely safe and under your control.

With SkySpotter, you can:

- **See if you nailed focus** — Show where the camera focused on the aircraft before you zoom in to check sharpness.
- **Know what you shot** — Get AI-driven suggestions for aircraft types across your folder.
- **Find and sort by type** — Search the gallery by model name, then use the **Magic Wand** to file photos into folders by aircraft.
- **Work straight from your files** — Open RAW and JPEG with a double-click; no slow import step, built to stay fast even on huge folders.

You still get the usual viewer essentials (zoom, pan, keyboard browsing, discard folder, EXIF info)—but the heart of SkySpotter is **aviation-first organization**, so you spend less time sorting and more time shooting.

**Not an aviation enthusiast?** Try **[RAWviewer](https://github.com/markyip/RAWviewer)** from the same family: the same fast local viewing workflow, aimed at general photography, with **local semantic search** (find images by describing them in words—still on your computer, not in the cloud).

SkySpotter adds aircraft recognition and auto-sort; RAWviewer skips those and focuses on flexible search instead.

---

## ⭐ Highlights

### 1. Precision focus area detection

See **where the camera focused** before you zoom in for sharpness:

- Overlays focus point(s) using manufacturer-specific **MakerNote** data (Canon, Nikon, Sony) plus EXIF **SubjectArea** / **SubjectLocation**
- **Orientation-aware** mapping and robust coordinate scaling on rotated images
- Press **`F`** to toggle the overlay
- Press **Space** to zoom in to the focus point

### 2. AI aircraft recognition, gallery filters & auto-sort

**Core selling points** for organizing an airshow folder. Everything below runs **offline on your machine**—no account, no cloud inference, no sending images to a server.

- **Automated aircraft classification**: Custom **Vision Transformer (ViT)** recognizes about **70** military and civil aircraft types (e.g. F-35, AH-64, A400M, Eurofighter Typhoon). Class list: [`labels.txt`](models/gallery-classifier/skyspotter-military-aircraft-vit/labels.txt)
- **One-click auto-sort**: **Magic Wand** moves images into subfolders by detected aircraft type; images without a label go to **`Unclassified/`**. After sorting, the gallery still shows those files (see folder scope in search section below)
- **Gallery filters — search by aircraft type**: `aircraft:F-35`, `aircraft:typhoon`, or type a model name after indexing; combine with EXIF (`camera:sony iso<800 aircraft:viper`, `format:raw`, `year>=2024`, and more)

Full search syntax: **[Gallery search](#-gallery-search-gallery-view)**.

### 3. Wide format support & fast performance

- **Many image formats**: Camera **RAW** (via LibRaw), **JPEG**, **TIFF**, and **HEIF** — open with a double-click, no import catalog
- **Lightning-fast** folder scans, decoding, and navigation across every supported format; single-image open shows your file first while the rest of the folder loads in the background
- Details: [Supported Image Formats](#-supported-image-formats)

---

## ✨ Core workflow (fast culling)

- Instant file previewing: no import steps — just drag & drop
- Zoom in with a single key to check sharpness immediately
- Stay in zoomed mode while browsing with arrow keys
- Quickly remove blurry photos from the queue with **`↓`** (moves them to a discard folder)
- No complex controls to memorize — just the essential keys to move fast

This is a **pre-filtering tool**, letting you go through hundreds of RAW files efficiently **before** committing to editing them in Lightroom or Photoshop.

---

## ✨ Features

- **100% local AI**: Aircraft detection and gallery indexing run on your PC or Mac only; nothing is uploaded for AI processing
- **Automated Aircraft Classification**: ViT model recognizes about **70** military and civil aircraft types (see [`labels.txt`](models/gallery-classifier/skyspotter-military-aircraft-vit/labels.txt))
- **One-Click Auto-Sort**: **Magic Wand** moves images into subfolders by detected aircraft type
- **Precision focus area detection**: MakerNote + EXIF subject overlays; press **`F`** to toggle (see [Highlights](#-highlights))
- **Gallery filters**: EXIF/metadata plus **aircraft label** search (`aircraft:`, or type a model name after indexing)
- **Wide RAW format support**: Canon (CR2, CR3), Nikon (NEF), Sony (ARW), Adobe DNG, and many more — plus JPEG, TIFF, HEIF
- **Ultra-fast performance**: Optimized folder loading and decoding for all supported formats
- **GPU acceleration**: Uses your graphics card when available to speed up folder indexing (no manual setup required)
- **Cross-platform support**: Windows and macOS
- **macOS file association**: Finder integration; set as default viewer; double-click to open
- **Intuitive navigation**: Keyboard shortcuts, mouse controls, and scroll wheel support
- **File management**: Move images to discard folder or delete permanently
- **EXIF data display**: Camera settings, focal length, ISO, aperture, and capture information
- **Single-image histogram**: Press **`H`** to show or hide the strip while viewing one image
- **Non-destructive visual rotate**: Rotate in the viewer by 90° steps without modifying originals (including RAW); gallery tiles refresh immediately

---

## 🚀 Quick Start

### Download Executable

#### Windows

1. Download the latest release from the [Releases Page](https://github.com/markyip/SkySpotter/releases/latest)
2. Download `SkySpotter.exe` directly (no zip extraction needed)
3. Double-click `SkySpotter.exe` to initiate the installation process. It will automatically download dependencies and the **gallery classifier** (`models/gallery-classifier/skyspotter-military-aircraft-vit/`). The installer bundles weights when you build after `git lfs pull`; otherwise it uses the GitHub release zip from `manifest.json` or `SkySpotter_APP_MODEL_URL`.
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

---

## ⌨️ Navigation & controls

How you move through photos, zoom, and switch views.

**Keyboard**

- **Space** — Toggle fit-to-window and 100% zoom (check sharpness)
- **`←` / `→`** — Previous / next image (stays zoomed if you were already zoomed in)
- **`↓`** — Move the current image to the Discard folder
- **Delete** — Delete the current image (with confirmation)
- **`H`** — Show or hide the histogram strip (single-image view)
- **`F`** — Show or hide the focus/subject overlay (see [Precision focus area detection](#1-precision-focus-area-detection))
- **`Esc`** — Back to the gallery from full-screen single-image view

**Mouse & trackpad**

- **Double-click** — Zoom in on the point you clicked (from fit), or zoom back out to fit
- **Pinch** (trackpad) or **Ctrl + scroll** — Zoom in/out; zoom stays anchored near your cursor
- **Click and drag** — Pan when zoomed in
- **Drag and drop** — Open a file or folder on the window
- **Scroll wheel (fit-to-window)** — Previous / next image (down = previous, up = next)
- **Scroll wheel (while zoomed)** — Pan up/down; tilt wheel pans left/right
- **Scroll wheel (gallery)** — Scroll the thumbnail grid

**Gallery ↔ single image**

Use the on-screen gallery button or **click a thumbnail** to open a photo full-screen. There is **no `G` keyboard shortcut**. **`Esc`** returns to the gallery.

**When the focus overlay is on (`F`)**

- **Space** from fit-to-window jumps to the focus box; double-click still zooms where you click.

---

## 🔎 Gallery search (Gallery view)

Open the bottom search panel to filter the grid. SkySpotter gallery search is **EXIF/metadata** plus **detected aircraft labels** (written during folder indexing). There is no free-text “describe this photo” semantic search and no face-based search in this app.

**What you can search:**

- **Aircraft type** (after indexing) — `aircraft:F-35`, `aircraft:typhoon`, or a model name such as `Typhoon` or `F-35`
- **Camera / lens / exposure** — `camera:sony`, `lens:70-200`, `iso<800`, `iso<=800`
- **Date / place / file** — `year>=2024`, `date:2024-05`, `city:tokyo`, `filename:_dsc`
- **Format** — `format:jpeg`, `format:raw`, `format:cr3` (`raw` uses the LibRaw set; see [Supported Image Formats](#-supported-image-formats))
- **GPS** — `has:gps`, `no:gps`
- **Combine filters** on one line — e.g. `camera:sony iso<800 aircraft:viper`
- **Clear** the field or use **×** to show the full folder again

Indexing must finish before aircraft-name filters match; Magic Wand also needs detected labels on your images.

### Gallery search syntax examples

Separate tokens with spaces. Filters use `key:value` or comparison forms.

| Kind | Example |
| --- | --- |
| Aircraft label | `aircraft:F-35` or `Typhoon` (indexed `detected_aircraft`) |
| Sharp / blurry | `sharp` · `blurry` (Laplacian score; **bottom 20%** of current folder = blurry; `SkySpotter_BLUR_BLURRY_FRACTION`) |
| Filter combo | `camera:sony iso<800 aircraft:viper blurry` |
| Camera / lens | `camera:canon` · `lens:70-200` |
| ISO / year | `iso<=800` · `year>=2024` |
| Place | `city:tokyo` · `country:jp` · `admin:california` |
| File name | `filename:_dsc` or `name:img_` |
| File format | `format:cr3` · `type:jpeg` · `format:raw` (see [`src/raw_file_extensions.py`](src/raw_file_extensions.py)) |
| Date prefix | `date:2024-05` |
| GPS | `has:gps` · `no:gps` |

---

## 📁 Supported Image Formats

Open files directly from disk—no import step. SkySpotter uses [LibRaw](https://www.libraw.org/) for camera RAW and also supports common finished formats.

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
- **And many more** via LibRaw (newer bodies may lag until LibRaw adds support—see [Known Issues](#-known-issues))

### Standard formats

- **JPEG**: JPG, JPEG
- **TIFF**: TIF, TIFF
- **HEIF**: HEIF

Gallery `format:raw` / `format:jpeg` filters use the same extension sets as the app (see [`src/raw_file_extensions.py`](src/raw_file_extensions.py)).

---

## 🏗️ Building from Source

### Prerequisites

- Install **[Pixi](https://pixi.sh/latest/)** — required for development and building from source
- **Do not use `pip install` on the project.** Dependencies are pinned in `pixi.toml` / `pixi.lock`; a manual virtualenv often breaks installs (wrong Python version or missing wheels).

### Dev environment (Pixi)

From the project root:

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

### Windows

```batch
scripts\launchers\build_windows.bat
```

Or: `pixi install` then `pixi run python build.py`

### macOS

```bash
./scripts/launchers/build_macos.sh
```

Or: `pixi install` then `pixi run python build.py`

### Dependencies & packaging

Everything is installed with **`pixi install`** (see `pixi.toml`). Use **`pixi run start`**, **`pixi run verify-model`**, and **`pixi run python build.py`** so commands run inside that environment.

**Packaging note:** `build.py` strips dev logs before PyInstaller runs. The Windows installer copies **`pixi.toml` and `pixi.lock`** and runs **`pixi install --locked`** on the user’s machine so installs match the pinned environment.

---

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
  - This is a native crash (viewer, RAW decoder, or graphics driver layer), not always a Python exception.
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

- **Build fails with `pip`, `pyexiv2`, or PyQt compile errors**
  - **Why it happens**: Trying to install dependencies outside Pixi (unsupported).
  - **The fix**: From the repo root run `pixi install`, then use `pixi run python build.py` or the `scripts/launchers/` build script. Remove any old manual virtualenv folders (`skyspotter_env`, `rawviewer_env`) if you created them earlier.
- **Homebrew delays on macOS 12 Monterey or older**:
  - Homebrew has officially dropped "binary bottle" support for Monterey. However, **it still works**. When the build script attempts to `brew install inih gettext`, Homebrew will simply compile them from source on your machine. This is completely normal but may take 2-3 extra minutes.
- **Permission Denied / Cannot Read Folder**: Modern macOS requires explicit permission for apps to access the Desktop or Documents.
  1. Go to **System Settings** > **Privacy & Security** > **Full Disk Access**.
  2. Click the **+** button and add `SkySpotter.app`.
  3. Toggle it to **ON**.
- **Gallery search only filters EXIF and aircraft labels:** This is expected. Phrases like “sunset” or “crowd” are not semantic image search—they only match if those words appear in metadata or an indexed aircraft label.
- **Magic Wand hidden:** Wait until gallery indexing finishes. The wand appears once images are indexed (labeled types get their own folder; others can go to `Unclassified/`).
- **“Exporting aircraft model” on first folder open:** Normal one-time setup on a new PC (often under a minute). Later opens of the same folder are much faster.

## 🧠 Customizing the Classifier

Train a **custom ViT classifier** on your own labeled folders—birds, animals, vehicles, military aircraft, or any other subjects. SkySpotter ships a default model under `models/gallery-classifier/skyspotter-military-aircraft-vit/`; **your trained checkpoint does not replace it until you copy the four weight files there** (or set `SkySpotter_GALLERY_CLASSIFIER_DIR`).

### Workflow overview

| Step | Folder / action | Purpose |
|------|-----------------|--------|
| 1. Label training photos | `training_data/classified_images/<class>/` | One subfolder per class |
| 2. Train | `scripts/launchers/train_model.*` → `customized_model/` | Fine-tune ViT; rembg runs automatically |
| 3. Test | `testing_data/test_images/` → `scripts/launchers/verify_model.*` | Confirm the checkpoint before gallery use |
| 4. Promote | Copy into **`models/gallery-classifier/<id>/`** (or `app_model/`) | **Active model** for labels and Magic Wand |
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

**Training:** Uses your GPU automatically when the machine provides one; otherwise it runs on CPU.

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

`scripts/poc_aircraft_detection.py` exercises the **same in-app classifier** the gallery uses. Use this only **after** you copy your checkpoint to step 4—not for the first check on `customized_model/`.

### 4. Promote to the gallery when ready

When verification looks good, **copy** these four files from `customized_model/` into `models/gallery-classifier/skyspotter-military-aircraft-vit/` (or legacy `app_model/`):

- `config.json`
- `model.safetensors`
- `preprocessor_config.json`
- `labels.txt`

Restart SkySpotter (or reload the folder) so indexing picks up your model. Open a folder with aircraft photos and confirm labels or Magic Wand behavior in the app.

### 5. Runtime behavior

Gallery classification loads the first valid checkpoint among `models/gallery-classifier/skyspotter-military-aircraft-vit/`, legacy `app_model/`, or paths from `SkySpotter_GALLERY_CLASSIFIER_DIR` / `SkySpotter_APP_MODEL_DIR`. See `models/gallery-classifier/README.md`.

**Clone from GitHub (developers):**

```bash
git clone https://github.com/markyip/SkySpotter.git
cd SkySpotter
git lfs install
git lfs pull
```

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

Gallery search uses a local index (EXIF + aircraft labels written while the folder is indexed).

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

**Third-party software and models** (ViT checkpoints, rembg / IS-Net, PyQt6, optional CLIP weights, etc.) are **not** covered by SkySpotter’s MIT license alone. See **[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)** for copyrights, attribution, and redistribution requirements. Blur **sharp** / **blurry** filters use a Laplacian heuristic only (no extra model license).

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

---

## ☕ Thank you

If SkySpotter has helped your workflow, a few things make a big difference:

- **Share it** with photographer friends who shoot airshows or military aviation—more people trying the project helps it improve.
- **Chip in** if you’d like to help fund my **RIAT tickets for next year**.
- **Not an aviation photographer?** Try **[RAWviewer](https://github.com/markyip/RAWviewer)** for the same fast, local workflow with **semantic search** instead of aircraft recognition.

Enjoy organizing your airshow shots! 📸
