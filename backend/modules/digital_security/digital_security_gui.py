"""
Bilgi Güvenliği ve Dijitalleşme Modülü
SDG 9: Industry, Innovation and Infrastructure
"""

import logging
import os
import re
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


class DigitalSecurityGUI:
    def __init__(self, parent, company_id) -> None:
        self.parent = parent
        self.company_id = company_id
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(base_dir, "data", "sdg_desktop.sqlite")

        # Veritabanı tablosunu oluştur
        self.create_table()

        # GUI'yi oluştur
        self.create_gui()

        # Verileri yükle
        self.load_data()

    def create_table(self) -> None:
        """Bilgi Güvenliği ve Dijitalleşme tablosunu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS digital_security_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    year INTEGER,
                    quarter INTEGER,
                    
                    -- Bilgi Güvenliği Sertifikaları
                    iso27001_certified BOOLEAN,
                    iso27001_certification_date TEXT,
                    other_security_certifications TEXT,
                    cybersecurity_framework TEXT,
                    
                    -- Siber Güvenlik
                    cybersecurity_training_hours INTEGER,
                    security_awareness_training INTEGER,
                    phishing_simulation_tests INTEGER,
                    incident_response_plan BOOLEAN,
                    security_incidents_count INTEGER,
                    data_breach_incidents INTEGER,
                    
                    -- Dijital Altyapı
                    cloud_adoption_percentage REAL,
                    digital_transformation_budget REAL,
                    legacy_system_replacement INTEGER,
                    api_integrations INTEGER,
                    automation_level REAL,
                    
                    -- Yapay Zeka ve Makine Öğrenmesi
                    ai_projects_active INTEGER,
                    ai_investment_budget REAL,
                    machine_learning_models INTEGER,
                    ai_ethics_policy BOOLEAN,
                    ai_bias_audit BOOLEAN,
                    
                    -- Veri Yönetimi
                    data_governance_policy BOOLEAN,
                    data_privacy_compliance TEXT,
                    gdpr_compliance BOOLEAN,
                    data_retention_policy BOOLEAN,
                    data_backup_frequency TEXT,
                    
                    -- Dijital Yetenekler
                    digital_skills_assessment BOOLEAN,
                    digital_training_programs INTEGER,
                    remote_work_percentage REAL,
                    digital_collaboration_tools INTEGER,
                    
                    -- E-ticaret ve Dijital Pazarlama
                    ecommerce_revenue_percentage REAL,
                    digital_marketing_budget REAL,
                    social_media_presence BOOLEAN,
                    customer_digital_experience_score REAL,
                    
                    -- Blockchain ve Fintech
                    blockchain_projects INTEGER,
                    cryptocurrency_adoption BOOLEAN,
                    fintech_partnerships INTEGER,
                    digital_payment_systems INTEGER,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                )
            ''')

            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Tablo oluşturma hatası: {e}")

    def create_gui(self) -> None:
        """GUI'yi oluştur"""
        # Ana container
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#8B0000', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Bilgi Güvenliği ve Dijitalleşme",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#8B0000')
        title_label.pack(expand=True)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_security_certifications_tab()
        self.create_cybersecurity_tab()
        self.create_digital_infrastructure_tab()
        self.create_ai_ml_tab()
        self.create_data_management_tab()
        self.create_digital_capabilities_tab()
        self.create_ecommerce_tab()
        self.create_blockchain_tab()

    def create_security_certifications_tab(self) -> None:
        """Bilgi Güvenliği Sertifikaları sekmesi"""
        cert_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(cert_frame, text="️ Güvenlik Sertifikaları")

        # Form alanları
        form_frame = tk.Frame(cert_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Yıl ve Çeyrek seçimi
        period_frame = tk.Frame(form_frame, bg='white')
        period_frame.pack(fill='x', pady=(0, 20))

        tk.Label(period_frame, text=" Dönem:", font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')

        period_select_frame = tk.Frame(period_frame, bg='white')
        period_select_frame.pack(fill='x', pady=(5, 0))

        tk.Label(period_select_frame, text="Yıl:", bg='white').pack(side='left', padx=(0, 10))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(period_select_frame, textvariable=self.year_var,
                                 values=list(range(2020, 2030)), width=10)
        year_combo.pack(side='left', padx=(0, 20))

        tk.Label(period_select_frame, text="Çeyrek:", bg='white').pack(side='left', padx=(0, 10))
        self.quarter_var = tk.StringVar(value="1")
        quarter_combo = ttk.Combobox(period_select_frame, textvariable=self.quarter_var,
                                    values=["1", "2", "3", "4"], width=10)
        quarter_combo.pack(side='left')

        # Güvenlik Sertifikaları
        cert_group = tk.LabelFrame(form_frame, text="️ Bilgi Güvenliği Sertifikaları",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        cert_group.pack(fill='x', pady=(0, 20))

        # ISO 27001
        iso_frame = tk.Frame(cert_group, bg='white')
        iso_frame.pack(fill='x', pady=10)

        self.iso27001_var = tk.BooleanVar()
        iso_check = tk.Checkbutton(iso_frame, text="ISO 27001 Sertifikalı",
                                  variable=self.iso27001_var, bg='white')
        iso_check.pack(side='left')

        tk.Label(iso_frame, text="Sertifika Tarihi:", bg='white').pack(side='left', padx=(20, 5))
        self.iso27001_date_entry = tk.Entry(iso_frame, width=15)
        self.iso27001_date_entry.pack(side='left', padx=(0, 10))

        # Diğer Sertifikalar
        tk.Label(cert_group, text="Diğer Güvenlik Sertifikaları:", bg='white').pack(anchor='w', pady=(10, 5))
        self.other_cert_text = tk.Text(cert_group, height=3, width=50)
        self.other_cert_text.pack(fill='x', pady=(0, 10))

        # Siber Güvenlik Çerçevesi
        tk.Label(cert_group, text="Siber Güvenlik Çerçevesi:", bg='white').pack(anchor='w', pady=(10, 5))
        self.framework_combo = ttk.Combobox(cert_group, values=[
            "NIST Cybersecurity Framework", "ISO/IEC 27001", "CIS Controls",
            "COBIT", "Diğer"
        ], width=40)
        self.framework_combo.pack(anchor='w', pady=(0, 10))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_security_cert_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_cybersecurity_tab(self) -> None:
        """Siber Güvenlik sekmesi"""
        cyber_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(cyber_frame, text=" Siber Güvenlik")

        form_frame = tk.Frame(cyber_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Siber Güvenlik Metrikleri
        cyber_group = tk.LabelFrame(form_frame, text=" Siber Güvenlik Metrikleri",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        cyber_group.pack(fill='x', pady=(0, 20))

        # Eğitim alanları
        training_frame = tk.Frame(cyber_group, bg='white')
        training_frame.pack(fill='x', pady=10)

        tk.Label(training_frame, text="Siber Güvenlik Eğitim Saati:", bg='white').pack(side='left')
        self.cyber_training_entry = tk.Entry(training_frame, width=15)
        self.cyber_training_entry.pack(side='left', padx=(10, 20))

        tk.Label(training_frame, text="Güvenlik Farkındalık Eğitimi:", bg='white').pack(side='left')
        self.awareness_training_entry = tk.Entry(training_frame, width=15)
        self.awareness_training_entry.pack(side='left', padx=(10, 0))

        # Test ve olay yönetimi
        incident_frame = tk.Frame(cyber_group, bg='white')
        incident_frame.pack(fill='x', pady=10)

        tk.Label(incident_frame, text="Phishing Simülasyon Testi:", bg='white').pack(side='left')
        self.phishing_tests_entry = tk.Entry(incident_frame, width=15)
        self.phishing_tests_entry.pack(side='left', padx=(10, 20))

        self.incident_plan_var = tk.BooleanVar()
        incident_check = tk.Checkbutton(incident_frame, text="Olay Müdahale Planı Var",
                                       variable=self.incident_plan_var, bg='white')
        incident_check.pack(side='left', padx=(20, 0))

        # Güvenlik olayları
        security_frame = tk.Frame(cyber_group, bg='white')
        security_frame.pack(fill='x', pady=10)

        tk.Label(security_frame, text="Güvenlik Olayı Sayısı:", bg='white').pack(side='left')
        self.security_incidents_entry = tk.Entry(security_frame, width=15)
        self.security_incidents_entry.pack(side='left', padx=(10, 20))

        tk.Label(security_frame, text="Veri İhlali Olayı:", bg='white').pack(side='left')
        self.data_breach_entry = tk.Entry(security_frame, width=15)
        self.data_breach_entry.pack(side='left', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_cybersecurity_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_digital_infrastructure_tab(self) -> None:
        """Dijital Altyapı sekmesi"""
        infra_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(infra_frame, text=" Dijital Altyapı")

        form_frame = tk.Frame(infra_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Dijital Altyapı Metrikleri
        infra_group = tk.LabelFrame(form_frame, text=" Dijital Altyapı Metrikleri",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        infra_group.pack(fill='x', pady=(0, 20))

        infra_fields = [
            ("Bulut Benimsenme Oranı (%):", "cloud_adoption_percentage"),
            ("Dijital Dönüşüm Bütçesi (TL):", "digital_transformation_budget"),
            ("Legacy Sistem Değişimi:", "legacy_system_replacement"),
            ("API Entegrasyonu:", "api_integrations"),
            ("Otomasyon Seviyesi (%):", "automation_level")
        ]

        self.infra_entries = {}
        for label, key in infra_fields:
            row_frame = tk.Frame(infra_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.infra_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_digital_infrastructure_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_ai_ml_tab(self) -> None:
        """Yapay Zeka ve Makine Öğrenmesi sekmesi"""
        ai_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ai_frame, text=" AI & ML")

        form_frame = tk.Frame(ai_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # AI/ML Metrikleri
        ai_group = tk.LabelFrame(form_frame, text=" Yapay Zeka ve Makine Öğrenmesi",
                                font=('Segoe UI', 12, 'bold'), bg='white')
        ai_group.pack(fill='x', pady=(0, 20))

        # AI Projeleri
        ai_projects_frame = tk.Frame(ai_group, bg='white')
        ai_projects_frame.pack(fill='x', pady=10)

        tk.Label(ai_projects_frame, text="Aktif AI Projeleri:", bg='white').pack(side='left')
        self.ai_projects_entry = tk.Entry(ai_projects_frame, width=15)
        self.ai_projects_entry.pack(side='left', padx=(10, 20))

        tk.Label(ai_projects_frame, text="AI Yatırım Bütçesi (TL):", bg='white').pack(side='left')
        self.ai_budget_entry = tk.Entry(ai_projects_frame, width=15)
        self.ai_budget_entry.pack(side='left', padx=(10, 0))

        # ML Modelleri
        ml_frame = tk.Frame(ai_group, bg='white')
        ml_frame.pack(fill='x', pady=10)

        tk.Label(ml_frame, text="Makine Öğrenmesi Modeli:", bg='white').pack(side='left')
        self.ml_models_entry = tk.Entry(ml_frame, width=15)
        self.ml_models_entry.pack(side='left', padx=(10, 20))

        # AI Etik Politikaları
        ethics_frame = tk.Frame(ai_group, bg='white')
        ethics_frame.pack(fill='x', pady=10)

        self.ai_ethics_var = tk.BooleanVar()
        ethics_check = tk.Checkbutton(ethics_frame, text="AI Etik Politikası",
                                     variable=self.ai_ethics_var, bg='white')
        ethics_check.pack(side='left')

        self.ai_bias_var = tk.BooleanVar()
        bias_check = tk.Checkbutton(ethics_frame, text="AI Bias Denetimi",
                                   variable=self.ai_bias_var, bg='white')
        bias_check.pack(side='left', padx=(20, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_ai_ml_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_data_management_tab(self) -> None:
        """Veri Yönetimi sekmesi"""
        data_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(data_frame, text=" Veri Yönetimi")

        form_frame = tk.Frame(data_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Veri Yönetimi Politikaları
        data_group = tk.LabelFrame(form_frame, text=" Veri Yönetimi Politikaları",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        data_group.pack(fill='x', pady=(0, 20))

        # Politikalar
        policies_frame = tk.Frame(data_group, bg='white')
        policies_frame.pack(fill='x', pady=10)

        self.data_governance_var = tk.BooleanVar()
        governance_check = tk.Checkbutton(policies_frame, text="Veri Yönetişim Politikası",
                                         variable=self.data_governance_var, bg='white')
        governance_check.pack(side='left')

        self.gdpr_compliance_var = tk.BooleanVar()
        gdpr_check = tk.Checkbutton(policies_frame, text="GDPR Uyumluluğu",
                                   variable=self.gdpr_compliance_var, bg='white')
        gdpr_check.pack(side='left', padx=(20, 0))

        # Veri gizliliği
        privacy_frame = tk.Frame(data_group, bg='white')
        privacy_frame.pack(fill='x', pady=10)

        tk.Label(privacy_frame, text="Veri Gizliliği Uyumluluğu:", bg='white').pack(side='left')
        self.privacy_compliance_combo = ttk.Combobox(privacy_frame, values=[
            "GDPR", "KVKK", "CCPA", "PIPEDA", "Diğer"
        ], width=15)
        self.privacy_compliance_combo.pack(side='left', padx=(10, 0))

        # Veri saklama
        retention_frame = tk.Frame(data_group, bg='white')
        retention_frame.pack(fill='x', pady=10)

        self.retention_policy_var = tk.BooleanVar()
        retention_check = tk.Checkbutton(retention_frame, text="Veri Saklama Politikası",
                                        variable=self.retention_policy_var, bg='white')
        retention_check.pack(side='left')

        tk.Label(retention_frame, text="Yedekleme Sıklığı:", bg='white').pack(side='left', padx=(20, 5))
        self.backup_frequency_entry = tk.Entry(retention_frame, width=15)
        self.backup_frequency_entry.pack(side='left', padx=(0, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_data_management_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_digital_capabilities_tab(self) -> None:
        """Dijital Yetenekler sekmesi"""
        capabilities_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(capabilities_frame, text=" Dijital Yetenekler")

        form_frame = tk.Frame(capabilities_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Dijital Yetenekler
        capabilities_group = tk.LabelFrame(form_frame, text=" Dijital Yetenekler",
                                          font=('Segoe UI', 12, 'bold'), bg='white')
        capabilities_group.pack(fill='x', pady=(0, 20))

        capabilities_fields = [
            ("Dijital Yetenek Değerlendirmesi:", "digital_skills_assessment"),
            ("Dijital Eğitim Programı:", "digital_training_programs"),
            ("Uzaktan Çalışma Oranı (%):", "remote_work_percentage"),
            ("Dijital İşbirliği Aracı:", "digital_collaboration_tools")
        ]

        self.capabilities_entries = {}
        for label, key in capabilities_fields:
            row_frame = tk.Frame(capabilities_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            if key == 'digital_skills_assessment':
                # Checkbox için özel frame
                check_frame = tk.Frame(row_frame, bg='white')
                check_frame.pack(fill='x')

                tk.Label(check_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
                self.capabilities_entries[key] = tk.BooleanVar()
                checkbox = tk.Checkbutton(check_frame, variable=self.capabilities_entries[key], bg='white')
                checkbox.pack(side='left', padx=(10, 0))
            else:
                tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
                entry = tk.Entry(row_frame, width=20)
                entry.pack(side='left', padx=(10, 0))
                self.capabilities_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_digital_capabilities_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_ecommerce_tab(self) -> None:
        """E-ticaret ve Dijital Pazarlama sekmesi"""
        ecommerce_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ecommerce_frame, text=" E-ticaret")

        form_frame = tk.Frame(ecommerce_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # E-ticaret Metrikleri
        ecommerce_group = tk.LabelFrame(form_frame, text=" E-ticaret ve Dijital Pazarlama",
                                       font=('Segoe UI', 12, 'bold'), bg='white')
        ecommerce_group.pack(fill='x', pady=(0, 20))

        ecommerce_fields = [
            ("E-ticaret Gelir Oranı (%):", "ecommerce_revenue_percentage"),
            ("Dijital Pazarlama Bütçesi (TL):", "digital_marketing_budget"),
            ("Sosyal Medya Varlığı:", "social_media_presence"),
            ("Müşteri Dijital Deneyim Skoru (1-10):", "customer_digital_experience_score")
        ]

        self.ecommerce_entries = {}
        for label, key in ecommerce_fields:
            row_frame = tk.Frame(ecommerce_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            if key == 'social_media_presence':
                # Checkbox için özel frame
                check_frame = tk.Frame(row_frame, bg='white')
                check_frame.pack(fill='x')

                tk.Label(check_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
                self.ecommerce_entries[key] = tk.BooleanVar()
                checkbox = tk.Checkbutton(check_frame, variable=self.ecommerce_entries[key], bg='white')
                checkbox.pack(side='left', padx=(10, 0))
            else:
                tk.Label(row_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
                entry = tk.Entry(row_frame, width=20)
                entry.pack(side='left', padx=(10, 0))
                self.ecommerce_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_ecommerce_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_blockchain_tab(self) -> None:
        """Blockchain ve Fintech sekmesi"""
        blockchain_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(blockchain_frame, text="️ Blockchain")

        form_frame = tk.Frame(blockchain_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Blockchain ve Fintech
        blockchain_group = tk.LabelFrame(form_frame, text="️ Blockchain ve Fintech",
                                        font=('Segoe UI', 12, 'bold'), bg='white')
        blockchain_group.pack(fill='x', pady=(0, 20))

        # Blockchain projeleri
        blockchain_projects_frame = tk.Frame(blockchain_group, bg='white')
        blockchain_projects_frame.pack(fill='x', pady=10)

        tk.Label(blockchain_projects_frame, text="Blockchain Projeleri:", bg='white').pack(side='left')
        self.blockchain_projects_entry = tk.Entry(blockchain_projects_frame, width=15)
        self.blockchain_projects_entry.pack(side='left', padx=(10, 20))

        self.crypto_adoption_var = tk.BooleanVar()
        crypto_check = tk.Checkbutton(blockchain_projects_frame, text="Kripto Para Benimsenmesi",
                                     variable=self.crypto_adoption_var, bg='white')
        crypto_check.pack(side='left')

        # Fintech ortaklıkları
        fintech_frame = tk.Frame(blockchain_group, bg='white')
        fintech_frame.pack(fill='x', pady=10)

        tk.Label(fintech_frame, text="Fintech Ortaklıkları:", bg='white').pack(side='left')
        self.fintech_partnerships_entry = tk.Entry(fintech_frame, width=15)
        self.fintech_partnerships_entry.pack(side='left', padx=(10, 20))

        tk.Label(fintech_frame, text="Dijital Ödeme Sistemleri:", bg='white').pack(side='left')
        self.digital_payment_entry = tk.Entry(fintech_frame, width=15)
        self.digital_payment_entry.pack(side='left', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_blockchain_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    # Kaydetme metodları
    def save_security_cert_data(self) -> None:
        """Güvenlik sertifika verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'iso27001_certified': self.iso27001_var.get(),
                'iso27001_certification_date': self.iso27001_date_entry.get(),
                'other_security_certifications': self.other_cert_text.get('1.0', tk.END).strip(),
                'cybersecurity_framework': self.framework_combo.get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(
                cursor,
                'digital_security_metrics',
                data,
                [
                    'iso27001_certified',
                    'iso27001_certification_date',
                    'other_security_certifications',
                    'cybersecurity_framework',
                ],
            )

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Güvenlik sertifika verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_cybersecurity_data(self) -> None:
        """Siber güvenlik verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'cybersecurity_training_hours': int(self.cyber_training_entry.get() or 0),
                'security_awareness_training': int(self.awareness_training_entry.get() or 0),
                'phishing_simulation_tests': int(self.phishing_tests_entry.get() or 0),
                'incident_response_plan': self.incident_plan_var.get(),
                'security_incidents_count': int(self.security_incidents_entry.get() or 0),
                'data_breach_incidents': int(self.data_breach_entry.get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'cybersecurity_training_hours', 'security_awareness_training', 'phishing_simulation_tests',
                'incident_response_plan', 'security_incidents_count', 'data_breach_incidents'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Siber güvenlik verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_digital_infrastructure_data(self) -> None:
        """Dijital altyapı verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'cloud_adoption_percentage': float(self.infra_entries['cloud_adoption_percentage'].get() or 0),
                'digital_transformation_budget': float(self.infra_entries['digital_transformation_budget'].get() or 0),
                'legacy_system_replacement': int(self.infra_entries['legacy_system_replacement'].get() or 0),
                'api_integrations': int(self.infra_entries['api_integrations'].get() or 0),
                'automation_level': float(self.infra_entries['automation_level'].get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'cloud_adoption_percentage', 'digital_transformation_budget', 'legacy_system_replacement',
                'api_integrations', 'automation_level'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Dijital altyapı verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_ai_ml_data(self) -> None:
        """AI/ML verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'ai_projects_active': int(self.ai_projects_entry.get() or 0),
                'ai_investment_budget': float(self.ai_budget_entry.get() or 0),
                'machine_learning_models': int(self.ml_models_entry.get() or 0),
                'ai_ethics_policy': self.ai_ethics_var.get(),
                'ai_bias_audit': self.ai_bias_var.get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'ai_projects_active', 'ai_investment_budget', 'machine_learning_models',
                'ai_ethics_policy', 'ai_bias_audit'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "AI/ML verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_data_management_data(self) -> None:
        """Veri yönetimi verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'data_governance_policy': self.data_governance_var.get(),
                'data_privacy_compliance': self.privacy_compliance_combo.get(),
                'gdpr_compliance': self.gdpr_compliance_var.get(),
                'data_retention_policy': self.retention_policy_var.get(),
                'data_backup_frequency': self.backup_frequency_entry.get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'data_governance_policy', 'data_privacy_compliance', 'gdpr_compliance',
                'data_retention_policy', 'data_backup_frequency'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Veri yönetimi verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_digital_capabilities_data(self) -> None:
        """Dijital yetenekler verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'digital_skills_assessment': self.capabilities_entries['digital_skills_assessment'].get(),
                'digital_training_programs': int(self.capabilities_entries['digital_training_programs'].get() or 0),
                'remote_work_percentage': float(self.capabilities_entries['remote_work_percentage'].get() or 0),
                'digital_collaboration_tools': int(self.capabilities_entries['digital_collaboration_tools'].get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'digital_skills_assessment', 'digital_training_programs', 'remote_work_percentage',
                'digital_collaboration_tools'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Dijital yetenekler verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_ecommerce_data(self) -> None:
        """E-ticaret verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'ecommerce_revenue_percentage': float(
                    self.ecommerce_entries['ecommerce_revenue_percentage'].get() or 0
                ),
                'digital_marketing_budget': float(self.ecommerce_entries['digital_marketing_budget'].get() or 0),
                'social_media_presence': self.ecommerce_entries['social_media_presence'].get(),
                'customer_digital_experience_score': float(
                    self.ecommerce_entries['customer_digital_experience_score'].get() or 0
                )
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'ecommerce_revenue_percentage', 'digital_marketing_budget', 'social_media_presence',
                'customer_digital_experience_score'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "E-ticaret verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_blockchain_data(self) -> None:
        """Blockchain verilerini kaydet"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Veri hazırla
            data = {
                'company_id': self.company_id,
                'year': year,
                'quarter': quarter,
                'blockchain_projects': int(self.blockchain_projects_entry.get() or 0),
                'cryptocurrency_adoption': self.crypto_adoption_var.get(),
                'fintech_partnerships': int(self.fintech_partnerships_entry.get() or 0),
                'digital_payment_systems': int(self.digital_payment_entry.get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'digital_security_metrics', data, [
                'blockchain_projects', 'cryptocurrency_adoption', 'fintech_partnerships',
                'digital_payment_systems'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Blockchain verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def _save_or_update_record(self, cursor, table_name, data, fields) -> None:
        """Kayıt kaydetme veya güncelleme yardımcı metodu"""
        if not re.fullmatch(r"[A-Za-z0-9_]+", table_name):
            raise ValueError("Geçersiz tablo adı")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone() is None:
            raise ValueError("Tablo bulunamadı")
        cursor.execute(
            f"""
            SELECT id FROM {table_name} 
            WHERE company_id = ? AND year = ? AND quarter = ?
            """,
            (data['company_id'], data['year'], data['quarter']),
        )

        existing = cursor.fetchone()

        if existing:
            # Güncelle
            set_clause = ', '.join([f'{field} = ?' for field in fields]) + ', updated_at = CURRENT_TIMESTAMP'
            values = [data[field] for field in fields] + [existing[0]]
            cursor.execute(
                f"""
                UPDATE {table_name} SET {set_clause}
                WHERE id = ?
                """,
                values,
            )
        else:
            # Yeni kayıt
            all_fields = ['company_id', 'year', 'quarter'] + fields
            placeholders = ', '.join(['?' for _ in all_fields])
            values = [data[field] for field in all_fields]
            cursor.execute(
                f"""
                INSERT INTO {table_name} ({', '.join(all_fields)})
                VALUES ({placeholders})
                """,
                values,
            )

    def load_data(self) -> None:
        """Mevcut verileri yükle"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM digital_security_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            row = cursor.fetchone()
            conn.close()

            if row:
                # Veritabanından gelen verileri forma yükle
                # Bu kısım veritabanı şemasına göre düzenlenmeli
                pass

        except Exception as e:
            logging.error(f"Veri yükleme hatası: {e}")
