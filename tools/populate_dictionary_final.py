
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
DICT_PATH = os.path.join(TOOLS_DIR, 'translation_dictionary.json')

# Professional translations for missing TR keys and common DE keys
TRANSLATIONS = {
    "activity_data": {"tr": "Aktivite Verisi", "de": "Aktivitätsdaten"},
    "add_data": {"tr": "Veri Ekle", "de": "Daten hinzufügen"},
    "add_question": {"tr": "Soru Ekle", "de": "Frage hinzufügen"},
    "address": {"tr": "Adres", "de": "Adresse"},
    "admin": {"tr": "Yönetici", "de": "Administrator"},
    "admin_required": {"tr": "Yönetici İzni Gerekli", "de": "Administrator erforderlich"},
    "approve": {"tr": "Onayla", "de": "Genehmigen"},
    "baseline": {"tr": "Referans", "de": "Basislinie"},
    "bio_species": {"tr": "Biyoçeşitlilik Türleri", "de": "Artenvielfalt"},
    "blue": {"tr": "Mavi", "de": "Blau"},
    "coming_soon": {"tr": "Çok Yakında", "de": "Demnächst"},
    "delete_record": {"tr": "Kaydı Sil", "de": "Eintrag löschen"},
    "description": {"tr": "Açıklama", "de": "Beschreibung"},
    "edit": {"tr": "Düzenle", "de": "Bearbeiten"},
    "Elektrik": {"tr": "Elektrik", "de": "Elektrizität", "en": "Electricity"},
    "email": {"tr": "E-posta", "de": "E-Mail"},
    "error": {"tr": "Hata", "de": "Fehler"},
    "export_excel": {"tr": "Excel'e Aktar", "de": "Excel exportieren"},
    "export_pdf": {"tr": "PDF'e Aktar", "de": "PDF exportieren"},
    "failed": {"tr": "Başarısız", "de": "Fehlgeschlagen"},
    "female": {"tr": "Kadın", "de": "Weiblich"},
    "file_upload": {"tr": "Dosya Yükle", "de": "Datei hochladen"},
    "filter": {"tr": "Filtrele", "de": "Filtern"},
    "general": {"tr": "Genel", "de": "Allgemein"},
    "gri_standards": {"tr": "GRI Standartları", "de": "GRI-Standards"},
    "home": {"tr": "Ana Sayfa", "de": "Startseite"},
    "id": {"tr": "Kimlik", "de": "ID"},
    "import_data": {"tr": "Veri İçe Aktar", "de": "Daten importieren"},
    "in_progress": {"tr": "Devam Ediyor", "de": "In Bearbeitung"},
    "info": {"tr": "Bilgi", "de": "Info"},
    "invalid_email": {"tr": "Geçersiz E-posta", "de": "Ungültige E-Mail"},
    "invalid_password": {"tr": "Geçersiz Parola", "de": "Ungültiges Passwort"},
    "loading": {"tr": "Yükleniyor...", "de": "Laden..."},
    "login": {"tr": "Giriş Yap", "de": "Anmelden"},
    "logout": {"tr": "Çıkış Yap", "de": "Abmelden"},
    "male": {"tr": "Erkek", "de": "Männlich"},
    "manager": {"tr": "Yönetici", "de": "Manager"},
    "missing_parameters": {"tr": "Eksik Parametreler", "de": "Fehlende Parameter"},
    "month": {"tr": "Ay", "de": "Monat"},
    "name": {"tr": "İsim", "de": "Name"},
    "network_error": {"tr": "Ağ Hatası", "de": "Netzwerkfehler"},
    "new": {"tr": "Yeni", "de": "Neu"},
    "next": {"tr": "İleri", "de": "Weiter"},
    "no": {"tr": "Hayır", "de": "Nein"},
    "not_started": {"tr": "Başlamadı", "de": "Nicht begonnen"},
    "ok": {"tr": "Tamam", "de": "OK"},
    "operation_successful": {"tr": "İşlem Başarılı", "de": "Vorgang erfolgreich"},
    "other": {"tr": "Diğer", "de": "Andere"},
    "password": {"tr": "Parola", "de": "Passwort"},
    "password_mismatch": {"tr": "Parolalar eşleşmiyor.", "de": "Passwörter stimmen nicht überein."},
    "pending": {"tr": "Beklemede", "de": "Ausstehend"},
    "phone": {"tr": "Telefon", "de": "Telefon"},
    "please_wait": {"tr": "Lütfen bekleyin...", "de": "Bitte warten..."},
    "previous": {"tr": "Geri", "de": "Zurück"},
    "profile": {"tr": "Profil", "de": "Profil"},
    "refresh": {"tr": "Yenile", "de": "Aktualisieren"},
    "register": {"tr": "Kayıt Ol", "de": "Registrieren"},
    "remove": {"tr": "Kaldır", "de": "Entfernen"},
    "required": {"tr": "Zorunlu", "de": "Erforderlich"},
    "reset": {"tr": "Sıfırla", "de": "Zurücksetzen"},
    "role": {"tr": "Rol", "de": "Rolle"},
    "save": {"tr": "Kaydet", "de": "Speichern"},
    "save_changes": {"tr": "Değişiklikleri Kaydet", "de": "Änderungen speichern"},
    "scope1": {"tr": "Kapsam 1 (Doğrudan Emisyonlar)", "de": "Scope 1 (Direkte Emissionen)"},
    "scope2": {"tr": "Kapsam 2 (Enerji Dolaylı)", "de": "Scope 2 (Indirekte Energieemissionen)"},
    "scope3": {"tr": "Kapsam 3 (Diğer Dolaylı)", "de": "Scope 3 (Andere indirekte Emissionen)"},
    "search": {"tr": "Ara", "de": "Suchen"},
    "select": {"tr": "Seç", "de": "Auswählen"},
    "settings": {"tr": "Ayarlar", "de": "Einstellungen"},
    "social_responsibility": {"tr": "Sosyal Sorumluluk", "de": "Soziale Verantwortung"},
    "status": {"tr": "Durum", "de": "Status"},
    "status_approved": {"tr": "Onaylandı", "de": "Genehmigt"},
    "status_cancelled": {"tr": "İptal Edildi", "de": "Abgebrochen"},
    "status_completed": {"tr": "Tamamlandı", "de": "Abgeschlossen"},
    "status_draft": {"tr": "Taslak", "de": "Entwurf"},
    "status_pending": {"tr": "Beklemede", "de": "Ausstehend"},
    "status_rejected": {"tr": "Reddedildi", "de": "Abgelehnt"},
    "submit": {"tr": "Gönder", "de": "Absenden"},
    "success": {"tr": "Başarılı", "de": "Erfolg"},
    "surname": {"tr": "Soyisim", "de": "Nachname"},
    "system_error": {"tr": "Sistem Hatası", "de": "Systemfehler"},
    "title": {"tr": "Başlık", "de": "Titel"},
    "total": {"tr": "Toplam", "de": "Gesamt"},
    "type": {"tr": "Tür", "de": "Typ"},
    "update": {"tr": "Güncelle", "de": "Aktualisieren"},
    "upload": {"tr": "Yükle", "de": "Hochladen"},
    "user": {"tr": "Kullanıcı", "de": "Benutzer"},
    "user_management": {"tr": "Kullanıcı Yönetimi", "de": "Benutzerverwaltung"},
    "username": {"tr": "Kullanıcı Adı", "de": "Benutzername"},
    "version": {"tr": "Sürüm 1.0.0", "de": "Version 1.0.0"},
    "view": {"tr": "Görüntüle", "de": "Anzeigen"},
    "viewer": {"tr": "İzleyici", "de": "Betrachter"},
    "warning": {"tr": "Uyarı", "de": "Warnung"},
    "year": {"tr": "Yıl", "de": "Jahr"},
    "yes": {"tr": "Evet", "de": "Ja"},
    "sasb_standards": {"tr": "SASB Standartları", "de": "SASB-Standards"},
    "Su": {"tr": "Su", "de": "Wasser", "en": "Water"},
    "security_desc": {"tr": "Güvenlik ayarlarını yönetin.", "de": "Sicherheitseinstellungen verwalten."},
    "esrs_impact_help": {"tr": "ESRS etki analizi yardımı.", "de": "ESRS-Wirkungsanalyse-Hilfe."},
    "opt_sasb": {"tr": "SASB Seçeneği", "de": "SASB-Option"},
    "scope_social": {"tr": "Sosyal Kapsam", "de": "Sozialer Geltungsbereich"},
    "sdg_total_goals": {"tr": "Toplam Hedef", "de": "Gesamtziele"},
    "new_investment_project": {"tr": "Yeni Yatırım Projesi", "de": "Neues Investitionsprojekt"},
    "investors": {"tr": "Yatırımcılar", "de": "Investoren"},
    "help_a2": {"tr": "Yardım", "de": "Hilfe"},
    "survey_search_placeholder": {"tr": "Anket ara...", "de": "Umfrage suchen..."},
    "baseline_value": {"tr": "Referans Değer", "de": "Basiswert"},
    "non_hazardous": {"tr": "Tehlikesiz", "de": "Nicht gefährlich"},
    "max_login_attempts_desc": {"tr": "Maksimum giriş denemesi.", "de": "Maximale Anmeldeversuche."},
    "cdp_desc": {"tr": "CDP Raporlama", "de": "CDP-Berichterstattung"}
}

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved: {path}")
    except Exception as e:
        print(f"Error saving {path}: {e}")

def populate():
    print("Loading translation dictionary...")
    dictionary = load_json(DICT_PATH)
    
    # Update dictionary with new translations
    for key, val in TRANSLATIONS.items():
        if key not in dictionary:
            dictionary[key] = {}
        
        dictionary[key]["en"] = val.get("en", key.replace("_", " ").title()) # Fallback for EN if not explicitly set above
        if "tr" in val:
            dictionary[key]["tr"] = val["tr"]
        if "de" in val:
            dictionary[key]["de"] = val["de"]

    save_json(DICT_PATH, dictionary)
    print("Translation dictionary updated.")

if __name__ == "__main__":
    populate()
