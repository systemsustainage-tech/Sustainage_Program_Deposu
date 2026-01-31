import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AB CSRD Tam Uyum GUI - TÜRKÇE
ESRS, XBRL, Çift Önemlendirme, Taxonomy, Checklist
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager

from .csrd_compliance_manager import CSRDComplianceManager


class CSRDGUI:
    """AB CSRD uyum GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.manager = CSRDComplianceManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """CSRD arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#003399', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr('csrd_title', "🇪🇺 AB CSRD Tam Uyum Sistemi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#003399')
        title_label.pack(expand=True)
        actions = tk.Frame(title_frame, bg='#003399')
        actions.pack(side='right', padx=10)
        ttk.Button(actions, text=self.lm.tr('btn_report_center', "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_csrd).pack(side='right')

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_esrs_tab()
        self.create_xbrl_tab()
        self.create_double_materiality_tab()
        self.create_taxonomy_tab()
        self.create_checklist_tab()

    def open_report_center_csrd(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('csrd')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for csrd: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error_title', "Hata"), f"{self.lm.tr('err_report_center_open', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=f" {self.lm.tr('tab_dashboard', 'Genel Bakış')}")

        # Başlık
        tk.Label(dashboard_frame, text=self.lm.tr('csrd_dashboard_title', "AB CSRD Uyum Dashboard"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = self.lm.tr('csrd_desc', """
        🇪🇺 AB CSRD (Corporate Sustainability Reporting Directive) Tam Uyum
        
         ESRS Formatında Rapor Export (PDF, Excel, JSON, XBRL)
         Digital Taxonomy Tagging (XBRL)
         Çift Önemlendirme Otomasyonu (Double Materiality)
         AB Taxonomy Uygunluk Raporu
         CSRD Compliance Checklist (30+ Madde)
        """)

        tk.Label(dashboard_frame, text=desc_text, font=('Segoe UI', 11),
                bg='white', justify='left').pack(padx=40, pady=20)

        # İstatistik kartları
        self.stats_frame = tk.Frame(dashboard_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

    def create_esrs_tab(self) -> None:
        """ESRS raporlama sekmesi"""
        esrs_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(esrs_frame, text=f" {self.lm.tr('tab_esrs_reporting', 'ESRS Raporlama')}")

        # Başlık
        tk.Label(esrs_frame, text=self.lm.tr('esrs_export_title', "ESRS Formatında Rapor Export"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # ESRS standartları
        esrs_text = self.lm.tr('esrs_standards_info', """
         ESRS Standartları (Türkçe):
        
         ESRS 2 - Genel Açıklamalar (Zorunlu)
         ESRS E1 - İklim Değişikliği (Zorunlu)
         ESRS E2 - Kirlilik (Koşullu)
         ESRS E3 - Su ve Deniz Kaynakları (Koşullu)
         ESRS E4 - Biyoçeşitlilik (Koşullu)
         ESRS E5 - Döngüsel Ekonomi (Koşullu)
         ESRS S1 - Kendi İşgücü (Zorunlu)
         ESRS S2-S4 - Değer Zinciri, Topluluk, Tüketici (Koşullu)
         ESRS G1 - İş Etiği (Zorunlu)
        
         Export Formatları:
        • PDF (ESRS formatında)
        • Excel (Detaylı veri)
        • JSON (Makine okunabilir)
        • XBRL (Dijital taxonomy)
        """)

        tk.Label(esrs_frame, text=esrs_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Export butonları
        btn_frame = tk.Frame(esrs_frame, bg='white')
        btn_frame.pack(pady=10)

        for fmt in ["PDF", "Excel", "JSON", "XBRL"]:
            ttk.Button(
                btn_frame,
                text=" " + self.lm.tr(f"export_{fmt.lower()}", f"{fmt} Export"),
                style='Primary.TButton',
                command=lambda f=fmt: self.export_esrs(f)
            ).pack(side='left', padx=5)

    def create_xbrl_tab(self) -> None:
        """XBRL tagging sekmesi"""
        xbrl_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(xbrl_frame, text=f" {self.lm.tr('tab_xbrl_tagging', 'XBRL Tagging')}")

        # Başlık
        tk.Label(xbrl_frame, text=self.lm.tr('xbrl_tagging_title', "Digital Taxonomy Tagging (XBRL)"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        xbrl_text = self.lm.tr('xbrl_info', """
        ️ XBRL (eXtensible Business Reporting Language):
        
        • Dijital raporlama standardı
        • Makine okunabilir veri
        • AB ESEF (European Single Electronic Format) uyumlu
        • ESRS taxonomy ile entegre
        
         Örnek XBRL Taglar:
        • esrs-e1:GHGEmissionsScope1
        • esrs-e1:GHGEmissionsScope2
        • esrs-e1:GHGEmissionsScope3
        • esrs-s1:TotalNumberOfEmployees
        • esrs-g1:AntiCorruptionPolicies
        """)

        tk.Label(xbrl_frame, text=xbrl_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # XBRL listesi
        columns = (
            self.lm.tr('col_data_point', 'Veri Noktası'),
            self.lm.tr('col_esrs_ref', 'ESRS Ref'),
            self.lm.tr('col_xbrl_tag', 'XBRL Tag'),
            self.lm.tr('col_value', 'Değer')
        )
        self.xbrl_tree = ttk.Treeview(xbrl_frame,
                                     columns=columns,
                                     show='headings', height=10)

        for col in columns:
            self.xbrl_tree.heading(col, text=col)
            self.xbrl_tree.column(col, width=150)

        self.xbrl_tree.pack(fill='both', expand=True, padx=20, pady=10)

    def create_double_materiality_tab(self) -> None:
        """Çift önemlendirme sekmesi"""
        dm_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dm_frame, text=f" {self.lm.tr('tab_double_materiality', 'Çift Önemlendirme')}")

        # Başlık
        tk.Label(dm_frame, text=self.lm.tr('double_materiality_title', "Çift Önemlendirme (Double Materiality)"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        dm_text = self.lm.tr('double_materiality_info', """
        ️ Çift Önemlendirme Boyutları:
        
        1️⃣ Etki Önemliliği (Impact Materiality - Inside-Out):
           • Şirketin çevre ve toplum üzerindeki etkileri
           • Pozitif veya negatif etkiler
           • Kısa, orta ve uzun vadeli etkiler
        
        2️⃣ Finansal Önemliliği (Financial Materiality - Outside-In):
           • Sürdürülebilirlik konularının şirket üzerindeki etkileri
           • Riskler ve fırsatlar
           • Finansal performans etkileri
        
         Değerlendirme:
        • Her konu için 1-5 puan
        • 3 ve üzeri = Önemli (Material)
        • Bir veya her iki boyutta önemli ise rapor edilir
        """)

        tk.Label(dm_frame, text=dm_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        # Değerlendirme butonu
        ttk.Button(dm_frame, text=f" {self.lm.tr('btn_auto_materiality', 'Otomatik Önemlendirme Analizi')}", style='Primary.TButton',
                   command=self.run_materiality_assessment).pack(pady=10)

    def create_taxonomy_tab(self) -> None:
        """AB Taxonomy sekmesi"""
        tax_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tax_frame, text=f" {self.lm.tr('tab_ab_taxonomy', 'AB Taxonomy')}")

        # Başlık
        tk.Label(tax_frame, text=self.lm.tr('ab_taxonomy_title', "AB Taxonomy Uygunluk Raporu"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        tax_text = self.lm.tr('ab_taxonomy_info', """
         AB Taxonomy Kriterleri:
        
         1. Önemli Katkı (Substantial Contribution):
           • 6 çevre hedefinden birine katkı
        
         2. DNSH (Do No Significant Harm):
           • Diğer 5 hedefe önemli zarar vermeme
        
         3. Minimum Korumalar (Minimum Safeguards):
           • İnsan hakları
           • İş standartları
           • Vergilendirme
           • Rekabet
        
         KPI'lar:
        • Revenue (Gelir) - Taxonomy uyumlu %
        • CapEx (Yatırım Harcaması) - Taxonomy uyumlu %
        • OpEx (İşletme Gideri) - Taxonomy uyumlu %
        """)

        tk.Label(tax_frame, text=tax_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=30, pady=10)

        ttk.Button(tax_frame, text=f" {self.lm.tr('btn_create_taxonomy_report', 'Taxonomy Uygunluk Raporu Oluştur')}", style='Primary.TButton',
                   command=self.generate_taxonomy_report).pack(pady=10)

    def create_checklist_tab(self) -> None:
        """Checklist sekmesi"""
        checklist_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(checklist_frame, text=f" {self.lm.tr('tab_checklist', 'Uyum Kontrol Listesi')}")

        # Başlık
        tk.Label(checklist_frame, text=self.lm.tr('checklist_title', "CSRD Compliance Checklist"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Checklist listesi
        columns = (
            self.lm.tr('col_category', 'Kategori'),
            self.lm.tr('col_code', 'Kod'),
            self.lm.tr('col_requirement', 'Gereklilik'),
            self.lm.tr('col_level', 'Seviye'),
            self.lm.tr('col_status', 'Durum')
        )
        self.checklist_tree = ttk.Treeview(checklist_frame,
                                          columns=columns,
                                          show='headings', height=15)

        for col in columns:
            self.checklist_tree.heading(col, text=col)
            self.checklist_tree.column(col, width=120)

        self.checklist_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Checklist başlat butonu
        btn_text = self.lm.tr('btn_start_checklist', "CSRD Checklist'i Başlat")
        ttk.Button(checklist_frame, text=f" {btn_text}", style='Primary.TButton',
                   command=self.initialize_checklist).pack(pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_dashboard_data()
        except Exception as e:
            logging.error(f"Veri yukleme hatasi: {e}")

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle"""
        try:
            summary = self.manager.get_csrd_compliance_summary(self.company_id)

            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats = [
                (self.lm.tr('stat_esrs_standards', "ESRS Standartları"), "12", '#003399'),
                (self.lm.tr('stat_xbrl_tags', "XBRL Taglar"), "100+", '#1976D2'),
                (self.lm.tr('stat_material_topics', "Önemli Konular"), "15", '#E65100'),
                (self.lm.tr('stat_compliance_rate', "Uyum %"), f"{summary.get('compliance_percentage', 0):.0f}%", '#2E7D32'),
            ]

            for i, (title, value, color) in enumerate(stats):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Dashboard yukleme hatasi: {e}")

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def export_esrs(self, format_type: str) -> None:
        """ESRS raporu export et"""
        try:
            period = datetime.now().strftime('%Y')
            file_path = self.manager.export_esrs_report(self.company_id, period, export_format=format_type.upper())
            if file_path:
                from modules.reporting.advanced_report_manager import AdvancedReportManager
                arm = AdvancedReportManager()
                arm.save_report(
                    company_id=self.company_id,
                    module_code='esrs',
                    report_name=f'ESRS Raporu {period}',
                    report_type=format_type.lower(),
                    source_file=file_path,
                    reporting_period=period,
                    tags=['esrs','csrd']
                )
                messagebox.showinfo(
                    self.lm.tr('success', "Başarılı"),
                    self.lm.tr('esrs_report_saved', "ESRS raporu oluşturuldu ve Rapor Merkezi'ne kaydedildi.") + "\n\n"
                    + f"{self.lm.tr('file', 'Dosya')}: {file_path}"
                )
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('esrs_report_failed', "ESRS raporu oluşturulamadı"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('export_error', 'Export sırasında hata')}: {e}")

    def run_materiality_assessment(self) -> None:
        """Önemlendirme analizi çalıştır"""
        messagebox.showinfo(self.lm.tr('double_materiality', "Çift Önemlendirme"),
                            self.lm.tr('double_materiality_info_popup',
                                       "Otomatik Çift Önemlendirme Analizi Başlatılacak!\n\n"
                                       "Her konu için:\n"
                                       " Etki önemliliği puanı (1-5)\n"
                                       " Finansal önemliliği puanı (1-5)\n"
                                       " Paydaş görüşleri\n\n"
                                       "3+ puan = Önemli (Material)"))

    def generate_taxonomy_report(self) -> None:
        """Taxonomy raporu oluştur"""
        messagebox.showinfo(self.lm.tr('ab_taxonomy', "AB Taxonomy"),
                            self.lm.tr('ab_taxonomy_info_popup',
                                       "AB Taxonomy Uygunluk Raporu Oluşturulacak!\n\n"
                                       "KPI'lar:\n"
                                       " Revenue (Gelir) uygunluk %\n"
                                       " CapEx (Yatırım) uygunluk %\n"
                                       " OpEx (İşletme) uygunluk %\n\n"
                                       "Kriterleri kontrol:\n"
                                       "• Önemli katkı\n"
                                       "• DNSH uyumu\n"
                                       "• Minimum korumalar"))

    def initialize_checklist(self) -> None:
        """Checklist başlat"""
        count = self.manager.initialize_csrd_checklist(self.company_id)
        messagebox.showinfo(self.lm.tr('csrd_checklist', "CSRD Checklist"),
                            self.lm.tr('csrd_checklist_started', "CSRD Compliance Checklist Başlatıldı!") + "\n\n"
                            + f"{self.lm.tr('total_items_added', 'Toplam')} {count} {self.lm.tr('items_added', 'madde eklendi')}:\n"
                            + self.lm.tr('general_requirements', " Genel gereklilikler") + "\n"
                            + self.lm.tr('esrs2_disclosures', " ESRS 2 açıklamaları") + "\n"
                            + self.lm.tr('double_materiality_item', " Çift önemlendirme") + "\n"
                            + self.lm.tr('climate_e1_requirements', " İklim (E1) gereklilikleri") + "\n"
                            + self.lm.tr('ab_taxonomy_kpis', " AB Taxonomy KPI'ları"))
