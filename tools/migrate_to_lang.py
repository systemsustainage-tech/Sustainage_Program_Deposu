import os
import re

def migrate_templates():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    
    print(f"Scanning templates in {templates_dir}...")
    
    count = 0
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for {{ _( or {% set ... = _(
                # We want to replace _( with lang( when it's a function call in Jinja
                # Be careful not to replace variables ending in _
                
                # Simple replacement for standard patterns
                new_content = content.replace("{{ _(", "{{ lang(")
                new_content = new_content.replace("= _(", "= lang(")
                
                if new_content != content:
                    print(f"Migrating {file}...")
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
                    
    print(f"Migrated {count} files.")

if __name__ == "__main__":
    migrate_templates()
