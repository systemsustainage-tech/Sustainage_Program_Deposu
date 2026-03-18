import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_PATH = "/var/www/sustainage/web_app.py"
LOCAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_app.py"))
REMOTE_DASHBOARD = "/var/www/sustainage/templates/dashboard.html"
LOCAL_DASHBOARD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "dashboard.html"))
REMOTE_BASE_TEMPLATE = "/var/www/sustainage/templates/base.html"
LOCAL_BASE_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "base.html"))
REMOTE_PASSWORD_RESET = "/var/www/sustainage/backend/security/core/password_reset.py"
LOCAL_PASSWORD_RESET = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "security", "core", "password_reset.py"))
REMOTE_BACKEND_EMAIL_SERVICE = "/var/www/sustainage/backend/services/email_service.py"
LOCAL_BACKEND_EMAIL_SERVICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "services", "email_service.py"))
REMOTE_USERS_TEMPLATE = "/var/www/sustainage/templates/users.html"
LOCAL_USERS_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "users.html"))
REMOTE_DB_MANAGER = "/var/www/sustainage/backend/core/database_manager.py"
LOCAL_DB_MANAGER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "core", "database_manager.py"))
REMOTE_COMPANIES_TEMPLATE = "/var/www/sustainage/templates/companies.html"
LOCAL_COMPANIES_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "companies.html"))
REMOTE_USER_MANAGER = "/var/www/sustainage/backend/yonetim/kullanici_yonetimi/models/user_manager.py"
LOCAL_USER_MANAGER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "yonetim", "kullanici_yonetimi", "models", "user_manager.py"))
REMOTE_YONETIM_CRYPTO = "/var/www/sustainage/backend/yonetim/security/core/crypto.py"
LOCAL_YONETIM_CRYPTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "yonetim", "security", "core", "crypto.py"))
REMOTE_MODULE_ACCESS = "/var/www/sustainage/backend/core/module_access.py"
LOCAL_MODULE_ACCESS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "core", "module_access.py"))
REMOTE_SUPER_USER_PROTECTION = "/var/www/sustainage/backend/security/core/super_user_protection.py"
LOCAL_SUPER_USER_PROTECTION = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "security", "core", "super_user_protection.py"))
REMOTE_TR_LOCALE = "/var/www/sustainage/locales/tr.json"
LOCAL_TR_LOCALE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "locales", "tr.json"))
REMOTE_SOCIAL_TEMPLATE = "/var/www/sustainage/templates/social.html"
LOCAL_SOCIAL_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "social.html"))
REMOTE_SUPPLY_CHAIN_TEMPLATE = "/var/www/sustainage/templates/supply_chain.html"
LOCAL_SUPPLY_CHAIN_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "supply_chain.html"))
REMOTE_CSRD_TEMPLATE = "/var/www/sustainage/templates/csrd.html"
LOCAL_CSRD_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "csrd.html"))
REMOTE_TAXONOMY_TEMPLATE = "/var/www/sustainage/templates/taxonomy.html"
LOCAL_TAXONOMY_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "taxonomy.html"))
REMOTE_PRIORITIZATION_TEMPLATE = "/var/www/sustainage/templates/prioritization.html"
LOCAL_PRIORITIZATION_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "prioritization.html"))
REMOTE_ECONOMIC_TEMPLATE = "/var/www/sustainage/templates/economic.html"
LOCAL_ECONOMIC_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "economic.html"))

