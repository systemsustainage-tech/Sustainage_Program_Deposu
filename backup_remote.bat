@echo off
set SCRIPT_PATH=C:\SUSTAINAGESERVER\backup_sustainage.ps1

rem Gerekirse asagidaki degiskenleri duzenleyebilirsin
set REMOTE_HOST=72.62.150.207
set REMOTE_USER=root
set REMOTE_DIR=/var/www/sustainage

echo Sustainage - Uzak sunucu yedegi aliniyor...
powershell -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -RemoteOnly -RemoteHost "%REMOTE_HOST%" -RemoteUser "%REMOTE_USER%" -RemoteDir "%REMOTE_DIR%"

echo.
echo Islem tamamlandi. Cikti klasoru: D:\SUSTAINAGE\YEDEK\remote
pause

