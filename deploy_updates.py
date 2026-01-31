import paramiko
import os
import time
import glob

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

files_to_deploy = [
    ('c:/SUSTAINAGESERVER/REPORTING_GAPS_PLAN.md', 'REPORTING_GAPS_PLAN.md'),
    ('c:/SUSTAINAGESERVER/tools/test_unified_report_full_features.py', 'tools/test_unified_report_full_features.py'),
    ('c:/SUSTAINAGESERVER/tools/setup_test_user.py', 'tools/setup_test_user.py'),
    ('c:/SUSTAINAGESERVER/tools/simulate_user_actions.py', 'tools/simulate_user_actions.py'),
    ('c:/SUSTAINAGESERVER/tools/create_report_registry.py', 'tools/create_report_registry.py'),
    ('c:/SUSTAINAGESERVER/tools/diagnose_db.py', 'tools/diagnose_db.py'),
    ('c:/SUSTAINAGESERVER/web_app.py', 'web_app.py'),
    ('c:/SUSTAINAGESERVER/remote_web_app.py', 'remote_web_app.py'),
    ('c:/SUSTAINAGESERVER/backend/config/smtp_config.json', 'backend/config/smtp_config.json'),
    ('c:/SUSTAINAGESERVER/backend/config/translations_tr.json', 'backend/config/translations_tr.json'),
    ('c:/SUSTAINAGESERVER/backend/config/translations_en.json', 'backend/config/translations_en.json'),
    ('c:/SUSTAINAGESERVER/backend/yonetim/kullanici_yonetimi/models/user_manager.py', 'backend/yonetim/kullanici_yonetimi/models/user_manager.py'),
    ('c:/SUSTAINAGESERVER/tools/reset_super_remote.py', 'tools/reset_super_remote.py'),
    ('c:/SUSTAINAGESERVER/tools/init_critical_modules_remote.py', 'tools/init_critical_modules_remote.py'),
    ('c:/SUSTAINAGESERVER/backend/core/universal_manager.py', 'backend/core/universal_manager.py'),
    ('c:/SUSTAINAGESERVER/backend/core/reporting_journey_manager.py', 'backend/core/reporting_journey_manager.py'),
    ('c:/SUSTAINAGESERVER/tools/migrate_company_info.py', 'tools/migrate_company_info.py'),
    ('c:/SUSTAINAGESERVER/tools/test_company_edit.py', 'tools/test_company_edit.py'),
    ('c:/SUSTAINAGESERVER/tools/update_survey_schema.py', 'tools/update_survey_schema.py'),
    ('c:/SUSTAINAGESERVER/backend/modules/prioritization/prioritization_manager.py', 'backend/modules/prioritization/prioritization_manager.py'),
    ('c:/SUSTAINAGESERVER/tools/diagnose_500.py', 'tools/diagnose_500.py'),
    ('c:/SUSTAINAGESERVER/tools/inspect_db_schema.py', 'tools/inspect_db_schema.py'),
    ('c:/SUSTAINAGESERVER/tools/diagnose_survey_questions.py', 'tools/diagnose_survey_questions.py'),
    ('c:/SUSTAINAGESERVER/tools/cleanup_templates.py', 'tools/cleanup_templates.py'),
    ('c:/SUSTAINAGESERVER/tools/check_remote_template.py', 'tools/check_remote_template.py'),
    ('c:/SUSTAINAGESERVER/tools/test_survey_template_copy.py', 'tools/test_survey_template_copy.py'),
    ('c:/SUSTAINAGESERVER/tools/apply_remote_schema_fixes.py', 'tools/apply_remote_schema_fixes.py'),
]

# Add all templates recursively (including subdirectories like 'includes')
for root, dirs, files in os.walk('c:/SUSTAINAGESERVER/templates'):
    for file in files:
        if file.endswith('.html'):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, 'c:/SUSTAINAGESERVER').replace('\\', '/')
            files_to_deploy.append((full_path.replace('\\', '/'), rel_path))

# Add all locales dynamically
for locale_file in glob.glob('c:/SUSTAINAGESERVER/locales/*.json'):
    basename = os.path.basename(locale_file)
    files_to_deploy.append((locale_file.replace('\\', '/'), f'locales/{basename}'))

# Add all backend modules (just in case)
for root, dirs, files in os.walk('c:/SUSTAINAGESERVER/backend/modules'):
    for file in files:
        if file.endswith('.py'):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, 'c:/SUSTAINAGESERVER').replace('\\', '/')
            files_to_deploy.append((full_path.replace('\\', '/'), rel_path))

