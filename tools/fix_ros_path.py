import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_ros_fos(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    # Replace ros.path with os.path
    new_content = new_content.replace('ros.path', 'os.path')
    # Replace fos.path with os.path
    new_content = new_content.replace('fos.path', 'os.path')
    
    if new_content != content:
        logging.info(f"Fixing {file_path}...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# List from grep
files = [
    r"c:\SDG\check_db_columns.py",
    r"c:\SDG\check_en_json.py",
    r"c:\SDG\check_en_keys.py",
    r"c:\SDG\check_keys.py",
    r"c:\SDG\cleanup_locales.py",
    r"c:\SDG\inspect_db.py",
    r"c:\SDG\update_adv_dashboard_keys.py",
    r"c:\SDG\update_company_info_keys.py",
    r"c:\SDG\update_company_keys.py",
    r"c:\SDG\update_dashboard_keys.py",
    r"c:\SDG\update_en_keys.py",
    r"c:\SDG\update_sdg_progress_keys.py",
    r"c:\SDG\update_sdg_reporting_keys.py",
    r"c:\SDG\update_tcfd_keys.py",
    r"c:\SDG\update_waste_keys.py",
    r"c:\SDG\verify_localization_coverage.py",
    r"c:\SDG\check_json.py",
    r"c:\SDG\test_energy_load.py",
    r"c:\SDG\test_language_init.py",
    r"c:\SDG\update_menu_keys.py",
    r"c:\SDG\update_sdg_goal_keys.py",
    r"c:\SDG\update_sdg_question_bank_keys_v2.py",
    r"c:\SDG\update_sdg_question_bank_keys_v3.py",
    r"c:\SDG\update_super_admin_keys.py",
    r"c:\SDG\update_translations_reporting_part3.py",
    r"c:\SDG\tools\fix_hardcoded_turkish.py",
    r"c:\SDG\tools\auto_fix_print_to_logging.py",
    r"c:\SDG\scripts\smoke_test_user_permissions_gui.py",
    r"c:\SDG\scripts\temp\compare_folders.py"
]

for f in files:
    if os.path.exists(f):
        fix_ros_fos(f)
