"""
AR-GE ve İnovasyon Modülü
SDG 9: Industry, Innovation and Infrastructure
"""

import logging
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


class InnovationGUI:
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
        """AR-GE ve İnovasyon tablosunu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS innovation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    year INTEGER,
                    quarter INTEGER,
                    
                    -- AR-GE Yatırımları
                    rnd_budget_total REAL,
                    rnd_budget_percentage REAL,
                    rnd_employees INTEGER,
                    rnd_projects_active INTEGER,
                    
                    -- Patent ve Fikri Mülkiyet
                    patents_applied INTEGER,
                    patents_granted INTEGER,
                    utility_models INTEGER,
                    trademarks INTEGER,
                    copyrights INTEGER,
                    
                    -- İnovasyon Projeleri
                    innovation_projects INTEGER,
                    eco_design_projects INTEGER,
                    lca_studies INTEGER,
                    sustainability_innovation_budget REAL,
                    
                    -- Teknoloji Transferi
                    technology_transfer_agreements INTEGER,
                    research_collaborations INTEGER,
                    university_partnerships INTEGER,
                    startup_investments INTEGER,
                    
                    -- Dijital İnovasyon
                    ai_projects INTEGER,
                    iot_implementations INTEGER,
                    blockchain_projects INTEGER,
                    automation_projects INTEGER,
                    
                    -- İnovasyon Metrikleri
                    innovation_index REAL,
                    time_to_market_days INTEGER,
                    innovation_success_rate REAL,
                    
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
        title_frame = tk.Frame(main_frame, bg='#2E8B57', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" AR-GE ve İnovasyon Modülü",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2E8B57')
        title_label.pack(expand=True)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeleri oluştur
        self.create_rnd_tab()
        self.create_patents_tab()
        self.create_innovation_tab()
        self.create_technology_tab()
        self.create_digital_tab()
        self.create_metrics_tab()

    def create_rnd_tab(self) -> None:
        """AR-GE Yatırımları sekmesi"""
        rnd_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(rnd_frame, text=" AR-GE Yatırımları")

        # Form alanları
        form_frame = tk.Frame(rnd_frame, bg='white')
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

        # AR-GE Bütçe Bilgileri
        budget_frame = tk.LabelFrame(form_frame, text=" AR-GE Bütçe Bilgileri",
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        budget_frame.pack(fill='x', pady=(0, 20))

        # Bütçe alanları
        budget_fields = [
            ("Toplam AR-GE Bütçesi (TL):", "rnd_budget_total"),
            ("Ciro İçindeki AR-GE Oranı (%):", "rnd_budget_percentage"),
            ("AR-GE Çalışan Sayısı:", "rnd_employees"),
            ("Aktif AR-GE Proje Sayısı:", "rnd_projects_active")
        ]

        self.rnd_entries = {}
        for i, (label, key) in enumerate(budget_fields):
            row_frame = tk.Frame(budget_frame, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.rnd_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_rnd_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_patents_tab(self) -> None:
        """Patent ve Fikri Mülkiyet sekmesi"""
        patents_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(patents_frame, text=" Patent & Fikri Mülkiyet")

        form_frame = tk.Frame(patents_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Patent Bilgileri
        patents_group = tk.LabelFrame(form_frame, text=" Patent Bilgileri",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        patents_group.pack(fill='x', pady=(0, 20))

        patent_fields = [
            ("Patent Başvuru Sayısı:", "patents_applied"),
            ("Verilen Patent Sayısı:", "patents_granted"),
            ("Faydalı Model Sayısı:", "utility_models"),
            ("Marka Tescili Sayısı:", "trademarks"),
            ("Telif Hakkı Sayısı:", "copyrights")
        ]

        self.patent_entries = {}
        for label, key in patent_fields:
            row_frame = tk.Frame(patents_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.patent_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_patent_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_innovation_tab(self) -> None:
        """İnovasyon Projeleri sekmesi"""
        innovation_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(innovation_frame, text=" İnovasyon Projeleri")

        form_frame = tk.Frame(innovation_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # İnovasyon Projeleri
        innovation_group = tk.LabelFrame(form_frame, text=" İnovasyon Projeleri",
                                        font=('Segoe UI', 12, 'bold'), bg='white')
        innovation_group.pack(fill='x', pady=(0, 20))

        innovation_fields = [
            ("Toplam İnovasyon Projesi:", "innovation_projects"),
            ("Eko-Tasarım Projeleri:", "eco_design_projects"),
            ("LCA Çalışması Sayısı:", "lca_studies"),
            ("Sürdürülebilirlik İnovasyon Bütçesi (TL):", "sustainability_innovation_budget")
        ]

        self.innovation_entries = {}
        for label, key in innovation_fields:
            row_frame = tk.Frame(innovation_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=30, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.innovation_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_innovation_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_technology_tab(self) -> None:
        """Teknoloji Transferi sekmesi"""
        tech_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tech_frame, text=" Teknoloji Transferi")

        form_frame = tk.Frame(tech_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Teknoloji Transferi
        tech_group = tk.LabelFrame(form_frame, text=" Teknoloji Transferi",
                                  font=('Segoe UI', 12, 'bold'), bg='white')
        tech_group.pack(fill='x', pady=(0, 20))

        tech_fields = [
            ("Teknoloji Transfer Anlaşması:", "technology_transfer_agreements"),
            ("Araştırma İşbirliği:", "research_collaborations"),
            ("Üniversite Ortaklığı:", "university_partnerships"),
            ("Startup Yatırımı:", "startup_investments")
        ]

        self.tech_entries = {}
        for label, key in tech_fields:
            row_frame = tk.Frame(tech_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.tech_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_tech_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_digital_tab(self) -> None:
        """Dijital İnovasyon sekmesi"""
        digital_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(digital_frame, text=" Dijital İnovasyon")

        form_frame = tk.Frame(digital_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Dijital İnovasyon
        digital_group = tk.LabelFrame(form_frame, text=" Dijital İnovasyon",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        digital_group.pack(fill='x', pady=(0, 20))

        digital_fields = [
            ("AI Projeleri:", "ai_projects"),
            ("IoT Uygulamaları:", "iot_implementations"),
            ("Blockchain Projeleri:", "blockchain_projects"),
            ("Otomasyon Projeleri:", "automation_projects")
        ]

        self.digital_entries = {}
        for label, key in digital_fields:
            row_frame = tk.Frame(digital_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.digital_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_digital_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def create_metrics_tab(self) -> None:
        """İnovasyon Metrikleri sekmesi"""
        metrics_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(metrics_frame, text=" İnovasyon Metrikleri")

        form_frame = tk.Frame(metrics_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # İnovasyon Metrikleri
        metrics_group = tk.LabelFrame(form_frame, text=" İnovasyon Metrikleri",
                                     font=('Segoe UI', 12, 'bold'), bg='white')
        metrics_group.pack(fill='x', pady=(0, 20))

        metrics_fields = [
            ("İnovasyon İndeksi (0-100):", "innovation_index"),
            ("Pazara Çıkış Süresi (Gün):", "time_to_market_days"),
            ("İnovasyon Başarı Oranı (%):", "innovation_success_rate")
        ]

        self.metrics_entries = {}
        for label, key in metrics_fields:
            row_frame = tk.Frame(metrics_group, bg='white')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label, width=25, anchor='w', bg='white').pack(side='left')
            entry = tk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=(10, 0))
            self.metrics_entries[key] = entry

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=" Kaydet", command=self.save_metrics_data,
                            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=20)

    def save_rnd_data(self) -> None:
        """AR-GE verilerini kaydet"""
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
                'rnd_budget_total': float(self.rnd_entries['rnd_budget_total'].get() or 0),
                'rnd_budget_percentage': float(self.rnd_entries['rnd_budget_percentage'].get() or 0),
                'rnd_employees': int(self.rnd_entries['rnd_employees'].get() or 0),
                'rnd_projects_active': int(self.rnd_entries['rnd_projects_active'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM innovation_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE innovation_metrics SET
                        rnd_budget_total = ?, rnd_budget_percentage = ?,
                        rnd_employees = ?, rnd_projects_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['rnd_budget_total'], data['rnd_budget_percentage'],
                      data['rnd_employees'], data['rnd_projects_active'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO innovation_metrics 
                    (company_id, year, quarter, rnd_budget_total, rnd_budget_percentage,
                     rnd_employees, rnd_projects_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['rnd_budget_total'], data['rnd_budget_percentage'],
                      data['rnd_employees'], data['rnd_projects_active']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "AR-GE verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_patent_data(self) -> None:
        """Patent verilerini kaydet"""
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
                'patents_applied': int(self.patent_entries['patents_applied'].get() or 0),
                'patents_granted': int(self.patent_entries['patents_granted'].get() or 0),
                'utility_models': int(self.patent_entries['utility_models'].get() or 0),
                'trademarks': int(self.patent_entries['trademarks'].get() or 0),
                'copyrights': int(self.patent_entries['copyrights'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM innovation_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE innovation_metrics SET
                        patents_applied = ?, patents_granted = ?, utility_models = ?,
                        trademarks = ?, copyrights = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['patents_applied'], data['patents_granted'], data['utility_models'],
                      data['trademarks'], data['copyrights'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO innovation_metrics 
                    (company_id, year, quarter, patents_applied, patents_granted,
                     utility_models, trademarks, copyrights)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['patents_applied'], data['patents_granted'], data['utility_models'],
                      data['trademarks'], data['copyrights']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Patent verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_innovation_data(self) -> None:
        """İnovasyon verilerini kaydet"""
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
                'innovation_projects': int(self.innovation_entries['innovation_projects'].get() or 0),
                'eco_design_projects': int(self.innovation_entries['eco_design_projects'].get() or 0),
                'lca_studies': int(self.innovation_entries['lca_studies'].get() or 0),
                'sustainability_innovation_budget': float(self.innovation_entries['sustainability_innovation_budget'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM innovation_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE innovation_metrics SET
                        innovation_projects = ?, eco_design_projects = ?,
                        lca_studies = ?, sustainability_innovation_budget = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['innovation_projects'], data['eco_design_projects'],
                      data['lca_studies'], data['sustainability_innovation_budget'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO innovation_metrics 
                    (company_id, year, quarter, innovation_projects, eco_design_projects,
                     lca_studies, sustainability_innovation_budget)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['innovation_projects'], data['eco_design_projects'],
                      data['lca_studies'], data['sustainability_innovation_budget']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "İnovasyon verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_tech_data(self) -> None:
        """Teknoloji transfer verilerini kaydet"""
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
                'technology_transfer_agreements': int(self.tech_entries['technology_transfer_agreements'].get() or 0),
                'research_collaborations': int(self.tech_entries['research_collaborations'].get() or 0),
                'university_partnerships': int(self.tech_entries['university_partnerships'].get() or 0),
                'startup_investments': int(self.tech_entries['startup_investments'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM innovation_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE innovation_metrics SET
                        technology_transfer_agreements = ?, research_collaborations = ?,
                        university_partnerships = ?, startup_investments = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['technology_transfer_agreements'], data['research_collaborations'],
                      data['university_partnerships'], data['startup_investments'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO innovation_metrics 
                    (company_id, year, quarter, technology_transfer_agreements,
                     research_collaborations, university_partnerships, startup_investments)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['technology_transfer_agreements'], data['research_collaborations'],
                      data['university_partnerships'], data['startup_investments']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Teknoloji transfer verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_digital_data(self) -> None:
        """Dijital inovasyon verilerini kaydet"""
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
                'ai_projects': int(self.digital_entries['ai_projects'].get() or 0),
                'iot_implementations': int(self.digital_entries['iot_implementations'].get() or 0),
                'blockchain_projects': int(self.digital_entries['blockchain_projects'].get() or 0),
                'automation_projects': int(self.digital_entries['automation_projects'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM innovation_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE innovation_metrics SET
                        ai_projects = ?, iot_implementations = ?,
                        blockchain_projects = ?, automation_projects = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['ai_projects'], data['iot_implementations'],
                      data['blockchain_projects'], data['automation_projects'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO innovation_metrics 
                    (company_id, year, quarter, ai_projects, iot_implementations,
                     blockchain_projects, automation_projects)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['ai_projects'], data['iot_implementations'],
                      data['blockchain_projects'], data['automation_projects']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Dijital inovasyon verileri kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydetme hatası: {e}")

    def save_metrics_data(self) -> None:
        """İnovasyon metriklerini kaydet"""
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
                'innovation_index': float(self.metrics_entries['innovation_index'].get() or 0),
                'time_to_market_days': int(self.metrics_entries['time_to_market_days'].get() or 0),
                'innovation_success_rate': float(self.metrics_entries['innovation_success_rate'].get() or 0)
            }

            # Mevcut kaydı kontrol et
            cursor.execute('''
                SELECT id FROM innovation_metrics 
                WHERE company_id = ? AND year = ? AND quarter = ?
            ''', (self.company_id, year, quarter))

            existing = cursor.fetchone()

            if existing:
                # Güncelle
                cursor.execute('''
                    UPDATE innovation_metrics SET
                        innovation_index = ?, time_to_market_days = ?,
                        innovation_success_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data['innovation_index'], data['time_to_market_days'],
                      data['innovation_success_rate'], existing[0]))
            else:
                # Yeni kayıt
                cursor.execute('''
                    INSERT INTO innovation_metrics 
                    (company_id, year, quarter, innovation_index, time_to_market_days,
                     innovation_success_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['company_id'], data['year'], data['quarter'],
                      data['innovation_index'], data['time_to_market_days'],
                      data['innovation_success_rate']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "İnovasyon metrikleri kaydedildi!")

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
                SELECT * FROM innovation_metrics 
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
