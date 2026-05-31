@echo off
call "%~dp0_root.bat"
setlocal

REM Optional override:
REM set SkySpotter_TRAIN_DATA_PATH=D:\Development\SkySpotter\training_data\classified_images

echo [SkySpotter] Installing/updating pixi environments (default + dev-ml)...
pixi install
pixi install -e dev-ml
if errorlevel 1 (
  echo [SkySpotter] pixi install failed.
  exit /b 1
)

echo [SkySpotter] Starting model training...
pixi run -e dev-ml train-model
if errorlevel 1 (
  echo [SkySpotter] Training failed.
  exit /b 1
)

echo [SkySpotter] Training completed successfully.
endlocal
