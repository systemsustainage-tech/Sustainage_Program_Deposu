#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Şirket Bilgileri Yönetim GUI
TSRS raporları için kapsamlı şirket bilgileri
"""

import logging
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import List

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme


class CompanyInfoGUI:
    """Şirket Bilgileri Yönetim GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()

        # Database path
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')

        self.setup_ui()
        self.load_company_data()

    def setup_ui(self) -> None:
        """UI oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#1e40af', height=60)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=self.lm.tr('company_info_header', " Şirket Bilgileri Yönetimi"),
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#1e40af').pack(side='left', padx=20, pady=15)

        # Ana içerik
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        # Sekmeler
        self.create_basic_info_tab()
        self.create_legal_info_tab()
        self.create_financial_info_tab()
        self.create_sustainability_info_tab()
        self.create_contact_info_tab()

        # Alt toolbar
        self.create_toolbar()

    def create_toolbar(self) -> None:
        """Alt toolbar oluştur"""
        toolbar_frame = tk.Frame(self.parent, bg='#e9ecef', height=50)
        toolbar_frame.pack(fill='x', side='bottom')
        toolbar_frame.pack_propagate(False)

        # Butonlar
        ttk.Button(toolbar_frame, text=self.lm.tr('btn_save', " Kaydet"), style='Primary.TButton',
                   command=self.save_company_data).pack(side='left', padx=(20, 10), pady=10)

        ttk.Button(toolbar_frame, text=self.lm.tr('btn_refresh', " Yenile"), style='Primary.TButton',
                   command=self.load_company_data).pack(side='left', padx=10, pady=10)

        ttk.Button(toolbar_frame, text=self.lm.tr('btn_tsrs_preview', " TSRS Önizleme"), style='Primary.TButton',
                   command=self.preview_tsrs_header).pack(side='left', padx=10, pady=10)
        ttk.Button(toolbar_frame, text=self.lm.tr('btn_report_center', " Rapor Merkezi"), style='Primary.TButton',
                   command=self.open_report_center_company).pack(side='left', padx=10, pady=10)

    def open_report_center_company(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"{self.lm.tr('err_report_center_open', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def create_basic_info_tab(self) -> None:
        """Temel bilgiler sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('tab_basic', " Temel Bilgiler"))

        # Scrollable frame
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form alanları
        self.create_form_section(scrollable_frame, self.lm.tr('sec_basic', "Temel Bilgiler"), [
            ("name", self.lm.tr('lbl_company_name', "Şirket Adı"), "text", self.lm.tr('tip_company_name', "Şirketin ticari adı")),
            ("legal_name", self.lm.tr('lbl_legal_name', "Yasal Unvan"), "text", self.lm.tr('tip_legal_name', "Şirketin yasal unvanı")),
            ("trading_name", self.lm.tr('lbl_trading_name', "Ticari Unvan"), "text", self.lm.tr('tip_trading_name', "Ticaret unvanı")),
            ("description", self.lm.tr('lbl_description', "Şirket Açıklaması"), "text_area", self.lm.tr('tip_description', "Şirket hakkında kısa açıklama")),
            ("business_model", self.lm.tr('lbl_business_model', "İş Modeli"), "text", self.lm.tr('tip_business_model', "Ana iş modeli açıklaması")),
            ("key_products_services", self.lm.tr('lbl_products', "Ana Ürün/Hizmetler"), "text_area", self.lm.tr('tip_products', "Ana ürün ve hizmetler")),
            ("markets_served", self.lm.tr('lbl_markets', "Hizmet Verilen Pazarlar"), "text_area", self.lm.tr('tip_markets', "Pazar kapsamı"))
        ])

        self.create_form_section(scrollable_frame, self.lm.tr('sec_sector', "Sektör ve Büyüklük"), [
            ("sector", self.lm.tr('lbl_sector', "Sektör"), "text", self.lm.tr('tip_sector', "Ana faaliyet alanı")),
            ("industry_code", self.lm.tr('lbl_nace', "NACE Kodu"), "text", self.lm.tr('tip_nace', "NACE sektör kodu")),
            ("industry_description", self.lm.tr('lbl_sector_desc', "Sektör Açıklaması"), "text", self.lm.tr('tip_sector_desc', "Detaylı sektör açıklaması")),
            ("company_size", self.lm.tr('lbl_size', "Şirket Büyüklüğü"), "combo", self.lm.tr('tip_size', "Küçük/Orta/Büyük")),
            ("employee_count", self.lm.tr('lbl_employees', "Çalışan Sayısı"), "number", self.lm.tr('tip_employees', "Toplam çalışan sayısı")),
            ("isic_code", self.lm.tr('lbl_isic', "ISIC Kodu"), "text", self.lm.tr('tip_isic', "ISIC faaliyet kodu"))
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_legal_info_tab(self) -> None:
        """Yasal bilgiler sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('tab_legal', " Yasal Bilgiler"))

        # Scrollable frame
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form alanları
        self.create_form_section(scrollable_frame, self.lm.tr('sec_registration', "Kayıt Bilgileri"), [
            ("registration_number", self.lm.tr('lbl_reg_num', "Sicil Numarası"), "text", self.lm.tr('tip_reg_num', "Ticaret sicil numarası")),
            ("tax_number", self.lm.tr('lbl_tax_num', "Vergi Numarası"), "text", self.lm.tr('tip_tax_num', "Vergi kimlik numarası")),
            ("legal_form", self.lm.tr('lbl_legal_form', "Hukuki Şekil"), "text", self.lm.tr('tip_legal_form', "Anonim Şirket, Limited Şirket vb.")),
            ("establishment_date", self.lm.tr('lbl_est_date', "Kuruluş Tarihi"), "date", self.lm.tr('tip_est_date', "Şirket kuruluş tarihi")),
            ("ownership_type", self.lm.tr('lbl_ownership', "Mülkiyet Türü"), "combo", self.lm.tr('tip_ownership', "Halka Açık/Kapalı/Aile Şirketi")),
            ("parent_company", self.lm.tr('lbl_parent_company', "Ana Şirket"), "text", self.lm.tr('tip_parent_company', "Ana şirket bilgisi")),
            ("subsidiaries", self.lm.tr('lbl_subsidiaries', "Bağlı Şirketler"), "text_area", self.lm.tr('tip_subsidiaries', "Bağlı şirketler listesi"))
        ])

        self.create_form_section(scrollable_frame, self.lm.tr('sec_stock', "Borsa Bilgileri"), [
            ("stock_exchange", self.lm.tr('lbl_stock_exchange', "Borsa"), "text", self.lm.tr('tip_stock_exchange', "İşlem gördüğü borsa")),
            ("ticker_symbol", self.lm.tr('lbl_ticker', "Hisse Senedi Sembolü"), "text", self.lm.tr('tip_ticker', "Borsa sembolü")),
            ("fiscal_year_end", self.lm.tr('lbl_fiscal_end', "Mali Yıl Sonu"), "text", self.lm.tr('tip_fiscal_end', "Mali yıl kapanış tarihi")),
            ("reporting_period", self.lm.tr('lbl_report_period', "Raporlama Dönemi"), "text", self.lm.tr('tip_report_period', "Raporlama dönemi"))
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_financial_info_tab(self) -> None:
        """Mali bilgiler sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('tab_financial', " Mali Bilgiler"))

        # Scrollable frame
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form alanları
        self.create_form_section(scrollable_frame, self.lm.tr('sec_financial', "Finansal Bilgiler"), [
            ("annual_revenue", self.lm.tr('lbl_revenue', "Yıllık Ciro"), "number", self.lm.tr('tip_revenue', "Son mali yıl cirosu")),
            ("currency", self.lm.tr('lbl_currency', "Para Birimi"), "combo", "TRY/USD/EUR"),
            ("auditor", self.lm.tr('lbl_auditor', "Denetim Şirketi"), "text", self.lm.tr('tip_auditor', "Bağımsız denetim şirketi"))
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_sustainability_info_tab(self) -> None:
        """Sürdürülebilirlik bilgileri sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('tab_sustainability', " Sürdürülebilirlik"))

        # Scrollable frame
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form alanları
        self.create_form_section(scrollable_frame, self.lm.tr('sec_sustain', "Sürdürülebilirlik Bilgileri"), [
            (
                "sustainability_strategy",
                self.lm.tr('lbl_strategy', "Sürdürülebilirlik Stratejisi"),
                "text_area",
                self.lm.tr('tip_strategy', "Ana sürdürülebilirlik stratejisi"),
            ),
            ("material_topics", self.lm.tr('lbl_material_topics', "Materyal Konular"), "text_area", self.lm.tr('tip_material_topics', "Önemli sürdürülebilirlik konuları")),
            ("stakeholder_groups", self.lm.tr('lbl_stakeholders', "Paydaş Grupları"), "text_area", self.lm.tr('tip_stakeholders', "Ana paydaş grupları")),
            ("esg_rating_agency", self.lm.tr('lbl_esg_agency', "ESG Değerlendirme Kuruluşu"), "text", self.lm.tr('tip_esg_agency', "ESG değerlendirme yapan kuruluş")),
            ("esg_rating", self.lm.tr('lbl_esg_rating', "ESG Puanı"), "text", self.lm.tr('tip_esg_rating', "ESG değerlendirme puanı")),
            ("certifications", self.lm.tr('lbl_certifications', "Sertifikalar"), "text_area", self.lm.tr('tip_certifications', "Sahip olunan sertifikalar")),
            ("memberships", self.lm.tr('lbl_memberships', "Üyelikler"), "text_area", self.lm.tr('tip_memberships', "Üye olunan organizasyonlar"))
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_contact_info_tab(self) -> None:
        """İletişim bilgileri sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('tab_contact', " İletişim"))

        # Scrollable frame
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form alanları
        self.create_form_section(scrollable_frame, self.lm.tr('sec_address', "Adres Bilgileri"), [
            ("headquarters_address", self.lm.tr('lbl_address', "Merkez Adresi"), "text_area", self.lm.tr('tip_address', "Ana merkez adresi")),
            ("city", self.lm.tr('lbl_city', "Şehir"), "text", self.lm.tr('tip_city', "Şehir")),
            ("postal_code", self.lm.tr('lbl_postal', "Posta Kodu"), "text", self.lm.tr('tip_postal', "Posta kodu")),
            ("country", self.lm.tr('lbl_country', "Ülke"), "text", self.lm.tr('tip_country', "Ülke"))
        ])

        self.create_form_section(scrollable_frame, self.lm.tr('sec_contact', "İletişim Bilgileri"), [
            ("phone", self.lm.tr('lbl_phone', "Telefon"), "text", self.lm.tr('tip_phone', "Ana telefon numarası")),
            ("email", self.lm.tr('lbl_email', "E-posta"), "text", self.lm.tr('tip_email', "Genel iletişim e-postası")),
            ("website", self.lm.tr('lbl_website', "Web Sitesi"), "text", self.lm.tr('tip_website', "Şirket web sitesi")),
            ("sustainability_contact", self.lm.tr('lbl_sustain_contact', "Sürdürülebilirlik İletişim"), "text", self.lm.tr('tip_sustain_contact', "Sürdürülebilirlik iletişim e-postası"))
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_form_section(self, parent, title: str, fields: List[tuple]) -> None:
        """Form bölümü oluştur"""
        # Bölüm başlığı
        section_frame = tk.LabelFrame(parent, text=title,
                                     font=('Segoe UI', 12, 'bold'),
                                     fg='#2c3e50', bg='white')
        section_frame.pack(fill='x', padx=20, pady=15)

        # Form alanları
        for field_name, label, field_type, tooltip in fields:
            self.create_form_field(section_frame, field_name, label, field_type, tooltip)

    def create_form_field(self, parent, field_name: str, label: str, field_type: str, tooltip: str) -> None:
        """Form alanı oluştur"""
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill='x', padx=10, pady=5)

        # Label
        label_widget = tk.Label(field_frame, text=label,
                               font=('Segoe UI', 10), bg='white',
                               fg='#495057', width=20, anchor='w')
        label_widget.pack(side='left', padx=(0, 10))

        # Input widget
        if field_type == "text":
            widget = tk.Entry(field_frame, font=('Segoe UI', 10), width=50)
        elif field_type == "text_area":
            widget = tk.Text(field_frame, font=('Segoe UI', 10), width=50, height=3)
        elif field_type == "number":
            widget = tk.Entry(field_frame, font=('Segoe UI', 10), width=50)
        elif field_type == "date":
            widget = tk.Entry(field_frame, font=('Segoe UI', 10), width=50)
        elif field_type == "combo":
            widget = ttk.Combobox(field_frame, font=('Segoe UI', 10), width=47)
            if field_name == "company_size":
                widget['values'] = [
                    self.lm.tr('size_small', 'Küçük'),
                    self.lm.tr('size_medium', 'Orta'),
                    self.lm.tr('size_large', 'Büyük')
                ]
            elif field_name == "currency":
                widget['values'] = ['TRY', 'USD', 'EUR', 'GBP']
            elif field_name == "ownership_type":
                widget['values'] = [
                    self.lm.tr('own_public', 'Halka Açık'),
                    self.lm.tr('own_private', 'Kapalı'),
                    self.lm.tr('own_family', 'Aile Şirketi'),
                    self.lm.tr('own_state', 'Kamu')
                ]

        widget.pack(side='left', fill='x', expand=True)

        # Store widget reference
        if not hasattr(self, 'form_widgets'):
            self.form_widgets = {}
        self.form_widgets[field_name] = widget

    def load_company_data(self) -> None:
        """Şirket verilerini yükle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM company_info WHERE company_id = ?",
                (self.company_id,)
            )

            row = cursor.fetchone()
            if row:
                # Get column names
                cursor.execute("PRAGMA table_info(company_info)")
                columns = [col[1] for col in cursor.fetchall()]

                # Create data dict
                data = dict(zip(columns, row))

                # Populate form fields
                for field_name, widget in self.form_widgets.items():
                    value = data.get(field_name, '')
                    if isinstance(widget, tk.Text):
                        widget.delete('1.0', tk.END)
                        widget.insert('1.0', str(value))
                    else:
                        widget.delete(0, tk.END)
                        widget.insert(0, str(value))

            conn.close()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_load_data', 'Veri yükleme hatası')}: {e}")

    def save_company_data(self) -> None:
        """Şirket verilerini kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Prepare data
            data = {}
            for field_name, widget in self.form_widgets.items():
                if isinstance(widget, tk.Text):
                    value = widget.get('1.0', tk.END).strip()
                else:
                    value = widget.get().strip()
                data[field_name] = value if value else None

            # Add update timestamp
            data['updated_at'] = datetime.now().isoformat()

            # Validation
            if 'email' in data and data['email']:
                import re
                if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                    messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_email', "Geçersiz e-posta adresi!"))
                    return

            if 'phone' in data and data['phone']:
                import re
                if not re.match(r"^[\d\s\+\-\(\)]+$", data['phone']):
                    messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_phone', "Geçersiz telefon numarası!"))
                    return

            if 'tax_number' in data and data['tax_number']:
                if not data['tax_number'].isdigit():
                     messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_tax_num', "Vergi numarası sadece rakamlardan oluşmalıdır!"))
                     return

            cursor.execute("PRAGMA table_info(company_info)")
            available_cols = {row[1] for row in cursor.fetchall()}
            # Check if company exists
            cursor.execute("SELECT company_id FROM company_info WHERE company_id = ?", (self.company_id,))
            exists = cursor.fetchone()

            if exists:
                # Update existing
                update_data = {k: v for k, v in data.items() if k in available_cols}
                if update_data:
                    set_clause = ', '.join([f"{k} = ?" for k in update_data.keys()])
                    values = list(update_data.values()) + [self.company_id]
                    cursor.execute(
                        f"UPDATE company_info SET {set_clause} WHERE company_id = ?",
                        values,
                    )
            else:
                # Insert new
                insert_data = {k: v for k, v in data.items() if k in available_cols}
                insert_data['company_id'] = self.company_id
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['?' for _ in insert_data])
                values = list(insert_data.values())
                cursor.execute(
                    f"INSERT INTO company_info ({columns}) VALUES ({placeholders})",
                    values,
                )

            conn.commit()
            conn.close()

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('success_company_info_saved', "Şirket bilgileri kaydedildi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_save', 'Kaydetme hatası')}: {e}")

    def preview_tsrs_header(self) -> None:
        """TSRS rapor başlığı önizlemesi"""
        try:
            # Get current data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM company_info WHERE company_id = ?", (self.company_id,))
            row = cursor.fetchone()

            if not row:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('warning_no_company_info', "Şirket bilgileri bulunamadı!"))
                return

            # Get column names
            cursor.execute("PRAGMA table_info(company_info)")
            columns = [col[1] for col in cursor.fetchall()]
            data = dict(zip(columns, row))

            conn.close()

            # Create preview window
            preview_window = tk.Toplevel(self.parent)
            preview_window.title(self.lm.tr('tsrs_preview_title', "TSRS Rapor Başlığı Önizlemesi"))
            preview_window.geometry("800x600")
            preview_window.configure(bg='white')

            no_data = self.lm.tr('no_data', "Veri Yok")

            # Header content
            header_content = f"""
{self.lm.tr('tsrs_header_title', 'SUSTAINABILITY REPORTING STANDARD (TSRS) - COMPANY INFORMATION')}

{self.lm.tr('tsrs_company_name', 'COMPANY NAME')}: {data.get('legal_name', no_data)}
{self.lm.tr('tsrs_trading_name', 'TRADING NAME')}: {data.get('trading_name', data.get('name', no_data))}
{self.lm.tr('tsrs_reg_num', 'REGISTRATION NUMBER')}: {data.get('registration_number', no_data)}
{self.lm.tr('tsrs_tax_num', 'TAX NUMBER')}: {data.get('tax_number', no_data)}
{self.lm.tr('tsrs_legal_form', 'LEGAL FORM')}: {data.get('legal_form', no_data)}
{self.lm.tr('tsrs_est_date', 'ESTABLISHMENT DATE')}: {data.get('establishment_date', no_data)}

{self.lm.tr('tsrs_hq_address', 'HEADQUARTERS ADDRESS')}:
{data.get('headquarters_address', no_data)}
{data.get('city', no_data)} {data.get('postal_code', no_data)}
{data.get('country', no_data)}

{self.lm.tr('tsrs_contact_info', 'CONTACT INFORMATION')}:
{self.lm.tr('tsrs_phone', 'Phone')}: {data.get('phone', no_data)}
{self.lm.tr('tsrs_email', 'Email')}: {data.get('email', no_data)}
{self.lm.tr('tsrs_website', 'Website')}: {data.get('website', no_data)}
{self.lm.tr('tsrs_sustain_contact', 'Sustainability Contact')}: {data.get('sustainability_contact', no_data)}

{self.lm.tr('tsrs_business_info', 'BUSINESS INFORMATION')}:
{self.lm.tr('tsrs_sector', 'Sector')}: {data.get('sector', no_data)}
{self.lm.tr('tsrs_industry_code', 'Industry Code (NACE)')}: {data.get('industry_code', no_data)}
{self.lm.tr('tsrs_company_size', 'Company Size')}: {data.get('company_size', no_data)}
{self.lm.tr('tsrs_employee_count', 'Employee Count')}: {data.get('employee_count', no_data)}
{self.lm.tr('tsrs_revenue', 'Annual Revenue')}: {data.get('annual_revenue', no_data)} {data.get('currency', 'TRY')}

{self.lm.tr('tsrs_stock_info', 'STOCK EXCHANGE INFORMATION')}:
{self.lm.tr('tsrs_stock_exchange', 'Stock Exchange')}: {data.get('stock_exchange', no_data)}
{self.lm.tr('tsrs_ticker', 'Ticker Symbol')}: {data.get('ticker_symbol', no_data)}
{self.lm.tr('tsrs_fiscal_end', 'Fiscal Year End')}: {data.get('fiscal_year_end', no_data)}
{self.lm.tr('tsrs_report_period', 'Reporting Period')}: {data.get('reporting_period', no_data)}

{self.lm.tr('tsrs_sustain_info', 'SUSTAINABILITY INFORMATION')}:
{self.lm.tr('tsrs_strategy', 'Sustainability Strategy')}: {data.get('sustainability_strategy', no_data)}
{self.lm.tr('tsrs_material_topics', 'Material Topics')}: {data.get('material_topics', no_data)}
{self.lm.tr('tsrs_esg_agency', 'ESG Rating Agency')}: {data.get('esg_rating_agency', no_data)}
{self.lm.tr('tsrs_esg_rating', 'ESG Rating')}: {data.get('esg_rating', no_data)}
{self.lm.tr('tsrs_certifications', 'Certifications')}: {data.get('certifications', no_data)}
{self.lm.tr('tsrs_memberships', 'Memberships')}: {data.get('memberships', no_data)}

{self.lm.tr('tsrs_auditor', 'AUDITOR')}: {data.get('auditor', no_data)}
{self.lm.tr('tsrs_last_updated', 'LAST UPDATED')}: {data.get('updated_at', no_data)}
"""

            # Display content
            text_widget = tk.Text(preview_window, font=('Consolas', 10),
                                 bg='#f8f9fa', fg='#212529', wrap=tk.WORD)
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert('1.0', header_content)
            text_widget.config(state='disabled')

            # Close button
            tk.Button(preview_window, text=self.lm.tr('btn_close', "Kapat"),
                     font=('Segoe UI', 11, 'bold'), fg='white', bg='#6c757d',
                     relief='flat', cursor='hand2', command=preview_window.destroy,
                     padx=20, pady=8).pack(pady=10)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_preview', 'Önizleme hatası')}: {e}")
