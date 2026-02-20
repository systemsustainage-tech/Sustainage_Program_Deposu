$files = @(
    "web_app.py",
    "remote_setup.sh",
    "locales/tr.json",
    "SDG_232.xlsx",
    "tools/init_sdg_remote.py",
    "templates/sdg.html",
    "templates/economic_edit.html",
    "templates/social_edit.html",
    "mapping/sdg_gri_mapping.py",
    "modules/sdg/sdg_manager.py"
)

foreach ($file in $files) {
    Write-Host "Uploading $file..."
    scp -i C:\Users\admin2\.ssh\id_ed25519 -o StrictHostKeyChecking=no "C:\SUSTAINAGESERVER\$file" root@72.62.150.207:/var/www/sustainage/$file
}

Write-Host "Initializing SDG database on remote..."
ssh -i C:\Users\admin2\.ssh\id_ed25519 -o StrictHostKeyChecking=no root@72.62.150.207 "cd /var/www/sustainage && python3 tools/init_sdg_remote.py"

Write-Host "Restarting service..."
ssh -i C:\Users\admin2\.ssh\id_ed25519 -o StrictHostKeyChecking=no root@72.62.150.207 "bash /var/www/sustainage/remote_setup.sh"
