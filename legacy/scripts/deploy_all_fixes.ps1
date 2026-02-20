$key = "C:\Users\admin2\.ssh\id_ed25519"
$server = "root@72.62.150.207"
$base_remote = "/var/www/sustainage"

$files = @(
    "web_app.py",
    "locales/tr.json",
    "templates/sdg.html",
    "templates/gri_edit.html",
    "templates/cdp_edit.html",
    "templates/governance_edit.html",
    "templates/social_edit.html",
    "templates/economic_edit.html",
    "templates/cbam_edit.html",
    "mapping/sdg_gri_mapping.py"
)

foreach ($file in $files) {
    Write-Host "Uploading $file..."
    $local = "c:\SUSTAINAGESERVER\$file"
    $remote = "$base_remote/$file"
    scp -i $key -o StrictHostKeyChecking=no $local ${server}:${remote}
}

Write-Host "Restarting Gunicorn..."
ssh -i $key -o StrictHostKeyChecking=no $server "pkill -f gunicorn; pkill -f web_app.py; cd /var/www/sustainage; source venv/bin/activate; venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 web_app:app --daemon --access-logfile access.log --error-logfile error.log"
