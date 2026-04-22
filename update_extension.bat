@echo off
echo ==============================================
echo Sindlish VS Code Extension Auto-Updater
echo ==============================================
echo.

set /p EXT_VERSION="Enter extension version (e.g., 1.0.1): "

echo.
echo 1. Updating bundled Python interpreter...
xcopy /E /I /Y interpreter vscode-extension\python-engine\interpreter >nul

echo.
echo 2. Regenerating grammar and definitions...
uv run python tools\generate_grammar.py

echo.
echo 3. Setting extension version to %EXT_VERSION%...
cd vscode-extension
call npm version %EXT_VERSION% --no-git-tag-version

echo.
echo 4. Packaging extension...
call vsce package

echo.
echo ==============================================
echo Upgrade Complete! Version %EXT_VERSION% .vsix file is ready.
echo ==============================================
pause