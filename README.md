# SkySpotter

<p align="center">
  <img src="icons/appicon.ico" alt="SkySpotter Icon" width="256"><br>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <a href="https://github.com/markyip/SkySpotter"><img src="https://img.shields.io/github/downloads/markyip/SkySpotter/total" alt="Downloads"></a>
  <a href="https://www.buymeacoffee.com/markyip"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-orange?logo=buy-me-a-coffee" alt="Buy Me a Coffee"></a>
</p>

## ✈️ Meet SkySpotter

You're an aviation photographer who just returned from an airshow, a base visit, or a day at the Mach Loop. You've come home with a full memory card and thousands of shots of fast jets, helicopters, and flybys—and now you're facing the real challenge: **sorting through them all**.

SkySpotter is a smart image viewer for Windows and Mac that helps you quickly sort, clean up, and organize massive folders of airplane photos before you start editing.

Best of all, it's built entirely around your privacy. All of the AI features—like recognizing aircraft types and auto-sorting them into folders—run 100% locally on your computer. Your photos are never uploaded to the cloud, meaning your files stay completely safe and under your control.

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

### 3. Ultra-Fast Viewing & Background Loading

Optimized to handle folders containing thousands of heavy camera RAW photos seamlessly:

- **Instant Photo Opening**: Double-click any photo on your computer and the viewer launches it instantly. You can view, zoom, and check your photo immediately without waiting for the rest of the folder to finish scanning.
- **Silky-Smooth Grid Scrolling**: Browse through massive galleries of large RAW images without stuttering, freezes, or lag.
- **Reliable 100% Zooming**: Double-clicking or pressing Spacebar to zoom in to check sharpness on DNG and RAW files is perfectly sharp, responsive, and consistent every single time.

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

- **100% Local AI**: All aircraft detection and gallery organizing run entirely offline on your own computer—your photos are never uploaded to the internet or shared.
- **Automated Aircraft Classification**: Smart recognition for about **70** military and civil aircraft types (see [`labels.txt`](models/gallery-classifier/skyspotter-military-aircraft-vit/labels.txt))
- **One-Click Auto-Sort**: **Magic Wand** files your photos into neat subfolders by detected aircraft type in a single click.
- **Precision Focus Area Detection**: See exactly where the camera focused on the aircraft before you zoom in; press **`F`** to toggle.
- **Smart Film Strip Sync**: The film strip at the bottom of the screen matches your active search filters perfectly. When you browse using the arrow keys, you will only see the filtered photos.
- **Seamless Search & Navigation**: Clicking a filtered thumbnail keeps your browsing restricted only to those search results.
- **Quick Send to Editors ("Open with...")**: Send your active photo to Lightroom, Photoshop, or any photo editor on your PC with a single click using the bottom-bar button.
- **Auto-Session Restore**: Reopens your last viewed folder, active image, and view mode (gallery vs. full screen) automatically when you launch the app.
- **Powerful Gallery Search**: Filter your grid easily using simple tags like `aircraft:F-35`, `camera:sony`, `iso<800`, or format types (`format:raw`).
- **Wide Format Support**: Canon (CR2, CR3), Nikon (NEF), Sony (ARW), Adobe DNG, and many more—plus JPEGs, TIFFs, and HEIF.
- **GPU Acceleration**: Speeds up organizing by automatically utilizing your graphics card, no setup required.
- **macOS File Association**: Integrates into Finder so you can set it as your default viewer and open files directly.
- **Intuitive Zoom & Pan**: Easy fit-to-window and 100% zoom modes with smooth dragging, plus native Mac trackpad pinch-to-zoom.
- **Fast File Management**: Discard bad shots instantly to clean up your folders.
- **EXIF Data HUD**: Transparent overlay showing camera model, lens, focal length, shutter speed, ISO, and capture time.
- **Histogram Visualizer**: Press **`H`** to slide out a color histogram when inspecting single images.
- **Modern UI**: Sleek Material Design 3 interface with beautiful modern icons and clean loading indicators.
- **Non-Destructive Rotation**: Rotate photos by 90° in the viewer without modifying or corrupting the original files on disk.

---

## 🚀 Quick Start

### Download Executable

#### Windows

