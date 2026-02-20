$key = "C:\Users\admin2\.ssh\id_ed25519"
$server = "root@72.62.150.207"
$remote_base = "/var/www/sustainage"

Write-Host "Uploading SDG Manager..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\backend\modules\sdg\sdg_manager.py ${server}:${remote_base}/backend/modules/sdg/sdg_manager.py

Write-Host "Uploading Master Table Creator..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\tools\create_master_tables.py ${server}:${remote_base}/tools/create_master_tables.py

Write-Host "Uploading Fix Schema Script..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\tools\fix_sdg_schema.py ${server}:${remote_base}/tools/fix_sdg_schema.py

Write-Host "Uploading Init SDG Remote Script..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\tools\init_sdg_remote.py ${server}:${remote_base}/tools/init_sdg_remote.py

Write-Host "Uploading SDG_232.xlsx..."
scp -i $key -o StrictHostKeyChecking=no c:\SUSTAINAGESERVER\SDG_232.xlsx ${server}:${remote_base}/SDG_232.xlsx

Write-Host "Running Schema Fix..."
ssh -i $key -o StrictHostKeyChecking=no $server "cd ${remote_base} && python3 tools/fix_sdg_schema.py"

Write-Host "Running SDG Init (Data Load)..."
ssh -i $key -o StrictHostKeyChecking=no $server "cd ${remote_base} && python3 tools/init_sdg_remote.py"

Write-Host "Restarting Service..."
ssh -i $key -o StrictHostKeyChecking=no $server "systemctl restart sustainage"

Write-Host "SDG Deployment Completed."
