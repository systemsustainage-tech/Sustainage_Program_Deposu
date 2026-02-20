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

Write-Host "Uploading SDG Manager to BACKEND..."
# Ensure backend directory exists (just in case)
# Upload to backend/modules/sdg/sdg_manager.py
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\modules\sdg\sdg_manager.py ${server}:${remote_base}/backend/modules/sdg/sdg_manager.py

Write-Host "Uploading SDG Images..."
ssh -i $key -o StrictHostKeyChecking=no $server "mkdir -p ${remote_base}/static/images"
scp -r -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\static\images\* ${server}:${remote_base}/static/images/

Write-Host "Uploading Venv Setup Script..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\remote_setup_venv.sh ${server}:${remote_base}/remote_setup_venv.sh
ssh -i $key -o StrictHostKeyChecking=no $server "chmod +x ${remote_base}/remote_setup_venv.sh"

Write-Host "Running Venv Setup..."
ssh -i $key -o StrictHostKeyChecking=no $server "${remote_base}/remote_setup_venv.sh"

Write-Host "Restarting Gunicorn..."
# Run from /var/www/sustainage where venv is located
ssh -i $key -o StrictHostKeyChecking=no $server "pkill -f gunicorn; pkill -f web_app.py; cd ${remote_base}; source venv/bin/activate; gunicorn -w 4 -b 0.0.0.0:5000 web_app:app --daemon --access-logfile access.log --error-logfile error.log"

Write-Host "Deployment Complete."
