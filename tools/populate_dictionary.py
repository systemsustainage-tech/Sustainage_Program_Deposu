
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
DICT_PATH = os.path.join(TOOLS_DIR, 'translation_dictionary.json')

# Professional translations
TRANSLATIONS = {
    "app_name": {"en": "Sustainage SPA", "de": "Sustainage SPA", "tr": "Sustainage SPA"},
    "key": {"en": "Key", "de": "Schlüssel"},
    "excel_report": {"en": "Excel Report", "de": "Excel-Bericht"},
    "lbl_phone": {"en": "Phone", "de": "Telefon"},
    "lbl_website": {"en": "Website", "de": "Webseite"},
    "lbl_address": {"en": "Address", "de": "Adresse"},
    "lbl_city": {"en": "City", "de": "Stadt"},
    "lbl_district": {"en": "District", "de": "Bezirk"},
    "lbl_postcode": {"en": "Postal Code", "de": "Postleitzahl"},
    "lbl_country": {"en": "Country", "de": "Land"},
    "lbl_employees": {"en": "Number of Employees", "de": "Anzahl der Mitarbeiter"},
    "lbl_commercial_title": {"en": "Commercial Title", "de": "Handelsname"},
    
    # Missing EN keys
    "rate_limit_exceeded": {"en": "Rate limit exceeded. Please try again later.", "de": "Ratenlimit überschritten. Bitte versuchen Sie es später erneut."},
    "too_many_requests": {"en": "Too many requests.", "de": "Zu viele Anfragen."},
    "data_saved": {"en": "Data saved successfully.", "de": "Daten erfolgreich gespeichert."},
    "invalid_module": {"en": "Invalid module.", "de": "Ungültiges Modul."},
    "api_endpoint_health": {"en": "Health Check Endpoint", "de": "Systemstatus-Endpunkt"},
    "api_endpoint_info": {"en": "API Info Endpoint", "de": "API-Info-Endpunkt"},
    "api_endpoint_company": {"en": "Company Endpoint", "de": "Unternehmens-Endpunkt"},
    "api_endpoint_carbon": {"en": "Carbon Endpoint", "de": "Kohlenstoff-Endpunkt"},
    "api_endpoint_carbon_add": {"en": "Add Carbon Data Endpoint", "de": "Kohlenstoffdaten hinzufügen Endpunkt"},
    "api_endpoint_sdg": {"en": "SDG Endpoint", "de": "SDG-Endpunkt"},
    "api_endpoint_reports": {"en": "Reports Endpoint", "de": "Berichte-Endpunkt"},

    # Vue Keys / Categories
    "category_environmental": {"en": "Environmental", "de": "Umwelt"},
    "category_social": {"en": "Social", "de": "Soziales"},
    "category_governance": {"en": "Governance", "de": "Unternehmensführung"},
    "category_compliance": {"en": "Compliance & Reporting", "de": "Compliance & Berichterstattung"},
    "dashboard_welcome": {"en": "Welcome to your Sustainability Dashboard", "de": "Willkommen in Ihrem Nachhaltigkeits-Dashboard"},
    "login_title": {"en": "Login to Sustainage", "de": "Bei Sustainage anmelden"},
    "status_active": {"en": "Active", "de": "Aktiv"},
    "status_pending": {"en": "Pending", "de": "Ausstehend"},
    "completion": {"en": "Completion", "de": "Fertigstellung"},
    "action_enter_data": {"en": "Enter Data", "de": "Daten eingeben"},
    "action_enter_data_short": {"en": "Enter", "de": "Eingeben"},
    "action_view_details": {"en": "View Details", "de": "Details anzeigen"},
    "action_create_report": {"en": "Create Report", "de": "Bericht erstellen"},
    "performance_score": {"en": "Performance Score", "de": "Leistungsbewertung"},
    "data_fetch_error": {"en": "Error fetching data.", "de": "Fehler beim Abrufen der Daten."},
    "dashboard_load_error": {"en": "Error loading dashboard.", "de": "Fehler beim Laden des Dashboards."},
    "dashboard_title": {"en": "Dashboard", "de": "Dashboard"},
    "dark_mode": {"en": "Dark Mode", "de": "Dunkelmodus"},
    "light_mode": {"en": "Light Mode", "de": "Heller Modus"},
    "share_button": {"en": "Share", "de": "Teilen"},
    "export_button": {"en": "Export", "de": "Exportieren"},
    "average_score": {"en": "Average Score", "de": "Durchschnittsbewertung"},
    "completed_reports": {"en": "Completed Reports", "de": "Abgeschlossene Berichte"},
    "next_deadline": {"en": "Next Deadline", "de": "Nächste Frist"},
    "loading": {"en": "Loading...", "de": "Laden..."},
    "retry_button": {"en": "Retry", "de": "Wiederholen"},
    "top_performance_metrics": {"en": "Top Performance Metrics", "de": "Top-Leistungskennzahlen"},
    "carbon_emissions": {"en": "Carbon Emissions", "de": "CO2-Emissionen"},
    "survey_status": {"en": "Survey Status", "de": "Umfragestatus"},
    "system_alert_title": {"en": "System Alerts", "de": "Systemwarnungen"},
    "pending_alerts_suffix": {"en": "pending alerts", "de": "ausstehende Warnungen"},

    # Additional LoginView keys
    "login_failed": {"en": "Login failed. Please check your credentials.", "de": "Anmeldung fehlgeschlagen. Bitte überprüfen Sie Ihre Zugangsdaten."},
    "server_error": {"en": "Server error. Please try again later.", "de": "Serverfehler. Bitte versuchen Sie es später erneut."},
    "logging_in": {"en": "Logging in...", "de": "Anmelden..."},
    "login_button": {"en": "Login", "de": "Anmelden"},
    "copyright_sustainage": {"en": "© 2024 Sustainage. All rights reserved.", "de": "© 2024 Sustainage. Alle Rechte vorbehalten."},
    "username": {"en": "Username", "de": "Benutzername"},
    "password": {"en": "Password", "de": "Passwort"},

    # DE translations for common missing keys
    "all": {"en": "All", "de": "Alle"},
    "back": {"en": "Back", "de": "Zurück"},
    "btn_save": {"en": "Save", "de": "Speichern"},
    "btn_cancel": {"en": "Cancel", "de": "Abbrechen"},
    "btn_delete": {"en": "Delete", "de": "Löschen"},
    "btn_update": {"en": "Update", "de": "Aktualisieren"},
    "btn_create_report": {"en": "Create Report", "de": "Bericht erstellen"},
    "carbon": {"en": "Carbon", "de": "Kohlenstoff"},
    "energy": {"en": "Energy", "de": "Energie"},
    "waste": {"en": "Waste", "de": "Abfall"},
    "water": {"en": "Water", "de": "Wasser"},
    "biodiversity": {"en": "Biodiversity", "de": "Biodiversität"},
    "cbam_title": {"en": "Carbon Border Adjustment (CBAM)", "de": "CO2-Grenzausgleichsmechanismus (CBAM)"},
    "cbam_desc": {"en": "CBAM reporting and liability tracking.", "de": "CBAM-Berichterstattung und Haftungsverfolgung."},
    "description": {"en": "Description", "de": "Beschreibung"},
    "date": {"en": "Date", "de": "Datum"},
    "year": {"en": "Year", "de": "Jahr"},
    "month": {"en": "Month", "de": "Monat"},
    "amount": {"en": "Amount", "de": "Menge"},
    "unit": {"en": "Unit", "de": "Einheit"},
    "total": {"en": "Total", "de": "Gesamt"},
    "status": {"en": "Status", "de": "Status"},
    "actions": {"en": "Actions", "de": "Aktionen"},
    "edit": {"en": "Edit", "de": "Bearbeiten"},
    "delete": {"en": "Delete", "de": "Löschen"},
    "save": {"en": "Save", "de": "Speichern"},
    "cancel": {"en": "Cancel", "de": "Abbrechen"},
    "confirm": {"en": "Confirm", "de": "Bestätigen"},
    "close": {"en": "Close", "de": "Schließen"},
    "logout": {"en": "Logout", "de": "Abmelden"},
    "login": {"en": "Login", "de": "Anmelden"},
    "register": {"en": "Register", "de": "Registrieren"},
    "profile": {"en": "Profile", "de": "Profil"},
    "settings": {"en": "Settings", "de": "Einstellungen"},
    "dashboard": {"en": "Dashboard", "de": "Dashboard"},
    "home": {"en": "Home", "de": "Startseite"},
    "reports": {"en": "Reports", "de": "Berichte"},
    "analytics": {"en": "Analytics", "de": "Analysen"},
    "users": {"en": "Users", "de": "Benutzer"},
    "companies": {"en": "Companies", "de": "Unternehmen"},
    "help": {"en": "Help", "de": "Hilfe"},
    "contact": {"en": "Contact", "de": "Kontakt"},
    "email": {"en": "Email", "de": "E-Mail"},
    "password": {"en": "Password", "de": "Passwort"},
    "username": {"en": "Username", "de": "Benutzername"},
    "name": {"en": "Name", "de": "Name"},
    "surname": {"en": "Surname", "de": "Nachname"},
    "role": {"en": "Role", "de": "Rolle"},
    "admin": {"en": "Admin", "de": "Administrator"},
    "user": {"en": "User", "de": "Benutzer"},
    "viewer": {"en": "Viewer", "de": "Betrachter"},
    "manager": {"en": "Manager", "de": "Manager"},
    "success": {"en": "Success", "de": "Erfolg"},
    "error": {"en": "Error", "de": "Fehler"},
    "warning": {"en": "Warning", "de": "Warnung"},
    "info": {"en": "Info", "de": "Info"},
    "confirm_delete": {"en": "Are you sure you want to delete this?", "de": "Sind Sie sicher, dass Sie dies löschen möchten?"},
    "no_data": {"en": "No data available", "de": "Keine Daten verfügbar"},
    "search": {"en": "Search", "de": "Suchen"},
    "filter": {"en": "Filter", "de": "Filtern"},
    "sort": {"en": "Sort", "de": "Sortieren"},
    "add_new": {"en": "Add New", "de": "Hinzufügen"},
    "view": {"en": "View", "de": "Ansehen"},
    "download": {"en": "Download", "de": "Herunterladen"},
    "upload": {"en": "Upload", "de": "Hochladen"},
    "import": {"en": "Import", "de": "Importieren"},
    "export": {"en": "Export", "de": "Exportieren"},
    "print": {"en": "Print", "de": "Drucken"}
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
        
        dictionary[key]["en"] = val["en"]
        dictionary[key]["de"] = val["de"]
        if "tr" in val:
            dictionary[key]["tr"] = val["tr"]

    save_json(DICT_PATH, dictionary)
    print("Translation dictionary updated.")

if __name__ == "__main__":
    populate()
