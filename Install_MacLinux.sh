#!/bin/bash

# CUP Modeler Build Script with Auto Python Installation
# Usage: ./Install_MacLinux_auto.sh

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎯 CUP Modeler Auto-Install Script"
echo "=================================="
echo "📁 Working from: $(pwd)"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python on macOS
install_python_macos() {
    echo "🍎 Installing Python on macOS..."
    
    # Check if Homebrew is installed
    if command_exists brew; then
        echo "✅ Homebrew found, installing Python..."
        brew install python3
    elif command_exists curl; then
        echo "📥 Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo "📥 Installing Python..."
        brew install python3
    else
        echo "❌ Cannot auto-install Python on macOS without curl"
        echo "Please manually install Python from: https://python.org/downloads/"
        echo "Or install Homebrew first: https://brew.sh/"
        read -p "Press Enter after installing Python..."
    fi
}

# Function to install Python on Linux
install_python_linux() {
    echo "🐧 Installing Python on Linux..."
    
    # Detect Linux distribution
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        echo "📥 Detected Debian/Ubuntu, installing Python..."
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev
    elif [ -f /etc/redhat-release ]; then
        # RedHat/CentOS/Fedora
        echo "📥 Detected RedHat/CentOS/Fedora, installing Python..."
        if command_exists dnf; then
            sudo dnf install -y python3 python3-pip python3-venv python3-devel
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip python3-venv python3-devel
        fi
    elif [ -f /etc/arch-release ]; then
        # Arch Linux
        echo "📥 Detected Arch Linux, installing Python..."
        sudo pacman -S --noconfirm python python-pip
    else
        echo "❌ Unknown Linux distribution"
        echo "Please manually install Python 3.9+ using your package manager"
        echo "Common commands:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "  CentOS/RHEL:   sudo yum install python3 python3-pip python3-venv"
        echo "  Fedora:        sudo dnf install python3 python3-pip python3-venv"
        echo "  Arch:          sudo pacman -S python python-pip"
        read -p "Press Enter after installing Python..."
    fi
}

# Function to verify Python installation
verify_python() {
    if command_exists python3; then
        PYTHON=python3
        PYTHON_VERSION=$($PYTHON --version 2>&1)
        echo "✅ Found: $PYTHON_VERSION"
        return 0
    elif command_exists python; then
        PYTHON=python
        PYTHON_VERSION=$($PYTHON --version 2>&1)
        echo "✅ Found: $PYTHON_VERSION"
        return 0
    else
        echo "❌ Python still not found after installation attempt"
        return 1
    fi
}

# Check if Python is available
echo "🔍 Checking for Python..."
if command_exists python3; then
    PYTHON=python3
    echo "✅ Found Python 3: $($PYTHON --version)"
elif command_exists python; then
    PYTHON=python
    echo "✅ Found Python: $($PYTHON --version)"
else
    echo "❌ Python not found. Attempting auto-installation..."
    
    # Detect OS and install Python
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_python_macos
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        install_python_linux
    else
        echo "❌ Unknown operating system: $OSTYPE"
        echo "Please manually install Python 3.9+ from: https://python.org/downloads/"
        read -p "Press Enter after installing Python..."
    fi
    
    # Verify installation worked
    if ! verify_python; then
        echo "❌ Python installation failed or not found"
        echo "Please manually install Python and try again"
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    echo "⚠️ Warning: Python $PYTHON_VERSION is quite old"
    echo "   Recommend Python 3.9+ for best compatibility"
fi

# Check for pip
echo "🔍 Checking for pip..."
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    echo "📥 Installing pip..."
    if command_exists curl; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON get-pip.py
        rm get-pip.py
    else
        echo "❌ Pip not found and cannot auto-install without curl"
        echo "Please install pip manually"
        exit 1
    fi
fi

echo "✅ Using Python: $PYTHON_VERSION"

# Check if virtual environment module is available
if ! $PYTHON -c "import venv" 2>/dev/null; then
    echo "📥 Installing python3-venv..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            sudo apt install -y python3-venv
        elif [ -f /etc/redhat-release ]; then
            if command_exists dnf; then
                sudo dnf install -y python3-venv
            elif command_exists yum; then
                sudo yum install -y python3-venv
            fi
        fi
    fi
fi

# Create virtual environment
echo "🔄 Creating virtual environment..."
$PYTHON -m venv cup_modeler_env

# Activate virtual environment
source cup_modeler_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
$PYTHON -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    echo "📝 Using requirements.txt"
    $PYTHON -m pip install -r requirements.txt
else
    echo "📝 Installing basic dependencies..."
    $PYTHON -m pip install matplotlib numpy pandas scipy numba Pillow
fi

# Install PyInstaller
echo "🔧 Installing PyInstaller..."
$PYTHON -m pip install pyinstaller

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in current directory!"
    echo "📂 Current directory contents:"
    ls -la
    echo ""
    echo "Make sure you're running this script from your project root."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Found main.py"

# Build with PyInstaller
echo "🚀 Building executable with PyInstaller..."

# Detect OS and build accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Building for macOS..."
    $PYTHON -m PyInstaller --onedir --windowed --name="CUP Modeler" \
        --icon="icon.icns" \
        --add-data="models:models" \
        --add-data="app:app" \
        --hidden-import=matplotlib.backends.backend_tkagg \
        --hidden-import=matplotlib.backends.backend_pdf \
        --hidden-import=scipy.io.matlab \
        --hidden-import=numba.core.types.scalars \
        --hidden-import=numba.core.types.common \
        --hidden-import=numba.typed \
        --exclude-module=IPython --exclude-module=jupyter --exclude-module=pytest \
        --exclude-module=sphinx --exclude-module=sympy \
        --exclude-module=cv2 --exclude-module=sklearn \
        --exclude-module=tensorflow --exclude-module=torch --exclude-module=keras \
        main.py
        
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Building for Linux..."
    $PYTHON -m PyInstaller --onedir --windowed --name="CUP Modeler" \
        --icon="icon.ico" \
        --add-data="models:models" \
        --add-data="app:app" \
        --hidden-import=matplotlib.backends.backend_tkagg \
        --hidden-import=matplotlib.backends.backend_pdf \
        --hidden-import=scipy.io.matlab \
        --hidden-import=numba.core.types.scalars \
        --hidden-import=numba.core.types.common \
        --hidden-import=numba.typed \
        --exclude-module=IPython --exclude-module=jupyter --exclude-module=pytest \
        --exclude-module=sphinx --exclude-module=sympy \
        --exclude-module=cv2 --exclude-module=sklearn \
        --exclude-module=tensorflow --exclude-module=torch --exclude-module=keras \
        main.py
else
    echo "❌ Unsupported operating system: $OSTYPE"
fi

# Set executable permissions
echo "🔧 Setting executable permissions..."
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    find dist/ -name "CUP Modeler" -type f -exec chmod +x {} \; 2>/dev/null || true
    
    # Create launcher script
    cat > run_cup_modeler.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/dist/CUP Modeler/CUP Modeler"
EOF
    chmod +x run_cup_modeler.sh 2>/dev/null || true
    echo "✅ Created launcher: run_cup_modeler.sh"
fi

# Optional cleanup
echo ""
echo "🧹 Cleaning up build artifacts..."
rm -rf build/ *.spec __pycache__/ 2>/dev/null || true

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo ""
echo "🎉 Build completed successfully!"
echo "📁 Your executable is ready"

# Keep window open
echo ""
read -p "Press Enter to close this installer..."