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
    WAIT = "⏳"         # Bekleniyor
    LOADING = "🔄"      # Yükleniyor
    SEARCH = "🔍"       # Arama
    SAVE = "💾"         # Kaydetme
    DELETE = "🗑️"       # Silme
    EDIT = "✏️"         # Düzenleme
    ADD = "➕"          # Ekleme
    REMOVE = "➖"       # Çıkarma
    SETTINGS = "⚙️"     # Ayarlar
    TOOLS = "🛠️"        # Araçlar
    
    # Nesne İkonları
    USER = "👤"         # Kullanıcı
    USERS = "👥"        # Kullanıcılar
    EMAIL = "📧"        # E-posta
    FILE = "📄"         # Dosya
    FOLDER = "📂"       # Klasör
    FOLDER_OPEN = "📂"  # Açık klasör
    REPORT = "📊"       # Rapor
    CHART_UP = "📈"     # Yükseliş
    CHART_DOWN = "📉"   # Düşüş
    DB = "🗄️"          # Veritabanı
    SECURE = "🔒"       # Güvenlik/Kilit
    UNLOCK = "🔓"       # Kilit açık
    KEY = "🔑"          # Anahtar
    ROCKET = "🚀"       # Başlatma/Hız
    FIRE = "🔥"         # Önemli/Acil
    STAR = "⭐"         # Favori
    LIGHTBULB = "💡"    # İpucu/Fikir
    PARTY = "🎉"        # Kutlama
    PLUG = "🔌"         # Fiş/Bağlantı
    LOCKED_KEY = "🔐"   # Kilitli Anahtar
    OUTBOX = "📤"       # Giden Kutusu
    MEMO = "📝"         # Not
    CLIPBOARD = "📋"    # Pano
    MAILBOX = "📬"      # Posta Kutusu
    WRENCH = "🔧"       # Tamir/Ayarlar
    KEYCAP_10 = "🔟"    # 10 Tuşu
    CALENDAR = "📅"     # Takvim
    TIME = "⏰"         # Zaman
    HOME = "🏠"         # Ana sayfa
    WORLD = "🌍"        # Dünya/Web
    LINK = "🔗"         # Bağlantı
    
    # Finans/Ticaret
    MONEY_BAG = "💰"    # Para Çantası
    SHOPPING_CART = "🛒" # Alışveriş Sepeti
    BRIEFCASE = "💼"    # İş/Çanta
    MONEY_WITH_WINGS = "💸" # Uçan Para
    
    # Doğa/Çevre (SDG için)
    LEAF = "🌿"         # Yaprak/Doğa
    TREE = "🌳"         # Ağaç
    EVERGREEN_TREE = "🌲" # Çam Ağacı
    SEED = "🌱"         # Tohum
    RECYCLE = "♻️"      # Geri dönüşüm
    WATER = "💧"        # Su (Eğer gerekirse)
    
    # Özel
    NEW = "🆕"          # Yeni
    EU_FLAG = "🇪🇺"      # AB Bayrağı
    TARGET = "🎯"       # Hedef
    
    # Yönlendirme
    RIGHT = "➡️"
    LEFT = "⬅️"
    UP = "⬆️"
    DOWN = "⬇️"
    NEXT = "⏭️"
    PREV = "⏮️"
    PLAY = "▶️"
    PAUSE = "⏸️"
    
    @classmethod
    def get(cls, name, default=""):
        """İsimden ikon getir"""
        return getattr(cls, name.upper(), default)
