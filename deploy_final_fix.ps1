
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

# 1. Copy backend (includes modified modules and config)
Copy-ToRemote "c:\SUSTAINAGESERVER\backend" "$remote_path/"

# 2. Copy tools (includes migrate_totp_secrets.py)
Copy-ToRemote "c:\SUSTAINAGESERVER\tools" "$remote_path/"

# 3. Copy web_app.py (CSRF fixes)
Copy-ToRemote "c:\SUSTAINAGESERVER\web_app.py" "$remote_path/web_app.py"

# 4. Copy templates (CSRF fixes)
Copy-ToRemote "c:\SUSTAINAGESERVER\templates" "$remote_path/"

# 5. Run TOTP Migration
Write-Host "Running TOTP Migration on remote..."
Run-Remote "cd $remote_path && python3 tools/migrate_totp_secrets.py"

# 6. Restart Service
Write-Host "Restarting Sustainage Service..."
Run-Remote "systemctl restart sustainage"

Write-Host "Deployment and Migration Complete."
