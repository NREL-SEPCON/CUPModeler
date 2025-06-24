#!/bin/bash

# Build script for CUP Modeler
# Run this locally to test your build before pushing to GitHub

echo "Building CUP Modeler..."

# Ensure we're in the project root (where requirements.txt should be)
if [ ! -f "requirements.txt" ]; then
    echo "Error: Not in project root directory. Please run from where requirements.txt is located."
    exit 1
fi

# Create launcher script for proper module importing
cat > launcher.py << 'EOF'
import sys
import os

# Add Scripts directory to path
scripts_dir = os.path.join(os.path.dirname(__file__), "Python Version", "Scripts")
sys.path.insert(0, scripts_dir)

# Change to Scripts directory for relative paths to work
os.chdir(scripts_dir)

# Import and run the app
if __name__ == "__main__":
    from app.main import main
    main()
EOF

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Detect OS and build accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Building for macOS..."
    pyinstaller \
        --onefile \
        --windowed \
        --name="CUP-Modeler-macOS" \
        --icon="Python Version/Scripts/icon.ico" \
        --add-data="Python Version/Scripts/models:models" \
        --add-data="Python Version/Scripts/app:app" \
        --collect-all numpy \
        --collect-all scipy \
        --collect-all matplotlib \
        --collect-all pandas \
        --hidden-import=numba.core.types.scalars \
        --hidden-import=scipy.special._ufuncs_cxx \
        --hidden-import=matplotlib.backends.backend_tkagg \
        --exclude-module=pytest \
        --exclude-module=IPython \
        --exclude-module=jupyter \
        --exclude-module=sphinx \
        --exclude-module=pytz \
        launcher.py
        
    echo "Creating macOS app bundle..."
    mkdir -p "CUP Modeler.app/Contents/MacOS"
    mkdir -p "CUP Modeler.app/Contents/Resources"
    
    cp "dist/CUP-Modeler-macOS" "CUP Modeler.app/Contents/MacOS/CUP Modeler"
    chmod +x "CUP Modeler.app/Contents/MacOS/CUP Modeler"
    
    # Create Info.plist
    cat > "CUP Modeler.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>CUP Modeler</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourorganization.cupmodeler</string>
    <key>CFBundleName</key>
    <string>CUP Modeler</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF
    
    echo "Build complete! Check 'CUP Modeler.app' folder."
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Building for Windows..."
    pyinstaller \
        --onefile \
        --windowed \
        --name="CUP-Modeler-Windows" \
        --icon="Python Version/Scripts/icon.ico" \
        --add-data="Python Version/Scripts/models;models" \
        --add-data="Python Version/Scripts/app;app" \
        --collect-all numpy \
        --collect-all scipy \
        --collect-all matplotlib \
        --collect-all pandas \
        --hidden-import=numba.core.types.scalars \
        --hidden-import=scipy.special._ufuncs_cxx \
        --hidden-import=matplotlib.backends.backend_tkagg \
        --exclude-module=pytest \
        --exclude-module=IPython \
        --exclude-module=jupyter \
        --exclude-module=sphinx \
        --exclude-module=pytz \
        launcher.py
    
    echo "Build complete! Check dist/CUP-Modeler-Windows.exe"
    
else
    echo "Building for Linux..."
    pyinstaller \
        --onefile \
        --windowed \
        --name="CUP-Modeler-Linux" \
        --add-data="Python Version/Scripts/models:models" \
        --add-data="Python Version/Scripts/app:app" \
        --collect-all numpy \
        --collect-all scipy \
        --collect-all matplotlib \
        --collect-all pandas \
        --hidden-import=numba.core.types.scalars \
        --hidden-import=scipy.special._ufuncs_cxx \
        --hidden-import=matplotlib.backends.backend_tkagg \
        --exclude-module=pytest \
        --exclude-module=IPython \
        --exclude-module=jupyter \
        --exclude-module=sphinx \
        --exclude-module=pytz \
        launcher.py
    
    echo "Build complete! Check dist/CUP-Modeler-Linux"
fi

echo "Build process finished!"