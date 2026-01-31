ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "mkdir -p /var/www/sustainage/templates /var/www/sustainage/mapping /var/www/sustainage/modules/sdg /var/www/sustainage/locales"

ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "mv /var/www/sustainage/sdg.html /var/www/sustainage/templates/ 2>/dev/null || true"
ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "mv /var/www/sustainage/sdg_gri_mapping.py /var/www/sustainage/mapping/ 2>/dev/null || true"
ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "mv /var/www/sustainage/sdg_manager.py /var/www/sustainage/modules/sdg/ 2>/dev/null || true"
ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "mv /var/www/sustainage/tr.json /var/www/sustainage/locales/ 2>/dev/null || true"

# Verify moves
ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "ls -l /var/www/sustainage/templates/sdg.html /var/www/sustainage/mapping/sdg_gri_mapping.py /var/www/sustainage/modules/sdg/sdg_manager.py /var/www/sustainage/locales/tr.json"

# Restart gunicorn
ssh -o StrictHostKeyChecking=no -i C:\Users\Administrator\.ssh\id_rsa root@72.62.150.207 "pkill -f gunicorn; cd /var/www/sustainage && nohup gunicorn --bind 0.0.0.0:5001 web_app:app > output.log 2>&1 &"
