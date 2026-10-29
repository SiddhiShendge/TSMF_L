@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv311\Scripts\python.exe" (
    py -3.11 -m venv .venv311
    if errorlevel 1 goto failed
)
".venv311\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv311\Scripts\python.exe" -c "import streamlit, pandas, numpy, matplotlib.pyplot, statsmodels.api"
if errorlevel 1 goto failed
echo.
echo Setup complete. Double-click star.bat to open the app.
pause
exit /b 0

:failed
echo.
echo Setup failed. Review the error above.
echo If Windows Application Control blocks Python or a DLL, an administrator must approve it.
pause
exit /b 1
