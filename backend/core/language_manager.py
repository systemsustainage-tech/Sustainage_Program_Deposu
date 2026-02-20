# -*- coding: utf-8 -*-
import json
import os
import logging
import time

class LanguageManager:
    """
    Singleton class to manage multi-language support for AI reports and system messages.
    Loads translations from backend/locales/*.json.
    """
    _instance = None
    _translations = {}
    _default_lang = 'tr'
    _file_mtimes = {}
    _last_check_time = 0
    _check_interval = 5

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._load_translations()
        return cls._instance

    @property
    def translations(self):
        self._check_for_updates()
        return self._translations

    def _load_translations(self):
        """Load all JSON translation files from locales directory."""
        self._last_check_time = time.time()
        # Assuming this file is in backend/core/language_manager.py
        try:
            abs_path = os.path.abspath(__file__)
            base_dir = os.path.dirname(os.path.dirname(abs_path)) # backend/
            project_root = os.path.dirname(base_dir) # root/
            
            # Priority 1: Check root/locales (where we deploy updates)
            locales_dir = os.path.join(project_root, 'locales')
            
            if not os.path.exists(locales_dir):
                # Priority 2: Check backend/locales (legacy)
                locales_dir = os.path.join(base_dir, 'locales')
                
            if not os.path.exists(locales_dir):
                # Try alternative path relative to CWD
                alt_dir = os.path.join(os.getcwd(), 'backend', 'locales')
                if os.path.exists(alt_dir):
                    locales_dir = alt_dir
                else:
                    logging.error(f"Locales directory not found: {locales_dir} or {alt_dir}")
                    return

            self._locales_dir = locales_dir # Save for updates
            logging.info(f"Loading translations from {locales_dir}")
            
            if not hasattr(self, '_file_mtimes'):
                self._file_mtimes = {}

            for filename in os.listdir(locales_dir):
                if filename.endswith('.json'):
                    lang_code = filename.split('.')[0]
                    file_path = os.path.join(locales_dir, filename)
                    try:
                        mtime = os.path.getmtime(file_path)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self._translations[lang_code] = json.load(f)
                        self._file_mtimes[lang_code] = mtime
                        logging.debug(f"Loaded {lang_code} translation (mtime: {mtime})")
                    except Exception as e:
                        logging.error(f"Error loading translation {filename}: {e}")
        except Exception as e:
            logging.error(f"Critical error in _load_translations: {e}")

    def _check_for_updates(self):
        """Check if language files have changed and reload."""
        try:
            now = time.time()
            if now - getattr(self, '_last_check_time', 0) < getattr(self, '_check_interval', 5):
                return

            self._last_check_time = now
            if not hasattr(self, '_locales_dir') or not self._locales_dir:
                return

            # Check each known language
            for lang_code in list(self._translations.keys()):
                file_path = os.path.join(self._locales_dir, f"{lang_code}.json")
                if os.path.exists(file_path):
                    try:
                        current_mtime = os.path.getmtime(file_path)
                        last_mtime = self._file_mtimes.get(lang_code, 0)
                        
                        if current_mtime > last_mtime:
                            logging.info(f"Language file {lang_code}.json changed. Reloading...")
                            with open(file_path, 'r', encoding='utf-8') as f:
                                self._translations[lang_code] = json.load(f)
                            self._file_mtimes[lang_code] = current_mtime
                    except Exception as e:
                        logging.error(f"Error reloading {lang_code}: {e}")
        except Exception as e:
            logging.error(f"Error in _check_for_updates: {e}")

    def get_version(self, lang='tr'):
        """Return a version string based on file mtime for ETag."""
        self._check_for_updates()
        return str(self._file_mtimes.get(lang, 0))

    def get_text(self, key, lang='tr', default=None, **kwargs):
        """
        Get translated text for a key.
        Supports nested keys (e.g. 'auth.login_failed')
        Strict Mode: Only check requested lang, then return key/default.
        Logs warning if missing.
        """
        lang = lang or self._default_lang
        
        # Check requested language only
        val = self._get_value(lang, key)
        
        if val is not None:
            try:
                return val.format(**kwargs)
            except KeyError:
                return val # Return raw if formatting fails
            except Exception:
                return val
        
        # Log warning for missing key
        logging.warning(f"MISSING TRANSLATION [{lang}]: {key}")
        
        # Return default or readable key
        if default is not None:
            return default
            
        return self._make_readable(key)

    def _make_readable(self, key):
        """Convert 'active_surveys' to 'Active surveys'."""
        if not key:
            return ""
        # Replace underscores/hyphens with spaces and capitalize first letter
        return key.replace('_', ' ').replace('-', ' ').strip().capitalize()

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
        self._check_for_updates()
        return self._translations.get(lang, {})
