import paramiko
import re
import sys

def fix_module_translations():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    translations = {
        # Common
        'common.back': 'Geri',
        'common.save': 'Kaydet',
        'common_delete': 'Sil',
        'common_edit': 'Düzenle',
        'common_export': 'Dışa Aktar',
        'btn_back': 'Geri',
        'btn_save': 'Kaydet',
        'btn_return_home': 'Ana Sayfaya Dön',
        'btn_create_ticket': 'Destek Talebi Oluştur',
        'btn_new_data_entry': 'Yeni Veri Girişi',
        'btn_view_guide': 'Kılavuzu Görüntüle',
        'btn_add_data': 'Veri Ekle',
        'btn_production_data': 'Üretim Verileri',
        'btn_view_report': 'Raporu Görüntüle',
        'btn_calculate': 'Hesapla',
        'no_data': 'Veri Yok',
        
        # SDG / Data Entry
        'sdg.data_entry': 'Veri Girişi',
        'sdg_manager_active': 'SDG Modülü Aktif',
        'sdg_goals_list': 'Sürdürülebilir Kalkınma Amaçları',
        'sdg_col_no': 'No',
        'sdg_col_title': 'Başlık',
        'sdg_col_desc': 'Açıklama',
        'sdg_col_goal': 'Hedef',
        
        # Dashboard & Modules Titles/Headers
        'title_dashboard': 'Kontrol Paneli',
        'biodiversity_header': 'Biyoçeşitlilik Yönetimi',
        'biodiversity_page_title': 'Biyoçeşitlilik - SDG Platform',
        'biodiversity_lead': 'Biyoçeşitlilik üzerindeki etkilerinizi izleyin ve yönetin.',
        'cdp_page_title': 'CDP Raporlama',
        'companies_header': 'Şirketler',
        'companies_page_title': 'Şirketler',
        'company_edit_title': 'Şirket Düzenle',
        'data_management_title': 'Veri Yönetimi',
        'docs_title': 'Dokümantasyon',
        'docs_desc': 'Kullanım kılavuzları ve API dokümantasyonu.',
        'gov_title': 'Yönetişim',
        'help_center_title': 'Yardım Merkezi',
        'issb_list_title': 'ISSB Standartları',
        'issb_page_title': 'ISSB Raporlama',
        'report_add_title': 'Yeni Rapor Ekle',
        'report_edit_title': 'Rapor Düzenle',
        'support_title': 'Destek',
        'support_desc': 'Teknik destek ve yardım talepleri.',
        'tcfd_list_title': 'TCFD Tavsiyeleri',
        'tcfd_page_title': 'TCFD Raporlama',
        'tnfd_list_title': 'TNFD Tavsiyeleri',
        'tnfd_page_title': 'TNFD Raporlama',
        'user_edit_title': 'Kullanıcı Düzenle',
        'users_header': 'Kullanıcılar',
        'users_page_title': 'Kullanıcılar',
        
        # Descriptions
        'bio_ecosystem_services': 'Ekosistem Hizmetleri',
        'bio_habitat_areas': 'Habitat Alanları',
        'bio_habitat_desc': 'Korunan veya restore edilen habitat alanları.',
        'bio_impact_management': 'Etki Yönetimi',
        'bio_species_desc': 'IUCN Kırmızı Listesi ve ulusal koruma listelerindeki türler.',
        'bio_species_protection': 'Tür Koruma',
        'eco_desc': 'Ekonomik performans göstergeleri.',
        'esrs_desc': 'Avrupa Sürdürülebilirlik Raporlama Standartları.',
        'iirc_desc': 'Entegre Raporlama Çerçevesi.',
        'tax_desc': 'Vergi stratejisi ve ödemeleri.',
        'sc_desc': 'Tedarik zinciri sürdürülebilirlik değerlendirmesi.',
        'support_desc': 'Teknik destek ve yardım talepleri.',
        
        # Table Columns
        'col_actions': 'İşlemler',
        'col_category': 'Kategori',
        'col_company_name': 'Şirket Adı',
        'col_consumption': 'Tüketim',
        'col_cost': 'Maliyet',
        'col_country': 'Ülke',
        'col_created_at': 'Oluşturulma Tarihi',
        'col_date': 'Tarih',
        'col_department': 'Departman',
        'col_full_name': 'Ad Soyad',
        'col_hazardous': 'Tehlikeli',
        'col_id': 'ID',
        'col_last_login': 'Son Giriş',
        'col_method': 'Yöntem',
        'col_quantity': 'Miktar',
        'col_role': 'Rol',
        'col_scope': 'Kapsam',
        'col_sector': 'Sektör',
        'col_status': 'Durum',
        'col_type': 'Tür',
        'col_unit': 'Birim',
        'col_username': 'Kullanıcı Adı',
        'col_year_month': 'Yıl/Ay',
        
        # Labels
        'lbl_company_name': 'Şirket Adı',
        'lbl_country': 'Ülke',
        'lbl_department': 'Departman',
        'lbl_description': 'Açıklama',
        'lbl_email': 'E-posta',
        'lbl_fullname': 'Ad Soyad',
        'lbl_module': 'Modül',
        'lbl_password': 'Şifre',
        'lbl_password_hint': '(Değiştirmek istemiyorsanız boş bırakın)',
        'lbl_report_file': 'Rapor Dosyası',
        'lbl_report_name': 'Rapor Adı',
        'lbl_report_type': 'Rapor Türü',
        'lbl_reporting_period': 'Raporlama Dönemi',
        'lbl_role': 'Rol',
        'lbl_sector': 'Sektör',
        'lbl_tax_number': 'Vergi No',
        'lbl_username': 'Kullanıcı Adı',
        'lbl_company_active': 'Şirket Aktif',
        'lbl_user_active': 'Kullanıcı Aktif',
        
        # Options / Values
        'opt_carbon': 'Karbon',
        'opt_energy': 'Enerji',
        'opt_water': 'Su',
        'opt_waste': 'Atık',
        'opt_social': 'Sosyal',
        'opt_governance': 'Yönetişim',
        'opt_general': 'Genel',
        'opt_other': 'Diğer',
        'status_active': 'Aktif',
        'status_passive': 'Pasif',
        'month_jan': 'Ocak',
        'month_feb': 'Şubat',
        'month_mar': 'Mart',
        'month_apr': 'Nisan',
        'month_may': 'Mayıs',
        'month_jun': 'Haziran',
        
        # Messages / Status
        'companies_no_records': 'Kayıtlı şirket bulunamadı.',
        'users_no_records': 'Kayıtlı kullanıcı bulunamadı.',
        'users_confirm_delete': 'Bu kullanıcıyı silmek istediğinize emin misiniz?',
        'companies_details_tooltip': 'Detayları Görüntüle',
        'module_active_badge': 'Modül Aktif',
        'module_preparing': 'Hazırlanıyor',
        'module_preparing_desc': 'Bu modül şu anda hazırlanma aşamasındadır.',
        'module_failed_title': 'Modül Yüklenemedi',
        'module_failed_desc': 'Modül yüklenirken bir hata oluştu.',
        'module_manager_error': 'Yönetici Hatası',
        'module_ready_title': 'Modül Hazır',
        'module_ready_desc': 'Modül kullanıma hazır.',
        'module_biodiversity_unavailable': 'Biyoçeşitlilik modülü şu anda kullanılamıyor.',
        'data_not_found_title': 'Veri Bulunamadı',
        'data_not_found_desc': 'Görüntülenecek veri bulunamadı.',
        
        # Dashboard & Charts
        'chart_emission_dist': 'Emisyon Dağılımı',
        'chart_emission_trend': 'Emisyon Trendi',
        'emission_tco2e': 'Emisyon (tCO2e)',
        'login_activity': 'Giriş Aktivitesi',
        'recent_activities': 'Son Aktiviteler',
        'quick_access_menu': 'Hızlı Erişim',
        'report_prepared_activity': 'Rapor Hazırlandı',
        'time_now': 'Şimdi',
        'time_2_hours_ago': '2 saat önce',
        
        # Specific Modules
        'eco_climate_risk': 'İklim Riski',
        'eco_financial_impact': 'Finansal Etki',
        'eco_revenue': 'Gelir',
        'eco_tax_mgmt': 'Vergi Yönetimi',
        'eco_tax_paid': 'Ödenen Vergi',
        'gov_board_members': 'Yönetim Kurulu Üyeleri',
        'gov_board_members_stat': 'YK Üye Sayısı',
        'gov_ethics_compliance': 'Etik & Uyum',
        'gov_manager_active': 'Yönetişim Modülü Aktif',
        'gov_training_hours': 'Eğitim Saatleri',
        'gri_col_category': 'Kategori',
        'gri_col_code': 'Kod',
        'gri_manager_active': 'GRI Modülü Aktif',
        'gri_standards_list': 'GRI Standartları',
        'issb_col_metric': 'Metrik',
        'issb_col_sector': 'Sektör',
        'issb_col_topic': 'Konu',
        'issb_list_title': 'ISSB Standartları',
        'social_employee_profile': 'Çalışan Profili',
        'social_incidents': 'Olaylar/Kazalar',
        'social_manager_active': 'Sosyal Modül Aktif',
        'social_ohs': 'İSG',
        'social_total_employees': 'Toplam Çalışan',
        'social_total_hours': 'Toplam Saat',
        'social_training': 'Eğitim',
        
        # Buttons from *_btn
        'companies_btn': 'Şirketler',
        'create_report_btn': 'Rapor Oluştur',
        'data_entry_btn': 'Veri Girişi',
        'help_btn': 'Yardım',
        'messages_btn': 'Mesajlar',
        'users_btn': 'Kullanıcılar',
        'companies_new_company': 'Yeni Şirket',
        'users_new_user': 'Yeni Kullanıcı',
        
        # Help
        'help_q1': 'Nasıl rapor oluşturabilirim?',
        'help_a1': 'Raporlar menüsünden \'Yeni Rapor\' butonuna tıklayarak oluşturabilirsiniz.',
        'help_q2': 'Veri girişi nasıl yapılır?',
        'help_a2': 'Veri Girişi menüsünden ilgili modülü seçerek veri girebilirsiniz.',
        'help_q3': 'Şifremi unuttum ne yapmalıyım?',
        'help_a3': 'Giriş ekranındaki \'Şifremi Unuttum\' bağlantısını kullanabilirsiniz.',
        'help_q4': 'Destek ekibine nasıl ulaşırım?',
        'help_a4': 'Yardım sayfasındaki destek formunu doldurabilirsiniz.',
        'help_report_file': 'Rapor Dosyası',
        
        # Previous fixes (ensure they persist)
        'carbon_title': 'Karbon Ayak İzi',
        'carbon_desc': 'Karbon emisyonlarınızı hesaplayın ve yönetin.',
        'scope_1_title': 'Kapsam 1',
        'scope_1_desc': 'Doğrudan Emisyonlar',
        'scope_2_title': 'Kapsam 2',
        'scope_2_desc': 'Dolaylı Enerji Emisyonları',
        'scope_3_title': 'Kapsam 3',
        'scope_3_desc': 'Diğer Dolaylı Emisyonlar',
        'btn_data_entry': 'Veri Girişi',
        'module_active': 'Aktif',
        'module_passive': 'Pasif',
        'module_load_error': 'Modül Yükleme Hatası',
        'module_unavailable': 'Modül Kullanılamıyor',
        'energy_title': 'Enerji Yönetimi',
        'energy_desc': 'Enerji tüketimini izleyin ve verimliliği artırın.',
        'waste_title': 'Atık Yönetimi',
        'waste_desc': 'Atık oluşumunu ve geri dönüşümü takip edin.',
        'water_title': 'Su Yönetimi',
        'water_desc': 'Su tüketimini ve ayak izinizi yönetin.',
        'biodiversity_title': 'Biyoçeşitlilik',
        'biodiversity_desc': 'Biyoçeşitlilik üzerindeki etkilerinizi izleyin.',
        'social_title': 'Sosyal Etki',
        'social_desc': 'Toplumsal katkı ve çalışan refahını yönetin.',
        'governance_title': 'Kurumsal Yönetim',
        'governance_desc': 'Yönetim kurulu yapısı ve etik politikaları izleyin.',
        'supply_chain_title': 'Tedarik Zinciri',
        'supply_chain_desc': 'Tedarikçi sürdürülebilirliğini değerlendirin.',
        'economic_title': 'Ekonomik Değer',
        'economic_desc': 'Ekonomik performans ve katma değeri ölçün.',
        'esg_title': 'ESG Skorlama',
        'esg_desc': 'Çevresel, Sosyal ve Yönetişim skorlarınızı hesaplayın.',
        'cbam_title': 'CBAM Raporlama',
        'cbam_desc': 'Sınırda Karbon Düzenleme Mekanizması uyumluluğu.',
        'csrd_title': 'CSRD Uyumu',
        'csrd_desc': 'Kurumsal Sürdürülebilirlik Raporlama Direktifi uyumluluğu.',
        'taxonomy_title': 'AB Taksonomisi',
        'taxonomy_desc': 'AB Taksonomisi uygunluk ve uyumluluk analizi.',
        'gri_title': 'GRI Standartları',
        'gri_desc': 'Küresel Raporlama Girişimi standartlarına göre raporlama.',
        'sdg_title': 'BM Sürdürülebilir Kalkınma Amaçları',
        'sdg_desc': 'BM SKA hedeflerine katkınızı ölçün.',
        'issb_title': 'IFRS S1/S2 (ISSB)',
        'issb_desc': 'Uluslararası Sürdürülebilirlik Standartları Kurulu raporlaması.',
        'tcfd_title': 'TCFD',
        'tcfd_desc': 'İklimle Bağlantılı Finansal Beyanlar Görev Gücü raporlaması.',
        'tnfd_title': 'TNFD',
        'tnfd_desc': 'Doğayla Bağlantılı Finansal Beyanlar Görev Gücü raporlaması.',
        'cdp_title': 'CDP Raporlama',
        'cdp_desc': 'Karbon Saydamlık Projesi veri toplama ve raporlama.',
        'energy_consumption_title': 'Enerji Tüketimi',
        'energy_consumption_desc': 'Tüketim verilerini girin ve izleyin.',
        'btn_consumption_data': 'Tüketim Verileri',
        'energy_renewable_title': 'Yenilenebilir Enerji',
        'energy_renewable_desc': 'Yenilenebilir enerji üretim verileri.',
        'btn_production_data': 'Üretim Verileri',
        'module_energy_unavailable': 'Enerji modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.',
        'water_ready_desc': 'Su yönetimi modülü kullanıma hazır. Veri girişi yapabilirsiniz.',
        'btn_add_water_data': 'Su Verisi Ekle',
        'module_water_unavailable': 'Su modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.',
        'waste_module_ready': 'Modül Hazır',
        'waste_ready_desc': 'Atık yönetimi modülü kullanıma hazır. Veri girişi yapabilirsiniz.',
        'btn_add_waste_data': 'Atık Verisi Ekle',
        'module_waste_unavailable': 'Atık modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.',
        
        # Tabs
        'tab_carbon': 'Karbon',
        'tab_energy': 'Enerji',
        'tab_waste': 'Atık',
        'tab_water': 'Su',
    }

    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Get list of html files
        stdin, stdout, stderr = client.exec_command("ls /var/www/sustainage/templates/*.html")
        files = stdout.read().decode().splitlines()
        
        for remote_path in files:
            filename = remote_path.split('/')[-1]
            print(f"Processing {filename}...")
            
            # Download
            local_path = f"c:\\SUSTAINAGESERVER\\temp_{filename}"
            sftp.get(remote_path, local_path)
            
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            # Replace all keys
            for key, text in translations.items():
                pattern = f"{{{{ _\\('{key}'\\) }}}}"
                content = re.sub(pattern, text, content)
                # Also try with double quotes
                pattern_dq = f"{{{{ _\\(\"{key}\"\\) }}}}"
                content = re.sub(pattern_dq, text, content)
            
            # Fix broken url_for parameters (persist this fix)
            if "data_type=" in content and "url_for('data_add'" in content:
                content = content.replace("data_type=", "type=")
                print(f"  - Fixed data_type parameter in {filename}")
            
            if content != original_content:
                print(f"  - Patched {filename}")
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write(content)
                sftp.put(local_path, remote_path)
            else:
                print(f"  - No changes needed for {filename}")
            
            # Cleanup
            try:
                import os
                os.remove(local_path)
            except:
                pass

        sftp.close()
        print("All templates patched.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_module_translations()
