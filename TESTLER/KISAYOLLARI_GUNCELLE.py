import os
import glob
import sys

# Hedef klasör
TARGET_DIR = r"c:\SDG\testler"
SOURCE_DIR = r"c:\SDG"

# Kelime çevirileri (Dosya adlarını Türkçeleştirmek için)
TRANSLATIONS = {
    "test": "Test",
    "login": "Giris",
    "email": "Eposta",
    "system": "Sistem",
    "full": "Tam",
    "integration": "Entegrasyon",
    "user": "Kullanici",
    "management": "Yonetimi",
    "manager": "Yonetici",
    "database": "Veritabani",
    "db": "Veritabani",
    "performance": "Performans",
    "report": "Rapor",
    "reporting": "Raporlama",
    "security": "Guvenlik",
    "secure": "Guvenli",
    "password": "Sifre",
    "reset": "Sifirlama",
    "connection": "Baglanti",
    "survey": "Anket",
    "template": "Sablon",
    "load": "Yukleme",
    "data": "Veri",
    "auth": "KimlikDogrulama",
    "authentication": "KimlikDogrulama",
    "ui": "Arayuz",
    "gui": "Arayuz",
    "api": "API",
    "direct": "Dogrudan",
    "wrapper": "Sarmalayici",
    "single": "Tekil",
    "status": "Durum",
    "offline": "Cevrimdisi",
    "module": "Modul",
    "access": "Erisim",
    "environmental": "Cevresel",
    "energy": "Enerji",
    "document": "Dokuman",
    "comparison": "Karsilastirma",
    "workflow": "IsAkisi",
    "error": "Hata",
    "handling": "Yonetimi",
    "auto": "Otomatik",
    "save": "Kayit",
    "trend": "Trend",
    "quality": "Kalite",
    "validation": "Dogrulama",
    "parser": "Ayristirici",
    "benchmark": "Kiyaslama",
    "task": "Gorev",
    "department": "Departman",
    "link": "Baglanti",
    "theme": "Tema",
    "progress": "Ilerleme",
    "engine": "Motor",
    "unit": "Birim",
    "rest": "REST",
    "collection": "Toplama",
    "restoration": "GeriYukleme",
    "processing": "Isleme",
    "fix": "Duzeltme",
    "license": "Lisans",
    "screen": "Ekran",
    "verify": "Dogrulama",
    "simple": "Basit",
    "new": "Yeni",
    "create": "Olusturma",
    "sender": "Gonderici",
    "name": "Isim",
    "logo": "Logo",
    "html": "HTML",
    "taxonomy": "Taksonomi",
    "water": "Su",
    "tcfd": "TCFD", # Özel terim
    "gri": "GRI",   # Özel terim
    "sdg": "SDG",   # Özel terim
    "sasb": "SASB", # Özel terim
    "cbam": "SKDM", # CBAM -> SKDM (Sınırda Karbon Düzenleme Mekanizması)
    "ungc": "UNGC", # Özel terim
    "tsrs": "TSRS", # Özel terim
}

# Özel dosya adı eşleşmeleri (Daha düzgün isimlendirme için)
SPECIAL_MAPPINGS = {
    "test_login.py": ("Giris_Islemleri_Testi.py", "Kullanıcı giriş ekranı ve kimlik doğrulama işlemlerini test eder."),
    "test_full_system.py": ("Tam_Sistem_Testi.py", "Sistemin genel işleyişini uçtan uca test eder."),
    "test_email_system.py": ("Eposta_Sistemi_Testi.py", "E-posta gönderme, şablonlar ve SMTP bağlantılarını test eder."),
    "test_database_performance.py": ("Veritabani_Performans_Testi.py", "Veritabanı okuma/yazma hızını ve sorgu performansını test eder."),
    "test_user_management.py": ("Kullanici_Yonetimi_Testi.py", "Kullanıcı ekleme, silme ve yetkilendirme işlemlerini test eder."),
    "test_sdg_integration.py": ("SDG_Entegrasyon_Testi.py", "Sürdürülebilir Kalkınma Amaçları modülünün entegrasyonunu test eder."),
    "test_energy_load.py": ("Enerji_Veri_Yukleme_Testi.py", "Enerji tüketim verilerinin sisteme yüklenmesini test eder."),
    "test_password_reset.py": ("Sifre_Sifirlama_Testi.py", "Şifre sıfırlama akışını ve e-posta gönderimini test eder."),
    "test_connection.py": ("Baglanti_Testi.py", "Veritabanı ve ağ bağlantılarını kontrol eder."),
}

