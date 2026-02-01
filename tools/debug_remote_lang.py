import sys
import os
import logging

# Add path to find backend modules
sys.path.insert(0, '/var/www/sustainage')

logging.basicConfig(level=logging.INFO)

try:
    from backend.core.language_manager import LanguageManager
    lm = LanguageManager()
    
    print(f"Translations loaded keys: {list(lm._translations.keys())}")
    
    # Check TR
    if 'tr' in lm._translations:
        print(f"TR keys count: {len(lm._translations['tr'])}")
        print(f"TR 'btn_save': {lm._translations['tr'].get('btn_save', 'MISSING')}")
        print(f"TR 'module_carbon': {lm._translations['tr'].get('module_carbon', 'MISSING')}")
    else:
        print("TR NOT LOADED")

    # Check EN
    if 'en' in lm._translations:
        print(f"EN keys count: {len(lm._translations['en'])}")
        print(f"EN 'btn_save': {lm._translations['en'].get('btn_save', 'MISSING')}")
        print(f"EN 'module_carbon': {lm._translations['en'].get('module_carbon', 'MISSING')}")
    else:
        print("EN NOT LOADED")
        
    # Test get_text with fallback
    print("Testing get_text('btn_save', lang='xx') (should be EN):")
    print(lm.get_text('btn_save', lang='xx'))
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
