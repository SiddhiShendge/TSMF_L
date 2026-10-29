@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv311\Scripts\python.exe" goto setup_required
".venv311\Scripts\python.exe" -c "import streamlit" >nul 2>&1
if errorlevel 1 goto setup_required

echo Starting Thane Weather Forecast at http://127.0.0.1:8501
echo Keep this window open while using the app.
echo.
".venv311\Scripts\python.exe" -m streamlit run "%~dp0app.py" --server.address=127.0.0.1 --server.port=8501 --browser.gatherUsageStats=false
if errorlevel 1 (
    echo.
    echo The app could not start. Check the error above.
    echo To install dependencies, double-click setup.bat.
)

echo.
echo Streamlit has stopped.
pause
exit /b

:setup_required
echo Double-click setup.bat first to install the app dependencies.
pause
exit /b 1
