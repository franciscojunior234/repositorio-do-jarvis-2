@echo off
REM JARVIS - Iniciar apenas a interface React
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" launcher_react.py
) else (
    python launcher_react.py
)

pause
