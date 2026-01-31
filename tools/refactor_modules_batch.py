import os
import json

# Configuration
LOCALES_DIR = r"c:\SDG\locales"
TEMPLATES_DIR = r"c:\SDG\server\templates"

# New keys to add
new_keys = {
    # Common Badges & Alerts
    "module_active_badge": {"tr": "Modül Aktif", "en": "Module Active"},
    "module_passive_badge": {"tr": "Modül Pasif", "en": "Module Passive"},
    "module_ready_title": {"tr": "Modül Hazır", "en": "Module Ready"},
    "module_ready_desc": {"tr": "Modül başarıyla yüklendi. Veri girişine başlayabilirsiniz.", "en": "Module loaded successfully. You can start data entry."},
    "module_failed_title": {"tr": "Modül Yüklenemedi!", "en": "Module Load Failed!"},
    "module_failed_desc": {"tr": "Modül şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.", "en": "Module is currently unavailable. Please contact system administrator."},
    "data_entry_btn": {"tr": "Veri Girişi", "en": "Data Entry"},
    "data_not_found_title": {"tr": "Veri Bulunamadı", "en": "Data Not Found"},
    "data_not_found_desc": {"tr": "Veriler henüz yüklenmemiş veya veritabanına erişilemiyor.", "en": "Data not loaded yet or database inaccessible."},
    
    # Economic
    "eco_desc": {"tr": "Doğrudan ekonomik değer üretimi ve dağıtımı (GRI 201).", "en": "Direct economic value generated and distributed (GRI 201)."},
    "eco_revenue": {"tr": "Gelir", "en": "Revenue"},
    "eco_climate_risk": {"tr": "İklim Riskleri", "en": "Climate Risks"},
    "eco_financial_impact": {"tr": "Finansal Etki", "en": "Financial Impact"},
    "eco_tax_mgmt": {"tr": "Vergi Yönetimi", "en": "Tax Management"},
    "eco_tax_paid": {"tr": "Toplam Ödenen Vergi", "en": "Total Tax Paid"},

    # TNFD
    "tnfd_page_title": {"tr": "TNFD Tavsiyeleri", "en": "TNFD Recommendations"},
    "tnfd_list_title": {"tr": "TNFD Tavsiyeleri Listesi", "en": "TNFD Recommendations List"},
    "tnfd_col_rec": {"tr": "Tavsiye", "en": "Recommendation"},

    # TCFD
    "tcfd_page_title": {"tr": "TCFD Tavsiyeleri", "en": "TCFD Recommendations"},
    "tcfd_list_title": {"tr": "TCFD Tavsiyeleri Listesi", "en": "TCFD Recommendations List"},

    # ISSB
    "issb_page_title": {"tr": "ISSB Standartları", "en": "ISSB Standards"},
    "issb_desc": {"tr": "IFRS S1 ve S2 sürdürülebilirlik ve iklim standartları (SASB Standartlarını içerir).", "en": "IFRS S1 and S2 sustainability and climate standards (includes SASB Standards)."},
    "issb_list_title": {"tr": "SASB / IFRS Sektörel Standartları", "en": "SASB / IFRS Sector Standards"},
    "issb_col_sector": {"tr": "Sektör", "en": "Sector"},
    "issb_col_topic": {"tr": "Konu", "en": "Topic"},
    "issb_col_metric": {"tr": "Metrik Kodu", "en": "Metric Code"},

    # Supply Chain
    "sc_desc": {"tr": "Tedarikçi denetimleri, sosyal ve çevresel kriterler.", "en": "Supplier audits, social and environmental criteria."},
    
    # CDP
    "cdp_page_title": {"tr": "CDP Raporlama", "en": "CDP Reporting"},
    "cdp_desc": {"tr": "Carbon Disclosure Project (CDP) soru setleri ve raporlama.", "en": "Carbon Disclosure Project (CDP) questionnaires and reporting."},

    # Biodiversity
    "bio_page_title": {"tr": "Biyoçeşitlilik", "en": "Biodiversity"},
    "gov_manager_active": {"tr": "Yönetişim Yöneticisi Aktif", "en": "Governance Manager Active"},
}

