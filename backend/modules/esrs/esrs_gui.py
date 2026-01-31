#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESRS GUI - Gelismis Arayuz"""

import logging
import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .esrs_module import ESRSModule
from config.database import DB_PATH


class ESRSGUI:
    """ESRS arayuzu"""

    def __init__(self, parent, company_id: int = 1, db_path: str = DB_PATH):
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.module = ESRSModule(db_path)
        self.current_year = datetime.datetime.now().year
        self.setup_ui()

    def setup_ui(self):
        """Ana UI"""
        # Mevcut widgetları temizle
        for widget in self.parent.winfo_children():
            widget.destroy()

        apply_theme(self.parent)
        
        # Ana Frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Üst Panel (Başlık ve Yıl)
        header_frame = tk.Frame(main_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text=self.lm.tr('esrs_module_title', "ESRS - Avrupa Sürdürülebilirlik Raporlama Standartları"),
            font=('Segoe UI', 20, 'bold'),
            fg='#1e293b',
            bg='#f0f2f5'
        ).pack(side='left')

        # Yıl Bilgisi
        year_frame = tk.Frame(header_frame, bg='white', padx=15, pady=8)
        year_frame.pack(side='right')
        
        tk.Label(
            year_frame, 
            text=self.lm.tr('reporting_year', "Raporlama Yılı: {year}").format(year=self.current_year),
            font=('Segoe UI', 10, 'bold'),
            fg='#334155',
            bg='white'
        ).pack()

        # Split Layout (Sol: Liste, Sağ: Detay)
        content_frame = tk.Frame(main_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True)

        # --- SOL PANEL (Konu Listesi) ---
        left_panel = tk.Frame(content_frame, bg='white', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)

        # Liste Başlığı
        tk.Label(left_panel, text=self.lm.tr('standards', "Standartlar"), font=('Segoe UI', 12, 'bold'), bg='white', fg='#334155').pack(anchor='w', padx=15, pady=15)
        
        # Treeview Container
        tree_container = tk.Frame(left_panel, bg='white')
        tree_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Custom Treeview Style
        style = ttk.Style()
        style.configure("ESRS.Treeview", font=('Segoe UI', 10), rowheight=28, borderwidth=0)
        style.configure("ESRS.Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map("ESRS.Treeview", background=[('selected', '#e6f0fa')], foreground=[('selected', '#1e293b')])

        self.tree = ttk.Treeview(tree_container, columns=('code', 'title'), show='headings', selectmode='browse', style="ESRS.Treeview")
        self.tree.heading('code', text=self.lm.tr('code', 'Kod'))
        self.tree.heading('title', text=self.lm.tr('title', 'Başlık'))
        self.tree.column('code', width=50, anchor='center')
        self.tree.column('title', width=180, anchor='w')
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<<TreeviewSelect>>', self.on_topic_select)

        # --- SAĞ PANEL (Detay ve Veri Girişi) ---
        self.right_frame = tk.Frame(content_frame, bg='white')
        self.right_frame.pack(side='left', fill='both', expand=True)

        # Detay Konteyneri
        self.detail_container = tk.Frame(self.right_frame, bg='white')
        self.detail_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Başlangıç mesajı
        self.placeholder_label = tk.Label(
            self.detail_container, 
            text=self.lm.tr('esrs_placeholder', "Detayları görüntülemek ve veri girmek için\nsoldaki listeden bir standart seçiniz."),
            font=('Segoe UI', 11),
            fg='#64748b',
            bg='white',
            justify='center'
        )
        self.placeholder_label.pack(expand=True)

        # --- ALT BUTONLAR ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(
            btn_frame,
            text=self.lm.tr('report_center', "Rapor Merkezi"),
            style='Primary.TButton',
            command=self.open_report_center_esrs
        ).pack(side='right')

        # Verileri Yükle
        self.load_topics()

    def load_topics(self):
        """Konuları listeye yükle"""
        topics = self.module.get_all_topics()
        self.topics_data = {}
        
        for topic in topics:
            self.tree.insert('', 'end', iid=topic['code'], values=(topic['code'], topic['title']))
            self.topics_data[topic['code']] = topic

    def on_topic_select(self, event):
        """Konu seçildiğinde sağ paneli güncelle"""
        selected = self.tree.selection()
        if not selected:
            return
            
        code = selected[0]
        topic = self.topics_data.get(code)
        
        if topic:
            self.show_topic_details(topic)

    def show_topic_details(self, topic):
        """Detay görünümünü oluştur"""
        # Konteyneri temizle
        for widget in self.detail_container.winfo_children():
            widget.destroy()
            
        # Başlık
        header_frame = ttk.Frame(self.detail_container)
        header_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            header_frame, 
            text=f"{topic['code']} - {topic['title']}", 
            font=('Segoe UI', 14, 'bold'),
            foreground='#2c3e50'
        ).pack(anchor='w')
        
        ttk.Label(
            header_frame, 
            text=f"{self.lm.tr('category', 'Kategori')}: {topic['category']}", 
            font=('Segoe UI', 9, 'italic'),
            foreground='gray'
        ).pack(anchor='w')

        # Açıklama Kutusu
        desc_frame = ttk.LabelFrame(self.detail_container, text=self.lm.tr('standard_description', "Standart Açıklaması"), padding=10)
        desc_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            desc_frame, 
            text=topic['description'], 
            wraplength=500,
            justify='left'
        ).pack(anchor='w', fill='x')

        # Veri Giriş Alanı
        input_frame = ttk.LabelFrame(self.detail_container, text=self.lm.tr('company_assessment_notes', "Şirket Değerlendirmesi / Notlar"), padding=10)
        input_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.note_text = scrolledtext.ScrolledText(input_frame, height=10, font=('Segoe UI', 10))
        self.note_text.pack(fill='both', expand=True)

        # Kaydet Butonu
        action_frame = ttk.Frame(self.detail_container)
        action_frame.pack(fill='x')
        
        ttk.Button(
            action_frame,
            text=self.lm.tr('save_changes', "Değişiklikleri Kaydet"),
            command=lambda: self.save_topic_note(topic['code'])
        ).pack(side='right')

        # Mevcut veriyi yükle
        self.load_topic_data(topic['code'])

    def load_topic_data(self, code):
        """Kayıtlı veriyi yükle"""
        data = self.module.get_company_data(self.company_id, code, self.current_year)
        # SUMMARY kodlu veriyi bul
        summary_data = next((d for d in data if d['datapoint_code'] == 'SUMMARY'), None)
        
        if summary_data:
            self.note_text.insert('1.0', summary_data['value'])

    def save_topic_note(self, code):
        """Notu veritabanına kaydet"""
        note = self.note_text.get('1.0', 'end-1c')
        # Datapoint code olarak 'SUMMARY' kullanıyoruz
        success = self.module.save_data(self.company_id, code, 'SUMMARY', note, self.current_year)
        
        if success:
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('data_saved_success', "Veriler başarıyla kaydedildi."))
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('save_error', "Kaydetme sırasında bir hata oluştu."))

    def open_report_center_esrs(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            gui.module_filter_var.set('esrs')
            gui.refresh_reports()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_center_open_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")
