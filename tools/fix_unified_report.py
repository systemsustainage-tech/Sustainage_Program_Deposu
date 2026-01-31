
import re

file_path = r'c:\SUSTAINAGESERVER\templates\unified_report.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the broken input lines
# <input %}="" %}checked{%="" 'carbon'="" and="" class="form-check-input" defined="" endif="" id="mod_carbon" if="" in="" is="" name="modules" suggested_modules="" type="checkbox" value="carbon" {%=""/>
# We want to replace it with:
# <input class="form-check-input" id="mod_carbon" name="modules" type="checkbox" value="carbon" {% if suggested_modules is defined and 'carbon' in suggested_modules %}checked{% endif %}/>

def replacement(match):
    # Extract value from the broken string
    # The broken string has value="carbon"
    val_match = re.search(r'value="([^"]+)"', match.group(0))
    if val_match:
        val = val_match.group(1)
        return f'<input class="form-check-input" id="mod_{val}" name="modules" type="checkbox" value="{val}" {{% if suggested_modules is defined and \'{val}\' in suggested_modules %}}checked{{% endif %}}/>'
    return match.group(0)

# Regex to match the broken input tag
# It starts with <input %}="" and ends with {%=""/>
pattern = r'<input %}="" .*? {%=""/>'

new_content = re.sub(pattern, replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed unified_report.html")
