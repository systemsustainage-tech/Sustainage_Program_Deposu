$key = "C:\Users\admin2\.ssh\id_ed25519"
$server = "root@72.62.150.207"
$local_dir = "c:\SUSTAINAGESERVER\locales"
$remote_dir = "/var/www/sustainage/locales"

Write-Host "Uploading web_app.py..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\web_app.py ${server}:/var/www/sustainage/web_app.py

Write-Host "Uploading run_ci_checks.bat..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\tools\run_ci_checks.bat ${server}:/var/www/sustainage/tools/run_ci_checks.bat

Write-Host "Uploading test_translations.py..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\tests\test_translations.py ${server}:/var/www/sustainage/tests/test_translations.py

Write-Host "Uploading translations..."
$files = Get-ChildItem $local_dir -Filter "*.json"
foreach ($file in $files) {
    Write-Host "Uploading $($file.Name)..."
    scp -i $key -o StrictHostKeyChecking=no $file.FullName ${server}:${remote_dir}/$($file.Name)
}

Write-Host "Restarting service..."
ssh -i $key -o StrictHostKeyChecking=no $server "cd /var/www/sustainage && python3 tools/restart_service.py"
