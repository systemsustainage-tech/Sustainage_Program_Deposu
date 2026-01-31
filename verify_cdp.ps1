$server = "72.62.150.207"
$user = "root"
$key = "C:\Users\Administrator\.ssh\id_rsa"

& "C:\Program Files\Git\usr\bin\ssh.exe" -i $key -o StrictHostKeyChecking=no $user@$server "grep 'ensure_company_questions' /var/www/sustainage/backend/modules/cdp/cdp_manager.py"
& "C:\Program Files\Git\usr\bin\ssh.exe" -i $key -o StrictHostKeyChecking=no $user@$server "grep 'manager.save_response(q_type' /var/www/sustainage/web_app.py"
