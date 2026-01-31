
import paramiko
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b)'
PORT = 22

REMOTE_BASE = '/var/www/sustainage'
LOCAL_BASE = os.getcwd()

FILES_TO_DEPLOY = [
    'PROJECT_ROADMAP.md',
    'trae_prompts_2_status.md',
    'backend/modules/reporting/target_manager.py',
    'backend/modules/reporting/unified_report_docx.py',
    'templates/targets.html',
    'templates/base.html',
    'templates/dashboard.html',
    'web_app.py',
    'locales/tr.json',
    'templates/login.html',
    'templates/reports.html',
    'templates/company_detail.html',
    'templates/carbon.html',
    'templates/water.html',
    'templates/waste.html',
    'backend/core/audit_manager.py',
    'backend/yonetim/security/core/auth.py',
    'backend/modules/supply_chain/supply_chain_manager.py',
    'backend/modules/environmental/carbon_manager.py',
    'backend/modules/environmental/water_manager.py',
    'backend/modules/environmental/waste_manager.py',
    'backend/modules/environmental/carbon_manager.py',
    'backend/modules/sdg/sdg_manager.py',
    'backend/modules/social/social_manager.py',
    'backend/modules/governance/corporate_governance.py',
    'backend/modules/esg/esg_manager.py',
    'backend/modules/csrd/csrd_compliance_manager.py',
    'backend/modules/eu_taxonomy/taxonomy_manager.py',
    'backend/modules/economic/economic_value_manager.py',
    'backend/modules/issb/issb_manager.py',
    'backend/modules/iirc/iirc_manager.py',
    'backend/modules/esrs/esrs_manager.py',
    'backend/modules/tcfd/tcfd_manager.py',
    'backend/modules/tcfd/tcfd_schema.sql',
    'backend/modules/tnfd/tnfd_manager.py',
    'backend/modules/cdp/cdp_manager.py',
    'backend/modules/stakeholder/stakeholder_manager.py',
    'backend/modules/prioritization/prioritization_manager.py',
    'backend/modules/ungc/ungc_manager.py',
    'backend/modules/strategic/risk_opportunity_manager.py',
    'tools/fix_remote_db.py'
]

DIRS_TO_DEPLOY = [
    ('backend/modules/supplier_portal', 'backend/modules/supplier_portal'),
    ('templates/supplier_portal', 'templates/supplier_portal'),
    ('backend/modules/tcfd/data', 'backend/modules/tcfd/data'),
    ('backend/modules/cdp/reports', 'backend/modules/cdp/reports'),
    ('backend/modules/iirc/reports', 'backend/modules/iirc/reports')
]

def put_dir_recursive(sftp, local_dir, remote_dir):
    """Recursively uploads a directory to the remote server."""
    # Create remote directory if it doesn't exist
    try:
        sftp.stat(remote_dir)
    except IOError:
        try:
            sftp.mkdir(remote_dir)
            logging.info(f"Created remote directory: {remote_dir}")
        except Exception as e:
            # Try creating parent dirs if needed, but for now assume mostly flat structure needs
            logging.error(f"Failed to create {remote_dir}: {e}")

    try:
        items = os.listdir(local_dir)
    except Exception as e:
        logging.error(f"Failed to list local directory {local_dir}: {e}")
        return

    for item in items:
        if item in ['.git', '__pycache__', '.env', 'venv', 'logs', '.DS_Store', 'sdg.db', 'sdg_desktop.sqlite', 'node_modules']:
            continue
            
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"

        if os.path.isdir(local_path):
            put_dir_recursive(sftp, local_path, remote_path)
        elif os.path.isfile(local_path):
            try:
                sftp.put(local_path, remote_path)
                logging.info(f"Uploaded: {item} -> {remote_path}")
            except Exception as e:
                logging.error(f"Failed to upload {local_path} to {remote_path}: {e}")

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()
        logging.info("Connected.")
        
        # 1. Deploy Individual Files
        for rel_path in FILES_TO_DEPLOY:
            local_path = os.path.join(LOCAL_BASE, rel_path)
            remote_path = f"{REMOTE_BASE}/{rel_path}"
            try:
                # Ensure directory exists for individual files too (e.g. backend/core)
                remote_dir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    try:
                        # Simple mkdir (might fail if parent doesn't exist, but 'backend/core' usually exists or we need recursive mkdir)
                        # backend/core might not exist if it's new. Let's try to create it.
                        sftp.mkdir(remote_dir)
                    except:
                        pass # Ignore if it fails, maybe it exists or we can't create it
                
                sftp.put(local_path, remote_path)
                logging.info(f"Uploaded: {rel_path}")
            except Exception as e:
                logging.error(f"Failed to upload {rel_path}: {e}")

        # 2. Deploy Directories
        for local_rel, remote_rel in DIRS_TO_DEPLOY:
            local_dir = os.path.join(LOCAL_BASE, local_rel)
            remote_dir = f"{REMOTE_BASE}/{remote_rel}"
            put_dir_recursive(sftp, local_dir, remote_dir)
            
        sftp.close()
        
        # 3. Update Remote Database Schema (Targets) - SKIPPED
        # logging.info("--- Updating Remote Database Schema (Targets) ---")
        # cmd = f"cd {REMOTE_BASE} && python3 tools/update_db_schema.py"
        # stdin, stdout, stderr = client.exec_command(cmd)
        # exit_code = stdout.channel.recv_exit_status()
        # if exit_code == 0:
        #     logging.info("Database schema updated successfully.")
        # else:
        #     logging.error(f"Schema update failed: {stderr.read().decode()}")

        # 4. Create Audit Log Table - SKIPPED
        # logging.info("--- Creating Audit Log Table ---")
        # cmd = f"cd {REMOTE_BASE} && python3 tools/create_audit_log_table.py"
        # stdin, stdout, stderr = client.exec_command(cmd)
        # exit_code = stdout.channel.recv_exit_status()
        # if exit_code == 0:
        #     logging.info("Audit log table created successfully.")
        # else:
        #     logging.error(f"Audit log table creation failed: {stderr.read().decode()}")

        logging.info("Deployment completed.")
        
        # Restart service
        logging.info("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logging.info("Service restarted successfully.")
        else:
            logging.error(f"Failed to restart service: {stderr.read().decode()}")

    except Exception as e:
        logging.error(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    main()
