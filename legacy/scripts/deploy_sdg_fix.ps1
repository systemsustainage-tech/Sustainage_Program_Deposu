$key = "C:\Users\admin2\.ssh\id_ed25519"
$server = "root@72.62.150.207"
$remote_base = "/var/www/sustainage"

Write-Host "Uploading web_app.py..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\web_app.py ${server}:${remote_base}/web_app.py

Write-Host "Uploading translations..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\locales\tr.json ${server}:${remote_base}/locales/tr.json

Write-Host "Uploading templates..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\templates\sdg.html ${server}:${remote_base}/templates/sdg.html

Write-Host "Uploading mapping logic..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\mapping\sdg_gri_mapping.py ${server}:${remote_base}/mapping/sdg_gri_mapping.py
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\SDG_232.xlsx ${server}:${remote_base}/SDG_232.xlsx

Write-Host "Uploading SDG Manager..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\modules\sdg\sdg_manager.py ${server}:${remote_base}/modules/sdg/sdg_manager.py

Write-Host "Uploading SDG Images..."
# Ensure remote directory exists
ssh -i $key -o StrictHostKeyChecking=no $server "mkdir -p ${remote_base}/static/images"
# Upload all images
scp -r -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\static\images\* ${server}:${remote_base}/static/images/

Write-Host "Restarting Gunicorn..."
ssh -i $key -o StrictHostKeyChecking=no $server "pkill -f gunicorn; pkill -f web_app.py; cd ${remote_base}; source venv/bin/activate; venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 web_app:app --daemon --access-logfile access.log --error-logfile error.log"

Write-Host "Deployment Complete."
