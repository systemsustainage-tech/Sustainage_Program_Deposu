$server = "root@72.62.150.207"
$remote_path = "/var/www/sustainage"
$key = "C:\Users\Administrator\.ssh\id_rsa"

# Files to deploy
$files = @(
    "web_app.py",
    "templates/sdg.html",
    "locales/tr.json",
    "mapping/sdg_gri_mapping.py",
    "modules/sdg/sdg_manager.py"
)

foreach ($file in $files) {
    $local_file = "C:\SUSTAINAGESERVER\$file"
    $remote_file = "$remote_path/$file"
    
    Write-Host "Deploying $file..."
    scp -o StrictHostKeyChecking=no -i $key $local_file "$server`:$remote_file"
}

# Restart service
Write-Host "Restarting web application..."
ssh -o StrictHostKeyChecking=no -i $key $server "pkill -f gunicorn; cd $remote_path && nohup gunicorn --bind 0.0.0.0:5001 web_app:app > output.log 2>&1 &"

Write-Host "Deployment complete!"
