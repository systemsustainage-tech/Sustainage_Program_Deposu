$key = "C:\Users\admin2\.ssh\id_ed25519"
$server = "root@72.62.150.207"
$remote_path = "/var/www/sustainage/locales/tr.json"
$local_path = "c:\SUSTAINAGESERVER\locales\tr.json"

Write-Host "Uploading translations..."
scp -i $key -o StrictHostKeyChecking=no $local_path ${server}:${remote_path}

Write-Host "Restarting Gunicorn on port 5001..."
ssh -i $key -o StrictHostKeyChecking=no $server "pkill -f gunicorn; pkill -f web_app.py; cd /var/www/sustainage; source venv/bin/activate; venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 web_app:app --daemon --access-logfile access.log --error-logfile error.log"