# Add all utils recursively
for root, dirs, files in os.walk('c:/SUSTAINAGESERVER/utils'):
    for file in files:
        if file.endswith('.py'):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, 'c:/SUSTAINAGESERVER').replace('\\', '/')
            files_to_deploy.append((full_path.replace('\\', '/'), rel_path))


def deploy_files():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        for local_path, remote_rel_path in files_to_deploy:
            if not os.path.exists(local_path):
                print(f"Local file not found: {local_path}")
                continue
                
            remote_path = f"{remote_base}/{remote_rel_path}"
            print(f"Uploading {local_path} to {remote_path}...")
            
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                print(f"Creating remote directory: {remote_dir}")
                ssh.exec_command(f"mkdir -p {remote_dir}")
            
            try:
                sftp.put(local_path, remote_path)
                print("Success.")
            except Exception as e:
                print(f"Failed to upload {remote_rel_path}: {e}")
                
        sftp.close()

        # Delete legacy config file if exists
        print("Removing legacy config/smtp_config.json...")
        ssh.exec_command(f"rm {remote_base}/config/smtp_config.json")

        # Fix permissions
        print("Fixing permissions...")
        ssh.exec_command(f"chown -R www-data:www-data {remote_base}")
        ssh.exec_command(f"chmod -R 775 {remote_base}")
        # Also ensure uploads dir exists and is writable
        ssh.exec_command(f"mkdir -p {remote_base}/uploads/reports")
        ssh.exec_command(f"chmod -R 777 {remote_base}/uploads")
        ssh.exec_command(f"chmod -R 777 {remote_base}/backend/data") # DB needs write

        print("Running DB fix (create_report_registry.py)...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/create_report_registry.py")
        print(stdout.read().decode())
        print(stderr.read().decode())

        print("Running DB diagnostics (diagnose_db.py)...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/diagnose_db.py")
        print(stdout.read().decode())
        print(stderr.read().decode())

        print("Running Super Admin Reset (reset_super_remote.py)...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/reset_super_remote.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from super reset: {err}")

        # Run Module Initialization
        print("Running Critical Module Initialization (init_critical_modules_remote.py)...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/init_critical_modules_remote.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from module init: {err}")

        # Run setup test user
        print("Running setup_test_user.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/setup_test_user.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from setup user: {err}")

        # Run DB Migration for Company Info
        print("Running migrate_company_info.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/migrate_company_info.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from migration: {err}")

        # Run report test script (backend logic test)
        print("Running test_unified_report_full_features.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/test_unified_report_full_features.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from report test script: {err}")

        # Run Survey Schema Update
        print("Running update_survey_schema.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/update_survey_schema.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from survey schema update: {err}")

        # Run Remote Schema Fixes (New)
        print("Running apply_remote_schema_fixes.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/apply_remote_schema_fixes.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from apply_remote_schema_fixes: {err}")

        # Setup Remote Backup (Cron)
        print("Running setup_remote_backup.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/setup_remote_backup.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from setup_remote_backup: {err}")
        
        # Restart service
        print("Restarting sustainage service...")
        
        # Fix permissions
        print("Fixing permissions...")
        ssh.exec_command(f"chown -R www-data:www-data {remote_base}")
        ssh.exec_command(f"chmod -R 775 {remote_base}")
        # Also ensure uploads dir exists and is writable
        ssh.exec_command(f"mkdir -p {remote_base}/uploads/reports")
        ssh.exec_command(f"chmod -R 777 {remote_base}/uploads")
        ssh.exec_command(f"chmod -R 777 {remote_base}/backend/data") # DB needs write
        
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Failed to restart service: {stderr.read().decode('utf-8')}")

        # Wait a moment for service to start
        print("Waiting 5 seconds for service to start...")
        time.sleep(5)

        # Run simulation script (http request test)
        print("Running simulate_user_actions.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/simulate_user_actions.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from simulation: {err}")

        # Run company_edit test
        print("Running test_company_edit.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/test_company_edit.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from company_edit test: {err}")

        # Run Diagnostics
        print("Running diagnose_500.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/diagnose_500.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from diagnostics: {err}")
            
        # Run DB Inspection
        print("Running inspect_db_schema.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/inspect_db_schema.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output from DB inspection: {err}")
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_files()
