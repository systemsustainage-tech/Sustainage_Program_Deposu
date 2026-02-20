import os
import re
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def scan_templates():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(project_root, 'templates')
    
    # Files to scan for render_template calls
    extensions = ['.py']
    
    missing_templates = set()
    found_templates = set()
    
    print(f"Scanning for render_template usage in {project_root}...")
    
    for root, dirs, files in os.walk(project_root):
        if 'venv' in root or '.git' in root or '__pycache__' in root or 'legacy' in root:
            continue
            
        for file in files:
            if file == 'verify_templates_exist.py': # Ignore self
                continue
            if not any(file.endswith(ext) for ext in extensions):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Regex to find render_template('filename.html', ...)
                    # Matches both ' and " quotes
                    matches = re.findall(r"render_template\s*\(\s*['\"]([^'\"]+)['\"]", content)
                    
                    for template_name in matches:
                        # Check if template exists
                        full_template_path = os.path.join(templates_dir, template_name)
                        
                        # Handle potential subdirectories in template name
                        if not os.path.exists(full_template_path):
                            # Try to see if it's relative? usually flask templates are relative to templates/
                            missing_templates.add((template_name, file_path))
                        else:
                            found_templates.add(template_name)
                            
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    print("\n--- Results ---")
    if missing_templates:
        print(f"❌ Found {len(missing_templates)} missing templates:")
        for t, f in missing_templates:
            print(f"  - {t} (referenced in {os.path.relpath(f, project_root)})")
    else:
        print("✅ All referenced templates exist.")
        
    print(f"ℹ️ Verified {len(found_templates)} unique existing templates.")

if __name__ == "__main__":
    scan_templates()
