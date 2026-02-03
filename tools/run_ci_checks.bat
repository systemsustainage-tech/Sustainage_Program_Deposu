@echo off
setlocal

echo [CI] Starting System Audit (Translation, Syntax, Code Patterns)...

:: Navigate to tools directory to ensure relative paths work
pushd %~dp0

:: Run comprehensive audit script
python audit_system.py
set EXIT_CODE=%ERRORLEVEL%

if "%EXIT_CODE%" NEQ "0" (
    echo [CI] ERROR: Critical issues detected in the system!
    echo [CI] Please check the 'AUDIT REPORT' above for details.
    echo [CI] If translation keys are missing, run 'python add_missing_keys.py' ^(after updating it to use the new report format if needed^).
    popd
    exit /b 1
)

echo [CI] Running Translation Tests...
python ../tests/test_translations.py
if %ERRORLEVEL% NEQ 0 (
    echo [CI] ERROR: Translation tests failed!
    popd
    exit /b 1
)

echo [CI] All system checks passed.
popd
exit /b 0
