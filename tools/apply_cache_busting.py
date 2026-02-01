import os

def update_file(path, replacements):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements:
            content = content.replace(old, new)
            
        if content != original_content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {path}")
        else:
            print(f"No changes for {path}")
    except Exception as e:
        print(f"Error updating {path}: {e}")

# PHP Cache Busting
php_replacements = [
    ('href="css/style.css"', 'href="css/style.css?v=<?php echo filemtime(\'css/style.css\'); ?>"'),
    ('src="js/survey.js"', 'src="js/survey.js?v=<?php echo filemtime(\'js/survey.js\'); ?>"')
]

update_file(r'c:\SUSTAINAGESERVER\anket\survey.php', php_replacements)

# Flask Cache Busting (Stakeholder)
flask_replacements = [
    ('src="/static/img/sdg/{{ sdg }}.png"', 'src="/static/img/sdg/{{ sdg }}.png?v={{ app_version }}"')
]
update_file(r'c:\SUSTAINAGESERVER\templates\stakeholder.html', flask_replacements)

print("Cache busting applied.")
