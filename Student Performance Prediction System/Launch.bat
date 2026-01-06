@echo off
echo =========================================
echo FORCING CORRECT PYTHON EXECUTION
echo =========================================

REM Set to current directory
cd /d "%~dp0"

REM Use the virtual environment Python directly
set VENV_PYTHON=myenv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo Creating new virtual environment...
    python -m venv myenv
    echo Installing packages...
    call myenv\Scripts\activate.bat
    pip install flask scikit-learn joblib pandas numpy
    echo Retraining model...
    %VENV_PYTHON% model_training.py
)

echo.
echo Using: %VENV_PYTHON%
echo.

REM Install packages if missing
%VENV_PYTHON% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing missing packages...
    %VENV_PYTHON% -m pip install flask scikit-learn joblib pandas numpy
)

echo Starting Flask application...
echo.
%VENV_PYTHON% app.py

pause