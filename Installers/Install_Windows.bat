@echo off
setlocal enabledelayedexpansion

REM CUP Modeler Installer
REM Usage: Install_Windows.bat [auto]

set "ORIGINAL_DIR=%USERPROFILE%\Desktop"
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
cd /d "%PROJECT_DIR%"

echo CUP Modeler Installer
echo =====================
echo Installer location: %SCRIPT_DIR%
echo Project directory: %PROJECT_DIR%
echo Will install to: %ORIGINAL_DIR%

set AUTO_MODE=0
if "%1"=="auto" set AUTO_MODE=1

goto :main

:command_exists
where "%1" >nul 2>&1
exit /b %errorlevel%

:prompt_yes_no
set "prompt_text=%~1"
set "default_val=%~2"
if "%default_val%"=="" set "default_val=y"
if %AUTO_MODE%==1 (
    echo %prompt_text% [%default_val%]
    exit /b 0
) else (
    set /p "response=%prompt_text% [%default_val%]: "
    if "!response!"=="" set "response=%default_val%"
    if /i "!response!"=="y" exit /b 0
    if /i "!response!"=="yes" exit /b 0
    exit /b 1
)

:choose_option
set "prompt_text=%~1"
set "default_val=%~2"
set "options_text=%~3"
echo %options_text%
if %AUTO_MODE%==1 (
    echo %prompt_text% [%default_val%]
    echo Auto mode: choosing default ^(%default_val%^)
    set "REPLY=%default_val%"
) else (
    set /p "REPLY=%prompt_text% [%default_val%]: "
    if "!REPLY!"=="" set "REPLY=%default_val%"
)
exit /b 0

:main
if %AUTO_MODE%==0 (
    echo.
    echo Choose installation mode:
    echo 1^) Automatic - Install everything without prompts
    echo 2^) Interactive - Choose each step
    echo 3^) Exit
    set /p "CHOICE=Enter choice: "
    if "!CHOICE!"=="" set "CHOICE=1"
    if "!CHOICE!"=="1" set AUTO_MODE=1
    if "!CHOICE!"=="2" set AUTO_MODE=0
    if "!CHOICE!"=="3" exit /b 0
    if not "!CHOICE!"=="1" if not "!CHOICE!"=="2" (
        echo Invalid choice
        exit /b 1
    )
)

echo.
if %AUTO_MODE%==1 (
    echo Running automatic installation...
) else (
    echo Running interactive installation...
)
echo.

REM Step 1: Python
echo [Step 1] Python Installation
echo ----------------------------
call :command_exists python
if %errorlevel%==0 (
    set PYTHON=python
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo Found Python: %%i
) else (
    call :command_exists py
    if !errorlevel!==0 (
        set PYTHON=py
        for /f "tokens=*" %%i in ('py --version 2^>^&1') do echo Found Python: %%i
    ) else (
        echo Python not found on your system.
        echo.
        call :choose_option "Choose option:" "1" "1) Let installer download and install Python 2) I'll install Python manually"
        if "!REPLY!"=="1" (
            echo.
            echo Installing Python...
            echo Downloading Python installer...
            powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile 'python_installer.exe'"
            echo Running Python installer...
            start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
            del python_installer.exe
            call :command_exists python
            if !errorlevel!==0 (
                set PYTHON=python
            ) else (
                call :command_exists py
                if !errorlevel!==0 (
                    set PYTHON=py
                ) else (
                    echo Failed to install Python
                    exit /b 1
                )
            )
        ) else (
            echo.
            echo Please install Python 3.9 or later from:
            echo https://python.org/downloads/
            echo.
            echo Then run this installer again.
            exit /b 1
        )
    )
)

REM Step 2: Project Files
echo.
echo [Step 2] Project Files
echo ----------------------
if not exist "main.py" (
    echo ERROR: main.py not found!
    echo.
    echo Please ensure you're running this installer from the Installer folder and that main.py is in the project root.
    echo.
    exit /b 1
)
echo Found main.py - project files OK

REM Step 3: Virtual Environment
echo.
echo [Step 3] Virtual Environment
echo ---------------------------
echo A virtual environment keeps dependencies isolated.
echo.
call :prompt_yes_no "Create virtual environment?" "y"
if %errorlevel%==0 (
    echo Creating virtual environment...
    %PYTHON% -m venv cup_env
    call cup_env\Scripts\activate.bat
    set PYTHON=python
) else (
    echo.
    echo Skipping virtual environment.
    echo NOTE: Dependencies will be installed globally.
    echo.
)

REM Step 4: Dependencies
echo.
echo [Step 4] Dependencies
echo ---------------------
echo Required packages:
if exist "requirements.txt" (
    echo From requirements.txt:
    type requirements.txt
) else (
    echo - matplotlib ^(plotting^)
    echo - numpy ^(numerical computing^)
    echo - pandas ^(data handling^)
    echo - scipy ^(scientific computing^)
    echo - numba ^(performance^)
    echo - Pillow ^(image handling^)
    echo - openpyxl ^(Excel support^)
)
echo.
call :choose_option "Choose option:" "1" "1) Install all dependencies automatically 2) I'll install them manually 3) Skip (already installed)"
if "!REPLY!"=="1" (
    echo.
    echo Installing dependencies...
    %PYTHON% -m pip install --upgrade pip
    if exist "requirements.txt" (
        %PYTHON% -m pip install -r requirements.txt
    ) else (
        %PYTHON% -m pip install matplotlib numpy pandas scipy numba Pillow openpyxl
    )
) else if "!REPLY!"=="2" (
    echo.
    echo Please install the dependencies using:
    if exist "requirements.txt" (
        echo   pip install -r requirements.txt
    ) else (
        echo   pip install matplotlib numpy pandas scipy numba Pillow openpyxl
    )
    echo.
    if %AUTO_MODE%==0 (
        pause
    )
)

