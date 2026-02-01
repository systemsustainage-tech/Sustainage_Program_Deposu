import sys
import os

# Add project root to path
sys.path.append('/var/www/sustainage')

from backend.core.language_manager import LanguageManager

def check_translation():
    lm = LanguageManager()
    key = 'dashboard_welcome'
    text = lm.get_text(key, lang='tr')
    print(f"Key: {key}")
    print(f"Text: {text}")
    
    if text == key:
        print("FAIL: Translation missing (returns key)")
    else:
        print("PASS: Translation found")

if __name__ == "__main__":
    check_translation()
