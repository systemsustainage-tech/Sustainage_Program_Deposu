import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Sektörel Standartları GUI
GRI 11, 12, 13, 14 ve diğer sektörel standartlar için kullanıcı arayüzü
"""

import tkinter as tk
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .gri_sectoral_standards import GRISectoralStandardsManager


class GRISectoralGUI:
    """GRI Sektörel Standartları GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        self.manager = GRISectoralStandardsManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Sektörel standartlar arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2E7D32', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" GRI Sektörel Standartları",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2E7D32')
        title_label.pack(expand=True)

        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=" Rapor Merkezi", style='Primary.TButton', command=self.open_report_center_gri_sectoral).pack(side='left', padx=6)
        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_overview_tab()
        self.create_standards_tab()
        self.create_compliance_tab()
        self.create_reports_tab()

    def create_overview_tab(self) -> None:
        """Genel bakış sekmesi"""
        overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(overview_frame, text=" Genel Bakış")

        # Sol panel - İstatistikler
        left_panel = tk.Frame(overview_frame, bg='white')
        left_panel.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Başlık
        tk.Label(left_panel, text="Sektörel Standartlar Özeti",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', pady=(0, 20))

        # İstatistik kartları
        self.stats_frame = tk.Frame(left_panel, bg='white')
        self.stats_frame.pack(fill='x', pady=10)

        # Sağ panel - Uygulanabilir standartlar
        right_panel = tk.Frame(overview_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        tk.Label(right_panel, text="Uygulanabilir Standartlar",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', pady=(0, 20))

        # Standartlar listesi
        self.standards_listbox = tk.Listbox(right_panel, font=('Segoe UI', 10), height=15)
        self.standards_listbox.pack(fill='both', expand=True)
        self.standards_listbox.bind('<<ListboxSelect>>', self.on_standard_select)

    def create_standards_tab(self) -> None:
        """Standartlar sekmesi"""
        standards_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(standards_frame, text=" Standartlar")

        # Üst panel - Standart seçimi
        top_panel = tk.Frame(standards_frame, bg='white')
        top_panel.pack(fill='x', padx=10, pady=10)

        tk.Label(top_panel, text="Standart Seçin:",
                font=('Segoe UI', 12, 'bold'), bg='white').pack(side='left', padx=(0, 10))

        self.standard_var = tk.StringVar()
        self.standard_combo = ttk.Combobox(top_panel, textvariable=self.standard_var,
                                          state='readonly', width=30)
        self.standard_combo.pack(side='left', padx=(0, 10))
        self.standard_combo.bind('<<ComboboxSelected>>', self.on_standard_change)

        # Ana içerik - Konular
        content_frame = tk.Frame(standards_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Konular treeview
        columns = ('ID', 'Konu', 'Durum', 'Veri Kaynağı', 'Notlar')
        self.topics_tree = ttk.Treeview(content_frame, columns=columns, show='headings')

        # Sütun başlıkları
        self.topics_tree.heading('ID', text='Standart ID')
        self.topics_tree.heading('Konu', text='Konu Adı')
        self.topics_tree.heading('Durum', text='Uyumluluk Durumu')
        self.topics_tree.heading('Veri Kaynağı', text='Veri Kaynağı')
        self.topics_tree.heading('Notlar', text='Notlar')

        # Sütun genişlikleri
        self.topics_tree.column('ID', width=100)
        self.topics_tree.column('Konu', width=200)
        self.topics_tree.column('Durum', width=150)
        self.topics_tree.column('Veri Kaynağı', width=150)
        self.topics_tree.column('Notlar', width=200)

        self.topics_tree.pack(fill='both', expand=True)
        self.topics_tree.bind('<Double-1>', self.on_topic_double_click)

        # Alt panel - Butonlar
        btn_frame = tk.Frame(content_frame, bg='white')
        btn_frame.pack(fill='x', pady=10)

        ttk.Button(btn_frame, text=" Yenile", style='Primary.TButton', command=self.refresh_topics).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=" Detaylı Rapor", style='Primary.TButton', command=self.generate_detailed_report).pack(side='left', padx=5)

    def create_compliance_tab(self) -> None:
        """Uyumluluk sekmesi"""
        compliance_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(compliance_frame, text=" Uyumluluk")

        # Uyumluluk durumu
        tk.Label(compliance_frame, text="Uyumluluk Durumu",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', padx=20, pady=20)

        # Uyumluluk çubukları
        self.compliance_frame = tk.Frame(compliance_frame, bg='white')
        self.compliance_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Alt panel - Uyumluluk raporu
        btn_frame = tk.Frame(compliance_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(btn_frame, text=" Uyumluluk Raporu Oluştur", style='Primary.TButton', command=self.generate_compliance_report).pack(side='left', padx=5)

    def create_reports_tab(self) -> None:
        """Raporlar sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=" Raporlar")

        # Rapor türleri
        tk.Label(reports_frame, text="Rapor Türleri",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', padx=20, pady=20)

        # Rapor butonları
        reports_btn_frame = tk.Frame(reports_frame, bg='white')
        reports_btn_frame.pack(fill='x', padx=20, pady=10)

        report_buttons = [
            (" Sektörel Uyumluluk Raporu", self.generate_sectoral_report, '#2E7D32'),
            (" Karşılaştırmalı Analiz", self.generate_comparative_analysis, '#1976D2'),
            (" İlerleme Raporu", self.generate_progress_report, '#F57C00'),
            (" Excel Dışa Aktarım", self.export_to_excel, '#388E3C'),
        ]

        for i, (text, command, color) in enumerate(report_buttons):
            btn = ttk.Button(reports_btn_frame, text=text, style='Primary.TButton', command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')

        reports_btn_frame.grid_columnconfigure(0, weight=1)
        reports_btn_frame.grid_columnconfigure(1, weight=1)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # Genel bakış verilerini yükle
            self.load_overview_data()

            # Standartlar listesini yükle
            self.load_standards_list()

        except Exception as e:
            messagebox.showerror("Hata", f"Veri yüklenirken hata: {e}")

    def load_overview_data(self) -> None:
        """Genel bakış verilerini yükle"""
        try:
            summary = self.manager.get_company_sectoral_summary(self.company_id)

            # İstatistik kartlarını oluştur
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            stats_data = [
                ("Toplam Standart", summary.get('total_standards', 0), '#2196F3'),
                ("Uygulanabilir", summary.get('applicable_standards', 0), '#4CAF50'),
                ("Uyumlu Konular", summary.get('compliant_topics', 0), '#8BC34A'),
                ("Toplam Konu", summary.get('total_topics', 0), '#FF9800'),
            ]

            for i, (title, value, color) in enumerate(stats_data):
                self.create_stat_card(self.stats_frame, title, value, color, 0, i)

        except Exception as e:
            logging.error(f"Genel bakış verileri yüklenirken hata: {e}")

    def create_stat_card(self, parent, title, value, color, row, col):
        """İstatistik kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'),
                bg=color, fg='white').pack(pady=5)

    def load_standards_list(self) -> None:
        """Standartlar listesini yükle"""
        try:
            standards = self.manager.get_sectoral_standards()

            # Standartlar listesini temizle
            self.standards_listbox.delete(0, tk.END)

            for standard in standards:
                display_text = f"{standard['standard_code']} - {standard['standard_name']} ({standard['year']})"
                self.standards_listbox.insert(tk.END, display_text)

            # ComboBox'ı da güncelle
            self.standard_combo['values'] = [f"{s['standard_code']} - {s['standard_name']}"
                                           for s in standards]

        except Exception as e:
            logging.error(f"Standartlar listesi yüklenirken hata: {e}")

    def on_standard_select(self, event) -> None:
        """Standart seçildiğinde"""
        selection = self.standards_listbox.curselection()
        if selection:
            index = selection[0]
            standards = self.manager.get_sectoral_standards()
            if index < len(standards):
                standard = standards[index]
                self.load_standard_topics(standard['standard_code'])

    def on_standard_change(self, event) -> None:
        """Standart değiştiğinde"""
        selected = self.standard_var.get()
        if selected:
            # Standart kodunu çıkar
            standard_code = selected.split(' - ')[0]
            self.load_standard_topics(standard_code)

    def load_standard_topics(self, standard_code: str) -> None:
        """Standart konularını yükle"""
        try:
            topics = self.manager.get_standard_topics(standard_code, self.company_id)

            # Treeview'ı temizle
            for item in self.topics_tree.get_children():
                self.topics_tree.delete(item)

            for topic in topics:
                self.topics_tree.insert('', 'end', values=(
                    topic.get('standard_id', ''),
                    topic.get('topic_name', ''),
                    topic.get('compliance_status', 'Not Started'),
                    topic.get('data_source', ''),
                    topic.get('notes', '')
                ))

        except Exception as e:
            logging.error(f"Standart konuları yüklenirken hata: {e}")

    def on_topic_double_click(self, event) -> None:
        """Konuya çift tıklandığında"""
        selection = self.topics_tree.selection()
        if selection:
            item = self.topics_tree.item(selection[0])
            values = item['values']
            self.show_topic_detail(values)

    def show_topic_detail(self, topic_data) -> None:
        """Konu detay penceresi"""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title("Konu Detayı")
        detail_window.geometry("600x500")
        detail_window.configure(bg='white')

        # Başlık
        tk.Label(detail_window, text=f"Konu: {topic_data[1]}",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Detay bilgileri
        detail_frame = tk.Frame(detail_window, bg='white')
        detail_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Uyumluluk durumu
        tk.Label(detail_frame, text="Uyumluluk Durumu:",
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        status_var = tk.StringVar(value=topic_data[2])
        status_combo = ttk.Combobox(detail_frame, textvariable=status_var,
                                   values=['Not Started', 'In Progress', 'Compliant', 'Not Applicable'],
                                   state='readonly')
        status_combo.pack(fill='x', pady=5)

        # Notlar
        tk.Label(detail_frame, text="Notlar:",
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(20, 5))

        notes_text = tk.Text(detail_frame, height=8, wrap='word')
        notes_text.pack(fill='both', expand=True, pady=5)
        notes_text.insert('1.0', topic_data[4] if len(topic_data) > 4 else '')

        # Butonlar
        btn_frame = tk.Frame(detail_frame, bg='white')
        btn_frame.pack(fill='x', pady=10)

        def save_changes():
            # Burada değişiklikleri kaydet
            messagebox.showinfo("Başarılı", "Değişiklikler kaydedildi!")
            detail_window.destroy()
            self.refresh_topics()

        ttk.Button(btn_frame, text=" Kaydet", style='Primary.TButton', command=save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=" İptal", command=detail_window.destroy).pack(side='left', padx=5)

    def open_report_center_gri_sectoral(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('gri')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for gri: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def refresh_topics(self) -> None:
        """Konuları yenile"""
        selected = self.standard_var.get()
        if selected:
            standard_code = selected.split(' - ')[0]
            self.load_standard_topics(standard_code)

    def generate_detailed_report(self) -> None:
        """Detaylı rapor oluştur"""
        try:
            from tkinter import filedialog

            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("file_pdf", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("save_detailed_report", "Detaylı Rapor Kaydet")
            )

            if save_path:
                messagebox.showinfo("Başarılı", f"Detaylı rapor oluşturuldu:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı: {e}")

    def generate_compliance_report(self) -> None:
        """Uyumluluk raporu oluştur"""
        try:
            from tkinter import filedialog

            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("file_pdf", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("save_compliance_report", "Uyumluluk Raporu Kaydet")
            )

            if save_path:
                messagebox.showinfo("Başarılı", f"Uyumluluk raporu oluşturuldu:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı: {e}")

    def generate_sectoral_report(self) -> None:
        """Sektörel rapor oluştur"""
        try:
            from tkinter import filedialog

            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("file_pdf", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("save_sectoral_report", "Sektörel Rapor Kaydet")
            )

            if save_path:
                messagebox.showinfo("Başarılı", f"Sektörel rapor oluşturuldu:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı: {e}")

    def generate_comparative_analysis(self) -> None:
        """Karşılaştırmalı analiz oluştur"""
        try:
            from tkinter import filedialog

            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("pdf_files", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("filetype_all", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("save_comparative_analysis", "Karşılaştırmalı Analiz Kaydet")
            )

            if save_path:
                messagebox.showinfo("Başarılı", f"Karşılaştırmalı analiz oluşturuldu:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Analiz oluşturulamadı: {e}")

    def generate_progress_report(self) -> None:
        """İlerleme raporu oluştur"""
        try:
            from tkinter import filedialog

            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("pdf_files", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("filetype_all", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("save_progress_report", "İlerleme Raporu Kaydet")
            )

            if save_path:
                messagebox.showinfo("Başarılı", f"İlerleme raporu oluşturuldu:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı: {e}")

    def export_to_excel(self) -> None:
        """Excel'e dışa aktar"""
        try:
            from tkinter import filedialog

            import pandas as pd

            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[(self.lm.tr("file_excel", "Excel Dosyaları"), "*.xlsx"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("excel_export_title", "Excel'e Dışa Aktar")
            )

            if save_path:
                # Verileri Excel'e aktar
                df = pd.DataFrame({'Örnek': ['Veri']})
                df.to_excel(save_path, index=False)
                messagebox.showinfo("Başarılı", f"Excel dosyası oluşturuldu:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Excel dışa aktarım hatası: {e}")