REM Verify dependencies
echo.
echo Checking installed dependencies...
%PYTHON% -c "import matplotlib, numpy, pandas, scipy, numba, PIL, openpyxl; print('All core dependencies OK')" >nul 2>&1
if %errorlevel%==0 (
    echo All core dependencies verified.
) else (
    echo.
    echo WARNING: Some dependencies are missing!
    echo The application may not work correctly.
    echo.
    call :prompt_yes_no "Continue anyway?" "n"
    if !errorlevel!==1 exit /b 1
)

REM Step 5: PyInstaller
echo.
echo [Step 5] PyInstaller
echo -------------------
echo PyInstaller creates the standalone executable.
echo.
call :prompt_yes_no "Install PyInstaller?" "y"
if %errorlevel%==0 (
    echo Installing PyInstaller...
    %PYTHON% -m pip install pyinstaller
)

REM Step 6: Build Executable
echo.
echo [Step 6] Build Executable
echo ------------------------
%PYTHON% -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not available. Cannot build executable.
    echo Environment is set up for development use.
    exit /b 0
)

echo Ready to build the standalone executable.
echo.
call :prompt_yes_no "Build CUP Modeler?" "y"
if %errorlevel%==1 (
    echo.
    echo Skipping build. Environment is ready for development.
    exit /b 0
)

echo.
echo Building executable ^(this may take a few minutes^)...

%PYTHON% -m PyInstaller -F --windowed --name="CUP Modeler" --icon=Installers\icon.ico --add-data="models;models" --add-data="app;app" --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=matplotlib.backends.backend_pdf --hidden-import=scipy.io.matlab --hidden-import=numba.core.types.scalars --hidden-import=numba.core.types.common --hidden-import=numba.typed --hidden-import=openpyxl --hidden-import=openpyxl.cell._writer --hidden-import=openpyxl.styles --exclude-module=IPython --exclude-module=jupyter --exclude-module=pytest main.py

if %errorlevel% neq 0 (
    echo.
    echo Build failed! Check error messages above.
    exit /b 1
)

REM Move executable with verification
echo.
echo Moving executable to desktop...
set MOVE_SUCCESS=0

if exist "%PROJECT_DIR%\dist\CUP Modeler.exe" (
    if exist "%ORIGINAL_DIR%\CUP Modeler.exe" del "%ORIGINAL_DIR%\CUP Modeler.exe"
    copy "%PROJECT_DIR%\dist\CUP Modeler.exe" "%ORIGINAL_DIR%\" >nul
    if exist "%ORIGINAL_DIR%\CUP Modeler.exe" (
        set MOVE_SUCCESS=1
        echo Successfully moved CUP Modeler.exe to %ORIGINAL_DIR%
    )
) else (
    echo Warning: Executable not found at expected location
    echo Looking for: %PROJECT_DIR%\dist\CUP Modeler.exe
    if exist "%PROJECT_DIR%\dist\" (
        dir "%PROJECT_DIR%\dist\"
    ) else (
        echo dist directory not found
    )
)

REM Step 7: Cleanup
echo.
echo [Step 7] Cleanup
echo ---------------
echo Temporary build files can be removed to save space.
echo.
call :prompt_yes_no "Remove temporary files?" "y"
if %errorlevel%==0 (
    echo Cleaning up...
    if exist cup_env\Scripts\deactivate.bat call cup_env\Scripts\deactivate.bat >nul 2>&1
    if exist "%PROJECT_DIR%\cup_env" rmdir /s /q "%PROJECT_DIR%\cup_env" >nul 2>&1
    if exist "%PROJECT_DIR%\dist" rmdir /s /q "%PROJECT_DIR%\dist" >nul 2>&1
    if exist "%PROJECT_DIR%\build" rmdir /s /q "%PROJECT_DIR%\build" >nul 2>&1
    if exist "%PROJECT_DIR%\*.spec" del "%PROJECT_DIR%\*.spec" >nul 2>&1
    if exist "%PROJECT_DIR%\__pycache__" rmdir /s /q "%PROJECT_DIR%\__pycache__" >nul 2>&1
    echo Cleanup complete
)

echo.
echo ================================
if %MOVE_SUCCESS%==1 (
    echo INSTALLATION COMPLETE!
    echo Executable: %ORIGINAL_DIR%\CUP Modeler.exe
) else (
    echo INSTALLATION COMPLETE WITH WARNINGS!
    echo The app was built but may not have been moved correctly.
    echo Check the dist\ folder in: %PROJECT_DIR%
)
echo ================================
echo.
pause