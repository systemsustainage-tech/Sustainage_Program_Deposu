import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB GUI - Gelişmiş Kullanıcı Arayüzü
- Sektör İnceleme
- Veri Girişi
- Raporlama
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .sasb_manager import SASBManager
from .sasb_report_generator import SASBReportGenerator
from config.icons import Icons


class SASBGUI:
    """SASB Modülü GUI"""

    def __init__(self, parent, company_id: int = 1, main_app=None) -> None:
        self.parent = parent
        self.company_id = company_id
        self.main_app = main_app
        self.lm = LanguageManager()
        self.manager = SASBManager()
        self.report_generator = SASBReportGenerator(self.manager.db_path)
        self.selected_sector_id = None
        self.current_year = datetime.now().year
        self.entry_widgets = {}  # metric_id -> {value_widget, note_widget}

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """UI oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # 1. Header
        header = tk.Frame(main_frame, bg='#2c3e50', height=80)
        header.pack(side='top', fill='x', pady=(0, 20))
        header.pack_propagate(False)

        # Navigasyon
        nav_frame = tk.Frame(header, bg='#2c3e50')
        nav_frame.pack(side='left', padx=20)
        tk.Button(nav_frame, text=self.lm.tr("btn_back", "← Geri"), bg='#34495e', fg='white', relief='flat',
                 command=self._go_back).pack(side='left', padx=(0, 10))

        tk.Label(header, text=self.lm.tr("sasb_title", "SASB (Sustainability Accounting Standards Board)"),
                font=('Segoe UI', 20, 'bold'), fg='white', bg='#2c3e50').pack(side='left', expand=True)

        # 2. Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Tablar
        self.tab_overview = tk.Frame(self.notebook, bg='white')
        self.tab_data_entry = tk.Frame(self.notebook, bg='white')
        self.tab_reports = tk.Frame(self.notebook, bg='white')

        self.notebook.add(self.tab_overview, text=f"{Icons.CLIPBOARD} {self.lm.tr('tab_overview', 'Genel Bakış')}")
        self.notebook.add(self.tab_data_entry, text=f"{Icons.EDIT} {self.lm.tr('tab_data_entry', 'Veri Girişi')}")
        self.notebook.add(self.tab_reports, text=f"{Icons.REPORT} {self.lm.tr('tab_reports', 'Raporlar')}")

        self.init_overview_tab()
        self.init_data_entry_tab()
        self.init_reports_tab()

    def init_overview_tab(self) -> None:
        """Genel bakış tabı"""
        # Sol: Sektör listesi
        left_frame = tk.LabelFrame(self.tab_overview, text=self.lm.tr("sasb_sectors_title", "77 SASB Sektörü"),
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        self.sector_listbox = tk.Listbox(left_frame, font=('Segoe UI', 10))
        self.sector_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.sector_listbox.bind('<<ListboxSelect>>', self.on_sector_select)

        scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=self.sector_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.sector_listbox.configure(yscrollcommand=scrollbar.set)

        # Sağ: Detaylar
        right_frame = tk.LabelFrame(self.tab_overview, text=self.lm.tr("sasb_sector_details", "Sektör Detayları"),
                                    font=('Segoe UI', 11, 'bold'), bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        self.detail_text = tk.Text(right_frame, font=('Segoe UI', 10), wrap='word')
        self.detail_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Butonlar
        btn_frame = tk.Frame(right_frame, bg='white')
        btn_frame.pack(fill='x', pady=5, padx=10)
        
        ttk.Button(btn_frame, text=self.lm.tr("btn_sasb_gri_mapping", "SASB-GRI Mapping"), command=self.show_gri_mapping).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr("btn_go_to_data_entry", "Veri Girişine Git"), command=lambda: self.notebook.select(1)).pack(side='right', padx=5)

    def init_data_entry_tab(self) -> None:
        """Veri girişi tabı"""
        # Top Bar
        top_bar = tk.Frame(self.tab_data_entry, bg='#f0f0f0', height=50)
        top_bar.pack(fill='x', side='top')
        
        tk.Label(top_bar, text=self.lm.tr("lbl_year", "Yıl:"), bg='#f0f0f0').pack(side='left', padx=(10, 5), pady=10)
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_cb = ttk.Combobox(top_bar, textvariable=self.year_var, width=6, 
                              values=[str(y) for y in range(2020, 2031)])
        year_cb.pack(side='left', pady=10)
        year_cb.bind('<<ComboboxSelected>>', self.on_year_change)

        ttk.Button(top_bar, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}", command=self.save_data).pack(side='right', padx=10, pady=10)
        
        self.sector_label = tk.Label(top_bar, text=self.lm.tr("msg_select_sector_first", "Lütfen Genel Bakış tabından bir sektör seçin"), 
                                   font=('Segoe UI', 10, 'bold'), fg='#e74c3c', bg='#f0f0f0')
        self.sector_label.pack(side='left', padx=20)

        # Scrollable Content
        self.canvas = tk.Canvas(self.tab_data_entry, bg='white')
        self.scrollbar = ttk.Scrollbar(self.tab_data_entry, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def init_reports_tab(self) -> None:
        """Raporlar tabı"""
        container = tk.Frame(self.tab_reports, bg='white')
        container.pack(fill='both', expand=True, padx=40, pady=40)

        tk.Label(container, text=self.lm.tr("report_center_title", "Rapor Merkezi"), font=('Segoe UI', 16, 'bold'), bg='white').pack(pady=(0, 20))

        # PDF Rapor
        f1 = tk.LabelFrame(container, text=self.lm.tr("pdf_report_title", "PDF Raporu"), bg='white', padx=15, pady=15)
        f1.pack(fill='x', pady=10)
        
        tk.Label(f1, text=self.lm.tr("pdf_report_desc", "Tüm SASB verilerini ve tamamlanma durumunu içeren detaylı PDF raporu."), 
                bg='white', wraplength=600, justify='left').pack(anchor='w')
        ttk.Button(f1, text=self.lm.tr("btn_create_pdf", "PDF Oluştur"), command=self.generate_pdf_report).pack(anchor='e', pady=5)

        # Word Rapor
        f2 = tk.LabelFrame(container, text=self.lm.tr("word_report_title", "Word Raporu"), bg='white', padx=15, pady=15)
        f2.pack(fill='x', pady=10)
        
        tk.Label(f2, text=self.lm.tr("word_report_desc", "Düzenlenebilir Word formatında SASB raporu."), 
                bg='white', wraplength=600, justify='left').pack(anchor='w')
        ttk.Button(f2, text=self.lm.tr("btn_create_word", "Word Oluştur"), command=self.generate_word_report).pack(anchor='e', pady=5)
        
        # Excel Export
        f3 = tk.LabelFrame(container, text=self.lm.tr("excel_export_title", "Excel Export"), bg='white', padx=15, pady=15)
        f3.pack(fill='x', pady=10)
        
        tk.Label(f3, text=self.lm.tr("excel_export_desc", "Ham verileri Excel formatında dışa aktarın."), 
                bg='white', wraplength=600, justify='left').pack(anchor='w')
        ttk.Button(f3, text=self.lm.tr("btn_export_excel", "Excel'e Aktar"), command=self.generate_excel_report).pack(anchor='e', pady=5)

    def _get_year_safe(self) -> int:
        """Yılı güvenli bir şekilde integer olarak döndür"""
        try:
            val = self.year_var.get()
            return int(str(val))
        except (ValueError, TypeError):
            return self.current_year

    def generate_pdf_report(self) -> None:
        """PDF raporu oluştur"""
        if not self.selected_sector_id:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_sector_warning", "Lütfen önce bir sektör seçin."))
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("pdf_files", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                initialfile=f"SASB_Raporu_{self.company_id}_{self.current_year}.pdf",
                title=self.lm.tr("save_report", "Raporu Kaydet")
            )

            if not file_path:
                return

            year = self._get_year_safe()
            success = self.report_generator.generate_pdf_report(
                self.company_id, file_path, year
            )

            if success:
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_pdf_created", "PDF raporu başarıyla oluşturuldu."))
                os.startfile(file_path) if os.name == 'nt' else None
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_report_error", "Rapor oluşturulurken bir hata oluştu."))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('error_unexpected', 'Beklenmeyen hata')}: {e}")

    def generate_word_report(self) -> None:
        """Word raporu oluştur"""
        if not self.selected_sector_id:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_sector_warning", "Lütfen önce bir sektör seçin."))
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[(self.lm.tr("word_files", "Word Dosyaları"), "*.docx"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                initialfile=f"SASB_Raporu_{self.company_id}_{self.current_year}.docx",
                title=self.lm.tr("save_report", "Raporu Kaydet")
            )

            if not file_path:
                return

            year = self._get_year_safe()
            success = self.report_generator.generate_word_report(
                self.company_id, file_path, year
            )

            if success:
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_word_created", "Word raporu başarıyla oluşturuldu."))
                os.startfile(file_path) if os.name == 'nt' else None
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_report_error", "Rapor oluşturulurken bir hata oluştu."))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('error_unexpected', 'Beklenmeyen hata')}: {e}")

    def generate_excel_report(self) -> None:
        """Excel raporu oluştur"""
        if not self.selected_sector_id:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_sector_warning", "Lütfen önce bir sektör seçin."))
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[(self.lm.tr("excel_files", "Excel Dosyaları"), "*.xlsx"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                initialfile=f"SASB_Raporu_{self.company_id}_{self.current_year}.xlsx",
                title=self.lm.tr("save_report", "Raporu Kaydet")
            )

            if not file_path:
                return

            year = self._get_year_safe()
            success = self.report_generator.generate_excel_report(
                self.company_id, file_path, year
            )

            if success:
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_excel_created", "Excel raporu başarıyla oluşturuldu."))
                os.startfile(file_path) if os.name == 'nt' else None
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_report_error", "Rapor oluşturulurken bir hata oluştu."))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('error_unexpected', 'Beklenmeyen hata')}: {e}")

    def _go_back(self) -> None:
        """Geri dön"""
        try:
            if self.main_app:
                self.main_app.show_dashboard()
            else:
                self.parent.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def load_data(self) -> None:
        """Sektörleri yükle"""
        sectors = self.manager.get_all_sectors()
        self.sector_listbox.delete(0, tk.END)
        self.sectors = sectors
        for sector in sectors:
            display = self.lm.tr("sasb_sector_display_format", "[{code}] {name}").format(
                code=sector['sector_code'], name=sector['sector_name']
            )
            self.sector_listbox.insert(tk.END, display)
        
        # İstatistik göster
        self.detail_text.insert('1.0', self._get_welcome_text(len(sectors)))

    def _get_welcome_text(self, count):
        template = self.lm.tr("sasb_welcome_text", """
