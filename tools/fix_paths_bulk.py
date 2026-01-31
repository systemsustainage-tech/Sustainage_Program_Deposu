import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Determine depth from root to decide on replacement logic
    # Assuming C:\SDG is root.
    # If file is in C:\SDG\tools\, depth is 1 (needs ..)
    # If file is in C:\SDG\, depth is 0 (needs .)
    
    abs_path = os.path.abspath(file_path)
    # simplistic approach: check if 'tools' or 'modules' or 'scripts' is in path
    
    # We will use a generic replacement that works relative to the file location
    # But hardcoded 'C:\\SDG' usually implies the root of the project.
    
    # Replacement string logic:
    # We want to replace "C:\\SDG" with a variable that points to the project root.
    # We can inject a helper or just use os.path.
    
    # Strategy: Replace string literals containing C:\SDG with dynamic construction
    # Pattern: matches "c:\sdg" optionally followed by more path chars
    # We want to capture the part after sdg
    pattern = r'(["\'])c:[\\/]sdg([\\/][^"\']*)?\1'
    
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    if not matches:
        return False

    logging.info(f"Fixing {file_path}...")

    # Ensure os is imported
    if not re.search(r'^import\s+os\b', content, re.MULTILINE) and not re.search(r'^from\s+os\b', content, re.MULTILINE):
        # Add import os after shebang or encoding or at top
        lines = content.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#'):
                insert_idx = i + 1
            else:
                break
        lines.insert(insert_idx, "import os")
        content = "\n".join(lines)

    # Calculate root replacement code
    full_path = os.path.abspath(file_path)
    norm_path = full_path.replace('\\', '/')
    
    if '/SDG/' in norm_path:
        parts = norm_path.split('/SDG/')
        if len(parts) > 1:
            rel_parts = parts[1].split('/')
            sub_path = os.path.dirname(parts[1])
            depth = len([x for x in sub_path.split('/') if x])
            
            if depth == 0:
                root_code = "os.path.dirname(os.path.abspath(__file__))"
            elif depth == 1:
                root_code = "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
            else:
                # e.g. os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
                dots = '../' * depth
                # remove trailing slash
                dots = dots.rstrip('/')
                root_code = f"os.path.abspath(os.path.join(os.path.dirname(__file__), '{dots}'))"
        else:
             logging.info(f"Skipping {file_path}: path structure unclear")
             return False
    else:
        logging.info(f"Skipping {file_path}: not in SDG folder?")
        return False

    def replace_match(match):
        quote = match.group(1)
        suffix = match.group(2) # e.g. \modules\foo.py
        
        if not suffix:
            return root_code
            
        # Clean suffix
        # Remove leading slash/backslash
        suffix = suffix.lstrip('\\/')
        
        # Split by slash or backslash
        parts = re.split(r'[\\/]', suffix)
        
        # Join with ', '
        joined_parts = "', '".join(parts)
        
        return f"os.path.join({root_code}, '{joined_parts}')"

    new_content = re.sub(pattern, replace_match, content, flags=re.IGNORECASE)
    
    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# List of files to fix (derived from grep)
files = [
    r"c:\SDG\tools\fix_hardcoded_turkish.py",
    r"c:\SDG\tools\rebuild_system_from_master.py",
    r"c:\SDG\tools\screenshot_helper.py",
    r"c:\SDG\tools\build_mapping_csvs_from_excel.py",
    r"c:\SDG\tools\generate_module_doc.py",
    r"c:\SDG\tools\load_sdg_master_data.py",
    r"c:\SDG\tools\auto_fix_print_to_logging.py",
    r"c:\SDG\tools\create_master_tables.py",
    r"c:\SDG\tools\cbam_xml_to_csv.py",
    r"c:\SDG\create_web_version.py",
    r"c:\SDG\verify_localization_coverage.py",
    r"c:\SDG\update_waste_keys.py",
    r"c:\SDG\upload_to_hosting.py",
    r"c:\SDG\update_translations_reporting_part3.py",
    r"c:\SDG\update_tcfd_keys.py",
    r"c:\SDG\update_super_admin_keys.py",
    r"c:\SDG\update_sdg_question_bank_keys_v3.py",
    r"c:\SDG\update_sdg_reporting_keys.py",
    r"c:\SDG\update_sdg_question_bank_keys_v2.py",
    r"c:\SDG\update_sdg_progress_keys.py",
    r"c:\SDG\update_sdg_goal_keys.py",
    r"c:\SDG\update_menu_keys.py",
    r"c:\SDG\update_en_keys.py",
    r"c:\SDG\update_dashboard_keys.py",
    r"c:\SDG\update_company_keys.py",
    r"c:\SDG\update_company_info_keys.py",
    r"c:\SDG\update_adv_dashboard_keys.py",
    r"c:\SDG\test_language_init.py",
    r"c:\SDG\test_energy_load.py",
    r"c:\SDG\inspect_db.py",
    r"c:\SDG\cleanup_locales.py",
    r"c:\SDG\check_json.py",
    r"c:\SDG\check_keys.py",
    r"c:\SDG\check_en_keys.py",
    r"c:\SDG\check_en_json.py",
    r"c:\SDG\check_db_columns.py",
    r"c:\SDG\modules\tsrs\tsrs_gui.py",
    r"c:\SDG\modules\surveys\hosting_survey_manager.py",
    r"c:\SDG\modules\sdg\sdg_gui.py",
    r"c:\SDG\modules\gri\gri_gui.py",
    r"c:\SDG\scripts\smoke_test_user_permissions_gui.py",
    r"c:\SDG\scripts\temp\compare_folders.py"
]

for f in files:
    if os.path.exists(f):
        try:
            if fix_file(f):
                logging.info(f"Fixed {f}")
            else:
                logging.info(f"No changes or skipped {f}")
        except Exception as e:
            logging.error(f"Error fixing {f}: {e}")
    else:
        logging.info(f"File not found: {f}")
