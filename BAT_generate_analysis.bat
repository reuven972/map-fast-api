@echo off
setlocal

REM Get the directory where this batch script is located
set "SCRIPT_DIR=%~dp0"

REM Define the project path relative to the script's location (assuming script is in project root)
set "PROJECT_ROOT=%SCRIPT_DIR%"

REM Change to the project directory
echo Changing directory to: %PROJECT_ROOT%
cd /d "%PROJECT_ROOT%"
if errorlevel 1 (
    echo ERROR: Could not change to directory %PROJECT_ROOT%
    pause
    exit /b 1
)

REM Check if virtual environment activate script exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment activation script not found at:
    echo %CD%\venv\Scripts\activate.bat
    echo Please ensure your virtual environment is named 'venv' and is in the project root.
    pause
    exit /b 1
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM --- MODIFICATION START ---
REM Check if the output file exists and delete it to ensure it's replaced
set "OUTPUT_FILE=full-analysis.txt"
if exist "%OUTPUT_FILE%" (
    echo Deleting existing %OUTPUT_FILE%...
    del "%OUTPUT_FILE%"
    if errorlevel 1 (
        echo WARNING: Could not delete existing %OUTPUT_FILE%.
        echo It might be locked by another process. Attempting to overwrite anyway.
        REM Optionnel: pause ici ou exit /b si la suppression est critique
        REM pause
        REM exit /b 1
    )
)
REM --- MODIFICATION END ---

REM Run the code2prompt command
REM Using "." for the project path because we have already CD'd into it.
echo Running code2prompt...
code2prompt . --exclude="/venv/,run.bat,structure.py,how-to.txt,files-structure.md,alambic.txt,.env,.gitignore,generate_analysis.bat" --tokens --output "%OUTPUT_FILE%"

if errorlevel 1 (
    echo ERROR: code2prompt command failed.
) else (
    echo code2prompt command completed successfully.
    echo Output saved to: %CD%\%OUTPUT_FILE%
)

REM Deactivate the virtual environment (optional, as cmd session will close)
REM call deactivate

endlocal
echo.
echo Script finished.
REM You can uncomment the line below if you want the window to stay open until a key is pressed
REM pause

 