@echo off
setlocal

echo [CI] Starting Translation Checks...

:: Navigate to tools directory to ensure relative paths work
pushd %~dp0

:: Run audit script with CI flag
python audit_translations.py --ci
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% NEQ 0 (
    echo [CI] ERROR: Missing translation keys detected!
    echo [CI] Please run 'python add_missing_keys.py' to generate placeholders.
    echo [CI] Then update the locale files with correct translations.
    popd
    exit /b 1
)

echo [CI] Translation checks passed.
popd
exit /b 0
