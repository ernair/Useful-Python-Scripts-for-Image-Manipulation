@echo off
SET "CURRENT_DIR=%~dp0"
IF "%CURRENT_DIR:~-1%"=="\" SET "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

start "" "C:\Program Files\Git\git-bash.exe" --cd="%CURRENT_DIR%"
