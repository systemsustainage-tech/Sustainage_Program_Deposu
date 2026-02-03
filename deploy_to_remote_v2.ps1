
$server = "root@72.62.150.207"
$remote_path = "/var/www/sustainage"
$key_path = "C:\Users\admin2\.ssh\id_ed25519"

# Helper function for SCP
function Copy-ToRemote {
    param($local, $remote)
    Write-Host "Copying $local to $remote..."
    scp -i $key_path -o StrictHostKeyChecking=no -r $local "${server}:${remote}"
}

# Helper function for SSH
function Run-Remote {
    param($command)
    Write-Host "Running remote command: $command"
    ssh -i $key_path -o StrictHostKeyChecking=no $server $command
}

# 1. Copy web_app.py
Copy-ToRemote "c:\SUSTAINAGESERVER\web_app.py" "$remote_path/web_app.py"

# 2. Copy backend (yeni modüller ve yöneticiler burada)
Copy-ToRemote "c:\SUSTAINAGESERVER\backend" "$remote_path/"

# 3. Copy templates
Copy-ToRemote "c:\SUSTAINAGESERVER\templates" "$remote_path/"

# 4. Copy static
Copy-ToRemote "c:\SUSTAINAGESERVER\static" "$remote_path/"

# 5. Copy modules (legacy paketler)
Copy-ToRemote "c:\SUSTAINAGESERVER\modules" "$remote_path/"

# 6. Copy locales
Copy-ToRemote "c:\SUSTAINAGESERVER\locales" "$remote_path/"

# 7. Copy top-level config (DB_PATH ve ayarlar için)
Copy-ToRemote "c:\SUSTAINAGESERVER\config" "$remote_path/"

# 8. Copy tools (Schema updates etc.)
Copy-ToRemote "c:\SUSTAINAGESERVER\tools" "$remote_path/"

# 9. Run schema update and Restart Service
Run-Remote "systemctl stop sustainage; pkill -f 'gunicorn --bind 0.0.0.0:5000 web_app:app' || true; python3 $remote_path/tools/update_remote_schema_multitenant.py; systemctl start sustainage"

Write-Host "Deployment complete."
