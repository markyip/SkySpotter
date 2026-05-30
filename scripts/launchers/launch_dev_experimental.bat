@echo off
call "%~dp0_root.bat"
setlocal

echo [SkySpotter] Launching with EXPERIMENTAL features (blur scoring)...
echo Uses Pixi environment "experimental" or SkySpotter_ENABLE_BLUR_SCORE=1.
echo.

set PYTHONUTF8=1
set SkySpotter_PREFER_DIRECTML=1
set SkySpotter_FEATURES_FILE=config\skyspotter_features.json
set SkySpotter_ENABLE_BLUR_SCORE=1
set RAWVIEWER_USE_PROCESS_POOL=0
set RAWVIEWER_VERBOSE_INFO_LOGS=0
set RAWVIEWER_VERBOSE_CONSOLE=0
set RAWVIEWER_FOCUS_GALLERY_SWITCH=1
set RAWVIEWER_FILE_LOG=1

where pixi >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  pixi run -e experimental start %*
) else (
  echo Pixi not found — using system Python with env override...
  python -u src/main.py %*
)
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
  echo [SkySpotter] Exited normally.
) else (
  echo [SkySpotter] Exited with code %EXIT_CODE%.
)
pause
endlocal
