import os
import json
import logging
from typing import Dict, Optional

class LanguageManager:
    def __init__(self, base_dir: str, default_lang: str = 'tr'):
        self.base_dir = base_dir
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_lang = default_lang
        self.load_languages()

    def load_languages(self):
        """Mevcut dil dosyalarını yükler (locales/*.json)"""
        locales_dir = os.path.join(self.base_dir, 'locales')
        if not os.path.exists(locales_dir):
            logging.warning(f"Locales directory not found: {locales_dir}")
            return

        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                lang_code = filename.split('.')[0]
                file_path = os.path.join(locales_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            self.translations[lang_code] = data
                            logging.info(f"Loaded translations for {lang_code}")
                except Exception as e:
                    logging.error(f"Error loading translation file {filename}: {e}")

        # Backend config overlay (legacy support)
        backend_tr_path = os.path.join(self.base_dir, 'backend', 'config', 'translations_tr.json')
        if os.path.exists(backend_tr_path):
            try:
                with open(backend_tr_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'tr' in self.translations:
                        # Only update root keys
                        for k, v in data.items():
                            if not isinstance(v, dict):
                                self.translations['tr'][k] = v
                        logging.info("Loaded overlay translations from backend/config/translations_tr.json")
            except Exception as e:
                logging.error(f"Error loading backend overlay translations: {e}")

    def get_text(self, key: str, lang: Optional[str] = None, default: Optional[str] = None) -> str:
        """Belirtilen anahtar için çeviriyi döndürür."""
        target_lang = lang or self.current_lang
        
        # Eğer istenen dil yoksa varsayılan dile düş
        if target_lang not in self.translations:
            target_lang = self.default_lang

        # Çeviriyi al
        translation = self.translations.get(target_lang, {}).get(key)
        
        if translation is None:
            # Fallback to default language if current is different
            if target_lang != self.default_lang:
                translation = self.translations.get(self.default_lang, {}).get(key)
            
            # Still None? Return default or key
            if translation is None:
                return default if default is not None else key
                
        return translation

    def set_language(self, lang: str):
        """Aktif dili değiştirir."""
        if lang in self.translations:
            self.current_lang = lang
        else:
            logging.warning(f"Language {lang} not found, keeping {self.current_lang}")

