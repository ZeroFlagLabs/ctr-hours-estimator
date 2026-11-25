#!/usr/bin/env bash
set -e

# ============================================================
# Resolve paths
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Detect if script is inside /tools
if [ "$(basename "$SCRIPT_DIR")" = "tools" ]; then
    PROJECT_ROOT="$PARENT_DIR"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

cd "$PROJECT_ROOT"

VENV_PATH="$PROJECT_ROOT/venv"
ACTIVATE_PATH="$VENV_PATH/Scripts/activate"
TOOLS_DIR="$PROJECT_ROOT/tools"

NEEDS_VENV=false
RECREATE=false

# ============================================================
# Detect state
# ============================================================

if [ ! -d "$VENV_PATH" ]; then
    NEEDS_VENV=true
elif [ ! -f "$ACTIVATE_PATH" ]; then
    NEEDS_VENV=true
    RECREATE=true
fi

# ============================================================
# Function: create Qt Designer Windows shortcut
# ============================================================

create_qt_designer_shortcut() {
    local designer_exe="$VENV_PATH/Lib/site-packages/qt6_applications/Qt/bin/designer.exe"
    local shortcut_path="$TOOLS_DIR/Qt Designer (venv specific shortcut).lnk"

    mkdir -p "$TOOLS_DIR"

    if [ ! -f "$designer_exe" ]; then
        echo "Qt Designer not found, shortcut not created."
        echo "Expected path: $designer_exe"
        echo ""
        return 0
    fi

    echo "Qt Designer detected."
    echo "Creating Windows shortcut..."

    local designer_exe_win
    local shortcut_path_win
    local project_root_win

    designer_exe_win="$(cygpath -w "$designer_exe")"
    shortcut_path_win="$(cygpath -w "$shortcut_path")"
    project_root_win="$(cygpath -w "$PROJECT_ROOT")"

    powershell.exe -NoProfile -ExecutionPolicy Bypass "
        \$WshShell = New-Object -ComObject WScript.Shell
        \$Shortcut = \$WshShell.CreateShortcut('$shortcut_path_win')
        \$Shortcut.TargetPath = '$designer_exe_win'
        \$Shortcut.WorkingDirectory = '$project_root_win'
        \$Shortcut.IconLocation = '$designer_exe_win,0'
        \$Shortcut.Save()
    "

    if [ -f "$shortcut_path" ]; then
        echo "Shortcut created: $shortcut_path"
    else
        echo "WARNING: Shortcut creation command ran, but file was not found afterwards."
    fi

    echo ""
}

# ============================================================
# Setup (only if needed)
# ============================================================

if [ "$NEEDS_VENV" = true ]; then
    echo "--------------------------------------------------"
    echo "Dev Shell (Setup Mode)"
    echo ""
    echo "Working directory: $PROJECT_ROOT"
    echo ""

    if [ "$SCRIPT_DIR" != "$PROJECT_ROOT" ]; then
        echo "Detected tools folder execution"
        echo "Using project root: $PROJECT_ROOT"
        echo ""
    fi

    if [ "$RECREATE" = true ]; then
        echo "WARNING: Existing venv is invalid and will be recreated."
    else
        echo "No venv found."
    fi

    echo ""
    read -p "Continue? (y/n): " confirm

    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Aborted."
        exit 1
    fi

    if [ "$RECREATE" = true ]; then
        rm -rf "$VENV_PATH"
    fi

    echo ""
    echo "Creating virtual environment..."
    python -m venv "$VENV_PATH"

    source "$ACTIVATE_PATH"

    echo "Upgrading pip..."
    python -m pip install --upgrade pip

    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        echo "Installing dependencies..."
        pip install -r "$PROJECT_ROOT/requirements.txt"
    else
        echo "No requirements.txt found, skipping dependency install."
    fi

    echo ""
    create_qt_designer_shortcut

    echo "Setup complete."
    echo "--------------------------------------------------"
    echo ""

else
    # ========================================================
    # Normal mode (quiet)
    # ========================================================

    source "$ACTIVATE_PATH"
fi

# ============================================================
# Minimal output (always)
# ============================================================

echo "Dev Shell"
echo "Working directory: $PROJECT_ROOT"
echo "venv: activated"
echo ""

# Start interactive shell with venv indicator
echo -ne "\033]0;Dev Shell\007"
exec bash --rcfile <(
    echo 'export PS1="\[\e[36m\](venv) \W\[\e[0m\] \$ "'
)