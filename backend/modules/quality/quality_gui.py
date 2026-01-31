"""
Ürün Kalitesi ve Müşteri Memnuniyeti Modülü
SDG 12: Responsible Consumption and Production
"""

import logging
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from config.icons import Icons


class QualityGUI:
    def __init__(self, parent, company_id) -> None:
        self.parent = parent
        self.company_id = company_id
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sdg_desktop.sqlite")

        # Veritabanı tablosunu oluştur
        self.create_table()

        # GUI'yi oluştur
        self.create_gui()

        # Verileri yükle
        self.load_data()

    def create_table(self) -> None:
        """Ürün Kalitesi ve Müşteri Memnuniyeti tablosunu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    year INTEGER,
                    quarter INTEGER,
                    
                    -- Kalite Yönetim Sistemi
                    iso9001_certified BOOLEAN,
                    iso9001_certification_date TEXT,
                    other_quality_certifications TEXT,
                    quality_management_system TEXT,
                    
                    -- Ürün Kalite Metrikleri
                    product_defect_rate REAL,
                    customer_complaint_rate REAL,
                    product_recall_count INTEGER,
                    warranty_claim_rate REAL,
                    first_pass_yield REAL,
                    
                    -- Müşteri Memnuniyeti
                    customer_satisfaction_score REAL,
                    net_promoter_score REAL,
                    customer_retention_rate REAL,
                    customer_surveys_conducted INTEGER,
                    response_rate REAL,
                    
                    -- Kalite Kontrol Süreçleri
                    quality_control_processes TEXT,
                    inspection_frequency TEXT,
                    testing_methods TEXT,
                    quality_audit_count INTEGER,
                    non_conformance_reports INTEGER,
                    
                    -- Tedarikçi Kalitesi
                    supplier_quality_score REAL,
                    supplier_audit_count INTEGER,
                    supplier_certification_rate REAL,
                    incoming_inspection_rate REAL,
                    
                    -- Süreç İyileştirme
                    process_improvement_projects INTEGER,
                    six_sigma_projects INTEGER,
                    lean_projects INTEGER,
                    cost_of_quality REAL,
                    
                    -- Eğitim ve Yetkinlik
                    quality_training_hours INTEGER,
                    certified_quality_personnel INTEGER,
                    training_programs_conducted INTEGER,
                    
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
        title_frame = tk.Frame(main_frame, bg='#4169E1', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=f"{Icons.STAR} Ürün Kalitesi ve Müşteri Memnuniyeti",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#4169E1')
        title_label.pack(expand=True)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_quality_system_tab()
        self.create_product_quality_tab()
        self.create_customer_satisfaction_tab()
        self.create_quality_control_tab()
        self.create_supplier_quality_tab()
        self.create_process_improvement_tab()
        self.create_training_tab()

    def create_quality_system_tab(self) -> None:
        """Kalite Yönetim Sistemi sekmesi"""
        system_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(system_frame, text=" Kalite Yönetim Sistemi")

        # Form alanları
        form_frame = tk.Frame(system_frame, bg='white')
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

        # Kalite Sertifikaları
        cert_frame = tk.LabelFrame(form_frame, text=" Kalite Sertifikaları",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        cert_frame.pack(fill='x', pady=(0, 20))

        # ISO 9001
        iso_frame = tk.Frame(cert_frame, bg='white')
        iso_frame.pack(fill='x', pady=10)

        self.iso9001_var = tk.BooleanVar()
        iso_check = tk.Checkbutton(iso_frame, text="ISO 9001 Sertifikalı",
                                  variable=self.iso9001_var, bg='white')
        iso_check.pack(side='left')

        tk.Label(iso_frame, text="Sertifika Tarihi:", bg='white').pack(side='left', padx=(20, 5))
        self.iso_date_entry = tk.Entry(iso_frame, width=15)
        self.iso_date_entry.pack(side='left', padx=(0, 10))

        # Diğer Sertifikalar
        tk.Label(cert_frame, text="Diğer Kalite Sertifikaları:", bg='white').pack(anchor='w', pady=(10, 5))
        self.other_cert_text = tk.Text(cert_frame, height=3, width=50)
        self.other_cert_text.pack(fill='x', pady=(0, 10))

        # Kalite Yönetim Sistemi
        tk.Label(cert_frame, text="Kalite Yönetim Sistemi:", bg='white').pack(anchor='w', pady=(10, 5))
        self.qms_combo = ttk.Combobox(cert_frame, values=[
            "ISO 9001:2015", "TS 16949", "ISO 14001", "AS9100", "Diğer"
        ], width=30)
        self.qms_combo.pack(anchor='w', pady=(0, 10))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_quality_system_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_product_quality_tab(self) -> None:
        """Ürün Kalite Metrikleri sekmesi"""
        product_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(product_frame, text=" Ürün Kalitesi")

        form_frame = tk.Frame(product_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Ürün Kalite Metrikleri
        metrics_group = tk.LabelFrame(form_frame, text=" Ürün Kalite Metrikleri",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        metrics_group.pack(fill='x', pady=(0, 20))

        quality_fields = [
            ("Ürün Hata Oranı (%):", "product_defect_rate"),
            ("Müşteri Şikayet Oranı (%):", "customer_complaint_rate"),
            ("Ürün Geri Çağırma Sayısı:", "product_recall_count"),
            ("Garanti Talebi Oranı (%):", "warranty_claim_rate"),
            ("İlk Geçiş Başarı Oranı (%):", "first_pass_yield")
        ]

        self.quality_entries = {}
        for label, key in quality_fields:
            row_frame = tk.Frame(metrics_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.quality_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_product_quality_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_customer_satisfaction_tab(self) -> None:
        """Müşteri Memnuniyeti sekmesi"""
        customer_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(customer_frame, text=" Müşteri Memnuniyeti")

        form_frame = tk.Frame(customer_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Müşteri Memnuniyeti Metrikleri
        satisfaction_group = tk.LabelFrame(form_frame, text=" Müşteri Memnuniyeti Metrikleri",
                                          font=('Segoe UI', 12, 'bold'), bg='white')
        satisfaction_group.pack(fill='x', pady=(0, 20))

        satisfaction_fields = [
            ("Müşteri Memnuniyet Skoru (1-10):", "customer_satisfaction_score"),
            ("Net Promoter Score (NPS):", "net_promoter_score"),
            ("Müşteri Sadakat Oranı (%):", "customer_retention_rate"),
            ("Yapılan Müşteri Anketi Sayısı:", "customer_surveys_conducted"),
            ("Anket Yanıt Oranı (%):", "response_rate")
        ]

        self.satisfaction_entries = {}
        for label, key in satisfaction_fields:
            row_frame = tk.Frame(satisfaction_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.satisfaction_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_customer_satisfaction_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_quality_control_tab(self) -> None:
        """Kalite Kontrol Süreçleri sekmesi"""
        control_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(control_frame, text=" Kalite Kontrol")

        form_frame = tk.Frame(control_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Kalite Kontrol Süreçleri
        control_group = tk.LabelFrame(form_frame, text=" Kalite Kontrol Süreçleri",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        control_group.pack(fill='x', pady=(0, 20))

        # Süreç açıklaması
        tk.Label(control_group, text="Kalite Kontrol Süreçleri:", bg='white').pack(anchor='w', pady=(10, 5))
        self.processes_text = tk.Text(control_group, height=3, width=50)
        self.processes_text.pack(fill='x', pady=(0, 10))

        # Kontrol alanları
        control_fields = [
            ("Kontrol Sıklığı:", "inspection_frequency"),
            ("Test Yöntemleri:", "testing_methods"),
            ("Kalite Denetim Sayısı:", "quality_audit_count"),
            ("Uygunsuzluk Raporu Sayısı:", "non_conformance_reports")
        ]

        self.control_entries = {}
        for label, key in control_fields:
            row_frame = tk.Frame(control_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.control_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), command=self.save_quality_control_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_supplier_quality_tab(self) -> None:
        """Tedarikçi Kalitesi sekmesi"""
        supplier_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(supplier_frame, text=" Tedarikçi Kalitesi")

        form_frame = tk.Frame(supplier_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Tedarikçi Kalitesi
        supplier_group = tk.LabelFrame(form_frame, text=" Tedarikçi Kalitesi",
                                      font=('Segoe UI', 12, 'bold'), bg='white')
        supplier_group.pack(fill='x', pady=(0, 20))

        supplier_fields = [
            ("Tedarikçi Kalite Skoru (1-10):", "supplier_quality_score"),
            ("Tedarikçi Denetim Sayısı:", "supplier_audit_count"),
            ("Tedarikçi Sertifikasyon Oranı (%):", "supplier_certification_rate"),
            ("Gelen Malzeme Kontrol Oranı (%):", "incoming_inspection_rate")
        ]

        self.supplier_entries = {}
        for label, key in supplier_fields:
            row_frame = tk.Frame(supplier_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.supplier_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_supplier_quality_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_process_improvement_tab(self) -> None:
        """Süreç İyileştirme sekmesi"""
        improvement_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(improvement_frame, text=" Süreç İyileştirme")

        form_frame = tk.Frame(improvement_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Süreç İyileştirme
        improvement_group = tk.LabelFrame(form_frame, text=" Süreç İyileştirme",
                                         font=('Segoe UI', 12, 'bold'), bg='white')
        improvement_group.pack(fill='x', pady=(0, 20))

        improvement_fields = [
            ("Süreç İyileştirme Projeleri:", "process_improvement_projects"),
            ("Six Sigma Projeleri:", "six_sigma_projects"),
            ("Lean Projeleri:", "lean_projects"),
            ("Kalite Maliyeti (TL):", "cost_of_quality")
        ]

        self.improvement_entries = {}
        for label, key in improvement_fields:
            row_frame = tk.Frame(improvement_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.improvement_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_process_improvement_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_training_tab(self) -> None:
        """Eğitim ve Yetkinlik sekmesi"""
        training_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(training_frame, text=" Eğitim & Yetkinlik")

        form_frame = tk.Frame(training_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Eğitim ve Yetkinlik
        training_group = tk.LabelFrame(form_frame, text=" Eğitim ve Yetkinlik",
                                      font=('Segoe UI', 12, 'bold'), bg='white')
        training_group.pack(fill='x', pady=(0, 20))

        training_fields = [
            ("Kalite Eğitim Saati:", "quality_training_hours"),
            ("Sertifikalı Kalite Personeli:", "certified_quality_personnel"),
            ("Düzenlenen Eğitim Programı:", "training_programs_conducted")
        ]

        self.training_entries = {}
        for label, key in training_fields:
            row_frame = tk.Frame(training_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.training_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_training_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def save_quality_system_data(self) -> None:
        """Kalite yönetim sistemi verilerini kaydet"""
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
                'iso9001_certified': self.iso9001_var.get(),
                'iso9001_certification_date': self.iso_date_entry.get(),
                'other_quality_certifications': self.other_cert_text.get('1.0', tk.END).strip(),
                'quality_management_system': self.qms_combo.get()
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        iso9001_certified = ?, iso9001_certification_date = ?,
                        other_quality_certifications = ?, quality_management_system = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['iso9001_certified'], data['iso9001_certification_date'],
                      data['other_quality_certifications'], data['quality_management_system'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, iso9001_certified, iso9001_certification_date,
                     other_quality_certifications, quality_management_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['iso9001_certified'], data['iso9001_certification_date'],
                      data['other_quality_certifications'], data['quality_management_system']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Kalite yönetim sistemi verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_product_quality_data(self) -> None:
        """Ürün kalite verilerini kaydet"""
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
                'product_defect_rate': float(self.quality_entries['product_defect_rate'].get() or 0),
                'customer_complaint_rate': float(self.quality_entries['customer_complaint_rate'].get() or 0),
                'product_recall_count': int(self.quality_entries['product_recall_count'].get() or 0),
                'warranty_claim_rate': float(self.quality_entries['warranty_claim_rate'].get() or 0),
                'first_pass_yield': float(self.quality_entries['first_pass_yield'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        product_defect_rate = ?, customer_complaint_rate = ?,
                        product_recall_count = ?, warranty_claim_rate = ?,
                        first_pass_yield = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['product_defect_rate'], data['customer_complaint_rate'],
                      data['product_recall_count'], data['warranty_claim_rate'],
                      data['first_pass_yield'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, product_defect_rate, customer_complaint_rate,
                     product_recall_count, warranty_claim_rate, first_pass_yield)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['product_defect_rate'], data['customer_complaint_rate'],
                      data['product_recall_count'], data['warranty_claim_rate'],
                      data['first_pass_yield']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Ürün kalite verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_customer_satisfaction_data(self) -> None:
        """Müşteri memnuniyet verilerini kaydet"""
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
                'customer_satisfaction_score': float(self.satisfaction_entries['customer_satisfaction_score'].get() or 0),
                'net_promoter_score': float(self.satisfaction_entries['net_promoter_score'].get() or 0),
                'customer_retention_rate': float(self.satisfaction_entries['customer_retention_rate'].get() or 0),
                'customer_surveys_conducted': int(self.satisfaction_entries['customer_surveys_conducted'].get() or 0),
                'response_rate': float(self.satisfaction_entries['response_rate'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        customer_satisfaction_score = ?, net_promoter_score = ?,
                        customer_retention_rate = ?, customer_surveys_conducted = ?,
                        response_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['customer_satisfaction_score'], data['net_promoter_score'],
                      data['customer_retention_rate'], data['customer_surveys_conducted'],
                      data['response_rate'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, customer_satisfaction_score, net_promoter_score,
                     customer_retention_rate, customer_surveys_conducted, response_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['customer_satisfaction_score'], data['net_promoter_score'],
                      data['customer_retention_rate'], data['customer_surveys_conducted'],
                      data['response_rate']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Müşteri memnuniyet verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_quality_control_data(self) -> None:
        """Kalite kontrol verilerini kaydet"""
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
                'quality_control_processes': self.processes_text.get('1.0', tk.END).strip(),
                'inspection_frequency': self.control_entries['inspection_frequency'].get(),
                'testing_methods': self.control_entries['testing_methods'].get(),
                'quality_audit_count': int(self.control_entries['quality_audit_count'].get() or 0),
                'non_conformance_reports': int(self.control_entries['non_conformance_reports'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        quality_control_processes = ?, inspection_frequency = ?,
                        testing_methods = ?, quality_audit_count = ?,
                        non_conformance_reports = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['quality_control_processes'], data['inspection_frequency'],
                      data['testing_methods'], data['quality_audit_count'],
                      data['non_conformance_reports'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, quality_control_processes, inspection_frequency,
                     testing_methods, quality_audit_count, non_conformance_reports)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['quality_control_processes'], data['inspection_frequency'],
                      data['testing_methods'], data['quality_audit_count'],
                      data['non_conformance_reports']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Kalite kontrol verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_supplier_quality_data(self) -> None:
        """Tedarikçi kalite verilerini kaydet"""
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
                'supplier_quality_score': float(self.supplier_entries['supplier_quality_score'].get() or 0),
                'supplier_audit_count': int(self.supplier_entries['supplier_audit_count'].get() or 0),
                'supplier_certification_rate': float(self.supplier_entries['supplier_certification_rate'].get() or 0),
                'incoming_inspection_rate': float(self.supplier_entries['incoming_inspection_rate'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        supplier_quality_score = ?, supplier_audit_count = ?,
                        supplier_certification_rate = ?, incoming_inspection_rate = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['supplier_quality_score'], data['supplier_audit_count'],
                      data['supplier_certification_rate'], data['incoming_inspection_rate'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, supplier_quality_score, supplier_audit_count,
                     supplier_certification_rate, incoming_inspection_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['supplier_quality_score'], data['supplier_audit_count'],
                      data['supplier_certification_rate'], data['incoming_inspection_rate']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Tedarikçi kalite verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_process_improvement_data(self) -> None:
        """Süreç iyileştirme verilerini kaydet"""
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
                'process_improvement_projects': int(self.improvement_entries['process_improvement_projects'].get() or 0),
                'six_sigma_projects': int(self.improvement_entries['six_sigma_projects'].get() or 0),
                'lean_projects': int(self.improvement_entries['lean_projects'].get() or 0),
                'cost_of_quality': float(self.improvement_entries['cost_of_quality'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        process_improvement_projects = ?, six_sigma_projects = ?,
                        lean_projects = ?, cost_of_quality = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['process_improvement_projects'], data['six_sigma_projects'],
                      data['lean_projects'], data['cost_of_quality'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, process_improvement_projects, six_sigma_projects,
                     lean_projects, cost_of_quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['process_improvement_projects'], data['six_sigma_projects'],
                      data['lean_projects'], data['cost_of_quality']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Süreç iyileştirme verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_training_data(self) -> None:
        """Eğitim verilerini kaydet"""
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
                'quality_training_hours': int(self.training_entries['quality_training_hours'].get() or 0),
                'certified_quality_personnel': int(self.training_entries['certified_quality_personnel'].get() or 0),
                'training_programs_conducted': int(self.training_entries['training_programs_conducted'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM quality_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE quality_metrics SET
                        quality_training_hours = ?, certified_quality_personnel = ?,
                        training_programs_conducted = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['quality_training_hours'], data['certified_quality_personnel'],
                      data['training_programs_conducted'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (company_id, year, quarter, quality_training_hours, certified_quality_personnel,
                     training_programs_conducted)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['quality_training_hours'], data['certified_quality_personnel'],
                      data['training_programs_conducted']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Eğitim verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def load_data(self) -> None:
        """Mevcut verileri yükle"""
        try:
            year = int(self.year_var.get())
            quarter = int(self.quarter_var.get())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM quality_metrics 
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
