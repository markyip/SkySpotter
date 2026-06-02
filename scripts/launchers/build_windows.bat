@echo off
call "%~dp0_root.bat"

echo SkySpotter Windows Build Script
echo ===============================
echo.

if not exist "SkySpotter_env" (
    echo Creating virtual environment...
    python -m venv SkySpotter_env
    echo Virtual environment created.
)

echo Activating virtual environment...
call SkySpotter_env\Scripts\activate.bat

echo Checking MobileCLIP2 ONNX models...
python scripts/download_mobileclip_onnx.py

echo Installing dependencies...
pip install --upgrade PyQt6 rawpy send2trash pyinstaller natsort exifread pyexiv2 Pillow psutil numpy qtawesome pyqtgraph onnxruntime-directml reverse-geocoder pycountry pywin32 opencv-contrib-python
python scripts/pixi_fix_opencv.py

echo Optional: enable experimental blur scoring for this build (default OFF)
if /I "%SkySpotter_BUILD_ENABLE_BLUR_SCORE%"=="1" (
  echo Building with experimental blur scoring enabled...
  python scripts/set_features.py --copy-experimental
) else (
  python scripts/set_features.py --blur-score off
)

echo Checking for running SkySpotter instances...
taskkill /F /IM SkySpotter.exe /T >nul 2>&1
if %errorlevel% == 0 (
    echo Closed running SkySpotter instances
    timeout /t 1 /nobreak >nul
)

echo Cleaning previous builds...
if exist build rmdir /s /q build 2>nul
if exist dist (
    if exist dist\SkySpotter.exe del /f /q dist\SkySpotter.exe 2>nul
    rmdir /s /q dist 2>nul
)
if exist *.spec del /q *.spec 2>nul

echo Building SkySpotter...
if /I "%SkySpotter_BUILD_ENABLE_BLUR_SCORE%"=="1" (
  python build.py --enable-blur-score
) else (
  python build.py --disable-blur-score
)
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed! Check the error messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo Build completed successfully!
echo   dist\SkySpotter\
pause
