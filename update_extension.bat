@echo off
echo ==============================================
echo Sindlish VS Code Extension Auto-Updater
echo ==============================================
echo.

echo 1. Updating bundled Python interpreter...
xcopy /E /I /Y interpreter vscode-extension\python-engine\interpreter >nul

echo.
echo 2. Regenerating grammar and definitions...
uv run python tools\generate_grammar.py

echo.
echo 3. Automatically incrementing extension version...
cd vscode-extension
call npm version patch --no-git-tag-version

echo.
echo 4. Packaging extension...
call vsce package

echo.
echo ==============================================
echo Upgrade Complete! The new automatically-versioned .vsix file is ready.
echo ==============================================
pause
