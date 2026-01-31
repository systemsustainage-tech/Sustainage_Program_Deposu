
import sys
import os

# Add path to sys.path
sys.path.append('/var/www/sustainage')

try:
    from web_app import load_translations, TRANSLATIONS, gettext
    
    print("Running load_translations()...")
    load_translations()
    
    print(f"TRANSLATIONS size: {len(TRANSLATIONS)}")
    print(f"btn_add_data: {TRANSLATIONS.get('btn_add_data')}")
    print(f"gettext('btn_add_data'): {gettext('btn_add_data')}")
    
except Exception as e:
    print(f"Error: {e}")
