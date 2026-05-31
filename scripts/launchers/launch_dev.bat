@echo off
call "%~dp0_root.bat"
setlocal

echo [SkySpotter] Launching in development mode...
echo Logs appear in this console. Press Ctrl+C to stop.
echo.

where pixi >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  set SKYSPOTTER_USE_PIXI=1
) else (
  set SKYSPOTTER_USE_PIXI=0
)

set PYTHONUTF8=1
set SkySpotter_FEATURES_FILE=config\skyspotter_features.json
set RAWVIEWER_USE_PROCESS_POOL=0
set SkySpotter_USE_PROCESS_POOL=1
set SkySpotter_PROGRESSIVE_RAW_LOAD=1
set SkySpotter_NAV_PRELOAD_DISPLAY=1
set RAWVIEWER_AUTO_METADATA_INDEX_IDLE_MS=5000
set RAWVIEWER_VERBOSE_INFO_LOGS=0
set RAWVIEWER_VERBOSE_CONSOLE=0
set RAWVIEWER_FOCUS_GALLERY_SWITCH=1
set RAWVIEWER_FILE_LOG=1

if %SKYSPOTTER_USE_PIXI% EQU 1 (
  echo Using Pixi environment...
  pixi run setup >nul 2>nul
  pixi run python -u src/main.py %*
) else (
  echo Pixi not found, falling back to system Python...
  python -u src/main.py %*
)
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
  echo [SkySpotter] Exited normally.
) else (
  echo [SkySpotter] Exited with code %EXIT_CODE%. Check src\logs\ or %%LOCALAPPDATA%%\SkySpotter\logs for details.
)
pause
endlocal
