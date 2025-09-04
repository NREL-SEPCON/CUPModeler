#!/bin/bash

# CUP Modeler Installer
# Usage: ./Install_MacLinux.sh [auto]

set -e

ORIGINAL_DIR="$HOME/Desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"  # Parent directory containing main.py
cd "$PROJECT_DIR"  # Work from project root

echo "CUP Modeler Installer"
echo "====================="
echo "Installer location: $SCRIPT_DIR"
echo "Project directory: $PROJECT_DIR"
echo "Will install to: $ORIGINAL_DIR"

AUTO_MODE=0
if [ "$1" = "auto" ]; then
    AUTO_MODE=1
fi

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    if [ $AUTO_MODE -eq 1 ]; then
        echo "$prompt [$default]"
        return 0
    else
        read -p "$prompt [$default]: " response
        response=${response:-$default}
        [[ "$response" =~ ^[Yy]$ ]]
    fi
}

choose_option() {
    local prompt="$1"
    local default="$2"
    local options="$3"
    echo "$options"
    if [ $AUTO_MODE -eq 1 ]; then
        echo "$prompt [$default]"
        echo "Auto mode: choosing default ($default)"
        REPLY="$default"
    else
        read -p "$prompt [$default]: " REPLY
        REPLY=${REPLY:-$default}
    fi
}

if [ $AUTO_MODE -eq 0 ]; then
    echo ""
    echo "Choose installation mode:"
    echo "1) Automatic - Install everything without prompts"
    echo "2) Interactive - Choose each step"
    echo "3) Exit"
    read -p "Enter choice: " CHOICE
    CHOICE=${CHOICE:-1}
    case $CHOICE in
        1) AUTO_MODE=1 ;;
        2) AUTO_MODE=0 ;;
        3) exit 0 ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
fi

echo ""
if [ $AUTO_MODE -eq 1 ]; then
    echo "Running automatic installation..."
else
    echo "Running interactive installation..."
fi
echo ""

# Step 1: Python
echo "[Step 1] Python Installation"
echo "----------------------------"
if command_exists python3; then
    PYTHON=python3
    echo "Found Python: $($PYTHON --version)"
elif command_exists python; then
    PYTHON=python
    echo "Found Python: $($PYTHON --version)"
else
    echo "Python not found on your system."
    echo ""
    choose_option "Choose option:" "1" "1) Let installer download and install Python
2) I'll install Python manually"
    if [ "$REPLY" = "1" ]; then
        echo ""
        echo "Installing Python..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if command_exists brew; then
                brew install python3
            else
                echo "Installing Homebrew first..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install python3
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if [ -f /etc/debian_version ]; then
                sudo apt update
                sudo apt install -y python3 python3-pip python3-venv
            elif [ -f /etc/redhat-release ]; then
                if command_exists dnf; then
                    sudo dnf install -y python3 python3-pip python3-venv
                else
                    sudo yum install -y python3 python3-pip python3-venv
                fi
            fi
        fi
        if command_exists python3; then
            PYTHON=python3
        elif command_exists python; then
            PYTHON=python
        else
            echo "Failed to install Python"
            exit 1
        fi
    else
        echo ""
        echo "Please install Python 3.9 or later from:"
        echo "https://python.org/downloads/"
        echo ""
        echo "Then run this installer again."
        exit 1
    fi
fi

# Step 2: Project Files
echo ""
echo "[Step 2] Project Files"
echo "----------------------"
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found!"
    echo ""
    echo "Please ensure you're running this installer from the Installer folder and that main.py is in the project root."
    echo ""
    exit 1
fi
echo "Found main.py - project files OK"

# Step 3: Virtual Environment
echo ""
echo "[Step 3] Virtual Environment"
echo "---------------------------"
echo "A virtual environment keeps dependencies isolated."
echo ""
if prompt_yes_no "Create virtual environment?" "y"; then
    echo "Creating virtual environment..."
    $PYTHON -m venv cup_env
    source cup_env/bin/activate
else
    echo ""
    echo "Skipping virtual environment."
    echo "NOTE: Dependencies will be installed globally."
    echo ""
fi

# Step 4: Dependencies
echo ""
echo "[Step 4] Dependencies"
echo "---------------------"
echo "Required packages:"
if [ -f "requirements.txt" ]; then
    echo "From requirements.txt:"
    cat requirements.txt
else
    echo "- matplotlib (plotting)"
    echo "- numpy (numerical computing)"
    echo "- pandas (data handling)"
    echo "- scipy (scientific computing)"
    echo "- numba (performance)"
    echo "- Pillow (image handling)"
    echo "- openpyxl (Excel support)"
fi
echo ""
choose_option "Choose option:" "1" "1) Install all dependencies automatically
2) I'll install them manually
3) Skip (already installed)"
if [ "$REPLY" = "1" ]; then
    echo ""
    echo "Installing dependencies..."
    $PYTHON -m pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        $PYTHON -m pip install -r requirements.txt
    else
        $PYTHON -m pip install matplotlib numpy pandas scipy numba Pillow openpyxl
    fi
elif [ "$REPLY" = "2" ]; then
    echo ""
    echo "Please install the dependencies using:"
    if [ -f "requirements.txt" ]; then
        echo "  pip install -r requirements.txt"
    else
        echo "  pip install matplotlib numpy pandas scipy numba Pillow openpyxl"
    fi
    echo ""
    if [ $AUTO_MODE -eq 0 ]; then
        read -p "Press Enter when done..."
    fi
