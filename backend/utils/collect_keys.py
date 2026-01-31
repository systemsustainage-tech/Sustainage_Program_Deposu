#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Key Collector
Scans the codebase for localization keys and updates tr.json
"""

import logging
import json
import os
import re

# Project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(ROOT_DIR, "locales")
TR_JSON_PATH = os.path.join(LOCALES_DIR, "tr.json")

# Regex patterns to find lm.tr('key', 'default') calls
# Supports single and double quotes, and multiline calls
PATTERNS = [
    r"lm\.tr\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",  # lm.tr('key', 'val')
    r"self\.lm\.tr\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",  # self.lm.tr('key', 'val')
    r"LanguageManager\(\)\.tr\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)" # LanguageManager().tr('key', 'val')
]

def collect_keys():
    """Scans all python files and collects translation keys."""
    logging.info(f"Scanning directory: {ROOT_DIR}")
    
    collected_keys = {}
    
    # Walk through all files
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    for pattern in PATTERNS:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            key = match.group(1)
                            value = match.group(2)
                            collected_keys[key] = value
                            
                except Exception as e:
                    logging.error(f"Error reading file {file_path}: {e}")

    logging.info(f"Found {len(collected_keys)} unique keys in code.")
    return collected_keys

def update_tr_json(new_keys):
    """Updates tr.json with new keys."""
    if not os.path.exists(LOCALES_DIR):
        os.makedirs(LOCALES_DIR)
        
    current_translations = {}
    if os.path.exists(TR_JSON_PATH):
        try:
            with open(TR_JSON_PATH, "r", encoding="utf-8") as f:
                current_translations = json.load(f)
        except Exception as e:
            logging.error(f"Error reading tr.json: {e}")
            
    # Update with new keys
    added_count = 0
    updated_count = 0
    
    for key, value in new_keys.items():
        if key not in current_translations:
            current_translations[key] = value
            added_count += 1
        # Uncomment below if you want to update existing keys with values from code
        # elif current_translations[key] != value:
        #     current_translations[key] = value
        #     updated_count += 1
            
    # Save back to file
    try:
        with open(TR_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(current_translations, f, ensure_ascii=False, indent=4, sort_keys=True)
        logging.info(f"Updated tr.json: {added_count} added, {updated_count} updated.")
        logging.info(f"Total keys: {len(current_translations)}")
    except Exception as e:
        logging.error(f"Error writing tr.json: {e}")

if __name__ == "__main__":
    keys = collect_keys()
    update_tr_json(keys)
