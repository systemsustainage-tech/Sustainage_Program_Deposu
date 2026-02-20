$server = "root@72.62.150.207"
$identity = "C:\Users\admin2\.ssh\id_ed25519"

# Upload web_app.py
Write-Host "Uploading web_app.py..."
scp -i $identity -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\web_app.py $server`:/var/www/sustainage/web_app.py

# Upload templates
Write-Host "Uploading templates..."
scp -i $identity -o StrictHostKeyChecking=no -r c:\SUSTAINAGESERVER\templates $server`:/var/www/sustainage/

# Upload static (just in case)
Write-Host "Uploading static..."
scp -i $identity -o StrictHostKeyChecking=no -r c:\SUSTAINAGESERVER\static $server`:/var/www/sustainage/

# Restart service
Write-Host "Restarting service..."
ssh -i $identity -o StrictHostKeyChecking=no $server "pkill -f gunicorn; pkill -f web_app.py; cd /var/www/sustainage && source venv/bin/activate && gunicorn --workers 4 --bind 0.0.0.0:5000 web_app:app --daemon"

Write-Host "Deployment complete."
