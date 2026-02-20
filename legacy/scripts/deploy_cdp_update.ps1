$server = "72.62.150.207"
$user = "root"
$key = "C:\Users\Administrator\.ssh\id_rsa"
$remote_path = "/var/www/sustainage"

# Function to run remote command
function Run-RemoteCommand {
    param($cmd)
    Write-Host "Running: $cmd" -ForegroundColor Cyan
    & "C:\Program Files\Git\usr\bin\ssh.exe" -i $key -o StrictHostKeyChecking=no $user@$server $cmd
}

# Function to copy file
function Copy-File {
    param($local, $remote)
    Write-Host "Copying $local to $remote" -ForegroundColor Cyan
    & "C:\Program Files\Git\usr\bin\scp.exe" -i $key -o StrictHostKeyChecking=no $local $user@$server`:$remote
}

# 1. Create remote directories
Run-RemoteCommand "mkdir -p $remote_path/backend/modules/cdp"
Run-RemoteCommand "mkdir -p $remote_path/templates"
Run-RemoteCommand "mkdir -p $remote_path/locales"

# 2. Copy files
Copy-File "c:\SUSTAINAGESERVER\web_app.py" "$remote_path/web_app.py"
Copy-File "c:\SUSTAINAGESERVER\backend\modules\cdp\cdp_manager.py" "$remote_path/backend/modules/cdp/cdp_manager.py"
Copy-File "c:\SUSTAINAGESERVER\templates\cdp.html" "$remote_path/templates/cdp.html"
Copy-File "c:\SUSTAINAGESERVER\locales\tr.json" "$remote_path/locales/tr.json"

# 3. Restart Gunicorn
Write-Host "Restarting Gunicorn..." -ForegroundColor Yellow
Run-RemoteCommand "pkill gunicorn; cd $remote_path && source venv/bin/activate && gunicorn --bind 0.0.0.0:5000 web_app:app --daemon"

Write-Host "Deployment Complete!" -ForegroundColor Green
