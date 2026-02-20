import json
import os

DICT_PATH = r"c:\SUSTAINAGESERVER\tools\translation_dictionary.json"
LOCALES_DIR = r"c:\SUSTAINAGESERVER\locales"

NEW_KEYS = {
    "admin_only_access": "Bu alana sadece yöneticiler erişebilir.",
    "cookie_accept": "Kabul Et",
    "cookie_msg": "Bu site deneyiminizi geliştirmek için çerezleri kullanır.",
    "copyright_sustainage": "© 2024 Sustainage. Tüm hakları saklıdır.",
    "create_report_btn": "Rapor Oluştur",
    "dashboard_load_error": "Dashboard verileri yüklenirken hata oluştu.",
    "data_fetch_error": "Veri çekme hatası.",
    "doc_account_settings_admin": "Hesap Ayarları ve Yönetici Paneli",
    "doc_account_settings_desc": "Kullanıcı profilinizi güncelleyin ve sistem ayarlarını yönetin.",
    "doc_account_settings_title": "Hesap Ayarları",
    "doc_data_entry_desc": "Sürdürülebilirlik verilerinizi sisteme nasıl gireceğinizi öğrenin.",
    "doc_data_entry_step1": "Veri Girişi menüsünden ilgili modülü seçin.",
    "doc_data_entry_step2": "Tarih, miktar ve birim bilgilerini girin.",
    "doc_data_entry_step3": "Varsa kanıt dokümanı yükleyin.",
    "doc_data_entry_step4": "Kaydet butonuna tıklayarak işlemi tamamlayın.",
    "doc_data_entry_title": "Veri Girişi",
    "doc_nav_help": "Yardım Merkezi'ne git",
    "doc_reporting_desc": "GRI, ESRS ve özel formatlarda rapor oluşturma rehberi.",
    "doc_reporting_title": "Raporlama",
    "doc_welcome_desc": "Sustainage platformuna hoş geldiniz. Hızlı başlangıç rehberi ile hemen başlayın.",
    "doc_welcome_title": "Hoş Geldiniz",
    "error_add": "Ekleme sırasında hata oluştu.",
    "error_occurred": "Bir hata oluştu.",
    "footer_contact_us": "Bize Ulaşın",
    "footer_copyright": "Telif Hakkı",
    "footer_dpa": "Veri İşleme Anlaşması",
    "footer_help_center": "Yardım Merkezi",
    "footer_legal": "Yasal",
    "footer_privacy": "Gizlilik Politikası",
    "footer_sla": "Hizmet Seviyesi Anlaşması (SLA)",
    "footer_slogan": "Sürdürülebilir Gelecek İçin",
    "footer_support": "Destek",
    "logging_in": "Giriş yapılıyor...",
    "login_button": "Giriş Yap",
    "login_failed": "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.",
    "login_title": "Giriş Yap",
    "manager_not_active": "Yönetici hesabı aktif değil.",
    "module_not_active": "Bu modül şu anda aktif değil.",
    "password": "Şifre",
    "record_added_error": "Kayıt eklenirken hata oluştu.",
    "record_added_success": "Kayıt başarıyla eklendi.",
    "role_create_error": "Rol oluşturulamadı.",
    "role_create_success": "Rol başarıyla oluşturuldu.",
    "role_delete_error": "Rol silinemedi.",
    "role_delete_success": "Rol başarıyla silindi.",
    "role_not_found": "Rol bulunamadı.",
    "role_system_delete_error": "Sistem rolleri silinemez.",
    "role_system_edit_error": "Sistem rolleri düzenlenemez.",
    "role_update_error": "Rol güncellenemedi.",
    "role_update_success": "Rol başarıyla güncellendi.",
    "server_error": "Sunucu hatası oluştu.",
    "session_expired": "Oturum süreniz doldu. Lütfen tekrar giriş yapın.",
    "settings_updated": "Ayarlar güncellendi.",
    "success_add": "Başarıyla eklendi.",
    "system_error": "Sistem hatası.",
    "unauthorized_access": "Yetkisiz erişim.",
    "username": "Kullanıcı Adı",
    "weights_reset": "Ağırlıklar sıfırlandı.",
    "weights_updated": "Ağırlıklar güncellendi."
}

def add_keys():
    # Load Dictionary
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    added_count = 0
    for key, value in NEW_KEYS.items():
        if key not in data:
            data[key] = value
            added_count += 1
            print(f"Added: {key}")
        else:
            # Optional: Update existing if needed, but safe to skip
            pass
            
    if added_count > 0:
        # Sort keys
        sorted_data = dict(sorted(data.items()))
        
        with open(DICT_PATH, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)
        print(f"\nSuccessfully added {added_count} keys to translation_dictionary.json")
    else:
        print("\nNo new keys added (all existed).")

if __name__ == "__main__":
    add_keys()