SASB (Sustainability Accounting Standards Board)
================================================

 Toplam Sektör: {count}
 
 Nasıl Kullanılır:
1. Sol taraftan sektörünüzü seçin
2. 'Veri Girişi' sekmesine gidin
3. Metrikler için değerlerinizi girin ve kaydedin
4. 'Raporlar' sekmesinden çıktınızı alın

 Not: Veriler otomatik olarak veritabanına kaydedilir.
""")
        return template.format(count=count)

    def on_sector_select(self, event) -> None:
        """Sektör seçildiğinde"""
        selection = self.sector_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        sector = self.sectors[index]
        self.selected_sector_id = sector['id']

        # 1. Overview Güncelle
        self.update_overview(sector)
        
        # 2. Data Entry Hazırla
        self.sector_label.config(text=f"{self.lm.tr('lbl_selected_sector', 'Seçili Sektör')}: {sector['sector_name']} ({sector['sector_code']})", fg='green')
        self.refresh_data_entry()

    def update_overview(self, sector):
        self.detail_text.delete('1.0', tk.END)
        topics = self.manager.get_sector_topics(sector['id'])
        
        text = f"""{self.lm.tr("lbl_sector", "Sektör")}: {sector['sector_name']} ({sector['sector_code']})
{self.lm.tr("lbl_group", "Grup")}: {sector['industry_group']}
{'='*60}
{self.lm.tr("lbl_description", "Açıklama")}: {sector['description'] or '-'}
{'='*60}
{self.lm.tr("lbl_material_topics", "MATERYAL DISCLOSURE TOPICS")} ({len(topics)} {self.lm.tr("lbl_count_suffix", "adet")}):
"""
        
        for topic in topics:
            text += f"\n• {topic['topic_name']} ({topic['topic_code']})\n"
            text += f"  {self.lm.tr('lbl_category', 'Kategori')}: {topic.get('topic_category', '-')}\n"
            # text += f"  {topic['description'][:100]}...\n"
        
        self.detail_text.insert('1.0', text)

    def on_year_change(self, event):
        if self.selected_sector_id:
            self.refresh_data_entry()

    def refresh_data_entry(self):
        """Veri giriş formunu yenile"""
        # Temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entry_widgets.clear()
        
        if not self.selected_sector_id:
            return

        year = self._get_year_safe()
        topics = self.manager.get_sector_topics(self.selected_sector_id)
        responses = self.manager.get_metric_responses(self.company_id, year)

        row_idx = 0
        
        # Başlıklar
        headers = [self.lm.tr("col_metric_code", "Metrik Kodu"), self.lm.tr("col_metric_name", "Metrik Adı"), self.lm.tr("col_value", "Değer"), self.lm.tr("col_unit", "Birim"), self.lm.tr("col_notes", "Notlar")]
        for col, text in enumerate(headers):
            tk.Label(self.scrollable_frame, text=text, font=('Segoe UI', 9, 'bold'), bg='#e0e0e0', padx=5, pady=5)\
                .grid(row=row_idx, column=col, sticky='nsew', padx=1, pady=1)
        row_idx += 1

        for topic in topics:
            # Topic Başlığı
            tk.Label(self.scrollable_frame, text=f"{topic['topic_name']} ({topic['category']})", 
                    font=('Segoe UI', 9, 'bold', 'italic'), bg='#d6eaf8', anchor='w')\
                .grid(row=row_idx, column=0, columnspan=5, sticky='ew', pady=(10, 0))
            row_idx += 1
            
            metrics = self.manager.get_topic_metrics(topic['id'])
            for metric in metrics:
                resp = responses.get(metric['id'], {})
                
                # Kod
                tk.Label(self.scrollable_frame, text=metric['metric_code'], bg='white', anchor='w')\
                    .grid(row=row_idx, column=0, sticky='w', padx=5, pady=2)
                
                # İsim (Tooltip eklenebilir)
                lbl = tk.Label(self.scrollable_frame, text=metric['metric_name'], bg='white', anchor='w', wraplength=300)
                lbl.grid(row=row_idx, column=1, sticky='w', padx=5, pady=2)
                
                # Değer Entry
                val_var = tk.StringVar(value=resp.get('response_value', ''))
                val_entry = ttk.Entry(self.scrollable_frame, textvariable=val_var, width=20)
                val_entry.grid(row=row_idx, column=2, padx=5, pady=2)
                
                # Birim
                unit_text = metric['unit'] or '-'
                tk.Label(self.scrollable_frame, text=unit_text, bg='white').grid(row=row_idx, column=3, padx=5)
                
                # Not Entry
                note_var = tk.StringVar(value=resp.get('notes', ''))
                note_entry = ttk.Entry(self.scrollable_frame, textvariable=note_var, width=20)
                note_entry.grid(row=row_idx, column=4, padx=5, pady=2)
                
                self.entry_widgets[metric['id']] = {
                    'value': val_var,
                    'note': note_var,
                    'unit': metric['unit']
                }
                
                row_idx += 1

    def save_data(self) -> None:
        """Verileri kaydet"""
        if not self.selected_sector_id:
            return

        try:
            year = int(self.year_var.get())
            count = 0
            
            # Sektör kaydı
            self.manager.select_company_sector(self.company_id, year, self.selected_sector_id)
            
            for metric_id, widgets in self.entry_widgets.items():
                val = widgets['value'].get().strip()
                note = widgets['note'].get().strip()
                
                if val or note: # Boş değilse kaydet
                    self.manager.save_metric_response(
                        company_id=self.company_id,
                        year=year,
                        metric_id=metric_id,
                        response_value=val,
                        unit=widgets['unit'],
                        notes=note
                    )
                    count += 1
            
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{count} {self.lm.tr('msg_data_saved_count', 'adet veri kaydedildi.')}")
            
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('error_save', 'Kaydetme hatası')}: {e}")

    def show_gri_mapping(self) -> None:
        """SASB-GRI mapping göster"""
        mappings = self.manager.get_sasb_gri_mappings()
        if not mappings:
            messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("msg_no_data", "Veri bulunamadı!"))
            return

        window = tk.Toplevel(self.parent)
        window.title(self.lm.tr("sasb_gri_mapping_title", "SASB-GRI Mapping"))
        window.geometry("900x600")

        columns = (self.lm.tr("col_sasb_code", "SASB Kodu"), self.lm.tr("col_gri_std", "GRI Standard"), self.lm.tr("col_gri_disc", "GRI Disclosure"), self.lm.tr("col_strength", "Güç"), self.lm.tr("col_notes", "Notlar"))
        tree = ttk.Treeview(window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(window, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(fill='both', expand=True)

        for m in mappings:
            tree.insert('', 'end', values=(m['sasb_code'], m['gri_standard'], m['gri_disclosure'], m['strength'], m['notes']))
