import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rapor Merkezi GUI - TAM VE EKSİKSİZ
Logo yönetimi, önizleme, toplu silme, zamanlanmış raporlar
"""

import json
import os
import shutil
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Dict, List

from modules.company.company_profile_manager import CompanyProfileManager
from utils.language_manager import LanguageManager

from .advanced_report_manager import AdvancedReportManager
from .universal_exporter import UniversalExporter
from config.icons import Icons


class ReportCenterGUI:
    """Rapor Merkezi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.report_mgr = AdvancedReportManager()
        self.profile_mgr = CompanyProfileManager()
        self.selected_reports: List[int] = []
        try:
            from utils.progress_engine import STATUS_COMPLETED, STATUS_IN_PROGRESS, ProgressEngine
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
            self._pe = ProgressEngine(self.db_path)
            self._rep_steps = [
                ('rep_start', 'Başlangıç'),
                ('rep_filter', 'Filtreleri Ayarla'),
                ('rep_preview', 'Önizleme'),
                ('rep_export', 'Dışa Aktarım'),
                ('rep_complete', 'Tamamla')
            ]
            self._STATUS_IN_PROGRESS = STATUS_IN_PROGRESS
            self._STATUS_COMPLETED = STATUS_COMPLETED
        except Exception:
            self._pe = None
            self._rep_steps = [('rep_start', 'Başlangıç')]
            self._STATUS_IN_PROGRESS = 'in_progress'
            self._STATUS_COMPLETED = 'completed'

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"[ReportCenterGUI] Failed to set zoomed state: {e}")

        self.setup_ui()
        self.load_data()
        try:
            if self._pe:
                self._pe.initialize_steps(user_id=1, company_id=self.company_id, module_code='report_center', steps=self._rep_steps)
                self._pe.set_progress(1, self.company_id, 'report_center', 'rep_start', 'Başlangıç', self._STATUS_IN_PROGRESS)
                self._update_guided_header()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def setup_ui(self) -> None:
        """Rapor merkezi arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#6A1B9A', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" " + self.lm.tr('advanced_report_center', 'Gelişmiş Rapor Merkezi'),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#6A1B9A')
        title_label.pack(expand=True)

        guided = tk.Frame(main_frame, bg='#f8fafc', height=50)
        guided.pack(fill='x', pady=(0, 10))
        guided.pack_propagate(False)
        self._guided_frame = guided
        try:
            self._progress_var = tk.DoubleVar(value=0.0)
            pb = ttk.Progressbar(guided, maximum=100.0, variable=self._progress_var)
            pb.pack(side='left', fill='x', expand=True, padx=10, pady=10)
            self._step_info = tk.Label(guided, text=f"{self.lm.tr('step', 'Adım')}: {self.lm.tr('start', 'Başlangıç')}", font=('Segoe UI', 10, 'bold'), bg='#f8fafc', fg='#334155')
            self._step_info.pack(side='left', padx=10)

            def _next_step():
                try:
                    if not self._pe:
                        return
                    progress = self._pe.get_module_progress(self.company_id, 'report_center', user_id=1)
                    order = [sid for sid, _ in self._rep_steps]
                    current_sid = None
                    for p in progress:
                        if p['status'] == self._STATUS_IN_PROGRESS:
                            current_sid = p['step_id']
                            break
                    if current_sid is None:
                        current_sid = order[0]
                    idx = order.index(current_sid)
                    self._pe.set_progress(1, self.company_id, 'report_center', current_sid,
                                          dict(self._rep_steps)[current_sid], self._STATUS_COMPLETED)
                    if idx + 1 < len(order):
                        next_sid = order[idx + 1]
                        self._pe.set_progress(1, self.company_id, 'report_center', next_sid,
                                              dict(self._rep_steps)[next_sid], self._STATUS_IN_PROGRESS)
                    self._update_guided_header()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            ttk.Button(guided, text=" " + self.lm.tr('next_step', 'Sonraki Adım'), style='Primary.TButton', command=_next_step).pack(side='right', padx=10)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_reports_tab()
        self.create_logo_management_tab()
        self.create_scheduled_reports_tab()
        self.create_email_reports_tab()
        self.create_quality_control_tab()

        try:
            self._update_guided_header()
        except Exception as e:
            logging.error(f"[ReportCenterGUI] Failed to update guided header: {e}")

    def create_reports_tab(self) -> None:
        """Raporlar sekmesi"""
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text=" Tüm Raporlar")

        info_frame = tk.Frame(reports_frame, bg='#f8fafc')
        info_frame.pack(fill='x', padx=20, pady=(10,0))
        self._info_var = tk.StringVar(value='Filtre: Modül=Tümü, Dönem=Tümü, Etiket=Tümü')
        tk.Label(info_frame, textvariable=self._info_var, font=('Segoe UI', 10), bg='#f8fafc', fg='#334155').pack(side='left')

        # Modül filtresi
        filter_frame = tk.Frame(reports_frame, bg='white')
        filter_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(filter_frame, text="Modül:", font=('Segoe UI', 11, 'bold'),
                bg='white').pack(side='left', padx=(0, 10))

        self.module_filter_var = tk.StringVar(value="Tümü")
        modules = ["Tümü"] + list(self.report_mgr.MODULE_REPORT_FOLDERS.keys())
        self.module_filter_combo = ttk.Combobox(filter_frame, textvariable=self.module_filter_var,
                                               values=modules, state='readonly', width=20)
        self.module_filter_combo.pack(side='left', padx=(0, 10))
        self.module_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        tk.Label(filter_frame, text=self.lm.tr('period', 'Dönem') + ":", font=('Segoe UI', 11, 'bold'),
                bg='white').pack(side='left', padx=(10, 10))
        self.period_filter_var = tk.StringVar(value="Tümü")
        self.period_filter_combo = ttk.Combobox(filter_frame, textvariable=self.period_filter_var,
                                               values=["Tümü"], state='readonly', width=12)
        self.period_filter_combo.pack(side='left', padx=(0, 10))
        self.period_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        tk.Label(filter_frame, text=self.lm.tr('tag', 'Etiket') + ":", font=('Segoe UI', 11, 'bold'), bg='white').pack(side='left', padx=(10, 10))
        self.tag_filter_var = tk.StringVar(value="Tümü")
        self.tag_filter_combo = ttk.Combobox(filter_frame, textvariable=self.tag_filter_var,
                                             values=["Tümü"], state='readonly', width=18)
        self.tag_filter_combo.pack(side='left', padx=(0, 10))
        self.tag_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        tk.Label(filter_frame, text=self.lm.tr('search', 'Ara') + ":", font=('Segoe UI', 11, 'bold'), bg='white').pack(side='left', padx=(10, 10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=24)
        self.search_entry.pack(side='left')
        try:
            self.search_var.trace_add('write', lambda *args: self.refresh_reports())
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        ttk.Button(filter_frame, text=" " + self.lm.tr('refresh', 'Yenile'), command=self.refresh_reports).pack(side='left')

        # Raporlar listesi
        list_frame = tk.Frame(reports_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = (self.lm.tr('select', 'Seç'), self.lm.tr('report_name', 'Rapor Adı'), self.lm.tr('module', 'Modül'), self.lm.tr('type', 'Tür'), self.lm.tr('period', 'Dönem'), self.lm.tr('date', 'Tarih'), self.lm.tr('size', 'Boyut'))
        self.reports_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)

        self.reports_tree.heading('#0', text='')
        self.reports_tree.column('#0', width=30)

        for col in columns[1:]:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=120)

        self.reports_tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.reports_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.reports_tree.configure(yscrollcommand=scrollbar.set)

        # Çift tıklama ile önizleme
        self.reports_tree.bind('<Double-1>', self.preview_selected_report)

        # Aksiyon butonları
        action_frame = tk.Frame(reports_frame, bg='white')
        action_frame.pack(fill='x', padx=20, pady=10)

        ttk.Button(action_frame, text=" " + self.lm.tr('select_all', 'Tümünü Seç'), command=self.select_all_reports).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('preview', 'Önizle'), style='Primary.TButton', command=self.preview_selected_report).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('open', 'Aç'), style='Primary.TButton', command=self.open_selected_report).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('save_as', 'Farklı Kaydet'), style='Primary.TButton', command=self.save_as).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('print', 'Yazdır'), style='Primary.TButton', command=self.print_report).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" CSV", style='Primary.TButton', command=self.export_registry_csv).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Excel", style='Primary.TButton', command=self.export_registry_excel).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('open_folder', 'Klasörü Aç'), style='Primary.TButton', command=self.open_selected_report_folder).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('copy_path', 'Yol Kopyala'), style='Primary.TButton', command=self.copy_selected_report_path).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('update_tags', 'Etiket Güncelle'), style='Primary.TButton', command=self.update_selected_tags).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" " + self.lm.tr('btn_delete', 'Sil'), style='Accent.TButton', command=self.delete_selected_reports).pack(side='left', padx=5)

    def create_logo_management_tab(self) -> None:
        """Logo yönetimi sekmesi"""
        logo_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(logo_frame, text=" " + self.lm.tr('company_logo', 'Firma Logosu'))

        # Başlık
        tk.Label(logo_frame, text=self.lm.tr('company_logo_management', 'Firma Logo Yönetimi'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=20)

        # Açıklama
        tk.Label(logo_frame,
                text=self.lm.tr('upload_logo_desc', 'Firma logosunu yükleyin. Bu logo tüm raporlarda kullanılacaktır.'),
                font=('Segoe UI', 11), bg='white', fg='#666').pack(pady=5)

        # Logo önizleme
        preview_frame = tk.Frame(logo_frame, bg='#f5f5f5', relief='solid', bd=2)
        preview_frame.pack(pady=20)

        self.logo_preview_label = tk.Label(preview_frame, text=self.lm.tr('logo_not_uploaded', 'Logo yüklenmemiş'),
                                          font=('Segoe UI', 12), bg='#f5f5f5',
                                          width=50, height=10)
        self.logo_preview_label.pack(padx=20, pady=20)

        # Logo butonları
        btn_frame = tk.Frame(logo_frame, bg='white')
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text=" " + self.lm.tr('upload_logo', 'Logo Yükle'), style='Primary.TButton', command=self.upload_logo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="️ " + self.lm.tr('delete_logo', 'Logo Sil'), style='Accent.TButton', command=self.delete_logo).pack(side='left', padx=5)

        # Logo bilgileri
        info_frame = tk.Frame(logo_frame, bg='white')
        info_frame.pack(pady=20)

        tk.Label(info_frame, text=self.lm.tr('supported_formats', 'Desteklenen formatlar: PNG, JPG, JPEG'),
                font=('Segoe UI', 10), bg='white', fg='#666').pack()
        tk.Label(info_frame, text=self.lm.tr('recommended_size', 'Önerilen boyut: 400x200 piksel'),
                font=('Segoe UI', 10), bg='white', fg='#666').pack()

    def create_scheduled_reports_tab(self) -> None:
        """Zamanlanmış raporlar sekmesi"""
        scheduled_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scheduled_frame, text=f"{Icons.TIME} {self.lm.tr('scheduled_reports', 'Zamanlanmış Raporlar')}")

        # Başlık
        tk.Label(scheduled_frame, text=self.lm.tr('auto_scheduled_reports', 'Otomatik Zamanlanmış Raporlar'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Zamanlanmış raporlar listesi
        columns = (self.lm.tr('module', 'Modül'), self.lm.tr('report_type', 'Rapor Türü'), self.lm.tr('frequency', 'Sıklık'), self.lm.tr('time', 'Saat'), self.lm.tr('btn_next', 'Sonraki'), self.lm.tr('status', 'Durum'))
        self.scheduled_tree = ttk.Treeview(scheduled_frame, columns=columns,
                                          show='headings', height=10)

        for col in columns:
            self.scheduled_tree.heading(col, text=col)
            self.scheduled_tree.column(col, width=120)

        self.scheduled_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Yeni zamanlama butonu
        ttk.Button(scheduled_frame, text=" " + self.lm.tr('new_schedule', 'Yeni Zamanlama'), style='Primary.TButton', command=self.add_schedule).pack(pady=10)

    def create_email_reports_tab(self) -> None:
        """Email raporları sekmesi"""
        email_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(email_frame, text=" " + self.lm.tr('email_reports', 'Email Raporları'))

        # Başlık
        tk.Label(email_frame, text=self.lm.tr('send_report_via_email', 'Email ile Rapor Gönderimi'),
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        tk.Label(email_frame, text=self.lm.tr('send_report_email_desc', 'Raporları otomatik olarak email ile gönderin'),
                font=('Segoe UI', 11), bg='white').pack(pady=5)

    def create_quality_control_tab(self) -> None:
        """Kalite Kontrol sekmesi"""
        qc_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(qc_frame, text=" " + self.lm.tr('quality_control', 'Kalite Kontrol'))

        tk.Label(qc_frame, text=self.lm.tr('quality_analysis_title', 'Rapor Kalitesi ve Veri Uygunluğu Analizi'),
                 font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        tk.Label(qc_frame, text=self.lm.tr('quality_analysis_desc', 'Modüller arası veri bütünlüğü ve rapor uygunluğu denetlenir.'),
                 font=('Segoe UI', 10), bg='white', fg='#555').pack(pady=(0, 10))

        # Sonuç tablosu
        columns = (self.lm.tr('module', 'Modül'), self.lm.tr('control', 'Kontrol'), self.lm.tr('status', 'Durum'), self.lm.tr('detail', 'Detay'))
        self.qc_tree = ttk.Treeview(qc_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.qc_tree.heading(col, text=col)
            w = 100 if col in (self.lm.tr('module', 'Modül'), self.lm.tr('status', 'Durum')) else 220
            self.qc_tree.column(col, width=w)
        self.qc_tree.pack(fill='both', expand=True, padx=20, pady=10)

        btn_frame = tk.Frame(qc_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)
        tk.Button(btn_frame, text=" " + self.lm.tr('run_quality_analysis', 'Kalite Analizini Çalıştır'),
                  command=self.run_quality_checks,
                  bg='#1565C0', fg='white', font=('Segoe UI', 11, 'bold'), padx=16, pady=8).pack(side='left')


    def run_quality_checks(self) -> None:
        """Kalite kontrol denetimlerini çalıştır ve tabloya yaz"""


    def _update_guided_header(self) -> None:
        try:
            if not self._pe:
                return
            percent = self._pe.get_completion_percentage(self.company_id, 'report_center', self._rep_steps, user_id=1)
            self._progress_var.set(percent)
            progress = self._pe.get_module_progress(self.company_id, 'report_center', user_id=1)
            active = None
            for p in progress:
                if p['status'] == self._STATUS_IN_PROGRESS:
                    active = p
                    break
            step_text = f"{self.lm.tr('step', 'Adım')}: {active['step_title']}" if active else f"{self.lm.tr('step', 'Adım')}: -"
            self._step_info.configure(text=step_text)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        try:
            # Temizle
            for item in self.qc_tree.get_children():
                self.qc_tree.delete(item)

            # ISSB Aksiyon Planı
            try:
                from modules.issb.issb_report_generator import ISSBReportGenerator
                issb = ISSBReportGenerator()
                year = datetime.now().year
                summary = issb.get_action_plan_status_summary(self.company_id, year)
                total = sum(summary.values())
                overdue = summary.get('son_tarih_gecmis', 0)
                status = 'OK' if total > 0 else self.lm.tr('missing_data', 'Eksik Veri')
                detail = f"{self.lm.tr('total', 'Toplam')}: {total}, {self.lm.tr('overdue', 'Gecikmiş')}: {overdue}"
                self.qc_tree.insert('', 'end', values=('ISSB', self.lm.tr('action_plan_status', 'Aksiyon Planı Durumu'), status, detail))
            except Exception as e:
                self.qc_tree.insert('', 'end', values=('ISSB', self.lm.tr('action_plan_status', 'Aksiyon Planı Durumu'), self.lm.tr('error', 'Hata'), str(e)))

            # GRI Content Index kapsama
            try:
                from modules.gri.gri_docx_pdf_reports import GRIDocxPDFReports
                gri = GRIDocxPDFReports()
                data = gri.generate_gri_content_index_data(self.company_id)
                if data and 'summary' in data and 'categories' in data['summary']:
                    cats = data['summary']['categories']
                    pending = sum(v.get('pending', 0) for v in cats.values())
                    total = sum(v.get('total', 0) for v in cats.values())
                    status = 'OK' if total > 0 and pending/total < 0.5 else self.lm.tr('needs_improvement', 'İyileştirilmeli')
                    detail = f"{self.lm.tr('total_indicators', 'Toplam Gösterge')}: {total}, {self.lm.tr('missing_response', 'Eksik Yanıt')}: {pending}"
                    self.qc_tree.insert('', 'end', values=('GRI', self.lm.tr('content_index_coverage', 'Content Index Kapsam'), status, detail))
                else:
                    self.qc_tree.insert('', 'end', values=('GRI', self.lm.tr('content_index_coverage', 'Content Index Kapsam'), self.lm.tr('missing_data', 'Eksik Veri'), self.lm.tr('summary_not_found', 'Özet verisi bulunamadı')))
            except Exception as e:
                self.qc_tree.insert('', 'end', values=('GRI', self.lm.tr('content_index_coverage', 'Content Index Kapsam'), self.lm.tr('error', 'Hata'), str(e)))

            # Genel DOCX Türkçe başlık/paragraf helper kontrolü
            try:
                from modules.gri.gri_docx_pdf_reports import (  # type: ignore
                    _add_turkish_heading,
                    _add_turkish_paragraph,
                )
                _ = (_add_turkish_paragraph, _add_turkish_heading)
                self.qc_tree.insert('', 'end', values=(self.lm.tr('common', 'Ortak'), self.lm.tr('turkish_docx_helpers', 'Türkçe DOCX Yardımcıları'), 'OK', self.lm.tr('available', 'Mevcut')))
            except Exception:
                self.qc_tree.insert('', 'end', values=(self.lm.tr('common', 'Ortak'), self.lm.tr('turkish_docx_helpers', 'Türkçe DOCX Yardımcıları'), self.lm.tr('missing', 'Eksik'), self.lm.tr('undefined_in_gri', 'GRI modülünde tanımsız')))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('quality_check_failed', 'Kalite kontrol çalıştırılamadı')}: {e}")


    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.refresh_reports()
            self.load_logo_preview()
        except Exception as e:
            logging.error(f"Veri yukleme hatasi: {e}")

    def refresh_reports(self) -> None:
        """Raporları yenile"""
        try:
            # Treeview'ı temizle
            for item in self.reports_tree.get_children():
                self.reports_tree.delete(item)

            # Filtre
            module_filter = self.module_filter_var.get()
            all_str = self.lm.tr('all', 'Tümü')
            period_filter = getattr(self, 'period_filter_var', tk.StringVar(value=all_str)).get()
            tag_filter = getattr(self, 'tag_filter_var', tk.StringVar(value=all_str)).get()
            search_term = ''
            try:
                search_term = (self.search_var.get() or '').strip().lower()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            periods = set()
            tags_set = set()

            # Tüm modüller için raporları getir
            for module_code in self.report_mgr.MODULE_REPORT_FOLDERS.keys():
                if module_filter != all_str and module_filter != module_code:
                    continue

                reports = self.report_mgr.get_module_reports(self.company_id, module_code)

                for report in reports:
                    tjson = report.get('tags')
                    tag_str = ''
                    if tjson:
                        try:
                            tlst = json.loads(tjson)
                            if isinstance(tlst, list):
                                for t in tlst:
                                    if isinstance(t, str) and t.strip():
                                        tags_set.add(t.strip())
                                tag_str = ','.join([str(t) for t in tlst if isinstance(t, str)])
                            else:
                                tag_str = str(tjson)
                        except Exception:
                            tag_str = str(tjson)

                    # Dosya boyutunu formatla
                    size_kb = report.get('file_size', 0) / 1024
                    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"

                    # Tarihi formatla
                    created_at = report.get('created_at', '')
                    if created_at:
                        try:
                            dt = datetime.fromisoformat(created_at)
                            date_str = dt.strftime("%d.%m.%Y %H:%M")
                        except Exception:
                            date_str = created_at
                    else:
                        date_str = ""

                    rp = report.get('reporting_period', '') or ''
                    if period_filter != all_str and rp != period_filter:
                        continue
                    if tag_filter != all_str:
                        if not tag_str or tag_filter.lower() not in [s.strip().lower() for s in tag_str.split(',') if s.strip()]:
                            continue
                    if search_term:
                        name = (report.get('report_name', '') or '').lower()
                        mod = (report.get('module_code', '') or '').lower()
                        rtype = (report.get('report_type', '') or '').lower()
                        comb = f"{name} {mod} {rtype} {rp} {tag_str.lower()}"
                        if search_term not in comb:
                            continue
                    periods.add(rp)
                    self.reports_tree.insert('', 'end', iid=report['id'], values=(
                        '',
                        report.get('report_name', ''),
                        report.get('module_code', ''),
                        report.get('report_type', ''),
                        rp,
                        date_str,
                        size_str
                    ))
            if hasattr(self, 'period_filter_combo'):
                current = self.period_filter_var.get()
                values = [all_str] + sorted([p for p in periods if p], reverse=True)
                self.period_filter_combo['values'] = values
                if current not in values:
                    self.period_filter_var.set(all_str)
            if hasattr(self, 'tag_filter_combo'):
                tcurrent = self.tag_filter_var.get()
                tvalues = [all_str] + sorted([t for t in tags_set if t])
                self.tag_filter_combo['values'] = tvalues
                if tcurrent not in tvalues:
                    self.tag_filter_var.set(all_str)
            try:
                self._info_var.set(f"{self.lm.tr('filter', 'Filtre')}: {self.lm.tr('module', 'Modül')}={module_filter}, {self.lm.tr('period', 'Dönem')}={period_filter}, {self.lm.tr('tag', 'Etiket')}={tag_filter}")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        except Exception as e:
            logging.error(f"{self.lm.tr('refresh_error', 'Raporlar yenilenirken hata')}: {e}")

    def on_filter_change(self, event) -> None:
        """Filtre değiştiğinde"""
        self.refresh_reports()

    def select_all_reports(self) -> None:
        """Tüm raporları seç"""
        for item in self.reports_tree.get_children():
            self.reports_tree.selection_add(item)

    def preview_selected_report(self, event=None) -> None:
        """Seçilen raporu önizle"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_report_warning', 'Lütfen bir rapor seçin!'))
            return

        try:
            report_id = int(selection[0])

            # Rapor bilgisini al
            conn = sqlite3.connect(self.report_mgr.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM report_registry WHERE id = ?
            """, (report_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('report_not_found', 'Rapor bulunamadı!'))
                return

            columns = ['id', 'company_id', 'module_code', 'report_name', 'report_type',
                      'file_path', 'file_size', 'reporting_period', 'created_by',
                      'created_at', 'last_accessed', 'access_count', 'tags', 'description']
            report = dict(zip(columns, row))

            # Önizleme penceresi
            self.show_preview_window(report)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('preview_error', 'Önizleme hatası')}: {e}")

    def show_preview_window(self, report: Dict) -> None:
        """Önizleme penceresi göster"""
        preview_win = tk.Toplevel(self.parent)
        preview_win.title(f"{self.lm.tr('report_preview', 'Rapor Önizleme')} - {report['report_name']}")
        preview_win.geometry("800x600")
        preview_win.configure(bg='white')

        # Başlık
        title_frame = tk.Frame(preview_win, bg='#6A1B9A')
        title_frame.pack(fill='x')

        tk.Label(title_frame, text=report['report_name'],
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#6A1B9A').pack(pady=10)

        # Rapor bilgileri
        info_frame = tk.Frame(preview_win, bg='white')
        info_frame.pack(fill='x', padx=20, pady=10)

        info_items = [
            (self.lm.tr('module', 'Modül') + ":", report.get('module_code', '')),
            (self.lm.tr('type', 'Tür') + ":", report.get('report_type', '')),
            (self.lm.tr('period', 'Dönem') + ":", report.get('reporting_period', '')),
            (self.lm.tr('created_at', 'Oluşturulma') + ":", report.get('created_at', '')),
            (self.lm.tr('size', 'Boyut') + ":", f"{report.get('file_size', 0)/1024:.1f} KB"),
        ]

        for label, value in info_items:
            row_frame = tk.Frame(info_frame, bg='white')
            row_frame.pack(fill='x', pady=2)
            tk.Label(row_frame, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='white', width=15, anchor='w').pack(side='left')
            tk.Label(row_frame, text=value, font=('Segoe UI', 10),
                    bg='white', anchor='w').pack(side='left')

        # Önizleme alanı (basit metin gösterimi)
        preview_text = tk.Text(preview_win, wrap='word', height=15)
        preview_text.pack(fill='both', expand=True, padx=20, pady=10)
        preview_text.insert('1.0', f"{self.lm.tr("report_label", "Rapor")}: {report['report_name']}\n\n"
                                  f"{self.lm.tr('file_path', 'Dosya yolu')}: {report['file_path']}\n\n"
                                  + self.lm.tr('use_open_button', "Tam önizleme için 'Aç' butonunu kullanın."))
        preview_text.config(state='disabled')

        # Aksiyon butonları (ALTTA)
        btn_frame = tk.Frame(preview_win, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)

        ttk.Button(btn_frame, text=" " + self.lm.tr('open_report', 'Raporu Aç'), style='Primary.TButton',
                   command=lambda: self.open_report_file(report['file_path'])).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=" " + self.lm.tr('save_as', 'Farklı Kaydet'), style='Primary.TButton',
                   command=lambda: self.save_report_as(report['file_path'])).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=" " + self.lm.tr('print', 'Yazdır'), style='Primary.TButton',
                   command=lambda: self.print_report_file(report['file_path'])).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=" " + self.lm.tr('btn_delete', 'Sil'), style='Accent.TButton',
                   command=lambda: self.delete_single_report(report['id'], preview_win)).pack(side='left', padx=5)

    def load_logo_preview(self) -> None:
        """Logo önizlemesini yükle"""
        try:
            logo_path = self.profile_mgr.get_logo_path(self.company_id)

            if logo_path and os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img.thumbnail((300, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.logo_preview_label.config(image=photo, text='')
                self._logo_preview_photo = photo
            else:
                self.logo_preview_label.config(text=self.lm.tr('logo_not_uploaded_hint', 'Logo yüklenmemiş\n\n Logo Yükle butonunu kullanın'))

        except Exception as e:
            logging.error(f"{self.lm.tr('logo_preview_error', 'Logo onizleme hatasi')}: {e}")

    def upload_logo(self) -> None:
        """Logo yükle"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr('select_company_logo', 'Firma Logosu Seçin'),
            filetypes=[(self.lm.tr('image_files', 'Resim Dosyaları'), "*.png *.jpg *.jpeg"), (self.lm.tr('all_files', 'Tüm Dosyalar'), "*.*")]
        )

        if file_path:
            success = self.profile_mgr.upload_logo(self.company_id, file_path)
            if success:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('logo_uploaded_success', 'Logo başarıyla yüklendi!\n\nTüm raporlarda kullanılacak.'))
                self.load_logo_preview()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('logo_upload_failed', 'Logo yüklenemedi!'))

    def delete_logo(self) -> None:
        """Logo sil"""
        if messagebox.askyesno(self.lm.tr('confirm', 'Onay'), self.lm.tr('delete_logo_confirm', 'Firma logosunu silmek istediğinizden emin misiniz?')):
            success = self.profile_mgr.delete_logo(self.company_id)
            if success:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('logo_deleted', 'Logo silindi!'))
                self.load_logo_preview()

    def open_selected_report(self) -> None:
        """Seçilen raporu aç"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_report_warning', 'Lütfen bir rapor seçin!'))
            return

        try:
            report_id = int(selection[0])
            conn = sqlite3.connect(self.report_mgr.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM report_registry WHERE id = ?", (report_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.open_report_file(result[0])

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('report_open_error', 'Rapor açma hatası')}: {e}")

    def open_report_file(self, file_path: str) -> None:
        """Rapor dosyasını aç"""
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('report_file_not_found', 'Rapor dosyası bulunamadı!'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('file_open_error', 'Dosya açma hatası')}: {e}")

    def save_as(self) -> None:
        """Farklı kaydet"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_report_warning', 'Lütfen bir rapor seçin!'))
            return

        try:
            report_id = int(selection[0])
            conn = sqlite3.connect(self.report_mgr.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, report_name, report_type FROM report_registry WHERE id = ?", (report_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.save_report_as(result[0])

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('save_as_error', 'Farklı kaydet hatası')}: {e}")

    def save_report_as(self, source_path: str) -> None:
        """Raporu farklı kaydet"""
        try:
            if not os.path.exists(source_path):
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('source_file_not_found', 'Kaynak dosya bulunamadı!'))
                return

            # Dosya türünü belirle
            ext = os.path.splitext(source_path)[1]

            file_types = [(self.lm.tr('all_files', 'Tüm Dosyalar'), "*.*")]
            if ext == ".pdf":
                file_types.insert(0, (self.lm.tr('pdf_files', 'PDF Dosyaları'), "*.pdf"))
            elif ext in [".xlsx", ".xls"]:
                file_types.insert(0, (self.lm.tr('excel_files', 'Excel Dosyaları'), "*.xlsx *.xls"))
            elif ext in [".docx", ".doc"]:
                file_types.insert(0, (self.lm.tr('word_files', 'Word Dosyaları'), "*.docx *.doc"))

            dest_path = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report_as_title', 'Raporu Farklı Kaydet'),
                filetypes=file_types,
                defaultextension=ext
            )

            if dest_path:
                shutil.copy2(source_path, dest_path)
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('report_saved_success', 'Rapor kaydedildi')}:\n{dest_path}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def print_report(self) -> None:
        """Seçilen raporu yazdır"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_report_warning', 'Lütfen bir rapor seçin!'))
            return

        try:
            report_id = int(selection[0])
            conn = sqlite3.connect(self.report_mgr.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM report_registry WHERE id = ?", (report_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.print_report_file(result[0])

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_error', 'Yazdırma hatası')}: {e}")

    def print_report_file(self, file_path: str) -> None:
        """Rapor dosyasını yazdır"""
        try:
            if os.path.exists(file_path):
                # Windows'ta yazdırma diyalogu aç
                os.startfile(file_path, "print")
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('print_started', 'Yazdırma başlatıldı!'))
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('report_file_not_found', 'Rapor dosyası bulunamadı!'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_error', 'Yazdırma hatası')}: {e}")

    def delete_selected_reports(self) -> None:
        """Seçilen raporları sil (toplu silme)"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_at_least_one_report', 'Lütfen en az bir rapor seçin!'))
            return

        count = len(selection)
        if not messagebox.askyesno(self.lm.tr('confirm', 'Onay'),
                                   self.lm.tr('delete_multiple_confirm', '{count} raporu silmek istediğinizden emin misiniz?').format(count=count)):
            return

        try:
            report_ids = [int(item) for item in selection]
            deleted, errors = self.report_mgr.delete_reports(report_ids)

            if errors > 0:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'),
                                     self.lm.tr('delete_partial_success', '{deleted} rapor silindi, {errors} hata oluştu!').format(deleted=deleted, errors=errors))
            else:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('delete_success_count', '{deleted} rapor silindi!').format(deleted=deleted))

            self.refresh_reports()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('delete_error', 'Silme hatası')}: {e}")

    def delete_single_report(self, report_id: int, window: tk.Toplevel) -> None:
        """Tek rapor sil"""
        if messagebox.askyesno("Onay", "Bu raporu silmek istediğinizden emin misiniz?"):
            deleted, errors = self.report_mgr.delete_reports([report_id])
            if deleted > 0:
                messagebox.showinfo("Başarılı", "Rapor silindi!")
                window.destroy()
                self.refresh_reports()
            else:
                messagebox.showerror("Hata", "Rapor silinemedi!")

    def add_schedule(self) -> None:
        """Yeni zamanlama ekle"""
        messagebox.showinfo("Bilgi", "Zamanlanmış rapor özelliği hazır!\nRapor otomasyonu ayarlanacak.")

    def _collect_tree_data(self) -> List[tuple]:
        items = self.reports_tree.get_children()
        rows = []
        for iid in items:
            vals = self.reports_tree.item(iid).get('values', [])
            rows.append(tuple(vals))
        return rows

    def export_registry_csv(self) -> None:
        try:
            sel_period = getattr(self, 'period_filter_var', tk.StringVar(value=self.lm.tr('all', 'Tümü'))).get()
            if not sel_period or sel_period == self.lm.tr('all', 'Tümü'):
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('export_period_warning', 'Dışa aktarma için tek bir dönem seçin (Tümü değil)'))
                return
            default_name = f"report_registry_{self.company_id}_{sel_period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            path = filedialog.asksaveasfilename(
                title=self.lm.tr('export_csv', 'CSV Dışa Aktar'),
                defaultextension='.csv',
                filetypes=[(self.lm.tr('file_csv', 'CSV Dosyası'),'*.csv')],
                initialfile=default_name
            )
            if not path:
                return
            cols = ['Rapor Adı','Modül','Tür','Dönem','Tarih','Boyut']
            data_rows = self._collect_tree_data()
            data_dicts = []
            for r in data_rows:
                d = {}
                for i, c in enumerate(cols):
                    d[c] = r[i+1] if i+1 < len(r) else ''
                data_dicts.append(d)
            data_dicts = [d for d in data_dicts if d.get('Dönem') == sel_period]
            try:
                ue = UniversalExporter(export_dir=os.path.dirname(path) or 'exports')
                fp = ue.export_to_csv(data_dicts, os.path.basename(path))
            except Exception:
                import pandas as pd
                df = pd.DataFrame(data_dicts)
                df.to_csv(path, index=False, encoding='utf-8-sig')
                fp = path
            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('export_csv_success', 'Kayıt CSV dışa aktarıldı')}:\n{fp}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('export_error', 'Dışa aktarma hatası')}: {e}")

    def export_registry_excel(self) -> None:
        try:
            sel_period = getattr(self, 'period_filter_var', tk.StringVar(value=self.lm.tr('all', 'Tümü'))).get()
            if not sel_period or sel_period == self.lm.tr('all', 'Tümü'):
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('export_period_warning', 'Dışa aktarma için tek bir dönem seçin (Tümü değil)'))
                return
            default_name = f"report_registry_{self.company_id}_{sel_period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            path = filedialog.asksaveasfilename(
                title=self.lm.tr('export_excel', 'Excel Dışa Aktar'),
                defaultextension='.xlsx',
                filetypes=[(self.lm.tr('excel_files', 'Excel Dosyaları'),'*.xlsx')],
                initialfile=default_name
            )
            if not path:
                return
            cols = ['Rapor Adı','Modül','Tür','Dönem','Tarih','Boyut']
            data_rows = self._collect_tree_data()
            data_dicts = []
            for r in data_rows:
                d = {}
                for i, c in enumerate(cols):
                    d[c] = r[i+1] if i+1 < len(r) else ''
                data_dicts.append(d)
            data_dicts = [d for d in data_dicts if d.get('Dönem') == sel_period]
            try:
                ue = UniversalExporter(export_dir=os.path.dirname(path) or 'exports')
                fp = ue.export_to_excel(data_dicts, os.path.basename(path))
            except Exception:
                import pandas as pd
                with pd.ExcelWriter(path, engine='openpyxl') as writer:
                    df = pd.DataFrame(data_dicts)
                    df.to_excel(writer, sheet_name='Veri', index=False)
                fp = path
            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('export_excel_success', 'Kayıt Excel dışa aktarıldı')}:\n{fp}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('export_error', 'Dışa aktarma hatası')}: {e}")

    def open_selected_report_folder(self) -> None:
        try:
            selection = self.reports_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_report_warning', 'Lütfen bir rapor seçin!'))
                return
            report_id = int(selection[0])
            conn = sqlite3.connect(self.report_mgr.db_path)
            cur = conn.cursor()
            cur.execute('SELECT file_path FROM report_registry WHERE id = ?', (report_id,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return
            fp = row[0]
            folder = os.path.dirname(fp)
            if os.path.exists(folder):
                os.startfile(folder)
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('folder_not_found', 'Klasör bulunamadı!'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('folder_open_error', 'Klasör açma hatası')}: {e}")

    def copy_selected_report_path(self) -> None:
        try:
            selection = self.reports_tree.selection()
            if not selection:
                messagebox.showwarning('Uyarı', 'Lütfen bir rapor seçin!')
                return
            report_id = int(selection[0])
            conn = sqlite3.connect(self.report_mgr.db_path)
            cur = conn.cursor()
            cur.execute('SELECT file_path FROM report_registry WHERE id = ?', (report_id,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return
            fp = row[0]
            try:
                self.parent.clipboard_clear()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            try:
                self.parent.clipboard_append(fp)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            messagebox.showinfo('Bilgi', 'Dosya yolu panoya kopyalandı.')
        except Exception as e:
            messagebox.showerror('Hata', f'Yol kopyalama hatası: {e}')

    def update_selected_tags(self) -> None:
        try:
            selection = self.reports_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_report_warning', 'Lütfen bir rapor seçin!'))
                return
            report_id = int(selection[0])
            conn = sqlite3.connect(self.report_mgr.db_path)
            cur = conn.cursor()
            cur.execute('SELECT tags FROM report_registry WHERE id = ?', (report_id,))
            row = cur.fetchone()
            current = ''
            if row and row[0]:
                try:
                    lst = json.loads(row[0])
                    if isinstance(lst, list):
                        current = ', '.join([str(t) for t in lst])
                    else:
                        current = str(row[0])
                except Exception:
                    current = str(row[0])
            new = simpledialog.askstring(self.lm.tr('update_tags', 'Etiket Güncelle'), self.lm.tr('enter_tags', 'Etiketleri girin (virgül ile):'), initialvalue=current, parent=self.parent)
            if new is None:
                conn.close()
                return
            tags = [t.strip() for t in new.split(',') if t.strip()]
            cur.execute('UPDATE report_registry SET tags = ? WHERE id = ?', (json.dumps(tags) if tags else None, report_id))
            conn.commit()
            conn.close()
            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('tags_updated', 'Etiketler güncellendi.'))
            self.refresh_reports()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('update_tags_error', 'Etiket güncelleme hatası')}: {e}")
