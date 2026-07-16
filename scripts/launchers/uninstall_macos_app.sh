#!/bin/bash
# Uninstall SkySpotter.app / SkySpotter_Lite.app and clear macOS caches/preferences.
# End users: open Terminal in the extracted zip folder and run: bash uninstall_macos_app.sh
# Or double-click "Uninstall SkySpotter.command"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

# Allow running from quarantined folders
xattr -cr "${SCRIPT_DIR}" 2>/dev/null || true

confirm_uninstall() {
    if command -v osascript >/dev/null 2>&1; then
        osascript <<EOF
display dialog "Are you sure you want to uninstall SkySpotter?

This will:
• Close SkySpotter if running
• Remove SkySpotter from your Applications folder
• Delete your photo cache (~/.skyspotter_cache)
• Delete app logs and preferences" with title "SkySpotter Uninstaller" buttons {"Cancel", "Uninstall"} default button "Uninstall" with icon caution
EOF
        return $?
    fi
    echo "Are you sure you want to uninstall SkySpotter? [y/N]"
    read -r ans
    [[ "${ans}" =~ ^[yY] ]]
}

show_success() {
    local msg="$1"
    echo "${msg}"
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display dialog \"${msg}\" with title \"SkySpotter Uninstaller\" buttons {\"OK\"} default button \"OK\" with icon note" 2>/dev/null || true
    fi
}

# 1. Confirm with user
confirm_uninstall || { echo "Uninstallation cancelled."; exit 0; }

echo "Closing SkySpotter if running..."
killall SkySpotter 2>/dev/null || true
killall SkySpotter_Lite 2>/dev/null || true
pkill -f "[p]ython.*main\.py" 2>/dev/null || true
pkill -f "[p]ython.*SkySpotter" 2>/dev/null || true
sleep 1

echo "Removing applications..."
REMOVED_APPS=()
if [ -d "/Applications/SkySpotter.app" ]; then
    rm -rf "/Applications/SkySpotter.app"
    REMOVED_APPS+=("SkySpotter.app")
fi
if [ -d "/Applications/SkySpotter_Lite.app" ]; then
    rm -rf "/Applications/SkySpotter_Lite.app"
    REMOVED_APPS+=("SkySpotter_Lite.app")
fi

echo "Removing photo cache (~/.skyspotter_cache)..."
rm -rf "${HOME}/.skyspotter_cache" 2>/dev/null || true

echo "Removing application support and logs..."
rm -rf "${HOME}/Library/Application Support/SkySpotter" 2>/dev/null || true
rm -rf "${HOME}/Library/Logs/SkySpotter" 2>/dev/null || true

echo "Removing preferences plists..."
plists=(
    "${HOME}/Library/Preferences/com.SkySpotter.SkySpotter.plist"
    "${HOME}/Library/Preferences/SkySpotter.plist"
    "${HOME}/Library/Preferences/com.skyspotter.SkySpotter.plist"
)
for plist in "${plists[@]}"; do
    if [ -f "$plist" ]; then
        rm -f "$plist"
    fi
done

# Any other wildcard casing preferences
shopt -s nullglob
for plist in "${HOME}/Library/Preferences/"*[Rr][Aa][Ww]viewer*.plist; do
    if [ -f "$plist" ]; then
        rm -f "$plist"
    fi
done
shopt -u nullglob

# Delete defaults domain
for domain in com.SkySpotter.SkySpotter SkySpotter com.skyspotter.SkySpotter; do
    if defaults read "$domain" &>/dev/null; then
        defaults delete "$domain" 2>/dev/null || true
    fi
done

# Prepare success message
if [ ${#REMOVED_APPS[@]} -gt 0 ]; then
    show_success "SkySpotter has been successfully uninstalled. All application bundles, logs, cache, and preferences have been removed."
else
    show_success "Caches and preferences were removed, but no SkySpotter app bundle was found in /Applications."
fi
