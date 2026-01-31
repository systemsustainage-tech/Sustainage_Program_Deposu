#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çok Dilli Raporlama Sistemi
TR/EN çeviri yönetimi ve raporlama
"""

import logging
import json
import os
from typing import Any, Dict, List, Optional


class TranslationManager:
    """Çeviri yönetim sistemi"""

    SUPPORTED_LANGUAGES = {
        'tr': 'Türkçe',
        'en': 'English'
    }

    def __init__(self, default_language: str = 'tr') -> None:
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()

    def load_translations(self) -> None:
        """Tüm çevirileri yükle"""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        config_dir = os.path.join(base_dir, 'config')

        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            trans_file = os.path.join(config_dir, f'translations_{lang_code}.json')

            if os.path.exists(trans_file):
                try:
                    with open(trans_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    logging.info(f"[OK] {lang_code.upper()} çevirileri yüklendi")
                except Exception as e:
                    logging.error(f"[HATA] {lang_code} yükleme: {e}")
                    self.translations[lang_code] = {}
            else:
                self.translations[lang_code] = {}

    def set_language(self, lang_code: str) -> bool:
        """Dili değiştir"""
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.current_language = lang_code
            return True
        return False

    def get(self, key: str, default: Optional[str] = None, lang: Optional[str] = None) -> str:
        """
        Çeviriyi getir
        
        Args:
            key: Çeviri anahtarı (örn: 'menu.dashboard' veya 'common.save')
            default: Bulunamazsa döndürülecek değer
            lang: Dil kodu (None ise current_language kullanılır)
        
        Returns:
            str: Çeviri metni
        """
        lang = lang or self.current_language

        # Key'i parse et (nested dict için)
        keys = key.split('.')
        value: Any = self.translations.get(lang, {})

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default or key

        if isinstance(value, str):
            return value
        return default or key

    def translate_dict(self, data: Dict[str, Any], mapping: Dict[str, str], lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Dictionary'i çevir
        
        Args:
            data: Çevrilecek veri
            mapping: Key mapping {'old_key': 'translation.key'}
            lang: Dil
        
        Returns:
            Dict: Çevrilmiş veri
        """
        lang = lang or self.current_language
        translated = {}

        for old_key, trans_key in mapping.items():
            if old_key in data:
                new_key = self.get(trans_key, old_key, lang)
                translated[new_key] = data[old_key]

        return translated

    def translate_list(self, items: List[str], prefix: str, lang: Optional[str] = None) -> List[str]:
        """
        Liste öğelerini çevir
        
        Args:
            items: Öğe listesi
            prefix: Çeviri prefix'i (örn: 'status')
            lang: Dil
        """
        lang = lang or self.current_language
        return [self.get(f"{prefix}.{item}", item, lang) for item in items]

    def get_report_template_translations(self, lang: Optional[str] = None) -> Dict[str, str]:
        """Rapor şablonu çevirilerini getir"""
        lang = lang or self.current_language

        return {
            'title': self.get('report.title', lang=lang),
            'period': self.get('report.period', lang=lang),
            'year': self.get('report.year', lang=lang),
            'executive_summary': self.get('report.executive_summary', lang=lang),
            'introduction': self.get('report.introduction', lang=lang),
            'methodology': self.get('report.methodology', lang=lang),
            'findings': self.get('report.findings', lang=lang),
            'recommendations': self.get('report.recommendations', lang=lang),
            'conclusion': self.get('report.conclusion', lang=lang),
            'appendices': self.get('report.appendices', lang=lang)
        }

    def add_translation(self, key: str, value: str, lang: str) -> None:
        """Yeni çeviri ekle (runtime)"""
        if lang not in self.translations:
            self.translations[lang] = {}

        keys = key.split('.')
        current = self.translations[lang]

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def save_translations(self, lang: str) -> bool:
        """Çevirileri dosyaya kaydet"""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            trans_file = os.path.join(base_dir, 'config', f'translations_{lang}.json')

            with open(trans_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[lang], f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            logging.error(f"Çeviri kaydetme hatası: {e}")
            return False


# Global translation manager instance
_translation_manager = None


def get_translation_manager(lang: str = 'tr') -> TranslationManager:
    """Global translation manager'ı getir (singleton)"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager(lang)
    return _translation_manager


def t(key: str, default: Optional[str] = None, lang: Optional[str] = None) -> str:
    """Kısa çeviri fonksiyonu"""
    tm = get_translation_manager()
    return tm.get(key, default, lang)

