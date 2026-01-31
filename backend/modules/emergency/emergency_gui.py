"""
Acil Durum ve Afet Yönetimi Modülü
SDG 11: Sustainable Cities and Communities
"""

import logging
import os
import re
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


class EmergencyGUI:
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
        """Acil Durum ve Afet Yönetimi tablosunu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_management_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    year INTEGER,
                    quarter INTEGER,
                    
                    -- Acil Durum Planları
                    emergency_response_plan BOOLEAN,
                    business_continuity_plan BOOLEAN,
                    disaster_recovery_plan BOOLEAN,
                    crisis_communication_plan BOOLEAN,
                    plan_last_updated TEXT,
                    plan_testing_frequency TEXT,
                    
                    -- Risk Değerlendirmesi
                    risk_assessment_conducted BOOLEAN,
                    risk_assessment_frequency TEXT,
                    identified_risks_count INTEGER,
                    high_risk_scenarios INTEGER,
                    risk_mitigation_measures INTEGER,
                    
                    -- Acil Durum Ekip ve Eğitim
                    emergency_response_team_size INTEGER,
                    emergency_coordinator_appointed BOOLEAN,
                    emergency_training_hours INTEGER,
                    emergency_drill_frequency TEXT,
                    last_emergency_drill_date TEXT,
                    
                    -- İletişim ve Uyarı Sistemleri
                    emergency_communication_system BOOLEAN,
                    alert_system_technology TEXT,
                    stakeholder_notification_system BOOLEAN,
                    backup_communication_methods TEXT,
                    
                    -- Kaynak ve Tesisler
                    emergency_supplies_stocked BOOLEAN,
                    emergency_facilities_count INTEGER,
                    backup_power_systems BOOLEAN,
                    water_emergency_supply_days INTEGER,
                    food_emergency_supply_days INTEGER,
                    
                    -- İş Sürekliliği
                    business_continuity_testing BOOLEAN,
                    backup_data_center BOOLEAN,
                    remote_work_capability REAL,
                    supply_chain_risk_mitigation BOOLEAN,
                    critical_process_identification BOOLEAN,
                    
                    -- Finansal Hazırlık
                    emergency_fund_available BOOLEAN,
                    emergency_fund_amount REAL,
                    insurance_coverage_adequate BOOLEAN,
                    business_interruption_insurance BOOLEAN,
                    
                    -- Toplum ve Çevre Desteği
                    community_emergency_support BOOLEAN,
                    environmental_impact_assessment BOOLEAN,
                    local_authority_coordination BOOLEAN,
                    volunteer_network_established BOOLEAN,
                    
                    -- Performans Metrikleri
                    emergency_response_time_minutes INTEGER,
                    business_recovery_time_hours INTEGER,
                    employee_safety_incidents INTEGER,
                    plan_effectiveness_score REAL,
                    
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
        title_frame = tk.Frame(main_frame, bg='#FF4500', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Acil Durum ve Afet Yönetimi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#FF4500')
        title_label.pack(expand=True)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_emergency_plans_tab()
        self.create_risk_assessment_tab()
        self.create_team_training_tab()
        self.create_communication_tab()
        self.create_resources_tab()
        self.create_business_continuity_tab()
        self.create_financial_preparedness_tab()
        self.create_community_support_tab()
        self.create_performance_tab()

    def create_emergency_plans_tab(self) -> None:
        """Acil Durum Planları sekmesi"""
        plans_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(plans_frame, text=" Acil Durum Planları")

        # Form alanları
        form_frame = tk.Frame(plans_frame, bg='white')
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

        # Acil Durum Planları
        plans_group = tk.LabelFrame(form_frame, text=" Acil Durum Planları",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        plans_group.pack(fill='x', pady=(0, 20))

        # Plan türleri
        plan_types = [
            ("Acil Müdahale Planı", "emergency_response_plan"),
            ("İş Sürekliliği Planı", "business_continuity_plan"),
            ("Afet Kurtarma Planı", "disaster_recovery_plan"),
            ("Kriz İletişim Planı", "crisis_communication_plan")
        ]

        self.plan_vars = {}
        for label, key in plan_types:
            row_frame = tk.Frame(plans_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            self.plan_vars[key] = tk.BooleanVar()
            plan_check = tk.Checkbutton(row_frame, text=label,
                                      variable=self.plan_vars[key], bg='white')
            plan_check.pack(side='left')

        # Plan güncelleme bilgileri
        update_frame = tk.Frame(plans_group, bg='white')
        update_frame.pack(fill='x', pady=(10, 0))

        tk.Label(update_frame, text="Plan Son Güncelleme Tarihi:", bg='white').pack(side='left')
        self.plan_update_entry = tk.Entry(update_frame, width=15)
        self.plan_update_entry.pack(side='left', padx=(10, 20))

        tk.Label(update_frame, text="Test Sıklığı:", bg='white').pack(side='left')
        self.test_frequency_combo = ttk.Combobox(update_frame, values=[
            "Aylık", "3 Aylık", "6 Aylık", "Yıllık", "İhtiyaç Halinde"
        ], width=15)
        self.test_frequency_combo.pack(side='left', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_emergency_plans_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_risk_assessment_tab(self) -> None:
        """Risk Değerlendirmesi sekmesi"""
        risk_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(risk_frame, text="️ Risk Değerlendirmesi")

        form_frame = tk.Frame(risk_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Risk Değerlendirmesi
        risk_group = tk.LabelFrame(form_frame, text="️ Risk Değerlendirmesi",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        risk_group.pack(fill='x', pady=(0, 20))

        # Risk değerlendirmesi yapıldı mı?
        assessment_frame = tk.Frame(risk_group, bg='white')
        assessment_frame.pack(fill='x', pady=10)

        self.risk_assessment_var = tk.BooleanVar()
        assessment_check = tk.Checkbutton(assessment_frame, text="Risk Değerlendirmesi Yapıldı",
                                         variable=self.risk_assessment_var, bg='white')
        assessment_check.pack(side='left')

        tk.Label(assessment_frame, text="Değerlendirme Sıklığı:", bg='white').pack(side='left', padx=(20, 5))
        self.assessment_frequency_combo = ttk.Combobox(assessment_frame, values=[
            "Aylık", "3 Aylık", "6 Aylık", "Yıllık", "İhtiyaç Halinde"
        ], width=15)
        self.assessment_frequency_combo.pack(side='left', padx=(0, 0))

        # Risk metrikleri
        risk_metrics = [
            ("Tespit Edilen Risk Sayısı:", "identified_risks_count"),
            ("Yüksek Risk Senaryosu:", "high_risk_scenarios"),
            ("Risk Azaltma Önlemi:", "risk_mitigation_measures")
        ]

        self.risk_entries = {}
        for label, key in risk_metrics:
            row_frame = tk.Frame(risk_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.risk_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_risk_assessment_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_team_training_tab(self) -> None:
        """Ekip ve Eğitim sekmesi"""
        team_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(team_frame, text=" Ekip & Eğitim")

        form_frame = tk.Frame(team_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Acil Durum Ekibi
        team_group = tk.LabelFrame(form_frame, text=" Acil Durum Ekibi",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        team_group.pack(fill='x', pady=(0, 20))

        # Ekip bilgileri
        team_info = [
            ("Acil Durum Ekibi Büyüklüğü:", "emergency_response_team_size"),
            ("Acil Durum Koordinatörü Atandı:", "emergency_coordinator_appointed"),
            ("Acil Durum Eğitim Saati:", "emergency_training_hours")
        ]

        self.team_entries = {}
        for label, key in team_info:
            row_frame = tk.Frame(team_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            if key == 'emergency_coordinator_appointed':
                # Checkbox için özel frame
                check_frame = tk.Frame(row_frame, bg='white')
                check_frame.pack(fill='x')

                tk.Label(check_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
                self.team_entries[key] = tk.BooleanVar()
                checkbox = tk.Checkbutton(check_frame, variable=self.team_entries[key], bg='white')
                checkbox.pack(side='left', padx=(10, 0))
            else:
                tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
                entry = tk.Entry(row_frame, width=20)
                entry.pack(side='left', padx=(10, 0))
                self.team_entries[key] = entry

        # Tatbikat bilgileri
        drill_frame = tk.Frame(team_group, bg='white')
        drill_frame.pack(fill='x', pady=(10, 0))

        tk.Label(drill_frame, text="Tatbikat Sıklığı:", bg='white').pack(side='left')
        self.drill_frequency_combo = ttk.Combobox(drill_frame, values=[
            "Aylık", "3 Aylık", "6 Aylık", "Yıllık", "İhtiyaç Halinde"
        ], width=15)
        self.drill_frequency_combo.pack(side='left', padx=(10, 20))

        tk.Label(drill_frame, text="Son Tatbikat Tarihi:", bg='white').pack(side='left')
        self.last_drill_entry = tk.Entry(drill_frame, width=15)
        self.last_drill_entry.pack(side='left', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_team_training_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_communication_tab(self) -> None:
        """İletişim ve Uyarı Sistemleri sekmesi"""
        comm_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(comm_frame, text=" İletişim")

        form_frame = tk.Frame(comm_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # İletişim Sistemleri
        comm_group = tk.LabelFrame(form_frame, text=" İletişim ve Uyarı Sistemleri",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        comm_group.pack(fill='x', pady=(0, 20))

        # İletişim sistemi
        comm_system_frame = tk.Frame(comm_group, bg='white')
        comm_system_frame.pack(fill='x', pady=10)

        self.comm_system_var = tk.BooleanVar()
        comm_check = tk.Checkbutton(comm_system_frame, text="Acil Durum İletişim Sistemi",
                                   variable=self.comm_system_var, bg='white')
        comm_check.pack(side='left')

        tk.Label(comm_system_frame, text="Uyarı Sistemi Teknolojisi:", bg='white').pack(side='left', padx=(20, 5))
        self.alert_tech_combo = ttk.Combobox(comm_system_frame, values=[
            "SMS", "E-posta", "Telefon", "Siren", "Mobil Uygulama", "Diğer"
        ], width=15)
        self.alert_tech_combo.pack(side='left', padx=(0, 0))

        # Paydaş bildirim sistemi
        stakeholder_frame = tk.Frame(comm_group, bg='white')
        stakeholder_frame.pack(fill='x', pady=10)

        self.stakeholder_notification_var = tk.BooleanVar()
        stakeholder_check = tk.Checkbutton(stakeholder_frame, text="Paydaş Bildirim Sistemi",
                                          variable=self.stakeholder_notification_var, bg='white')
        stakeholder_check.pack(side='left')

        # Yedek iletişim yöntemleri
        backup_frame = tk.Frame(comm_group, bg='white')
        backup_frame.pack(fill='x', pady=10)

        tk.Label(backup_frame, text="Yedek İletişim Yöntemleri:", bg='white').pack(anchor='w', pady=(0, 5))
        self.backup_comm_text = tk.Text(backup_frame, height=3, width=50)
        self.backup_comm_text.pack(fill='x', pady=(0, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_communication_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_resources_tab(self) -> None:
        """Kaynak ve Tesisler sekmesi"""
        resources_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(resources_frame, text="️ Kaynaklar")

        form_frame = tk.Frame(resources_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Kaynak ve Tesisler
        resources_group = tk.LabelFrame(form_frame, text="️ Kaynak ve Tesisler",
                                       font=('Segoe UI', 12, 'bold'), bg='white')
        resources_group.pack(fill='x', pady=(0, 20))

        # Acil durum malzemeleri
        supplies_frame = tk.Frame(resources_group, bg='white')
        supplies_frame.pack(fill='x', pady=10)

        self.supplies_stocked_var = tk.BooleanVar()
        supplies_check = tk.Checkbutton(supplies_frame, text="Acil Durum Malzemeleri Stoklandı",
                                       variable=self.supplies_stocked_var, bg='white')
        supplies_check.pack(side='left')

        tk.Label(supplies_frame, text="Acil Durum Tesisi Sayısı:", bg='white').pack(side='left', padx=(20, 5))
        self.facilities_entry = tk.Entry(supplies_frame, width=15)
        self.facilities_entry.pack(side='left', padx=(0, 0))

        # Altyapı sistemleri
        infrastructure_frame = tk.Frame(resources_group, bg='white')
        infrastructure_frame.pack(fill='x', pady=10)

        self.backup_power_var = tk.BooleanVar()
        power_check = tk.Checkbutton(infrastructure_frame, text="Yedek Güç Sistemi",
                                    variable=self.backup_power_var, bg='white')
        power_check.pack(side='left')

        # Acil durum stokları
        stock_frame = tk.Frame(resources_group, bg='white')
        stock_frame.pack(fill='x', pady=10)

        tk.Label(stock_frame, text="Su Acil Durum Stoku (Gün):", bg='white').pack(side='left')
        self.water_supply_entry = tk.Entry(stock_frame, width=15)
        self.water_supply_entry.pack(side='left', padx=(10, 20))

        tk.Label(stock_frame, text="Yiyecek Acil Durum Stoku (Gün):", bg='white').pack(side='left')
        self.food_supply_entry = tk.Entry(stock_frame, width=15)
        self.food_supply_entry.pack(side='left', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_resources_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_business_continuity_tab(self) -> None:
        """İş Sürekliliği sekmesi"""
        continuity_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(continuity_frame, text=" İş Sürekliliği")

        form_frame = tk.Frame(continuity_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # İş Sürekliliği
        continuity_group = tk.LabelFrame(form_frame, text=" İş Sürekliliği",
                                        font=('Segoe UI', 12, 'bold'), bg='white')
        continuity_group.pack(fill='x', pady=(0, 20))

        # İş sürekliliği özellikleri
        continuity_features = [
            ("İş Sürekliliği Testi Yapıldı:", "business_continuity_testing"),
            ("Yedek Veri Merkezi:", "backup_data_center"),
            ("Uzaktan Çalışma Kapasitesi (%):", "remote_work_capability"),
            ("Tedarik Zinciri Risk Azaltma:", "supply_chain_risk_mitigation"),
            ("Kritik Süreç Tanımlaması:", "critical_process_identification")
        ]

        self.continuity_entries = {}
        for label, key in continuity_features:
            row_frame = tk.Frame(continuity_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            if key == 'remote_work_capability':
                # Sayısal değer için entry
                tk.Label(row_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
                entry = tk.Entry(row_frame, width=20)
                entry.pack(side='left', padx=(10, 0))
                self.continuity_entries[key] = entry
            else:
                # Checkbox için özel frame
                check_frame = tk.Frame(row_frame, bg='white')
                check_frame.pack(fill='x')

                tk.Label(check_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
                self.continuity_entries[key] = tk.BooleanVar()
                checkbox = tk.Checkbutton(check_frame, variable=self.continuity_entries[key], bg='white')
                checkbox.pack(side='left', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_business_continuity_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_financial_preparedness_tab(self) -> None:
        """Finansal Hazırlık sekmesi"""
        financial_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(financial_frame, text=" Finansal Hazırlık")

        form_frame = tk.Frame(financial_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Finansal Hazırlık
        financial_group = tk.LabelFrame(form_frame, text=" Finansal Hazırlık",
                                       font=('Segoe UI', 12, 'bold'), bg='white')
        financial_group.pack(fill='x', pady=(0, 20))

        # Acil durum fonu
        fund_frame = tk.Frame(financial_group, bg='white')
        fund_frame.pack(fill='x', pady=10)

        self.emergency_fund_var = tk.BooleanVar()
        fund_check = tk.Checkbutton(fund_frame, text="Acil Durum Fonu Mevcut",
                                   variable=self.emergency_fund_var, bg='white')
        fund_check.pack(side='left')

        tk.Label(fund_frame, text="Fon Miktarı (TL):", bg='white').pack(side='left', padx=(20, 5))
        self.fund_amount_entry = tk.Entry(fund_frame, width=20)
        self.fund_amount_entry.pack(side='left', padx=(0, 0))

        # Sigorta kapsamı
        insurance_frame = tk.Frame(financial_group, bg='white')
        insurance_frame.pack(fill='x', pady=10)

        self.insurance_adequate_var = tk.BooleanVar()
        insurance_check = tk.Checkbutton(insurance_frame, text="Sigorta Kapsamı Yeterli",
                                        variable=self.insurance_adequate_var, bg='white')
        insurance_check.pack(side='left')

        self.business_interruption_var = tk.BooleanVar()
        interruption_check = tk.Checkbutton(insurance_frame, text="İş Kesintisi Sigortası",
                                           variable=self.business_interruption_var, bg='white')
        interruption_check.pack(side='left', padx=(20, 0))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_financial_preparedness_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_community_support_tab(self) -> None:
        """Toplum ve Çevre Desteği sekmesi"""
        community_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(community_frame, text=" Toplum Desteği")

        form_frame = tk.Frame(community_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Toplum ve Çevre Desteği
        community_group = tk.LabelFrame(form_frame, text=" Toplum ve Çevre Desteği",
                                       font=('Segoe UI', 12, 'bold'), bg='white')
        community_group.pack(fill='x', pady=(0, 20))

        # Toplum desteği özellikleri
        support_features = [
            ("Toplum Acil Durum Desteği:", "community_emergency_support"),
            ("Çevresel Etki Değerlendirmesi:", "environmental_impact_assessment"),
            ("Yerel Otorite Koordinasyonu:", "local_authority_coordination"),
            ("Gönüllü Ağı Kuruldu:", "volunteer_network_established")
        ]

        self.support_entries = {}
        for label, key in support_features:
            row_frame = tk.Frame(community_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            self.support_entries[key] = tk.BooleanVar()
            support_check = tk.Checkbutton(row_frame, text=label,
                                          variable=self.support_entries[key], bg='white')
            support_check.pack(side='left')

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_community_support_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_performance_tab(self) -> None:
        """Performans Metrikleri sekmesi"""
        performance_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(performance_frame, text=" Performans")

        form_frame = tk.Frame(performance_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Performans Metrikleri
        performance_group = tk.LabelFrame(form_frame, text=" Performans Metrikleri",
                                         font=('Segoe UI', 12, 'bold'), bg='white')
        performance_group.pack(fill='x', pady=(0, 20))

        performance_metrics = [
            ("Acil Müdahale Süresi (Dakika):", "emergency_response_time_minutes"),
            ("İş Kurtarma Süresi (Saat):", "business_recovery_time_hours"),
            ("Çalışan Güvenlik Olayı:", "employee_safety_incidents"),
            ("Plan Etkinlik Skoru (1-10):", "plan_effectiveness_score")
        ]

        self.performance_entries = {}
        for label, key in performance_metrics:
            row_frame = tk.Frame(performance_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.performance_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_performance_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    # Kaydetme metodları
    def save_emergency_plans_data(self) -> None:
        """Acil durum planları verilerini kaydet"""
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
                'emergency_response_plan': self.plan_vars['emergency_response_plan'].get(),
                'business_continuity_plan': self.plan_vars['business_continuity_plan'].get(),
                'disaster_recovery_plan': self.plan_vars['disaster_recovery_plan'].get(),
                'crisis_communication_plan': self.plan_vars['crisis_communication_plan'].get(),
                'plan_last_updated': self.plan_update_entry.get(),
                'plan_testing_frequency': self.test_frequency_combo.get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'emergency_response_plan', 'business_continuity_plan', 'disaster_recovery_plan',
                'crisis_communication_plan', 'plan_last_updated', 'plan_testing_frequency'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Acil durum planları verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_risk_assessment_data(self) -> None:
        """Risk değerlendirmesi verilerini kaydet"""
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
                'risk_assessment_conducted': self.risk_assessment_var.get(),
                'risk_assessment_frequency': self.assessment_frequency_combo.get(),
                'identified_risks_count': int(self.risk_entries['identified_risks_count'].get() or 0),
                'high_risk_scenarios': int(self.risk_entries['high_risk_scenarios'].get() or 0),
                'risk_mitigation_measures': int(self.risk_entries['risk_mitigation_measures'].get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'risk_assessment_conducted', 'risk_assessment_frequency', 'identified_risks_count',
                'high_risk_scenarios', 'risk_mitigation_measures'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Risk değerlendirmesi verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_team_training_data(self) -> None:
        """Ekip ve eğitim verilerini kaydet"""
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
                'emergency_response_team_size': int(self.team_entries['emergency_response_team_size'].get() or 0),
                'emergency_coordinator_appointed': self.team_entries['emergency_coordinator_appointed'].get(),
                'emergency_training_hours': int(self.team_entries['emergency_training_hours'].get() or 0),
                'emergency_drill_frequency': self.drill_frequency_combo.get(),
                'last_emergency_drill_date': self.last_drill_entry.get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'emergency_response_team_size', 'emergency_coordinator_appointed', 'emergency_training_hours',
                'emergency_drill_frequency', 'last_emergency_drill_date'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Ekip ve eğitim verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_communication_data(self) -> None:
        """İletişim verilerini kaydet"""
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
                'emergency_communication_system': self.comm_system_var.get(),
                'alert_system_technology': self.alert_tech_combo.get(),
                'stakeholder_notification_system': self.stakeholder_notification_var.get(),
                'backup_communication_methods': self.backup_comm_text.get('1.0', tk.END).strip()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'emergency_communication_system', 'alert_system_technology', 'stakeholder_notification_system',
                'backup_communication_methods'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "İletişim verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_resources_data(self) -> None:
        """Kaynak verilerini kaydet"""
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
                'emergency_supplies_stocked': self.supplies_stocked_var.get(),
                'emergency_facilities_count': int(self.facilities_entry.get() or 0),
                'backup_power_systems': self.backup_power_var.get(),
                'water_emergency_supply_days': int(self.water_supply_entry.get() or 0),
                'food_emergency_supply_days': int(self.food_supply_entry.get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'emergency_supplies_stocked', 'emergency_facilities_count', 'backup_power_systems',
                'water_emergency_supply_days', 'food_emergency_supply_days'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Kaynak verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_business_continuity_data(self) -> None:
        """İş sürekliliği verilerini kaydet"""
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
                'business_continuity_testing': self.continuity_entries['business_continuity_testing'].get(),
                'backup_data_center': self.continuity_entries['backup_data_center'].get(),
                'remote_work_capability': float(self.continuity_entries['remote_work_capability'].get() or 0),
                'supply_chain_risk_mitigation': self.continuity_entries['supply_chain_risk_mitigation'].get(),
                'critical_process_identification': self.continuity_entries['critical_process_identification'].get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'business_continuity_testing', 'backup_data_center', 'remote_work_capability',
                'supply_chain_risk_mitigation', 'critical_process_identification'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "İş sürekliliği verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_financial_preparedness_data(self) -> None:
        """Finansal hazırlık verilerini kaydet"""
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
                'emergency_fund_available': self.emergency_fund_var.get(),
                'emergency_fund_amount': float(self.fund_amount_entry.get() or 0),
                'insurance_coverage_adequate': self.insurance_adequate_var.get(),
                'business_interruption_insurance': self.business_interruption_var.get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'emergency_fund_available', 'emergency_fund_amount', 'insurance_coverage_adequate',
                'business_interruption_insurance'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Finansal hazırlık verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_community_support_data(self) -> None:
        """Toplum desteği verilerini kaydet"""
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
                'community_emergency_support': self.support_entries['community_emergency_support'].get(),
                'environmental_impact_assessment': self.support_entries['environmental_impact_assessment'].get(),
                'local_authority_coordination': self.support_entries['local_authority_coordination'].get(),
                'volunteer_network_established': self.support_entries['volunteer_network_established'].get()
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'community_emergency_support', 'environmental_impact_assessment', 'local_authority_coordination',
                'volunteer_network_established'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Toplum desteği verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_performance_data(self) -> None:
        """Performans verilerini kaydet"""
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
                'emergency_response_time_minutes': int(
                    self.performance_entries['emergency_response_time_minutes'].get() or 0
                ),
                'business_recovery_time_hours': int(
                    self.performance_entries['business_recovery_time_hours'].get() or 0
                ),
                'employee_safety_incidents': int(self.performance_entries['employee_safety_incidents'].get() or 0),
                'plan_effectiveness_score': float(self.performance_entries['plan_effectiveness_score'].get() or 0)
            }

            # Mevcut kaydı kontrol et ve güncelle/ekle
            self._save_or_update_record(cursor, 'emergency_management_metrics', data, [
                'emergency_response_time_minutes', 'business_recovery_time_hours', 'employee_safety_incidents',
                'plan_effectiveness_score'
            ])

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Performans verileri kaydedildi!")

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
                SELECT * FROM emergency_management_metrics 
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
