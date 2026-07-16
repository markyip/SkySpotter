#!/usr/bin/env bash
# Full cache + session wipe for SkySpotter (dev and installed builds).
# Removes ~/.skyspotter_cache, ~/.skyspotter_cache (legacy), logs, macOS QSettings.
# Does NOT remove the app bundle or bundled models.

set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

CLEARED=0
FAILED=0

echo
echo "========================================"
echo " SkySpotter - clear ALL cache and state"
echo "========================================"
echo

kill_app() {
    echo "Closing SkySpotter if running..."
    killall SkySpotter 2>/dev/null || true
    killall SkySpotter 2>/dev/null || true
    pkill -f "[p]ython.*main\.py" 2>/dev/null || true
    pkill -f "[p]ython.*SkySpotter" 2>/dev/null || true
    sleep 2
}

remove_tree() {
    local target="$1"
    local label="$2"
    if [ ! -e "$target" ]; then
        return 0
    fi
    echo "Removing ${label}:"
    echo "  ${target}"
    local tries=0
    while [ "$tries" -lt 5 ]; do
        tries=$((tries + 1))
        rm -rf "$target" 2>/dev/null || true
        if [ ! -e "$target" ]; then
            CLEARED=1
            return 0
        fi
        sleep 1
    done
    echo "  WARNING: Could not fully remove."
    FAILED=1
}

clear_qsettings() {
    echo "Clearing QSettings / session..."
    local removed=0
    local plists=(
        "${HOME}/Library/Preferences/com.SkySpotter.SkySpotter.plist"
        "${HOME}/Library/Preferences/SkySpotter.plist"
        "${HOME}/Library/Preferences/com.SkySpotter.SkySpotter.plist"
        "${HOME}/Library/Preferences/SkySpotter.plist"
    )
    for plist in "${plists[@]}"; do
        if [ -f "$plist" ]; then
            rm -f "$plist" && removed=1 && echo "  Removed ${plist}"
        fi
    done
    shopt -s nullglob
    for plist in "${HOME}/Library/Preferences/"*[Ss]ky[Ss]potter*.plist "${HOME}/Library/Preferences/"*[Rr][Aa][Ww]viewer*.plist; do
        if [ -f "$plist" ]; then
            rm -f "$plist" && removed=1 && echo "  Removed ${plist}"
        fi
    done
    shopt -u nullglob
    if [ "$removed" -eq 1 ]; then
        CLEARED=1
    else
        echo "  Preferences already clean"
    fi
}

kill_app

remove_tree "${HOME}/.skyspotter_cache" "SkySpotter cache"
remove_tree "${HOME}/.skyspotter_cache" "legacy SkySpotter cache"
remove_tree "${HOME}/Library/Application Support/SkySpotter/logs" "SkySpotter logs (Application Support)"
remove_tree "${HOME}/Library/Logs/SkySpotter" "SkySpotter logs (Library/Logs)"
remove_tree "${ROOT}/src/logs" "repository dev logs (src/logs)"
clear_qsettings

touch "${ROOT}/.skyspotter_cold_start"

echo
if [ "$FAILED" -eq 1 ]; then
    echo "Finished with warnings."
else
    echo "Cache and session cleared. Restart SkySpotter for a fresh start."
fi
echo "Tip: SkySpotter_DISABLE_SESSION_RESTORE=1 skips auto-restore on next launch."
echo
