import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Generator
Generates missing translations for other languages using Google Translate API (via LanguageManager)
"""

import json
import os

try:
    from utils.language_manager import LanguageManager
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.language_manager import LanguageManager

# Project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(ROOT_DIR, "locales")
TR_JSON_PATH = os.path.join(LOCALES_DIR, "tr.json")

# Target languages to generate
TARGET_LANGUAGES = ["en", "de", "fr", "es", "it", "ru", "ar", "zh", "ja", "pt", "nl", "ko"]

def generate_translations():
    """Generates translations for all target languages."""
    if not os.path.exists(TR_JSON_PATH):
        logging.info("tr.json not found! Run collect_keys.py first.")
        return

    lm = LanguageManager()
    
    # Load source (Turkish)
    with open(TR_JSON_PATH, "r", encoding="utf-8") as f:
        source_data = json.load(f)
    
    total_keys = len(source_data)
    logging.info(f"Source (tr) has {total_keys} keys.")

    for lang_code in TARGET_LANGUAGES:
        lang_file = os.path.join(LOCALES_DIR, f"{lang_code}.json")
        
        # Load existing translations
        target_data = {}
        if os.path.exists(lang_file):
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    target_data = json.load(f)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        
        # Identify missing keys
        missing_keys = []
        for key, value in source_data.items():
            if key not in target_data:
                missing_keys.append(key)
        
        if not missing_keys:
            logging.info(f"[{lang_code}] Up to date.")
            continue
            
        logging.info(f"[{lang_code}] Found {len(missing_keys)} missing keys. Translating...")
        
        # Translate missing keys using LanguageManager's generate_language method
        try:
            logging.info(f"[{lang_code}] Generating translations via LanguageManager...")
            lm.generate_language(lang_code)
            logging.info(f"[{lang_code}] Completed.")
        except Exception as e:
            logging.error(f"[{lang_code}] Error generating translations: {e}")

if __name__ == "__main__":
    generate_translations()
