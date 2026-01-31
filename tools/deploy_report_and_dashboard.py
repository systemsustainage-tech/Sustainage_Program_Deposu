import paramiko
import os
import sys
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()

        files_to_deploy = [
            (r'C:\SUSTAINAGESERVER\web_app.py', '/var/www/sustainage/web_app.py'),
            (r'C:\SUSTAINAGESERVER\templates\dashboard.html', '/var/www/sustainage/templates/dashboard.html'),
            (r'C:\SUSTAINAGESERVER\backend\modules\reporting\unified_report_docx.py', '/var/www/sustainage/backend/modules/reporting/unified_report_docx.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\ai\ai_manager.py', '/var/www/sustainage/backend/modules/ai/ai_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\esg\esg_manager.py', '/var/www/sustainage/backend/modules/esg/esg_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\csrd\csrd_compliance_manager.py', '/var/www/sustainage/backend/modules/csrd/csrd_compliance_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\eu_taxonomy\taxonomy_manager.py', '/var/www/sustainage/backend/modules/eu_taxonomy/taxonomy_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\economic\economic_value_manager.py', '/var/www/sustainage/backend/modules/economic/economic_value_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\issb\issb_manager.py', '/var/www/sustainage/backend/modules/issb/issb_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\iirc\iirc_manager.py', '/var/www/sustainage/backend/modules/iirc/iirc_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\esrs\esrs_manager.py', '/var/www/sustainage/backend/modules/esrs/esrs_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\prioritization\prioritization_manager.py', '/var/www/sustainage/backend/modules/prioritization/prioritization_manager.py'),
            (r'C:\SUSTAINAGESERVER\backend\modules\reporting\target_manager.py', '/var/www/sustainage/backend/modules/reporting/target_manager.py'),
            (r'C:\SUSTAINAGESERVER\templates\targets.html', '/var/www/sustainage/templates/targets.html'),
            (r'C:\SUSTAINAGESERVER\templates\prioritization.html', '/var/www/sustainage/templates/prioritization.html'),
            (r'C:\SUSTAINAGESERVER\templates\surveys.html', '/var/www/sustainage/templates/surveys.html'),
            (r'C:\SUSTAINAGESERVER\backend\data\stakeholder_questions.json', '/var/www/sustainage/backend/data/stakeholder_questions.json'),
            (r'C:\SUSTAINAGESERVER\locales\tr.json', '/var/www/sustainage/locales/tr.json'),
            # Removed verify_full_status_remote.py as it does not exist
        ]

        for local, remote in files_to_deploy:
            if os.path.exists(local):
                print(f"Uploading {local} to {remote}...")
                # Ensure directory exists
                remote_dir = os.path.dirname(remote).replace('\\', '/')
                try:
                    client.exec_command(f'mkdir -p {remote_dir}')
                except:
                    pass
                sftp.put(local, remote)
            else:
                print(f"Warning: Local file not found: {local}")

        # Set permissions
        print("Setting permissions...")
        client.exec_command("chown -R www-data:www-data /var/www/sustainage")
        client.exec_command("chmod -R 775 /var/www/sustainage")
        
        # Restart Service
        print("Restarting Service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("Systemctl output:", out)
        if err:
            print("Systemctl error:", err)
        
        client.exec_command("pkill -HUP gunicorn")
        time.sleep(2)
        
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print("Service Status:\n", stdout.read().decode())

        # Git operations
        try:
            print("Initializing remote Git repository...")
            git_cmds = [
                "cd /var/www/sustainage",
                "git config --global --add safe.directory /var/www/sustainage",
                "git config user.name \"Sustainage System\"",
                "git config user.email \"system@sustainage.cloud\"",
                "git add .",
                "git diff --cached --quiet || git commit -m \"Auto commit via deploy script\""
            ]
            remote_script = "bash -lc '" + " && ".join(git_cmds) + "'"
            stdin, stdout, stderr = client.exec_command(remote_script)
            print(stdout.read().decode())
        except Exception as e:
            print(f"Remote Git init failed: {e}")

        # Upload tools
        try:
            print("Uploading tools...")
            sftp = client.open_sftp()
            try:
                client.exec_command('mkdir -p /var/www/sustainage/tools')
            except:
                pass
            
            tools_to_upload = [
                ("fix_esrs_schema.py", "/var/www/sustainage/tools/fix_esrs_schema.py"),
                ("init_survey_db_sqlite.py", "/var/www/sustainage/tools/init_survey_db_sqlite.py"),
                ("create_test_survey_data.py", "/var/www/sustainage/tools/create_test_survey_data.py"),
                ("verify_survey_counts_remote.py", "/var/www/sustainage/tools/verify_survey_counts_remote.py"),
                ("check_actual_schema.py", "/var/www/sustainage/tools/check_actual_schema.py")
            ]
            
            for tool_name, remote_path in tools_to_upload:
                local_path = os.path.join(r"C:\SUSTAINAGESERVER\tools", tool_name)
                if os.path.exists(local_path):
                    sftp.put(local_path, remote_path)
                else:
                    print(f"Warning: Tool not found: {local_path}")
            
            sftp.close()
            
            # Run remote tools
            print("Running remote verification tools...")
            
            # 1. Fix ESRS Schema
            stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/fix_esrs_schema.py")
            print("ESRS Fix Output:\n", stdout.read().decode())
            
            # 2. Init Survey DB
            stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/init_survey_db_sqlite.py")
            print("Survey Init Output:\n", stdout.read().decode())
            
            # 3. Create Test Survey Data
            stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/create_test_survey_data.py")
            print("Create Data Output:\n", stdout.read().decode())
            
            # 4. Verify Counts
            stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/verify_survey_counts_remote.py")
            print("Verify Counts Output:\n", stdout.read().decode())
            
            # 5. Check Schema
            stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/check_actual_schema.py")
            print("Check Schema Output:\n", stdout.read().decode())
            
        except Exception as e:
            print(f"Remote tools execution failed: {e}")

        sftp.close()
        client.close()
        print("Deployment completed.")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy()