def deploy():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {HOST} as {USER}...")
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        # Upload web_app.py
        sftp = ssh.open_sftp()
        print(f"Uploading {LOCAL_PATH} to {REMOTE_PATH}...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        
        # Upload dashboard.html template explicitly
        print(f"Uploading {LOCAL_DASHBOARD} to {REMOTE_DASHBOARD}...")
        sftp.put(LOCAL_DASHBOARD, REMOTE_DASHBOARD)
        
        print(f"Uploading {LOCAL_BASE_TEMPLATE} to {REMOTE_BASE_TEMPLATE}...")
        sftp.put(LOCAL_BASE_TEMPLATE, REMOTE_BASE_TEMPLATE)

        print(f"Uploading {LOCAL_PASSWORD_RESET} to {REMOTE_PASSWORD_RESET}...")
        sftp.put(LOCAL_PASSWORD_RESET, REMOTE_PASSWORD_RESET)

        print(f"Uploading {LOCAL_BACKEND_EMAIL_SERVICE} to {REMOTE_BACKEND_EMAIL_SERVICE}...")
        sftp.put(LOCAL_BACKEND_EMAIL_SERVICE, REMOTE_BACKEND_EMAIL_SERVICE)

        print(f"Uploading {LOCAL_USERS_TEMPLATE} to {REMOTE_USERS_TEMPLATE}...")
        sftp.put(LOCAL_USERS_TEMPLATE, REMOTE_USERS_TEMPLATE)

        print(f"Uploading {LOCAL_DB_MANAGER} to {REMOTE_DB_MANAGER}...")
        sftp.put(LOCAL_DB_MANAGER, REMOTE_DB_MANAGER)

        print(f"Uploading {LOCAL_COMPANIES_TEMPLATE} to {REMOTE_COMPANIES_TEMPLATE}...")
        sftp.put(LOCAL_COMPANIES_TEMPLATE, REMOTE_COMPANIES_TEMPLATE)

        print(f"Uploading {LOCAL_USER_MANAGER} to {REMOTE_USER_MANAGER}...")
        sftp.put(LOCAL_USER_MANAGER, REMOTE_USER_MANAGER)

        print(f"Uploading {LOCAL_YONETIM_CRYPTO} to {REMOTE_YONETIM_CRYPTO}...")
        sftp.put(LOCAL_YONETIM_CRYPTO, REMOTE_YONETIM_CRYPTO)

        print(f"Uploading {LOCAL_MODULE_ACCESS} to {REMOTE_MODULE_ACCESS}...")
        sftp.put(LOCAL_MODULE_ACCESS, REMOTE_MODULE_ACCESS)

        print(f"Uploading {LOCAL_SUPER_USER_PROTECTION} to {REMOTE_SUPER_USER_PROTECTION}...")
        sftp.put(LOCAL_SUPER_USER_PROTECTION, REMOTE_SUPER_USER_PROTECTION)

        print(f"Uploading {LOCAL_TR_LOCALE} to {REMOTE_TR_LOCALE}...")
        sftp.put(LOCAL_TR_LOCALE, REMOTE_TR_LOCALE)

        print(f"Uploading {LOCAL_SOCIAL_TEMPLATE} to {REMOTE_SOCIAL_TEMPLATE}...")
        sftp.put(LOCAL_SOCIAL_TEMPLATE, REMOTE_SOCIAL_TEMPLATE)

        print(f"Uploading {LOCAL_SUPPLY_CHAIN_TEMPLATE} to {REMOTE_SUPPLY_CHAIN_TEMPLATE}...")
        sftp.put(LOCAL_SUPPLY_CHAIN_TEMPLATE, REMOTE_SUPPLY_CHAIN_TEMPLATE)

        print(f"Uploading {LOCAL_CSRD_TEMPLATE} to {REMOTE_CSRD_TEMPLATE}...")
        sftp.put(LOCAL_CSRD_TEMPLATE, REMOTE_CSRD_TEMPLATE)

        print(f"Uploading {LOCAL_TAXONOMY_TEMPLATE} to {REMOTE_TAXONOMY_TEMPLATE}...")
        sftp.put(LOCAL_TAXONOMY_TEMPLATE, REMOTE_TAXONOMY_TEMPLATE)

        print(f"Uploading {LOCAL_PRIORITIZATION_TEMPLATE} to {REMOTE_PRIORITIZATION_TEMPLATE}...")
        sftp.put(LOCAL_PRIORITIZATION_TEMPLATE, REMOTE_PRIORITIZATION_TEMPLATE)

        print(f"Uploading {LOCAL_ECONOMIC_TEMPLATE} to {REMOTE_ECONOMIC_TEMPLATE}...")
        sftp.put(LOCAL_ECONOMIC_TEMPLATE, REMOTE_ECONOMIC_TEMPLATE)
        sftp.close()
        
        # Restart Service
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print("STDOUT:", out)
        if err: print("STDERR:", err)
        
        ssh.close()
        print("Deployment and restart complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy()
