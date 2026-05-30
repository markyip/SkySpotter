# Launcher scripts

Run from the **project root** (examples):

| Platform | Dev launch | Experimental dev | Train | Verify | Build |
|----------|------------|------------------|-------|--------|-------|
| **Windows** | `scripts\launchers\launch_dev.bat` | `launch_dev_experimental.bat` | `train_model.bat` | `verify_model.bat` | `build_windows.bat` |
| **macOS** | `./scripts/launchers/launch_dev.sh` | `launch_dev_experimental.sh` | `train_model.sh` | `verify_model.sh` | `build_macos.sh` |

**Build flags:** set `SkySpotter_BUILD_ENABLE_BLUR_SCORE=1` before `build_windows.bat` to bundle experimental blur scoring, or pass `python build.py --enable-blur-score`.

`uninstall.bat` stays at the repo root — it is tied to the installed app layout.
