import logging
import json
import os
import threading
import time

try:
    from google.cloud import translate_v2 as translate
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

GOOGLETRANS_AVAILABLE = False

class LanguageManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LanguageManager, cls).__new__(cls)
                cls._instance.initialized = False
            return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.locales_dir = os.path.join(self.base_dir, 'locales')
        self.current_lang = 'tr'
        self.translations = {}
        self.debug_log_path = os.path.join(self.base_dir, 'debug_lang.txt')
        
        # Google Cloud Translate Client init
        self.translate_client = None
        self.google_key_path = os.path.join(self.base_dir, 'google_key.json')
        # User provided key path
        self.user_key_path = os.path.join(self.base_dir, 'tidal-nectar-474719-b4-2d41f3d76adc.json')
        
        key_to_use = None
        if os.path.exists(self.user_key_path):
            key_to_use = self.user_key_path
            logging.info(f"Found Google Cloud key at: {self.user_key_path}")
        elif os.path.exists(self.google_key_path):
            key_to_use = self.google_key_path
            logging.info(f"Found Google Cloud key at: {self.google_key_path}")
            
        if GOOGLE_CLOUD_AVAILABLE and key_to_use:
            try:
                self.translate_client = translate.Client.from_service_account_json(key_to_use)
                logging.info("Google Cloud Translation API initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Google Cloud Translation API: {e}")
        
        self.translator = None

        self.available_languages = {
            'tr': 'Türkçe',
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'it': 'Italiano',
            'ru': 'Русский',
            'ar': 'العربية',
            'zh-cn': '中文'
        }
        self.ensure_locales_dir()
        self.load_language('tr')
        self.initialized = True

    def ensure_locales_dir(self):
        if not os.path.exists(self.locales_dir):
            os.makedirs(self.locales_dir)

    def load_language(self, lang_code):
        """Loads the language file. If not found, defaults to empty dict and starts background generation."""
        self.current_lang = lang_code
        file_path = os.path.join(self.locales_dir, f"{lang_code}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                logging.error(f"Error loading language {lang_code}: {e}")
                self.translations = {}
        else:
            self.translations = {}
            # If trying to load a non-TR language and it doesn't exist, try to generate it in background
            if lang_code != 'tr':
                logging.info(f"Language file {lang_code}.json not found. Starting background generation...")
                threading.Thread(target=self._generate_language_background, args=(lang_code,), daemon=True).start()

    def _generate_language_background(self, lang_code):
        """Wrapper to run generation in background and reload if active."""
        try:
            self.generate_language(lang_code)
            # Reload if current language is still the same
            if self.current_lang == lang_code:
                 file_path = os.path.join(self.locales_dir, f"{lang_code}.json")
                 if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            new_trans = json.load(f)
                        self.translations = new_trans
                        logging.info(f"Background generation for {lang_code} completed and loaded.")
                    except Exception as e:
                        logging.error(f"Error reloading generated language {lang_code}: {e}")
        except Exception as e:
            logging.error(f"Background generation failed for {lang_code}: {e}")
            
    def tr(self, key, default=None):
        """Translate a key. If key is missing and default is provided, add to tr.json."""
        # If key is not in translations
        if key not in self.translations:
            if default:
                # If we are in TR or if the key is missing in loaded lang, 
                # we might want to record it in tr.json for future translations
                self._add_missing_key(key, default)
                return default
            return key
        return self.translations[key]

    def _add_missing_key(self, key, value):
        """Add a missing key to tr.json if it doesn't exist there."""
        tr_path = os.path.join(self.locales_dir, "tr.json")
        try:
            if os.path.exists(tr_path):
                with open(tr_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            if key not in data:
                data[key] = value
                with open(tr_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                # Also update current translations if we are in TR
                if self.current_lang == 'tr':
                    self.translations[key] = value
        except Exception as e:
            logging.error(f"Error adding missing key {key}: {e}")

    def generate_language(self, target_lang_code):
        """
        Generates a new language file based on 'tr.json' using Google Translate.
        This is a blocking operation, should be used carefully.
        """
        source_path = os.path.join(self.locales_dir, "tr.json")
        target_path = os.path.join(self.locales_dir, f"{target_lang_code}.json")
        
        if not os.path.exists(source_path):
            logging.info("Source 'tr.json' not found.")
            return

        with open(source_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        target_data = {}
        if os.path.exists(target_path):
            with open(target_path, 'r', encoding='utf-8') as f:
                target_data = json.load(f)

        updated = False
        logging.info(f"Translating to {target_lang_code}...")

        # Identify missing keys
        missing_keys = [k for k in source_data if k not in target_data]
        
        if not missing_keys:
             logging.info("No new translations needed.")
             return

        if self.translate_client:
            # Use Official Google Cloud API
            logging.info(f"Using Google Cloud API for {len(missing_keys)} keys...")
            chunk_size = 50
            client_failed = False
            for i in range(0, len(missing_keys), chunk_size):
                if client_failed:
                    break
                
                chunk_keys = missing_keys[i:i + chunk_size]
                chunk_texts = [source_data[k] for k in chunk_keys]
                
                try:
                    # Translate batch
                    results = self.translate_client.translate(
                        chunk_texts, 
                        target_language=target_lang_code,
                        source_language='tr'
                    )
                    
                    # Ensure results is a list (single item might be dict)
                    if isinstance(results, dict):
                        results = [results]
                        
                    for key, res in zip(chunk_keys, results):
                        translated_text = res['translatedText']
                        # Handle HTML entities if any (Google API sometimes returns &#39;)
                        import html
                        translated_text = html.unescape(translated_text)
                        
                        target_data[key] = translated_text
                        updated = True
                        logging.info(f"Translated [{key}]: {source_data[key][:20]}... -> {translated_text[:20]}...")
                        
                except Exception as e:
                    logging.error(f"Batch translation error: {e}")
                    client_failed = True

        # Re-evaluate missing keys in case client failed or didn't cover everything
        missing_keys = [k for k in source_data if k not in target_data]

        if missing_keys and self.translator:
            # Fallback to unofficial googletrans
            logging.info(f"Falling back to googletrans for {len(missing_keys)} keys...")
            count = 0
            for key in missing_keys:
                value = source_data[key]
                try:
                    threading.Event().wait(0.5) # Avoid rate limiting
                    translation = self.translator.translate(value, src='tr', dest=target_lang_code)
                    if translation and translation.text:
                        target_data[key] = translation.text
                        updated = True
                        count += 1
                        logging.info(f"Translated (Unofficial) [{key}]: {value[:20]}... -> {translation.text[:20]}...")
                        
                        # Save periodically
                        if count % 10 == 0:
                            with open(target_path, 'w', encoding='utf-8') as f:
                                json.dump(target_data, f, indent=4, ensure_ascii=False)
                            logging.info(f"Saved progress ({count} keys)...")
                            
                except Exception as e:
                    logging.error(f"Error translating '{value}': {e}")
        else:
             logging.info("No translation service available.")
        
        if updated:
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(target_data, f, indent=4, ensure_ascii=False)
            logging.info(f"Saved {target_lang_code}.json")
        else:
            logging.info("No new translations saved.")

# Global instance
language_manager = LanguageManager()
