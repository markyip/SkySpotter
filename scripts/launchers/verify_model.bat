@echo off
call "%~dp0_root.bat"
setlocal

REM Optional overrides:
REM set SkySpotter_VERIFY_INPUT_DIR=...\testing_data\test_images
REM set SkySpotter_VERIFY_MODEL_DIR=...\customized_model
REM set SkySpotter_VERIFY_OUTPUT_DIR=...\testing_data\test_output

echo [SkySpotter] Installing/updating pixi environment...
pixi install
if errorlevel 1 (
  echo [SkySpotter] pixi install failed.
  exit /b 1
)

echo [SkySpotter] Verifying trained model on testing_data/test_images...
echo [SkySpotter] Checkpoint: customized_model/  (override with SkySpotter_VERIFY_MODEL_DIR)
echo [SkySpotter] Results: testing_data/test_output/

set "VERIFY_ARGS="
if defined SkySpotter_VERIFY_INPUT_DIR set "VERIFY_ARGS=%VERIFY_ARGS% --input-dir "%SkySpotter_VERIFY_INPUT_DIR%""
if defined SkySpotter_VERIFY_MODEL_DIR set "VERIFY_ARGS=%VERIFY_ARGS% --model-dir "%SkySpotter_VERIFY_MODEL_DIR%""
if defined SkySpotter_VERIFY_OUTPUT_DIR set "VERIFY_ARGS=%VERIFY_ARGS% --output-dir "%SkySpotter_VERIFY_OUTPUT_DIR%""

pixi run python scripts/batch_test_classifier.py %VERIFY_ARGS%
if errorlevel 1 (
  echo [SkySpotter] Verification failed.
  exit /b 1
)

echo [SkySpotter] Verification completed. See testing_data\test_output\top3_detection_scores.csv
endlocal
