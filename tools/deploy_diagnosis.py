import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.modules.file_manager.advanced_file_manager import AdvancedFileManager

def deploy_diagnosis():
    # 1. Upload diagnosis script
    print("Uploading diagnosis script...")
    os.system("scp -i C:\\Sustainage_Key_New.pem tools/diagnose_user_company.py ubuntu@72.62.150.207:/var/www/sustainage/tools/")
    
    # 2. Run it remotely
    print("Running diagnosis remotely...")
    cmd = "ssh -i C:\\Sustainage_Key_New.pem ubuntu@72.62.150.207 \"cd /var/www/sustainage && source venv/bin/activate && python tools/diagnose_user_company.py super.admin\""
    os.system(cmd)

if __name__ == "__main__":
    deploy_diagnosis()
