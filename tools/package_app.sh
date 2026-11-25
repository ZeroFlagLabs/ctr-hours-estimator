#!/usr/bin/env bash
set -e
trap 'echo ""; echo "ERROR: Build failed. Press Enter to inspect..."; read' ERR

# ============================================================
# Error helper
# ============================================================

fail() {
    echo ""
    echo "ERROR: $1"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
}

# ============================================================
# Resolve project root
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

if [ "$(basename "$SCRIPT_DIR")" = "tools" ]; then
    PROJECT_ROOT="$PARENT_DIR"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

cd "$PROJECT_ROOT"

# ============================================================
# Activate venv
# ============================================================

VENV_PATH="$PROJECT_ROOT/venv"
ACTIVATE_PATH="$VENV_PATH/Scripts/activate"

if [ -f "$ACTIVATE_PATH" ]; then
    echo "Activating virtual environment..."
    source "$ACTIVATE_PATH"
else
    fail "venv not found. Run dev_shell.sh first."
fi

# ============================================================
# Config
# ============================================================

ENTRY_POINT="src/main.py"
ICON_PATH="src/resources/icons/icon.ico"

# ============================================================
# Ask for app details
# ============================================================

echo ""
echo "------------------------------------------"
echo "Package App (PyInstaller)"
echo "------------------------------------------"
echo ""

read -p "Enter App Name: " APP_NAME
[ -z "$APP_NAME" ] && fail "App name cannot be empty."

read -p "Enter Version (e.g. 1.0): " APP_VERSION
[ -z "$APP_VERSION" ] && fail "Version cannot be empty."

FINAL_NAME="$APP_NAME v$APP_VERSION"

# ============================================================
# Helper: add-data builder
# ============================================================

ADD_DATA_ARGS=()

add_data() {
    local src="$1"
    local dest="$2"

    if [ -f "$src" ] || [ -d "$src" ]; then
        ADD_DATA_ARGS+=("--add-data" "$src;$dest")
        echo "✔ Including: $src -> $dest"
    else
        echo "– Skipping: $src"
    fi
}

# ============================================================
# Validation
# ============================================================

echo ""
echo "Checking project structure..."
echo ""

ERROR=false

[ -f "$ENTRY_POINT" ] && echo "✔ Entry point: $ENTRY_POINT" || { echo "✖ Missing: $ENTRY_POINT"; ERROR=true; }

[ -d "src/ui" ] && echo "✔ UI folder found" || echo "– No UI folder"
[ -d "src/resources/images" ] && echo "✔ Images folder found" || echo "– No images folder"
[ -d "src/resources/data" ] && echo "✔ Data folder found" || echo "– No data folder"

[ -f "$ICON_PATH" ] && echo "✔ Icon found" || echo "⚠ Icon not found (optional)"

echo ""

[ "$ERROR" = true ] && fail "Build aborted due to missing required files."

# ============================================================
# Confirmation
# ============================================================

read -p "Proceed with build? (y/n): " confirm
[[ "$confirm" != "y" && "$confirm" != "Y" ]] && { echo "Build cancelled."; exit 0; }

# ============================================================
# Collect resources (STANDARDISED)
# ============================================================

echo ""
echo "Collecting resources..."

add_data "src/ui" "ui"
add_data "src/resources/images" "resources/images"
add_data "src/resources/data" "resources/data"

# ============================================================
# Clean
# ============================================================

echo ""
echo "Cleaning old build..."
rm -rf build dist 2>/dev/null || true
rm -f *.spec 2>/dev/null || true

# ============================================================
# Build
# ============================================================

echo ""
echo "Running PyInstaller..."

pyinstaller \
    --onefile \
    --windowed \
    --name "$FINAL_NAME" \
    --icon="$ICON_PATH" \
    "${ADD_DATA_ARGS[@]}" \
    "$ENTRY_POINT"

# ============================================================
# Done
# ============================================================

echo ""
echo "Build complete."
echo "Output: $PROJECT_ROOT/dist"
echo "------------------------------------------"

echo ""
echo "Cleaning up spec files..."
rm -f "$PROJECT_ROOT"/*.spec 2>/dev/null || true

# Open dist folder
explorer.exe "$(cygpath -w "$PROJECT_ROOT/dist")" >/dev/null 2>&1 &

# Keep window open
echo ""
echo "Entering interactive shell..."
echo -ne "\033]0;Build Complete\007"

exec bash --rcfile <(
    echo 'export PS1="\[\e[36m\](venv) \W\[\e[0m\] \$ "'
)