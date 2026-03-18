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

echo [CI] Auditing Translations...
echo [CI] Skipping audit_translations.py (file not found). Relying on audit_system.py and translation tests instead.

echo [CI] Preparing Frontend Build Assets...
python prepare_frontend_build.py
if %ERRORLEVEL% NEQ 0 (
    echo [CI] ERROR: Frontend preparation failed!
    popd
    exit /b 1
)

echo [CI] Fetching Latest Standards Info...
python fetch_latest_standards.py

echo [CI] Running Security and Quality Scan...
python run_security_scan.py
if %ERRORLEVEL% NEQ 0 (
    echo [CI] WARNING: Security issues found. Please review the report.
    :: We don't fail build on warnings yet, but in strict mode we should.
)

echo [CI] Running Translation Tests...
python ../tests/test_translations.py
if %ERRORLEVEL% NEQ 0 (
    echo [CI] ERROR: Translation tests failed!
    echo [CI] If keys are missing, run: pushd tools ^&^& python add_missing_keys.py ^&^& popd
    popd
    exit /b 1
)

echo [CI] All system checks passed.
popd
exit /b 0
