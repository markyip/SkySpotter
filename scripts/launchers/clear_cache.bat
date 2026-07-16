@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM Full cache + session wipe for SkySpotter (dev and installed builds).
REM Removes: ~/.skyspotter_cache + ~/.skyspotter_cache (legacy), logs, dev logs,
REM and QSettings under HKCU\Software\SkySpotter + HKCU\Software\SkySpotter (legacy).
REM Does NOT remove: %%LOCALAPPDATA%%\SkySpotter app install (SkySpotter.exe, bundled models).
cd /d "%~dp0..\..\.."

echo.
echo ========================================
echo  SkySpotter - clear ALL cache and state
echo ========================================
echo.

call :KillApp
timeout /t 2 /nobreak >nul

set "CLEARED=0"
set "FAILED=0"

call :RemoveTree "%USERPROFILE%\.skyspotter_cache" "image/EXIF/semantic/thumbnail cache (SkySpotter)"
call :RemoveTree "%USERPROFILE%\.skyspotter_cache" "legacy image/EXIF/semantic/thumbnail cache (SkySpotter)"
call :RemoveTree "%LOCALAPPDATA%\SkySpotter\logs" "runtime logs (%%LOCALAPPDATA%%\SkySpotter\logs)"
call :RemoveTree "%APPDATA%\SkySpotter\logs" "roaming logs (%%APPDATA%%\SkySpotter\logs)"
call :RemoveTree "%LOCALAPPDATA%\SkySpotter\logs" "legacy runtime logs (%%LOCALAPPDATA%%\SkySpotter\logs)"
call :RemoveTree "%APPDATA%\SkySpotter\logs" "legacy roaming logs (%%APPDATA%%\SkySpotter\logs)"
call :RemoveTree "src\logs" "repository dev logs (src\logs)"

REM Optional cache subfolders under the install root (if present).
call :RemoveTree "%LOCALAPPDATA%\SkySpotter\cache" "install cache folder (SkySpotter)"
call :RemoveTree "%LOCALAPPDATA%\SkySpotter\CrashDumps" "crash dumps (SkySpotter)"
call :RemoveTree "%LOCALAPPDATA%\SkySpotter\cache" "legacy install cache folder (SkySpotter)"
call :RemoveTree "%LOCALAPPDATA%\SkySpotter\CrashDumps" "legacy crash dumps (SkySpotter)"

echo Clearing QSettings / session registry (window, sort, last folder, rotations, semantic flags)...
call :RemoveRegistryKey "HKCU\Software\SkySpotter"
call :RemoveRegistryKey "HKCU\Software\SkySpotter"

echo.
if "!FAILED!"=="1" (
    echo Finished with warnings. Close SkySpotter and any Python dev instance, then run again.
) else if "!CLEARED!"=="1" (
    echo All cache and session state cleared. Restart SkySpotter for a completely fresh start.
) else (
    echo Nothing found to clear ^(already clean^).
)
echo.
echo Not removed: %%LOCALAPPDATA%%\SkySpotter application files ^(exe, installer models^).
echo Tip: set SkySpotter_DISABLE_SESSION_RESTORE=1 ^(or RAWVIEWER_DISABLE_SESSION_RESTORE=1^) to skip auto-restore on next launch.
echo.
pause
exit /b 0

:KillApp
echo Closing SkySpotter if running...
taskkill /IM SkySpotter.exe /F >nul 2>&1
taskkill /IM SkySpotter.exe /F >nul 2>&1
REM Dev runs via python main.py — stop common launcher patterns.
for /f "tokens=2" %%P in ('wmic process where "name='python.exe' and CommandLine like '%%main.py%%'" get ProcessId 2^>nul ^| findstr /r "[0-9]"') do (
    taskkill /PID %%P /F >nul 2>&1
)
for /f "tokens=2" %%P in ('wmic process where "name='python.exe' and CommandLine like '%%SkySpotter%%'" get ProcessId 2^>nul ^| findstr /r "[0-9]"') do (
    taskkill /PID %%P /F >nul 2>&1
)
for /f "tokens=2" %%P in ('wmic process where "name='python.exe' and CommandLine like '%%SkySpotter%%'" get ProcessId 2^>nul ^| findstr /r "[0-9]"') do (
    taskkill /PID %%P /F >nul 2>&1
)
exit /b 0

:RemoveRegistryKey
set "REGKEY=%~1"
reg query "%REGKEY%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    reg delete "%REGKEY%" /f >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "CLEARED=1"
        echo   Removed %REGKEY%
    ) else (
        echo   WARNING: Could not remove registry key %REGKEY%
        set "FAILED=1"
    )
) else (
    echo   %REGKEY% already clean
)
exit /b 0

:RemoveTree
set "TARGET=%~1"
set "LABEL=%~2"
if not exist "%TARGET%" exit /b 0
echo Removing %LABEL%:
echo   %TARGET%
set "TRIES=0"
:RemoveTreeRetry
set /a TRIES+=1
rmdir /S /Q "%TARGET%" 2>nul
if exist "%TARGET%" (
    if !TRIES! LSS 5 (
        timeout /t 1 /nobreak >nul
        goto RemoveTreeRetry
    )
    echo   WARNING: Could not fully remove - file may be locked.
    set "FAILED=1"
) else (
    set "CLEARED=1"
)
exit /b 0
