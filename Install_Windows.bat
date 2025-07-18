@echo off
REM CUP Modeler Windows Auto-Installer with Python
REM Requires Windows 10+ with winget or will fall back to manual download

echo 🎯 CUP Modeler Windows Auto-Installer
echo ======================================

cd /d "%~dp0"
echo 📁 Working from: %CD%

echo 🔍 Checking for Python...

REM Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    goto :python_found
)

echo ❌ Python not found. Attempting auto-installation...
echo.

REM Method 1: Try winget (Windows 10+ with App Installer)
echo 📥 Trying winget installation...
winget --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Winget found, installing Python...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% == 0 (
        echo ✅ Python installed via winget
        echo 🔄 Refreshing PATH...
        call refreshenv.cmd 2>nul || echo "Note: You may need to restart this script"
        goto :verify_python
    )
)

REM Method 2: Try Chocolatey
echo 📥 Trying Chocolatey installation...
choco --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Chocolatey found, installing Python...
    choco install python3 -y
    if %errorlevel% == 0 (
        echo ✅ Python installed via Chocolatey
        call refreshenv.cmd 2>nul
        goto :verify_python
    )
)

REM Method 3: Direct download and install
echo 📥 Downloading Python installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'}"

if exist python-installer.exe (
    echo 🚀 Installing Python...
    echo    This will open the Python installer. Please:
    echo    ✅ Check "Add Python to PATH"
    echo    ✅ Choose "Install Now"
    echo.
    pause
    
    REM Run installer with silent options that add to PATH
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    REM Clean up
    del python-installer.exe
    
    echo ✅ Python installation completed
    echo 🔄 Please close and reopen this command prompt, then run the script again
    pause
    exit /b 0
) else (
    echo ❌ Failed to download Python installer
    goto :manual_install
)

:verify_python
REM Check if Python is now available
timeout /t 3 /nobreak >nul
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    goto :python_found
)

echo ⚠️ Python installed but not found in PATH
echo Please restart this command prompt and try again
pause
exit /b 1

:manual_install
echo ❌ Auto-installation failed
echo.
echo Please manually install Python:
echo 1. Go to https://python.org/downloads/
echo 2. Download Python 3.11 or newer
echo 3. ⚠️ IMPORTANT: Check "Add Python to PATH" during installation
echo 4. Run this script again after installation
echo.
pause
exit /b 1

:python_found
echo ✅ Found Python
%PYTHON% --version

REM Check for main.py
if not exist "main.py" (
    echo ❌ main.py not found!
    echo Please run this installer from the CUP Modeler project folder
    echo.
    pause
    exit /b 1
)

echo ✅ Found main.py

REM Create virtual environment
echo 📦 Creating virtual environment...
%PYTHON% -m venv cup_modeler_env
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call cup_modeler_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install packages
echo 📚 Installing Python packages...
python -m pip install --upgrade pip --quiet

if exist "requirements.txt" (
    echo 📝 Using requirements.txt
    python -m pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo 📝 Installing basic dependencies...
    python -m pip install matplotlib numpy pandas scipy numba Pillow --quiet
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo 🔧 Installing PyInstaller...
python -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyInstaller
    pause
    exit /b 1
)

REM Build executable
echo 🚀 Building executable with PyInstaller...
echo 🪟 Building for Windows...
python -m PyInstaller --onedir --windowed --name="CUP Modeler" --add-data="models;models" --add-data="app;app" --icon="icon.ico" --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=matplotlib.backends.backend_pdf --hidden-import=scipy.io.matlab --hidden-import=numba.core.types.scalars --hidden-import=numba.core.types.common --hidden-import=numba.typed --exclude-module=IPython --exclude-module=jupyter --exclude-module=pytest --exclude-module=sphinx --exclude-module=sympy --exclude-module=cv2 --exclude-module=sklearn --exclude-module=tensorflow --exclude-module=torch --exclude-module=keras main.py

REM Move executable to current directory
echo 📦 Finalizing executable...
if exist "dist\CUP Modeler\CUP Modeler.exe" (
    move "dist\CUP Modeler\CUP Modeler.exe" ".\CUP Modeler.exe"
    echo ✅ Executable moved to project root
) else (
    echo ❌ Executable not found! Check for build errors above.
    pause
    exit /b 1
)

REM Clean up build artifacts
echo 🧹 Cleaning up build files...
if exist "dist\" rmdir /s /q "dist\" 2>nul
if exist "build\" rmdir /s /q "build\" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul
if exist "__pycache__\" rmdir /s /q "__pycache__\" 2>nul

REM Deactivate virtual environment
echo 🔄 Deactivating virtual environment...
call deactivate 2>nul

echo.
echo 🎉 Build completed successfully!
echo ========================
echo.
echo 📁 Your executable is ready
echo.
pause