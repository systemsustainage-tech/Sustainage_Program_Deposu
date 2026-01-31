# -*- coding: utf-8 -*-
import json
import os
import logging

class LanguageManager:
    """
    Singleton class to manage multi-language support for AI reports and system messages.
    Loads translations from backend/locales/*.json.
    """
    _instance = None
    _translations = {}
    _default_lang = 'tr'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._load_translations()
        return cls._instance

    def _load_translations(self):
        """Load all JSON translation files from locales directory."""
        # Assuming this file is in backend/core/language_manager.py
        base_dir = os.path.dirname(os.path.dirname(__file__)) # backend/
        locales_dir = os.path.join(base_dir, 'locales')
        
        if not os.path.exists(locales_dir):
            logging.error(f"Locales directory not found: {locales_dir}")
            return

        logging.info(f"Loading translations from {locales_dir}")
        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                lang_code = filename.split('.')[0]
                try:
                    with open(os.path.join(locales_dir, filename), 'r', encoding='utf-8') as f:
                        self._translations[lang_code] = json.load(f)
                    logging.debug(f"Loaded {lang_code} translation")
                except Exception as e:
                    logging.error(f"Error loading translation {filename}: {e}")

    def get_text(self, key, lang='tr', **kwargs):
        """
        Get translated text for a key.
        Supports nested keys (e.g. 'auth.login_failed')
        Fallback: requested_lang -> en -> tr -> key
        """
        lang = lang or self._default_lang
        
        # Fallback chain
        langs_to_try = [lang]
        if lang != 'en': langs_to_try.append('en')
        if lang != 'tr' and 'tr' not in langs_to_try: langs_to_try.append('tr')

        for l in langs_to_try:
            val = self._get_value(l, key)
            if val is not None:
                try:
                    return val.format(**kwargs)
                except KeyError:
                    return val # Return raw if formatting fails
                except Exception:
                    return val
        
        return key # Return key if nothing found

    def _get_value(self, lang, key):
        if lang not in self._translations:
            return None
        
        data = self._translations[lang]
        keys = key.split('.')
        
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return None
        
        return data if isinstance(data, str) else None

    def get_all_translations(self, lang):
        return self._translations.get(lang, {})
