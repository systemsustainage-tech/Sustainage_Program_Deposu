# -*- coding: utf-8 -*-
"""
Merkezi ikon ve emoji tanımlamaları.
Kod içerisinde doğrudan emoji kullanımı yerine bu sınıf kullanılmalıdır.
Bu sayede encoding sorunları önlenir ve yönetim kolaylaşır.
"""

class Icons:
    """Uygulama genelinde kullanılan ikonlar"""
    
    # Durum İkonları
    SUCCESS = "✅"      # İşlem başarılı
    FAIL = "❌"         # İşlem başarısız
    WARNING = "⚠️"      # Uyarı
    INFO = "ℹ️"         # Bilgi
    ERROR = "⛔"        # Kritik hata
    PASS = "✓"          # Geçti
    REJECT = "✗"        # Reddedildi
    
    # İşlem İkonları
    LOADING = "🔄"      # Yükleniyor
    SAVE = "💾"         # Kaydetme
    ADD = "➕"          # Ekleme
    
    # Nesne İkonları
    EMAIL = "📧"        # E-posta
    FILE = "📄"         # Dosya
    REPORT = "📊"       # Rapor
    CHART_UP = "📈"     # Yükseliş
    KEY = "🔑"          # Anahtar
    STAR = "⭐"         # Favori
    LOCKED_KEY = "🔐"   # Kilitli Anahtar
    CLIPBOARD = "📋"    # Pano
    TIME = "⏰"         # Zaman
    
    # Yönlendirme
    RIGHT = "➡️"
    LEFT = "⬅️"
    NEXT = "⏭️"
    
    @classmethod
    def get(cls, name, default=""):
        """İsimden ikon getir"""
        return getattr(cls, name.upper(), default)
