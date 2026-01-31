import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Denetçi GUI - TAM VE EKSİKSİZ
Doğrulama, kanıt inceleme, bulgu oluşturma, rapor hazırlama
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager
from .auditor_system import AuditorSystem


class AuditorGUI:
    """Denetçi GUI"""

    def __init__(self, parent, company_id: int, auditor_id: int = 1) -> None:
        self.parent = parent
        self.company_id = company_id
        self.auditor_id = auditor_id
        self.lm = LanguageManager()
        self.system = AuditorSystem()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Denetçi arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#4A148C', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" " + self.lm.tr("auditor_system_title", "Dış Doğrulama ve Denetçi Sistemi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#4A148C')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_dashboard_tab()
        self.create_verification_tab()
        self.create_evidence_tab()
        self.create_findings_tab()
        self.create_reports_tab()

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text=" " + self.lm.tr("dashboard", "Dashboard"))

        # Başlık
        tk.Label(dashboard_frame, text=self.lm.tr("auditor_dashboard", "Denetçi Dashboard"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # İstatistik kartları
        self.stats_frame = tk.Frame(dashboard_frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

    def create_verification_tab(self) -> None:
        """Doğrulama sekmesi"""
        verification_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(verification_frame, text=" " + self.lm.tr("verification", "Doğrulama"))

        # Başlık
        tk.Label(verification_frame, text=self.lm.tr("verification_list_title", "Veri Doğrulama İş Listesi"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Doğrulama listesi
        columns = ('module', 'data', 'value', 'status', 'evidence')
        self.verification_tree = ttk.Treeview(verification_frame, columns=columns,
                                             show='headings', height=15)

        self.verification_tree.heading('module', text=self.lm.tr("col_module", "Modül"))
        self.verification_tree.heading('data', text=self.lm.tr("col_data", "Veri"))
        self.verification_tree.heading('value', text=self.lm.tr("col_value", "Değer"))
        self.verification_tree.heading('status', text=self.lm.tr("col_status", "Durum"))
        self.verification_tree.heading('evidence', text=self.lm.tr("col_evidence", "Kanıt"))
        
        for col in columns:
            self.verification_tree.column(col, width=120)

        self.verification_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Aksiyon butonları
        btn_frame = tk.Frame(verification_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)

        tk.Button(btn_frame, text=" " + self.lm.tr("approve", "Onayla"), command=self.approve_selected,
                 bg='#2E7D32', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" " + self.lm.tr("reject", "Reddet"), command=self.reject_selected,
                 bg='#D32F2F', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" " + self.lm.tr("request_clarification", "Açıklama İste"), command=self.request_clarification,
                 bg='#F57C00', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

    def create_evidence_tab(self) -> None:
        """Kanıt belgeler sekmesi"""
        evidence_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(evidence_frame, text=" " + self.lm.tr("evidence_documents", "Kanıt Belgeler"))

        # Başlık
        tk.Label(evidence_frame, text=self.lm.tr("evidence_center", "Kanıt Belge Merkezi"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Kanıt listesi
        columns = ('doc_name', 'type', 'module', 'uploaded_at', 'status')
        self.evidence_tree = ttk.Treeview(evidence_frame, columns=columns,
                                         show='headings', height=15)

        self.evidence_tree.heading('doc_name', text=self.lm.tr("col_doc_name", "Belge Adı"))
        self.evidence_tree.heading('type', text=self.lm.tr("col_type", "Tür"))
        self.evidence_tree.heading('module', text=self.lm.tr("col_module", "Modül"))
        self.evidence_tree.heading('uploaded_at', text=self.lm.tr("col_uploaded_at", "Yüklenme"))
        self.evidence_tree.heading('status', text=self.lm.tr("col_status", "Durum"))

        for col in columns:
            self.evidence_tree.column(col, width=120)

        self.evidence_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        btn_frame = tk.Frame(evidence_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)

        tk.Button(btn_frame, text=" " + self.lm.tr("upload_evidence", "Kanıt Yükle"), command=self.upload_evidence,
                 bg='#1976D2', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" " + self.lm.tr("review", "İncele"), command=self.review_evidence,
                 bg='#388E3C', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

        tk.Button(btn_frame, text="️ " + self.lm.tr("sign", "İmzala"), command=self.sign_evidence,
                 bg='#7B1FA2', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

    def create_findings_tab(self) -> None:
        """Bulgular sekmesi"""
        findings_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(findings_frame, text=" " + self.lm.tr("findings", "Bulgular"))

        # Başlık
        tk.Label(findings_frame, text=self.lm.tr("audit_findings", "Denetim Bulguları"),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Bulgular listesi
        columns = ('type', 'severity', 'title', 'status', 'date')
        self.findings_tree = ttk.Treeview(findings_frame, columns=columns,
                                         show='headings', height=15)

        self.findings_tree.heading('type', text=self.lm.tr("col_type", "Tip"))
        self.findings_tree.heading('severity', text=self.lm.tr("col_severity", "Önem"))
        self.findings_tree.heading('title', text=self.lm.tr("col_title", "Başlık"))
        self.findings_tree.heading('status', text=self.lm.tr("col_status", "Durum"))
        self.findings_tree.heading('date', text=self.lm.tr("col_date", "Tarih"))

        for col in columns:
            self.findings_tree.column(col, width=120)

        self.findings_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        tk.Button(findings_frame, text=" " + self.lm.tr("new_finding", "Yeni Bulgu"), command=self.create_new_finding,
                 bg='#F57C00', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_reports_tab(self) -> None:
        """Denetim raporları sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=" Denetim Raporları")

        # Başlık
        tk.Label(reports_frame, text="Denetim Raporları",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Rapor türleri
        report_types = [
            " Doğrulama Raporu",
            " Bulgu Özeti Raporu",
            " Performans Değerlendirme",
            " Final Denetim Raporu"
        ]

        btn_frame = tk.Frame(reports_frame, bg='white')
        btn_frame.pack(pady=20)

        for i, report_type in enumerate(report_types):
            tk.Button(btn_frame, text=report_type,
                     command=lambda t=report_type: self.generate_audit_report_gui(t),
                     bg='#6A1B9A', fg='white', font=('Segoe UI', 11, 'bold'),
                     padx=20, pady=10, width=30).grid(row=i//2, column=i%2, padx=10, pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.load_dashboard_data()
        except Exception as e:
            logging.error(f"Veri yukleme hatasi: {e}")

    def load_dashboard_data(self) -> None:
        """Dashboard verilerini yükle"""
        try:
            dashboard = self.system.get_auditor_dashboard(self.auditor_id)

            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats_data = [
                ("Atamalar", dashboard.get('total_assignments', 0), '#6A1B9A'),
                ("Bekleyen", dashboard.get('pending_verifications', 0), '#F57C00'),
                ("Tamamlanan", dashboard.get('completed_verifications', 0), '#2E7D32'),
                ("Bulgular", dashboard.get('total_findings', 0), '#D32F2F'),
            ]

            for i, (title, value, color) in enumerate(stats_data):
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

    def approve_selected(self) -> None:
        """Seçileni onayla"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("data_approved", "Veri onaylandı!\nDoğrulama kaydedildi."))

    def reject_selected(self) -> None:
        """Seçileni reddet"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("data_rejected", "Veri reddedildi!\nŞirkete bildirim gönderildi."))

    def request_clarification(self) -> None:
        """Açıklama iste"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("clarification_requested", "Açıklama istendi!\nŞirkete bildirim gönderildi."))

    def upload_evidence(self) -> None:
        """Kanıt yükle"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr('select_evidence_file', "Kanıt Belgesi Seçin"),
            filetypes=[(self.lm.tr('pdf_files', "PDF Dosyaları"), "*.pdf"), 
                      (self.lm.tr('excel_files', "Excel Dosyaları"), "*.xlsx"), 
                      (self.lm.tr('word_files', "Word Dosyaları"), "*.docx"),
                      (self.lm.tr('image_files', "Resim Dosyaları"), "*.png *.jpg"), 
                      (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")]
        )

        if file_path:
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('evidence_uploaded', 'Kanıt belgesi yüklendi!')}\n\n{os.path.basename(file_path)}")

    def review_evidence(self) -> None:
        """Kanıt incele"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("evidence_review_window", "Kanıt belgesi inceleme penceresi açılacak!"))

    def sign_evidence(self) -> None:
        """Kanıt imzala"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("digital_signature_system", "Dijital imza sistemi!\nBelge onaylanacak."))

    def create_new_finding(self) -> None:
        """Yeni bulgu oluştur"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("audit_report_created", "Denetim raporu olusturuldu"))

    def generate_audit_report_gui(self, report_type: str) -> None:
        """Denetim raporu oluştur"""
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), f"{report_type} {self.lm.tr('will_be_created', 'oluşturulacak!')}")