fi

# Verify dependencies
echo ""
echo "Checking installed dependencies..."
if $PYTHON -c "import matplotlib, numpy, pandas, scipy, numba, PIL, openpyxl; print('All core dependencies OK')" 2>/dev/null; then
    echo "All core dependencies verified."
else
    echo ""
    echo "WARNING: Some dependencies are missing!"
    echo "The application may not work correctly."
    echo ""
    if ! prompt_yes_no "Continue anyway?" "n"; then
        exit 1
    fi
fi

# Step 5: PyInstaller
echo ""
echo "[Step 5] PyInstaller"
echo "-------------------"
echo "PyInstaller creates the standalone executable."
echo ""
if prompt_yes_no "Install PyInstaller?" "y"; then
    echo "Installing PyInstaller..."
    $PYTHON -m pip install pyinstaller
fi

# Step 6: Build Executable
echo ""
echo "[Step 6] Build Executable"
echo "------------------------"
if ! $PYTHON -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not available. Cannot build executable."
    echo "Environment is set up for development use."
    exit 0
fi

echo "Ready to build the standalone executable."
echo ""
if ! prompt_yes_no "Build CUP Modeler?" "y"; then
    echo ""
    echo "Skipping build. Environment is ready for development."
    exit 0
fi

echo ""
echo "Building executable (this may take a few minutes)..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    ICON_OPT=""
    [ -f "Installers/icon.icns" ] && ICON_OPT="--icon=Installers/icon.icns"
    APP_NAME="CUP Modeler.app"
    PYINSTALLER_MODE=""  # onedir mode (default) for macOS .app bundles
else
    ICON_OPT=""
    [ -f "Installers/icon.ico" ] && ICON_OPT="--icon=Installers/icon.ico"
    APP_NAME="CUP Modeler"
    PYINSTALLER_MODE="-F"  # onefile mode for other platforms
fi

$PYTHON -m PyInstaller $PYINSTALLER_MODE --windowed --name="CUP Modeler" \
    $ICON_OPT \
    --add-data="models:models" \
    --add-data="app:app" \
    --hidden-import=matplotlib.backends.backend_tkagg \
    --hidden-import=matplotlib.backends.backend_pdf \
    --hidden-import=scipy.io.matlab \
    --hidden-import=numba.core.types.scalars \
    --hidden-import=numba.core.types.common \
    --hidden-import=numba.typed \
    --hidden-import=openpyxl \
    --hidden-import=openpyxl.cell._writer \
    --hidden-import=openpyxl.styles \
    --exclude-module=IPython \
    --exclude-module=jupyter \
    --exclude-module=pytest \
    main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Build failed! Check error messages above."
    exit 1
fi

# Move executable with proper verification
echo ""
echo "Moving executable to desktop..."
MOVE_SUCCESS=0

if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "$PROJECT_DIR/dist/CUP Modeler.app" ]; then
        rm -rf "$ORIGINAL_DIR/CUP Modeler.app" 2>/dev/null || true
        cp -R "$PROJECT_DIR/dist/CUP Modeler.app" "$ORIGINAL_DIR/"
        if [ -d "$ORIGINAL_DIR/CUP Modeler.app" ]; then
            MOVE_SUCCESS=1
            echo "Successfully moved $APP_NAME to $ORIGINAL_DIR"
        fi
    else
        echo "Warning: App bundle not found at expected location"
        echo "Looking for: $PROJECT_DIR/dist/CUP Modeler.app"
        ls -la "$PROJECT_DIR/dist/" 2>/dev/null || echo "dist directory not found"
    fi
else
    if [ -f "$PROJECT_DIR/dist/CUP Modeler" ]; then
        cp "$PROJECT_DIR/dist/CUP Modeler" "$ORIGINAL_DIR/"
        chmod +x "$ORIGINAL_DIR/CUP Modeler"
        if [ -f "$ORIGINAL_DIR/CUP Modeler" ]; then
            MOVE_SUCCESS=1
            echo "Successfully moved $APP_NAME to $ORIGINAL_DIR"
        fi
    else
        echo "Warning: Executable not found at expected location"
        echo "Looking for: $PROJECT_DIR/dist/CUP Modeler"
        ls -la "$PROJECT_DIR/dist/" 2>/dev/null || echo "dist directory not found"
    fi
fi

# Step 7: Cleanup
echo ""
echo "[Step 7] Cleanup"
echo "---------------"
echo "Temporary build files can be removed to save space."
echo ""
if prompt_yes_no "Remove temporary files?" "y"; then
    echo "Cleaning up..."
    deactivate 2>/dev/null || true
    rm -rf "$PROJECT_DIR/cup_env" 2>/dev/null
    rm -rf "$PROJECT_DIR/dist" 2>/dev/null
    rm -rf "$PROJECT_DIR/build" 2>/dev/null
    rm -f "$PROJECT_DIR"/*.spec 2>/dev/null
    rm -rf "$PROJECT_DIR/__pycache__" 2>/dev/null
    echo "Cleanup complete"
fi

echo ""
echo "================================"
if [ $MOVE_SUCCESS -eq 1 ]; then
    echo "INSTALLATION COMPLETE!"
    echo "Executable: $ORIGINAL_DIR/$APP_NAME"
else
    echo "INSTALLATION COMPLETE WITH WARNINGS!"
    echo "The app was built but may not have been moved correctly."
    echo "Check the dist/ folder in: $PROJECT_DIR"
fi
echo "================================"
echo ""