1. Download the latest release from the [Releases Page](https://github.com/markyip/SkySpotter/releases/latest)
2. Download `SkySpotter.exe` directly (no zip extraction needed)
3. Double-click `SkySpotter.exe` to initiate the installation process. It will automatically download dependencies and the **gallery classifier** (`models/gallery-classifier/skyspotter-military-aircraft-vit/`). The installer bundles weights when you build after `git lfs pull`; otherwise it uses the GitHub release zip from `manifest.json` or `SkySpotter_APP_MODEL_URL`.
4. Launch SkySpotter from the Desktop shortcut created during installation! (You can safely delete the original `SkySpotter.exe` installer afterwards).

#### macOS

> **Minimum supported macOS (official prebuilt release): macOS 13 Ventura or newer.**

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

Open the bottom search panel to filter the grid. SkySpotter gallery search is **EXIF/metadata** plus **detected aircraft labels** (written during folder indexing). There is no free-text "describe this photo" semantic search and no face-based search in this app.

**What you can search:**

- **Aircraft type** (after indexing) — `aircraft:F-35`, `aircraft:typhoon`, or a model name such as `Typhoon` or `F-35`
- **Camera / lens / exposure** — `camera:sony`, `lens:70-200`, `iso<800`, `iso<=800`
- **Date / place / file** — `year>=2024`, `date:2024-05`, `city:tokyo`, `filename:_dsc`
- **Format** — `format:jpeg`, `format:raw`, `format:cr3` (`raw` uses the LibRaw set; see [Supported Image Formats](#-supported-image-formats))
- **GPS** — `has:gps`, `no:gps`
- **Combine filters** on one line — e.g. `camera:sony iso<800 aircraft:viper`
- **Clear** the field or use **×** to show the full folder again

Indexing must finish before aircraft-name filters match; Magic Wand also needs detected labels on your images.

### Indexing behavior (current default)

- **Aircraft classification** runs during semantic indexing (search-ready when labels are written).
- **Face detection** is **off by default** in SkySpotter (`"face_scan": false` in [`config/skyspotter_features.json`](config/skyspotter_features.json)). It only powers RAWviewer-style gallery tokens such as `people` and `portrait`; enable it if you need those filters.
- When face scan is enabled, indexing may run in two passes: metadata + semantic first, then face-count backfill in the background.
- Advanced face-scan environment switches (only when `face_scan` is on):
  - `RAWVIEWER_INDEX_DEFER_FACE_SCAN=1` (default): run face scan after the semantic pass
  - `RAWVIEWER_FACE_SCAN_WARM_THUMBS=0` (default): disable full warm-up prepass
  - `RAWVIEWER_FACE_SCAN_WARM_MAX_FILES=256` (default): cap warm-up batch size
  - `RAWVIEWER_FACE_SCAN_WARM_MAX_SECONDS=25` (default): cap warm-up wall time

### Classifier speed vs accuracy (GPU tuning)

Indexing runs **rembg + ViT** per image. ViT inference is fast on CUDA; **rembg and RAW decode** often dominate wall time. Parallel workers help when the GPU has spare VRAM.

| Goal | Setting | Notes |
| --- | --- | --- |
| **Faster index** (default auto) | *(no env)* | CUDA ViT + DirectML rembg: **2 workers** on 4070; rembg on CPU allows 4 |
| **Max throughput** | `SkySpotter_AIRCRAFT_CLASSIFY_WORKERS=3` | Raise only if stable; lower to `1` if ORT/DML crashes |
| **rembg on CPU** | `SkySpotter_REMBG_CPU=1` | Frees GPU for more ViT workers |
| **Sharper crops / labels** | `SkySpotter_INDEX_MAX_SIZE=2048` | Larger source before rembg; slower per file |
| **Fewer false labels** | `SkySpotter_CLASSIFIER_MIN_CONF=0.50` | Higher = stricter (more “unidentified”) |
| **More labels (riskier)** | `SkySpotter_CLASSIFIER_MIN_CONF=0.30` | Lower = more detections, more mistakes |

Auto defaults (when env vars are unset):

- **Workers:** CUDA ViT + DirectML rembg → **2** on 11+ GiB (`RTX 4070`); set `SkySpotter_REMBG_CPU=1` for up to **4** ViT workers.
- **Index resolution:** `1920` px long edge on CUDA ≥10 GiB, else `1280`.
- **Thumbnail warm-up** (before classify, uncached RAW only):

Embedded thumbnails are warmed **during the metadata parallel pass** by default (`SkySpotter_AIRCRAFT_WARM_WITH_METADATA=1`). A short top-up pass before classify covers files that skipped metadata extraction. Set `SkySpotter_AIRCRAFT_WARM_WITH_METADATA=0` to restore a separate warm phase before classify.

| GPU VRAM | Folder (uncached) | max files | time budget |
| --- | --- | --- | --- |
| ≥11 GiB | any | all | unlimited |
| ≥8 GiB | ≤2000 | all | unlimited |
| ≥8 GiB | >2000 | 1500 | 180s |
| ≥6 GiB | any | up to 1024 | ~30–120s (scaled) |
| else | any | up to 384 | ~20–45s (scaled) |

Override: `SkySpotter_AIRCRAFT_WARM_MAX_FILES=-1` (all), `SkySpotter_AIRCRAFT_WARM_MAX_SECONDS=0` (no limit).

Benchmark warm-up vs no warm:

```powershell
pixi run python scripts/benchmark_thumbnail_warmup.py "K:\Photos\23092025 Mach Loop" --max-images 50
```

Benchmark classifier throughput:

```powershell
pixi run benchmark-classifier "K:\Photos\23092025 Mach Loop" --max-images 50
```

### Gallery search syntax examples

Separate tokens with spaces. Filters use `key:value` or comparison forms.

| Kind | Example |
| --- | --- |
| Aircraft label | `aircraft:F-35` or `Typhoon` (indexed `detected_aircraft`) |
| Filter combo | `camera:sony iso<800 aircraft:viper` |
| Camera / lens | `camera:canon` · `lens:70-200` |
| ISO / year | `iso<=800` · `year>=2024` |
| Place | `city:tokyo` · `country:jp` · `admin:california` |
| File name | `filename:_dsc` or `name:img_` |
| File format | `format:cr3` · `type:jpeg` · `format:raw` (see [`src/raw_file_extensions.py`](src/raw_file_extensions.py)) |
| Date prefix | `date:2024-05` |
| GPS | `has:gps` · `no:gps` |

---

## Experimental features

These capabilities exist in the codebase but are **off by default**. We tried them in real airshow folders; results were **not reliable enough** for everyday culling (rankings did not always match how sharp a photo looks). You can still enable them to experiment on your own machine.

### Blur detection (`sharp` / `blurry` gallery filters)

Laplacian sharpness on a **`subject_rect`** crop of the original image (rembg bounding box, no white compositing), indexed as `blur_score`. Gallery tokens such as `sharp`, `blurry`, and `blur>=N` rank images within the current folder (default: bottom **20%** = blurry).

**Default:** off — see [`config/skyspotter_features.json`](config/skyspotter_features.json) (`"blur_score": false`).

Flags are resolved in order: **environment variable** → **features JSON file** → default (off).

#### Development (Pixi / launchers)

| Method | Command |
| --- | --- |
| Normal dev (blur off) | `pixi run start` or `scripts\launchers\launch_dev.bat` |
| Experimental Pixi env | `pixi run -e experimental start` |
| Experimental launcher | `scripts\launchers\launch_dev_experimental.bat` (Windows) / `launch_dev_experimental.sh` (macOS) |
| One-off env override | `$env:SkySpotter_ENABLE_BLUR_SCORE = "1"` then `pixi run start` |
| Write flags file | `pixi run set-features-experimental` or `pixi run set-features-off` |
| Show active file | `pixi run features-show` |

After enabling, **re-index** the folder so `blur_score` is written.

#### Building the Windows app

| Build type | How |
| --- | --- |
| **Release (blur off)** | `scripts\launchers\build_windows.bat` (writes `"blur_score": false` into the bundled config) |
| **Experimental build** | `set SkySpotter_BUILD_ENABLE_BLUR_SCORE=1` then `build_windows.bat`, or `python build.py --enable-blur-score` |

The installer bundles `config/skyspotter_features.json`; end users inherit whatever you baked at build time unless they override env vars.

**Optional tuning**

| Variable | Default | Purpose |
| --- | --- | --- |
| `SkySpotter_BLUR_MAX_SIZE` | `1920` | Max thumbnail side for blur scoring |
| `SkySpotter_BLUR_BLURRY_FRACTION` | `0.2` | Fraction ranked as blurry |
| `SkySpotter_BLUR_SUBJECT_BBOX_PAD` | `0.08` | Padding around rembg bbox |
| `SkySpotter_INDEX_MAX_SIZE` | `1280` | Classifier load size (independent unless you align with blur) |

**POC scripts (batch validation, not required for normal use)**

```powershell
pixi run fix-opencv
pixi run python scripts/poc_blur_detect.py "D:\path\to\photos"
```

See also `scripts/poc_blur_compare_modes.py` and `scripts/poc_blur_compare_sizes.py`. Implementation: [`src/blur_score.py`](src/blur_score.py).

Treat scores as **reference only**, not ground truth.

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

Launch and build scripts live under [`scripts/launchers/`](scripts/launchers/README.md). Upstream RAWviewer uses `scripts/Launch/`; SkySpotter keeps the `scripts/launchers/` layout instead.

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

**Virtual environments:** `pixi install` → `pixi run start` uses `.pixi/`. Build/debug batch scripts may create a local `rawviewer_env/` (created automatically). `.venv/` is optional for IDE use only.

**Optional dev toggles:**

| Variable | Effect |
|----------|--------|
| `RAWVIEWER_GPU_VIEW=1` | Use the experimental GPU-accelerated single-image viewport (smoother zoom/pan; default remains the classic scroll area) |
| `RAWVIEWER_GPU_VIEW_NO_GL=1` | Force raster viewport when GPU view is enabled (debug / fallback) |
| `RAWVIEWER_PERSISTENT_CACHE=1` | Enable disk/SQLite cache persistence (off by default) |

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

**Packaging note:** `build.py` strips dev logs before PyInstaller runs. The Windows installer copies **`pixi.toml` and `pixi.lock`** and runs **`pixi install --locked`** on the user's machine so installs match the pinned environment.

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
- **"Open with another app" does nothing**: Ensure a file is loaded in single-image view; restart the app after upgrading. The picker uses the native `OpenAs_RunDLLW` API (Unicode paths supported).
- **AttributeError with stdout**: This is normal for windowed builds - the application runs without a console window
- **Installer stuck on "Downloading MobileCLIP ONNX Models" / `No module named 'requests'`**:
  - Fixed in recent builds (`requests` in `pixi.toml`). Re-run the installer from a fresh build, or in the install folder run `_internal\pixi\pixi.exe install` then retry.
  - Public Hugging Face models download **without** an account or token.
- **Crash code `-1073741819` / `0xC0000005` (access violation)**:
  - This is a native crash (viewer, RAW decoder, or graphics driver layer), not always a Python exception.
  - Check **`%LOCALAPPDATA%\SkySpotter\logs\`** for `fatal_dump_*.log` and `crash_report_*.txt` (see **Crash logs** above). If you run from a git checkout, also check `<project>\src\logs\`.

### macOS

- **Minimum supported macOS (official prebuilt app): 13.0 (Ventura)**
  - macOS 12 and older may fail to launch the prebuilt binary; use a local Pixi build instead.

- **"App is damaged and should be moved to the Trash" / "Apple could not verify SkySpotter is free of malware"**:
  - **Why it happens**: Apple heavily restricts apps downloaded outside the App Store that aren't signed with a paid developer certificate. On newer macOS versions (especially Apple Silicon M1/M2/M3), macOS breaks the app's ad-hoc signature and aggressively blocks opening it.
  - **The Fix (Fastest)**: Open your **Terminal** app and run the following command to remove the quarantine flag:
    ```bash
    xattr -cr /Applications/SkySpotter.app
    ```
    _(Note: If you placed the app somewhere other than the Applications folder, update the path accordingly)._
- **"Symbol not found: (_mkfifoat)" or App crashes instantly on macOS 12 (Monterey) or older**:
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
- **Gallery search only filters EXIF and aircraft labels:** This is expected. Phrases like "sunset" or "crowd" are not semantic image search—they only match if those words appear in metadata or an indexed aircraft label.
- **Magic Wand hidden:** Wait until gallery indexing finishes. The wand appears once images are indexed (labeled types get their own folder; others can go to `Unclassified/`).
- **"Exporting aircraft model" on first folder open:** Normal one-time setup on a new PC (often under a minute). Later opens of the same folder are much faster.

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

**Third-party software and models** (ViT checkpoints, rembg / IS-Net, PyQt6, optional CLIP weights, etc.) are **not** covered by SkySpotter's MIT license alone. See **[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)** for copyrights, attribution, and redistribution requirements.

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
- **Chip in** if you'd like to help fund my **RIAT tickets for next year**.
- **Not an aviation photographer?** Try **[RAWviewer](https://github.com/markyip/RAWviewer)** for the same fast, local workflow with **semantic search** instead of aircraft recognition.

Enjoy organizing your airshow shots! 📸