replacements = {
    "economic.html": [
        ('{{ _(\'economic_title\') }} - SDG Platform', "{{ _('economic_title') }} - SDG"),
        ('{{ _(\'economic_title\') }} (Economic Value)', "{{ _('economic_title') }}"),
        ("'Modül Aktif' if manager_available else 'Modül Pasif'", "_('module_active_badge') if manager_available else _('module_passive_badge')"),
        ('Doğrudan ekonomik değer üretimi ve dağıtımı (GRI 201).', "{{ _('eco_desc') }}"),
        ('Toplam {{ _(\'eco_revenue\') }}', "{{ _('eco_revenue') }}"), # Fixing potential double wrap or just replace logic
        ('İklim Riskleri', "{{ _('eco_climate_risk') }}"),
        ('Finansal Etki', "{{ _('eco_financial_impact') }}"),
        ('Vergi Yönetimi', "{{ _('eco_tax_mgmt') }}"),
        ('Toplam Ödenen Vergi', "{{ _('eco_tax_paid') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_failed_title') }}"),
        ('{{ _(\'economic_title\') }} modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_failed_desc') }}"),
        ('>Veri Girişi<', ">{{ _('data_entry_btn') }}<"),
    ],
    "tnfd.html": [
        ('TNFD Tavsiyeleri - SDG Platform', "{{ _('tnfd_page_title') }} - SDG"),
        ('TNFD Tavsiyeleri (Nature-related Financial Disclosures)', "{{ _('tnfd_page_title') }}"),
        ("'Modül Aktif' if manager_available else 'Modül Pasif'", "_('module_active_badge') if manager_available else _('module_passive_badge')"),
        ('Doğa ile ilgili finansal beyanlar için çerçeve.', "{{ _('tnfd_desc') }}"),
        ('TNFD Tavsiyeleri Listesi', "{{ _('tnfd_list_title') }}"),
        ('<th>Kod</th>', "<th>{{ _('gri_col_code') }}</th>"),
        ('<th>Kategori</th>', "<th>{{ _('gri_col_category') }}</th>"),
        ('<th>Tavsiye</th>', "<th>{{ _('tnfd_col_rec') }}</th>"),
        ('<th>Açıklama</th>', "<th>{{ _('sdg_col_desc') }}</th>"),
        ('Veri Bulunamadı', "{{ _('data_not_found_title') }}"),
        ('TNFD tavsiyeleri henüz yüklenmemiş veya veritabanına erişilemiyor.', "{{ _('data_not_found_desc') }}"),
    ],
    "tcfd.html": [
        ('TCFD Tavsiyeleri - SDG Platform', "{{ _('tcfd_page_title') }} - SDG"),
        ('TCFD Tavsiyeleri (Climate-related Financial Disclosures)', "{{ _('tcfd_page_title') }}"),
        ("'Modül Aktif' if manager_available else 'Modül Pasif'", "_('module_active_badge') if manager_available else _('module_passive_badge')"),
        ('İklim ile ilgili finansal beyanlar için çerçeve.', "{{ _('tcfd_desc') }}"),
        ('TCFD Tavsiyeleri Listesi', "{{ _('tcfd_list_title') }}"),
        ('<th>Kod</th>', "<th>{{ _('gri_col_code') }}</th>"),
        ('<th>Kategori</th>', "<th>{{ _('gri_col_category') }}</th>"),
        ('<th>Tavsiye</th>', "<th>{{ _('tnfd_col_rec') }}</th>"),
        ('<th>Açıklama</th>', "<th>{{ _('sdg_col_desc') }}</th>"),
        ('Veri Bulunamadı', "{{ _('data_not_found_title') }}"),
        ('TCFD tavsiyeleri henüz yüklenmemiş veya veritabanına erişilemiyor.', "{{ _('data_not_found_desc') }}"),
    ],
    "issb.html": [
        ('ISSB Standartları - SDG Platform', "{{ _('issb_page_title') }} - SDG"),
        ('ISSB Standartları (ISSB Standards)', "{{ _('issb_page_title') }}"),
        ("'Modül Aktif' if manager_available else 'Modül Pasif'", "_('module_active_badge') if manager_available else _('module_passive_badge')"),
        ('IFRS S1 ve S2 sürdürülebilirlik ve iklim standartları (SASB Standartlarını içerir).', "{{ _('issb_desc') }}"),
        ('SASB / IFRS Sektörel Standartları', "{{ _('issb_list_title') }}"),
        ('<th>Sektör</th>', "<th>{{ _('issb_col_sector') }}</th>"),
        ('<th>Konu</th>', "<th>{{ _('issb_col_topic') }}</th>"),
        ('<th>Metrik Kodu</th>', "<th>{{ _('issb_col_metric') }}</th>"),
        ('<th>Kategori</th>', "<th>{{ _('gri_col_category') }}</th>"),
        ('Modül Hazır', "{{ _('module_ready_title') }}"),
        ('ISSB modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.', "{{ _('module_ready_desc') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_failed_title') }}"),
        ('ISSB modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_failed_desc') }}"),
    ],
    "supply_chain.html": [
        ('{{ _(\'supply_chain_title\') }} - SDG Platform', "{{ _('supply_chain_title') }} - SDG"),
        ('{{ _(\'supply_chain_title\') }} (Supply Chain)', "{{ _('supply_chain_title') }}"),
        ("'Modül Aktif' if manager_available else 'Modül Pasif'", "_('module_active_badge') if manager_available else _('module_passive_badge')"),
        ('Tedarikçi denetimleri, sosyal ve çevresel kriterler.', "{{ _('sc_desc') }}"),
        ('Modül Hazır', "{{ _('module_ready_title') }}"),
        ('Tedarik zinciri modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.', "{{ _('module_ready_desc') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_failed_title') }}"),
        ('{{ _(\'supply_chain_title\') }} modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_failed_desc') }}"),
    ],
    "cdp.html": [
        ('CDP Raporlama - SDG Platform', "{{ _('cdp_page_title') }} - SDG"),
        ('CDP Raporlama (CDP Reporting)', "{{ _('cdp_page_title') }}"),
        ("'Modül Aktif' if manager_available else 'Modül Pasif'", "_('module_active_badge') if manager_available else _('module_passive_badge')"),
        ('Carbon Disclosure Project (CDP) soru setleri ve raporlama.', "{{ _('cdp_desc') }}"),
        ('Modül Hazır', "{{ _('module_ready_title') }}"),
        ('CDP modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.', "{{ _('module_ready_desc') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_failed_title') }}"),
        ('CDP modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_failed_desc') }}"),
    ],
    "biodiversity.html": [
        ("{{ '{{ _('module_active') }}' if manager_available else '{{ _('module_passive') }}' }}", "{{ _('module_active') if manager_available else _('module_passive') }}"),
    ],
    "carbon.html": [
        ("Karbon Yönetimi - SDG Platform", "{{ _('carbon_title') }} - SDG Platform"),
        ("{{ '{{ _('module_active') }}' if manager_available else '{{ _('module_passive') }}' }}", "{{ _('module_active') if manager_available else _('module_passive') }}"),
    ],
    "social.html": [
        ("Sosyal Modülü - SDG", "{{ _('social_title') }} - SDG"),
    ],
    "governance.html": [
        ("{{ _('gov_title') }} Yöneticisi Aktif", "{{ _('gov_manager_active') }}"),
    ]
}

def update_locales():
    for lang in ['tr', 'en']:
        file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = False
            for key, values in new_keys.items():
                if key not in data:
                    data[key] = values[lang]
                    updated = True
            
            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Updated {file_path}")
            else:
                print(f"No changes for {file_path}")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")

def refactor_templates():
    for filename, rules in replacements.items():
        file_path = os.path.join(TEMPLATES_DIR, filename)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for old, new in rules:
                content = content.replace(old, new)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Refactored {filename}")
            else:
                print(f"No changes for {filename}")
        except Exception as e:
            print(f"Error refactoring {filename}: {e}")

if __name__ == "__main__":
    update_locales()
    refactor_templates()