def translate_name(filename):
    """Dosya adını Türkçeye çevirir."""
    name_part = filename.replace("test_", "").replace("_test", "").replace(".py", "")
    parts = name_part.split("_")
    translated_parts = []
    
    for part in parts:
        translated = TRANSLATIONS.get(part, part.capitalize())
        translated_parts.append(translated)
        
    return "_".join(translated_parts) + "_Testi.py"

def generate_wrapper_content(original_path, description):
    """Wrapper dosya içeriğini oluşturur."""
    return f'''"""
BU DOSYA OTOMATİK OLUŞTURULMUŞ BİR KISAYOLDUR.
--------------------------------------------------
Açıklama: {description}
Orijinal Dosya: {original_path}
--------------------------------------------------
"""
import sys
import os
import subprocess
import time

# Orijinal dosyanın yolu
original_file = r"{original_path}"

def main():
    print("=" * 70)
    print(f"TEST BAŞLATILIYOR: {{os.path.basename(sys.argv[0])}}")
    print(f"Hedef: {{original_file}}")
    print("-" * 70)
    
    if not os.path.exists(original_file):
        print(f"HATA: Orijinal dosya bulunamadı!")
        input("Çıkmak için Enter'a basın...")
        return

    try:
        # Çalışma dizinini orijinal dosyanın olduğu yere ayarla (import sorunlarını önlemek için)
        original_dir = os.path.dirname(original_file)
        env = os.environ.copy()
        env["PYTHONPATH"] = r"c:\SDG" + os.pathsep + os.path.dirname(original_dir) + os.pathsep + env.get("PYTHONPATH", "")
        
        # Testi çalıştır
        result = subprocess.run([sys.executable, original_file], cwd=original_dir, env=env)
        
        print("-" * 70)
        if result.returncode == 0:
            print("✅ TEST BAŞARIYLA TAMAMLANDI")
        else:
            print(f"❌ TEST HATAYLA SONLANDI (Kod: {{result.returncode}})")
            
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {{e}}")

    print("=" * 70)
    input("\\nPencereyi kapatmak için Enter'a basın...")

if __name__ == "__main__":
    main()
'''

def main():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Klasör oluşturuldu: {TARGET_DIR}")

    # Test dosyalarını bul
    test_files = glob.glob(os.path.join(SOURCE_DIR, "**/test_*.py"), recursive=True)
    test_files += glob.glob(os.path.join(SOURCE_DIR, "**/*_test.py"), recursive=True)
    
    # Tekrar edenleri temizle
    test_files = list(set(test_files))
    
    print(f"Toplam {len(test_files)} test dosyası bulundu.")
    
    for file_path in test_files:
        filename = os.path.basename(file_path)
        
        # Bu scripti atla
        if filename == "create_test_shortcuts.py":
            continue

        # İsimlendirme ve Açıklama
        if filename in SPECIAL_MAPPINGS:
            new_name, description = SPECIAL_MAPPINGS[filename]
        else:
            new_name = translate_name(filename)
            description = f"Bu test dosyası '{filename}' dosyasını çalıştırır. Otomatik oluşturulmuştur."

        target_path = os.path.join(TARGET_DIR, new_name)
        
        # Wrapper dosyasını yaz
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(generate_wrapper_content(file_path, description))
            print(f"Oluşturuldu: {new_name}")
        except Exception as e:
            print(f"Hata ({filename}): {e}")

    print("\nİşlem tamamlandı.")

if __name__ == "__main__":
    main()
