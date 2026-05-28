@echo off
echo Running SkySpotter in debug mode...
echo All debug logs will be displayed in this console window.
echo.
echo Press Ctrl+C to stop the application.
echo.

REM Prefer Pixi environment for reproducible local development
where pixi >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set SKYSPOTTER_USE_PIXI=1
) else (
    set SKYSPOTTER_USE_PIXI=0
)

REM Run the application with debug output
set RAWVIEWER_USE_PROCESS_POOL=0
set RAWVIEWER_VERBOSE_INFO_LOGS=0
set RAWVIEWER_VERBOSE_CONSOLE=0
set RAWVIEWER_FOCUS_GALLERY_SWITCH=1
set RAWVIEWER_FILE_LOG=1
echo.
echo ========================================
echo Starting Python application...
echo ========================================
echo.
if %SKYSPOTTER_USE_PIXI% EQU 1 (
    echo Using Pixi environment...
    pixi run python -u src/main.py %*
) else (
    echo Pixi not found, falling back to system Python...
    python -u src/main.py %*
)
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
if %EXIT_CODE% EQU 0 (
    echo Application exited normally (code: %EXIT_CODE%)
) else (
    echo Application exited with error code: %EXIT_CODE%
    echo.
    echo Check the log file in src\logs\ for detailed error information.
)
echo ========================================
echo.

REM Always pause to keep window open so user can see any error messages
pause
