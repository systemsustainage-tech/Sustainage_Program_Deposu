import json
import os
import shutil

def apply_cleanup():
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cleanup_report.json')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not os.path.exists(report_path):
        print(f"Report file not found: {report_path}")
        return

    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    # 1. Cleanup Static Files
    print("Cleaning up static files...")
    for file_path in report.get('unused_static', []):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        else:
            print(f"File not found (already deleted?): {file_path}")

    # 2. Cleanup Translation Keys
    print("\nCleaning up translation keys...")
    unused_keys = set(report.get('unused_keys', []))
    
    locales_dir = os.path.join(project_root, 'locales')
    # Process tr.json and en.json if they exist
    for lang_file in ['tr.json', 'en.json']:
        file_path = os.path.join(locales_dir, lang_file)
        if not os.path.exists(file_path):
            continue
            
        print(f"Processing {lang_file}...")
        
        # Backup
        shutil.copy2(file_path, file_path + '.bak')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        initial_count = len(data)
        new_data = {k: v for k, v in data.items() if k not in unused_keys}
        final_count = len(new_data)
        
        removed_count = initial_count - final_count
        print(f"Removed {removed_count} keys from {lang_file}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    apply_cleanup()
