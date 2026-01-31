import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.language_manager import LanguageManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def propagate_translations():
    lm = LanguageManager()
    
    available_langs = lm.available_languages
    target_langs = [code for code in available_langs.keys() if code != 'tr']
    
    logging.info(f"Propagating translations to: {', '.join(target_langs)}")
    
    for lang_code in target_langs:
        logging.info(f"\n--- Processing {lang_code} ({available_langs[lang_code]}) ---")
        try:
            lm.generate_language(lang_code)
            logging.info(f"Completed {lang_code}")
        except Exception as e:
            logging.error(f"Error processing {lang_code}: {e}")

if __name__ == "__main__":
    propagate_translations()
