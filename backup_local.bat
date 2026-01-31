@echo off
set SCRIPT_PATH=C:\SUSTAINAGESERVER\backup_sustainage.ps1

echo Sustainage - Lokal yedek aliniyor...
powershell -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -LocalOnly

echo.
echo Islem tamamlandi. Cikti klasoru: D:\SUSTAINAGE\YEDEK\local
pause

