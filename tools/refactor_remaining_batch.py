import json
import os

# Paths
BASE_DIR = r"c:\SDG"
TR_PATH = os.path.join(BASE_DIR, "locales", "tr.json")
EN_PATH = os.path.join(BASE_DIR, "locales", "en.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "server", "templates")

# Files to refactor
FILES = {
    "energy.html": os.path.join(TEMPLATES_DIR, "energy.html"),
    "waste.html": os.path.join(TEMPLATES_DIR, "waste.html"),
    "water.html": os.path.join(TEMPLATES_DIR, "water.html"),
    "company_edit.html": os.path.join(TEMPLATES_DIR, "company_edit.html"),
    "user_edit.html": os.path.join(TEMPLATES_DIR, "user_edit.html"),
    "report_edit.html": os.path.join(TEMPLATES_DIR, "report_edit.html"),
    "help.html": os.path.join(TEMPLATES_DIR, "help.html")
}

# New Keys Definition
new_keys = {
    # Energy
    "energy_title": {"tr": "Enerji Yönetimi (Energy Management)", "en": "Energy Management"},
    "energy_desc": {"tr": "Enerji tüketimi takibi, verimlilik projeleri ve yenilenebilir enerji yönetimi.", "en": "Energy consumption tracking, efficiency projects and renewable energy management."},
    "energy_consumption_title": {"tr": "Tüketim Takibi", "en": "Consumption Tracking"},
    "energy_consumption_desc": {"tr": "Elektrik, Doğalgaz ve diğer yakıt tüketimlerini izleyin.", "en": "Track Electricity, Natural Gas and other fuel consumption."},
    "btn_consumption_data": {"tr": "Tüketim Verileri", "en": "Consumption Data"},
    "energy_renewable_title": {"tr": "Yenilenebilir Enerji", "en": "Renewable Energy"},
    "energy_renewable_desc": {"tr": "Yenilenebilir enerji kaynakları ve üretim verileri.", "en": "Renewable energy sources and production data."},
    "btn_production_data": {"tr": "Üretim Verileri", "en": "Production Data"},
    "module_energy_unavailable": {"tr": "Enerji Yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.", "en": "Energy Management module is currently unavailable. Please contact system administrator."},

    # Waste
    "waste_title": {"tr": "Atık Yönetimi (Waste Management)", "en": "Waste Management"},
    "waste_desc": {"tr": "Atık türleri, miktarları ve geri dönüşüm süreçlerinin takibi.", "en": "Tracking of waste types, amounts and recycling processes."},
    "waste_module_ready": {"tr": "Modül Hazır", "en": "Module Ready"},
    "waste_ready_desc": {"tr": "Atık yönetimi modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.", "en": "Waste management module loaded successfully. You can start data entry."},
    "btn_add_waste_data": {"tr": "Yeni Atık Verisi Ekle", "en": "Add New Waste Data"},
    "module_waste_unavailable": {"tr": "Atık Yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.", "en": "Waste Management module is currently unavailable. Please contact system administrator."},

    # Water
    "water_title": {"tr": "Su Yönetimi (Water Management)", "en": "Water Management"},
    "water_desc": {"tr": "Su tüketimi, atık su deşarjı ve su ayak izi takibi.", "en": "Water consumption, wastewater discharge and water footprint tracking."},
    "water_ready_desc": {"tr": "Su yönetimi modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.", "en": "Water management module loaded successfully. You can start data entry."},
    "btn_add_water_data": {"tr": "Yeni Su Tüketimi Verisi Ekle", "en": "Add New Water Consumption Data"},
    "module_water_unavailable": {"tr": "Su Yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.", "en": "Water Management module is currently unavailable. Please contact system administrator."},

    # Company Edit
    "company_edit_title": {"tr": "Şirket Düzenle", "en": "Edit Company"},
    "company_new_title": {"tr": "Yeni Şirket", "en": "New Company"},
    "company_add_title": {"tr": "Yeni Şirket Ekle", "en": "Add New Company"},
    "lbl_company_name": {"tr": "Şirket Adı", "en": "Company Name"},
    "lbl_sector": {"tr": "Sektör", "en": "Sector"},
    "lbl_country": {"tr": "Ülke", "en": "Country"},
    "lbl_company_active": {"tr": "Şirket Aktif", "en": "Company Active"},
    "btn_save": {"tr": "Kaydet", "en": "Save"},
    "btn_back": {"tr": "Geri Dön", "en": "Go Back"},

    # User Edit
    "user_edit_title": {"tr": "Kullanıcı Düzenle", "en": "Edit User"},
    "user_new_title": {"tr": "Yeni Kullanıcı", "en": "New User"},
    "lbl_username": {"tr": "Kullanıcı Adı", "en": "Username"},
    "lbl_email": {"tr": "E-posta", "en": "Email"},
    "lbl_fullname": {"tr": "Ad Soyad", "en": "Full Name"},
    "lbl_role": {"tr": "Rol", "en": "Role"},
    "lbl_password": {"tr": "Parola", "en": "Password"},
    "lbl_password_hint": {"tr": "(Boş bırakılırsa değişmez)", "en": "(Leave blank to keep unchanged)"},
    "lbl_department": {"tr": "Departman", "en": "Department"},
    "lbl_user_active": {"tr": "Kullanıcı Aktif", "en": "User Active"},

    # Report Edit
    "report_add_title": {"tr": "Yeni Rapor Ekle", "en": "Add New Report"},
    "report_edit_title": {"tr": "Rapor Ekle", "en": "Add Report"},
    "lbl_report_name": {"tr": "Rapor Adı", "en": "Report Name"},
    "lbl_module": {"tr": "Modül", "en": "Module"},
    "lbl_report_type": {"tr": "Rapor Türü", "en": "Report Type"},
    "lbl_reporting_period": {"tr": "Raporlama Dönemi", "en": "Reporting Period"},
    "lbl_description": {"tr": "Açıklama", "en": "Description"},
    "lbl_report_file": {"tr": "Rapor Dosyası", "en": "Report File"},
    "help_report_file": {"tr": "Yüklemek istediğiniz rapor dosyasını seçin.", "en": "Select the report file you want to upload."},
    "opt_general": {"tr": "Genel", "en": "General"},
    "opt_carbon": {"tr": "Karbon", "en": "Carbon"},
    "opt_energy": {"tr": "Enerji", "en": "Energy"},
    "opt_water": {"tr": "Su", "en": "Water"},
    "opt_waste": {"tr": "Atık", "en": "Waste"},
    "opt_social": {"tr": "Sosyal", "en": "Social"},
    "opt_governance": {"tr": "Yönetişim", "en": "Governance"},
    "opt_other": {"tr": "Diğer", "en": "Other"},

    # Help
    "help_center_title": {"tr": "Yardım Merkezi", "en": "Help Center"},
    "help_q1": {"tr": "Nasıl yeni kullanıcı ekleyebilirim?", "en": "How can I add a new user?"},
    "help_a1": {"tr": "Yeni kullanıcı eklemek için <strong>Kullanıcı Yönetimi</strong> sayfasına gidin ve sağ üst köşedeki \"Yeni Kullanıcı\" butonuna tıklayın. Gerekli bilgileri doldurduktan sonra \"Kaydet\" butonuna basarak işlemi tamamlayabilirsiniz.", "en": "To add a new user, go to the <strong>User Management</strong> page and click the \"New User\" button in the top right corner. After filling in the required information, you can complete the process by clicking the \"Save\" button."},
    "help_q2": {"tr": "Raporları nasıl dışa aktarabilirim?", "en": "How can I export reports?"},
    "help_a2": {"tr": "<strong>Raporlar</strong> sayfasında, dışa aktarmak istediğiniz raporun yanındaki \"İndir\" ikonuna tıklayarak raporu PDF veya Excel formatında indirebilirsiniz.", "en": "On the <strong>Reports</strong> page, you can download the report in PDF or Excel format by clicking the \"Download\" icon next to the report you want to export."},
    "help_q3": {"tr": "Şifremi unuttum, ne yapmalıyım?", "en": "I forgot my password, what should I do?"},
    "help_a3": {"tr": "Şifrenizi sıfırlamak için giriş ekranındaki \"Şifremi Unuttum\" bağlantısını kullanabilir veya sistem yöneticinizle iletişime geçebilirsiniz. Yönetici hesabınız varsa, Kullanıcı Yönetimi sayfasından şifrenizi güncelleyebilirsiniz.", "en": "You can use the \"Forgot Password\" link on the login screen to reset your password or contact your system administrator. If you have an administrator account, you can update your password from the User Management page."},
    "help_q4": {"tr": "Veri girişi nasıl yapılır?", "en": "How to enter data?"},
    "help_a4": {"tr": "<strong>Veri Yönetimi</strong> sayfasından Karbon, Enerji, Su veya Atık sekmelerinden ilgili kategoriyi seçip \"Yeni Veri Girişi\" butonuna tıklayarak verilerinizi sisteme girebilirsiniz.", "en": "You can enter your data into the system by selecting the relevant category from the Carbon, Energy, Water or Waste tabs on the <strong>Data Management</strong> page and clicking the \"New Data Entry\" button."},
    "support_title": {"tr": "Destek Hattı", "en": "Support Line"},
    "support_desc": {"tr": "Daha fazla yardıma mı ihtiyacınız var? Destek ekibimizle iletişime geçin.", "en": "Need more help? Contact our support team."},
    "btn_create_ticket": {"tr": "Destek Talebi Oluştur", "en": "Create Support Ticket"},
    "docs_title": {"tr": "Dokümantasyon", "en": "Documentation"},
    "docs_desc": {"tr": "Detaylı kullanım kılavuzu ve teknik dokümanlar için kütüphanemizi ziyaret edin.", "en": "Visit our library for detailed user manuals and technical documents."},
    "btn_view_guide": {"tr": "Kılavuzu İncele", "en": "View Guide"}
}

# Replacement Rules (File specific)
replacements = {
    "energy.html": [
        ('Enerji Yönetimi (Energy Management)', "{{ _('energy_title') }}"),
        ('Modül Aktif', "{{ _('module_active') }}"),
        ('Modül Pasif', "{{ _('module_passive') }}"),
        ('Enerji tüketimi takibi, verimlilik projeleri ve yenilenebilir enerji yönetimi.', "{{ _('energy_desc') }}"),
        ('Tüketim Takibi', "{{ _('energy_consumption_title') }}"),
        ('Elektrik, Doğalgaz ve diğer yakıt tüketimlerini izleyin.', "{{ _('energy_consumption_desc') }}"),
        ('Tüketim Verileri', "{{ _('btn_consumption_data') }}"),
        ('Yenilenebilir Enerji', "{{ _('energy_renewable_title') }}"),
        ('Yenilenebilir enerji kaynakları ve üretim verileri.', "{{ _('energy_renewable_desc') }}"),
        ('Üretim Verileri', "{{ _('btn_production_data') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_load_error') }}"),
        ('Enerji Yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_energy_unavailable') }}"),
        ('{% block title %}Enerji Yönetimi - SDG Platform{% endblock %}', '{% block title %}{{ _(\'energy_title\') }} - SDG Platform{% endblock %}')
    ],
    "waste.html": [
        ('Atık Yönetimi (Waste Management)', "{{ _('waste_title') }}"),
        ('Modül Aktif', "{{ _('module_active') }}"),
        ('Modül Pasif', "{{ _('module_passive') }}"),
        ('Atık türleri, miktarları ve geri dönüşüm süreçlerinin takibi.', "{{ _('waste_desc') }}"),
        ('Modül Hazır', "{{ _('waste_module_ready') }}"),
        ('Atık yönetimi modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.', "{{ _('waste_ready_desc') }}"),
        ('Yeni Atık Verisi Ekle', "{{ _('btn_add_waste_data') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_load_error') }}"),
        ('Atık Yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_waste_unavailable') }}"),
        ('{% block title %}Atık Yönetimi - SDG Platform{% endblock %}', '{% block title %}{{ _(\'waste_title\') }} - SDG Platform{% endblock %}')
    ],
    "water.html": [
        ('Su Yönetimi (Water Management)', "{{ _('water_title') }}"),
        ('Modül Aktif', "{{ _('module_active') }}"),
        ('Modül Pasif', "{{ _('module_passive') }}"),
        ('Su tüketimi, atık su deşarjı ve su ayak izi takibi.', "{{ _('water_desc') }}"),
        ('Modül Hazır', "{{ _('waste_module_ready') }}"),
        ('Su yönetimi modülü başarıyla yüklendi. Veri girişine başlayabilirsiniz.', "{{ _('water_ready_desc') }}"),
        ('Yeni Su Tüketimi Verisi Ekle', "{{ _('btn_add_water_data') }}"),
        ('Modül Yüklenemedi!', "{{ _('module_load_error') }}"),
        ('Su Yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.', "{{ _('module_water_unavailable') }}"),
        ('{% block title %}Su Yönetimi - SDG Platform{% endblock %}', '{% block title %}{{ _(\'water_title\') }} - SDG Platform{% endblock %}')
    ],
    "company_edit.html": [
        ("'Şirket Düzenle' if company else 'Yeni Şirket'", "'{{ _('company_edit_title') }}' if company else '{{ _('company_new_title') }}'"),
        ("'Şirket Düzenle' if company else 'Yeni Şirket Ekle'", "'{{ _('company_edit_title') }}' if company else '{{ _('company_add_title') }}'"),
        ('Geri Dön', "{{ _('btn_back') }}"),
        ('Şirket Adı', "{{ _('lbl_company_name') }}"),
        ('Sektör', "{{ _('lbl_sector') }}"),
        ('Ülke', "{{ _('lbl_country') }}"),
        ('Şirket Aktif', "{{ _('lbl_company_active') }}"),
        ('Kaydet', "{{ _('btn_save') }}")
    ],
    "user_edit.html": [
        ("'Kullanıcı Düzenle' if user else 'Yeni Kullanıcı'", "'{{ _('user_edit_title') }}' if user else '{{ _('user_new_title') }}'"),
        ('Geri Dön', "{{ _('btn_back') }}"),
        ('Kullanıcı Adı', "{{ _('lbl_username') }}"),
        ('E-posta', "{{ _('lbl_email') }}"),
        ('Ad Soyad', "{{ _('lbl_fullname') }}"),
        ('Rol', "{{ _('lbl_role') }}"),
        ('Parola', "{{ _('lbl_password') }}"),
        ("'(Boş bırakılırsa değişmez)'", "'{{ _('lbl_password_hint') }}'"),
        ('Departman', "{{ _('lbl_department') }}"),
        ('Kullanıcı Aktif', "{{ _('lbl_user_active') }}"),
        ('Kaydet', "{{ _('btn_save') }}")
    ],
    "report_edit.html": [
        ('Yeni Rapor Ekle', "{{ _('report_add_title') }}"),
        ('Rapor Ekle', "{{ _('report_edit_title') }}"),
        ('Geri Dön', "{{ _('btn_back') }}"),
        ('Rapor Adı', "{{ _('lbl_report_name') }}"),
        ('Modül', "{{ _('lbl_module') }}"),
        ('Rapor Türü', "{{ _('lbl_report_type') }}"),
        ('Raporlama Dönemi', "{{ _('lbl_reporting_period') }}"),
        ('Açıklama', "{{ _('lbl_description') }}"),
        ('Rapor Dosyası', "{{ _('lbl_report_file') }}"),
        ('Yüklemek istediğiniz rapor dosyasını seçin.', "{{ _('help_report_file') }}"),
        ('Kaydet', "{{ _('btn_save') }}"),
        ('>Genel<', ">{{ _('opt_general') }}<"),
        ('>Karbon<', ">{{ _('opt_carbon') }}<"),
        ('>Enerji<', ">{{ _('opt_energy') }}<"),
        ('>Su<', ">{{ _('opt_water') }}<"),
        ('>Atık<', ">{{ _('opt_waste') }}<"),
        ('>Sosyal<', ">{{ _('opt_social') }}<"),
        ('>Yönetişim<', ">{{ _('opt_governance') }}<"),
        ('>Diğer<', ">{{ _('opt_other') }}<")
    ],
    "help.html": [
        ('Yardım Merkezi', "{{ _('help_center_title') }}"),
        ('Nasıl yeni kullanıcı ekleyebilirim?', "{{ _('help_q1') }}"),
        ('Yeni kullanıcı eklemek için <strong>Kullanıcı Yönetimi</strong> sayfasına gidin ve sağ üst köşedeki "Yeni Kullanıcı" butonuna tıklayın. Gerekli bilgileri doldurduktan sonra "Kaydet" butonuna basarak işlemi tamamlayabilirsiniz.', "{{ _('help_a1') }}"),
        ('Raporları nasıl dışa aktarabilirim?', "{{ _('help_q2') }}"),
        ('<strong>Raporlar</strong> sayfasında, dışa aktarmak istediğiniz raporun yanındaki "İndir" ikonuna tıklayarak raporu PDF veya Excel formatında indirebilirsiniz.', "{{ _('help_a2') }}"),
        ('Şifremi unuttum, ne yapmalıyım?', "{{ _('help_q3') }}"),
        ('Şifrenizi sıfırlamak için giriş ekranındaki "Şifremi Unuttum" bağlantısını kullanabilir veya sistem yöneticinizle iletişime geçebilirsiniz. Yönetici hesabınız varsa, Kullanıcı Yönetimi sayfasından şifrenizi güncelleyebilirsiniz.', "{{ _('help_a3') }}"),
        ('Veri girişi nasıl yapılır?', "{{ _('help_q4') }}"),
        ('<strong>Veri Yönetimi</strong> sayfasından Karbon, Enerji, Su veya Atık sekmelerinden ilgili kategoriyi seçip "Yeni Veri Girişi" butonuna tıklayarak verilerinizi sisteme girebilirsiniz.', "{{ _('help_a4') }}"),
        ('Destek Hattı', "{{ _('support_title') }}"),
        ('Daha fazla yardıma mı ihtiyacınız var? Destek ekibimizle iletişime geçin.', "{{ _('support_desc') }}"),
        ('Destek Talebi Oluştur', "{{ _('btn_create_ticket') }}"),
        ('Dokümantasyon', "{{ _('docs_title') }}"),
        ('Detaylı kullanım kılavuzu ve teknik dokümanlar için kütüphanemizi ziyaret edin.', "{{ _('docs_desc') }}"),
        ('Kılavuzu İncele', "{{ _('btn_view_guide') }}")
    ]
}

def update_json(path, lang_key):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    updated = False
    for key, val in new_keys.items():
        if key not in data:
            data[key] = val[lang_key]
            updated = True
    
    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
        print(f"Updated {path}")
    else:
        print(f"No changes for {path}")

def update_templates():
    for filename, rules in replacements.items():
        path = FILES[filename]
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        for old, new in rules:
            new_content = new_content.replace(old, new)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"No changes for {filename}")

if __name__ == "__main__":
    update_json(TR_PATH, 'tr')
    update_json(EN_PATH, 'en')
    update_templates()
