import logging
"""
ISSB (International Sustainability Standards Board) GUI
IFRS S1 ve S2 standartları için kullanıcı arayüzü
"""
import json
import os
import sqlite3
import tkinter as tk
import urllib.request
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List

import pandas as pd

from modules.data_import.import_templates import ImportTemplateManager
from modules.esrs.esrs_gui import ESRSGUI
from modules.tcfd.tcfd_manager import TCFDManager
from modules.ungc.ungc_cop_generator import UNGCCOPGenerator
from utils.language_manager import LanguageManager
from utils.tooltip import TOOLTIP_TEXTS, add_rich_tooltip, add_tooltip, bind_treeview_header_tooltips

from .issb_manager import ISSBManager
from .issb_report_generator import ISSBReportGenerator
from config.database import DB_PATH


class ISSBGUI:
    """ISSB Standartları GUI Sınıfı"""

    def __init__(self, parent, company_id):
        self.parent = parent
        self.company_id = company_id
        try:
            from config.settings import get_db_path
            self.db_path = get_db_path()
        except Exception:
            self.db_path = DB_PATH
        self.lm = LanguageManager()
        self.manager = ISSBManager(self.db_path)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """UI'yi oluştur"""
        # Ana çerçeve
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(title_frame, text=f"ISSB - {self.lm.tr('issb_full_title', 'International Sustainability Standards Board')}",
                              font=('Segoe UI', 18, 'bold'), bg='white', fg='#1e40af')
        title_label.pack(side='left')

        # Alt başlık
        subtitle_label = tk.Label(title_frame, text=self.lm.tr('issb_subtitle', "IFRS S1 & S2 Standartları"),
                                 font=('Segoe UI', 12), bg='white', fg='#6b7280')
        subtitle_label.pack(side='left', padx=(10, 0))

        actions_frame = tk.Frame(title_frame, bg='white')
        actions_frame.pack(side='right')
        ttk.Button(actions_frame, text=self.lm.tr('btn_report_center', "Rapor Merkezi"), style='Primary.TButton',
                   command=self.open_report_center_issb).pack(side='right')

        # Durum kartları
        self.create_status_cards(main_frame)

        # Tab kontrolü
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(20, 0))

        # IFRS S1 Tab
        s1_frame = tk.Frame(notebook, bg='white')
        notebook.add(s1_frame, text=self.lm.tr('ifrs_s1_tab', "IFRS S1 - Genel Gereksinimler"))
        self.create_s1_tab(s1_frame)

        # IFRS S2 Tab
        s2_frame = tk.Frame(notebook, bg='white')
        notebook.add(s2_frame, text=self.lm.tr('ifrs_s2_tab', "IFRS S2 - İklim Açıklamaları"))
        self.create_s2_tab(s2_frame)

        # Raporlama Tab
        report_frame = tk.Frame(notebook, bg='white')
        notebook.add(report_frame, text=self.lm.tr('reporting', "Raporlama"))
        self.create_report_tab(report_frame)

        # Aksiyon Planı Tab
        action_frame = tk.Frame(notebook, bg='white')
        notebook.add(action_frame, text=self.lm.tr('action_plan', "Aksiyon Planı"))
        self.create_action_plan_tab(action_frame)

    def open_report_center_issb(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('issb')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for issb: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('err_open_report_center', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def create_status_cards(self, parent):
        """Durum kartlarını oluştur"""
        cards_frame = tk.Frame(parent, bg='white')
        cards_frame.pack(fill='x', pady=(0, 20))

        # IFRS S1 Kartı
        s1_card = tk.Frame(cards_frame, bg='#3b82f6', relief='raised', bd=2)
        s1_card.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(s1_card, text="IFRS S1", font=('Segoe UI', 14, 'bold'),
                bg='#3b82f6', fg='white').pack(pady=(10, 5))
        self.s1_compliance_label = tk.Label(s1_card, text="0%", font=('Segoe UI', 24, 'bold'),
                                          bg='#3b82f6', fg='white')
        self.s1_compliance_label.pack()
        tk.Label(s1_card, text=self.lm.tr('general_requirements', "Genel Gereksinimler"), font=('Segoe UI', 10),
                bg='#3b82f6', fg='white').pack(pady=(0, 10))

        # IFRS S2 Kartı
        s2_card = tk.Frame(cards_frame, bg='#10b981', relief='raised', bd=2)
        s2_card.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(s2_card, text="IFRS S2", font=('Segoe UI', 14, 'bold'),
                bg='#10b981', fg='white').pack(pady=(10, 5))
        self.s2_compliance_label = tk.Label(s2_card, text="0%", font=('Segoe UI', 24, 'bold'),
                                          bg='#10b981', fg='white')
        self.s2_compliance_label.pack()
        tk.Label(s2_card, text=self.lm.tr('climate_disclosures', "İklim Açıklamaları"), font=('Segoe UI', 10),
                bg='#10b981', fg='white').pack(pady=(0, 10))

        # Genel Uyumluluk Kartı
        overall_card = tk.Frame(cards_frame, bg='#f59e0b', relief='raised', bd=2)
        overall_card.pack(side='left', fill='x', expand=True)

        tk.Label(overall_card, text=self.lm.tr('overall_compliance', "Genel Uyumluluk"), font=('Segoe UI', 14, 'bold'),
                bg='#f59e0b', fg='white').pack(pady=(10, 5))
        self.overall_compliance_label = tk.Label(overall_card, text="0%", font=('Segoe UI', 24, 'bold'),
                                               bg='#f59e0b', fg='white')
        self.overall_compliance_label.pack()
        tk.Label(overall_card, text=self.lm.tr('issb_readiness', "ISSB Hazırlık"), font=('Segoe UI', 10),
                bg='#f59e0b', fg='white').pack(pady=(0, 10))

    def create_s1_tab(self, parent):
        """IFRS S1 tab'ını oluştur"""
        # Filtreler
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(filter_frame, text=self.lm.tr('category_label', "Kategori:"), bg='white').pack(side='left', padx=(0, 5))
        self.s1_category_var = tk.StringVar(value=self.lm.tr('all', "Tümü"))
        s1_category_combo = ttk.Combobox(filter_frame, textvariable=self.s1_category_var,
                                        values=[self.lm.tr('all', "Tümü"), self.lm.tr('general', "Genel"), self.lm.tr('risk', "Risk"), self.lm.tr('strategy', "Strateji")])
        s1_category_combo.pack(side='left', padx=(0, 20))
        try:
            add_rich_tooltip(
                s1_category_combo,
                title=self.lm.tr('s1_category_title', "IFRS S1 Kategori"),
                text=self.lm.tr('s1_category_tooltip', "IFRS S1 gereksinimlerini üst kategoriye göre filtreler. Kategori seçimi, raporun bölüm bazlı düzenlenmesini ve boşluk analizi odaklanmasını kolaylaştırır."),
                example=self.lm.tr('s1_category_example', "Genel: yönetişim/temel ilkeler; Risk: risk tanımı ve süreçler; Strateji: iş modeli, kaynak tahsisi, hedefler")
            )
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        tk.Label(filter_frame, text=self.lm.tr('status_label', "Durum:"), bg='white').pack(side='left', padx=(0, 5))
        self.s1_status_var = tk.StringVar(value=self.lm.tr('all', "Tümü"))
        s1_status_combo = ttk.Combobox(filter_frame, textvariable=self.s1_status_var,
                                      values=[self.lm.tr('all', "Tümü"), "Not Started", "In Progress", "Completed"])
        s1_status_combo.pack(side='left', padx=(0, 20))
        try:
            add_rich_tooltip(
                s1_status_combo,
                title=self.lm.tr('progress_status_title', "İlerleme Durumu"),
                text=self.lm.tr('progress_status_tooltip', "Gereksinimlerin ilerleme durumuna göre filtreleme. Durum takibi, denetime hazırlık ve aksiyon planı önceliklendirmesi için kullanılır."),
                example=self.lm.tr('progress_status_example', "Not Started: henüz başlanmadı; In Progress: devam ediyor; Completed: tamamlandı")
            )
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        ttk.Button(filter_frame, text=self.lm.tr('filter', "Filtrele"), style='Primary.TButton', command=self.filter_s1_data).pack(side='left', padx=10)

        # S1 Tablosu
        # Use localized headers but keep internal IDs if possible, or mapping
        # Here we use a separate list for IDs and a mapping for headers to ensure consistency
        self.s1_cols = ['code', 'title', 'category', 'subcategory', 'status', 'last_update']
        self.s1_tree = ttk.Treeview(parent, columns=self.s1_cols, show='headings', height=15)

        headers = {
            'code': self.lm.tr('code', 'Kod'),
            'title': self.lm.tr('title', 'Başlık'),
            'category': self.lm.tr('category', 'Kategori'),
            'subcategory': self.lm.tr('subcategory', 'Alt Kategori'),
            'status': self.lm.tr('status', 'Durum'),
            'last_update': self.lm.tr('last_update', 'Son Güncelleme')
        }

        for col in self.s1_cols:
            self.s1_tree.heading(col, text=headers.get(col, col))
            self.s1_tree.column(col, width=120)

        self.s1_header_tips = {
            'code': self.lm.tr('tip_code', 'IFRS S1 gereksinim kodu; tekil tanımlayıcıdır ve izlenebilirlik için kullanılır.'),
            'title': self.lm.tr('tip_title', 'Kısa başlık; rapor bölümlerinde ve aksiyon planında referans olarak görünür.'),
            'category': self.lm.tr('tip_category', 'Üst kategori; Genel, Risk, Strateji gibi gruplamayı belirtir.'),
            'subcategory': self.lm.tr('tip_subcategory', 'Alt kırılım; politika, süreç, hedef vb. ayrımı sağlar.'),
            'status': self.lm.tr('tip_status', 'İlerleme: Not Started, In Progress, Completed. Denetim hazırlığı için kritiktir.'),
            'last_update': self.lm.tr('tip_last_update', 'Son düzenleme tarihi/saat bilgisi; kayıt güncelliğini gösterir.')
        }
        try:
            bind_treeview_header_tooltips(self.s1_tree, self.s1_header_tips)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Scrollbar
        s1_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.s1_tree.yview)
        self.s1_tree.configure(yscrollcommand=s1_scrollbar.set)

        self.s1_tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=(0, 20))
        s1_scrollbar.pack(side='right', fill='y', pady=(0, 20))

        # S1 İşlemleri
        s1_actions = tk.Frame(parent, bg='white')
        s1_actions.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Button(s1_actions, text=self.lm.tr('update_status', "Durum Güncelle"), style='Primary.TButton', command=self.update_s1_status).pack(side='left', padx=5)
        ttk.Button(s1_actions, text=self.lm.tr('view_detail', "Detay Görüntüle"), style='Primary.TButton', command=self.show_s1_detail).pack(side='left', padx=5)
        ttk.Button(s1_actions, text=self.lm.tr('refresh', "Yenile"), command=self.load_s1_data).pack(side='left', padx=5)

    def create_s2_tab(self, parent):
        """IFRS S2 tab'ını oluştur"""
        # Filtreler
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(filter_frame, text=self.lm.tr('category_label', "Kategori:"), bg='white').pack(side='left', padx=(0, 5))
        self.s2_category_var = tk.StringVar(value=self.lm.tr('all', "Tümü"))
        s2_category_combo = ttk.Combobox(filter_frame, textvariable=self.s2_category_var,
                                        values=[self.lm.tr('all', "Tümü"), self.lm.tr('management', "Yönetim"), self.lm.tr('risk', "Risk"), self.lm.tr('metric', "Metrik"), self.lm.tr('target', "Hedef")])
        s2_category_combo.pack(side='left', padx=(0, 20))
        try:
            add_rich_tooltip(
                s2_category_combo,
                title=self.lm.tr('s2_category_title', "IFRS S2 Kategori"),
                text=self.lm.tr('s2_category_tooltip', "İklimle ilgili açıklamaları kategoriye göre filtreler. Yönetim, Risk, Metrik, Hedef ayrımı iklim raporlamasının ana yapı taşlarını temsil eder."),
                example=self.lm.tr('s2_category_example', "Yönetim: roller/sorumluluklar; Risk: iklim risk süreçleri; Metrik: ölçümler (örn. emisyon); Hedef: net sıfır vb.")
            )
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        tk.Label(filter_frame, text=self.lm.tr('status_label', "Durum:"), bg='white').pack(side='left', padx=(0, 5))
        self.s2_status_var = tk.StringVar(value=self.lm.tr('all', "Tümü"))
        s2_status_combo = ttk.Combobox(filter_frame, textvariable=self.s2_status_var,
                                      values=[self.lm.tr('all', "Tümü"), "Not Started", "In Progress", "Completed"])
        s2_status_combo.pack(side='left', padx=(0, 20))
        try:
            add_rich_tooltip(
                s2_status_combo,
                title=self.lm.tr('progress_status_title', "İlerleme Durumu"),
                text=self.lm.tr('progress_status_tooltip2', "Açıklamaların ilerleme durumuna göre filtreleme. Denetim ve yatırımcı iletişimi için şeffaflık sağlar."),
                example=self.lm.tr('progress_status_example2', "Not Started: başlangıç aşaması; In Progress: uygulama devam ediyor; Completed: yayımlanmış/dokümante")
            )
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        ttk.Button(filter_frame, text=self.lm.tr('filter', "Filtrele"), style='Primary.TButton', command=self.filter_s2_data).pack(side='left', padx=10)

        # S2 Tablosu
        self.s2_cols = ['code', 'title', 'category', 'subcategory', 'status', 'last_update']
        self.s2_tree = ttk.Treeview(parent, columns=self.s2_cols, show='headings', height=15)

        headers = {
            'code': self.lm.tr('code', 'Kod'),
            'title': self.lm.tr('title', 'Başlık'),
            'category': self.lm.tr('category', 'Kategori'),
            'subcategory': self.lm.tr('subcategory', 'Alt Kategori'),
            'status': self.lm.tr('status', 'Durum'),
            'last_update': self.lm.tr('last_update', 'Son Güncelleme')
        }

        for col in self.s2_cols:
            self.s2_tree.heading(col, text=headers.get(col, col))
            self.s2_tree.column(col, width=120)

        self.s2_header_tips = {
            'code': self.lm.tr('tip_code_s2', 'IFRS S2 açıklama kodu; iklimle ilgili gereksinimler için tekil tanımlayıcıdır.'),
            'title': self.lm.tr('tip_title_s2', 'Kısa açıklama başlığı; iklim beyanlarında referans olarak kullanılır.'),
            'category': self.lm.tr('tip_category_s2', 'Yönetim, Risk, Metrik, Hedef ana grubu; entegrasyon ve odak sağlar.'),
            'subcategory': self.lm.tr('tip_subcategory', 'Alt kırılım; metodoloji, kapsam, politika vb. ayrımı sağlar.'),
            'status': self.lm.tr('tip_status_s2', 'İlerleme: Not Started, In Progress, Completed. İzleme ve raporlama tutarlılığı için önemlidir.'),
            'last_update': self.lm.tr('tip_last_update', 'Son düzenleme zaman damgası; değişiklik izlenebilirliği sağlar.')
        }
        try:
            bind_treeview_header_tooltips(self.s2_tree, self.s2_header_tips)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Scrollbar
        s2_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.s2_tree.yview)
        self.s2_tree.configure(yscrollcommand=s2_scrollbar.set)

        self.s2_tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=(0, 20))
        s2_scrollbar.pack(side='right', fill='y', pady=(0, 20))

        # S2 İşlemleri
        s2_actions = tk.Frame(parent, bg='white')
        s2_actions.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Button(s2_actions, text=self.lm.tr('update_status', "Durum Güncelle"), style='Primary.TButton', command=self.update_s2_status).pack(side='left', padx=5)
        ttk.Button(s2_actions, text=self.lm.tr('view_detail', "Detay Görüntüle"), style='Primary.TButton', command=self.show_s2_detail).pack(side='left', padx=5)
        ttk.Button(s2_actions, text=self.lm.tr('refresh', "Yenile"), command=self.load_s2_data).pack(side='left', padx=5)
        ttk.Button(s2_actions, text=self.lm.tr('operational_data_entry', "Operasyonel Veri Girişi"), style='Primary.TButton', command=self.show_operational_import_window).pack(side='left', padx=5)

    def show_operational_import_window(self):
        win = tk.Toplevel(self.parent)
        win.title(self.lm.tr('operational_metrics', "Operasyonel Metrikler"))
        win.geometry("700x420")
        win.configure(bg='white')
        frame = tk.Frame(win, bg='white')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(frame, text=self.lm.tr('year', "Yıl"), bg='white').grid(row=0, column=0, sticky='w')
        year_var = tk.StringVar(value=str(datetime.now().year))
        tk.Entry(frame, textvariable=year_var, width=12).grid(row=0, column=1, padx=8, pady=6, sticky='w')
        tk.Label(frame, text=self.lm.tr('data_url', "Veri URL (JSON)"), bg='white').grid(row=1, column=0, sticky='w')
        url_var = tk.StringVar()
        tk.Entry(frame, textvariable=url_var, width=48).grid(row=1, column=1, padx=8, pady=6, sticky='w')
        btns = tk.Frame(frame, bg='white')
        btns.grid(row=2, column=0, columnspan=2, pady=10, sticky='w')
        def _create_template():
            path = filedialog.asksaveasfilename(
                title=self.lm.tr('save_template', "Şablon Kaydet"),
                defaultextension='.xlsx',
                filetypes=[(self.lm.tr('excel_files', 'Excel Dosyaları'),'*.xlsx')]
            )
            if not path:
                return
            ok = ImportTemplateManager.create_template_file('operational_common', path, format='excel')
            if ok:
                messagebox.showinfo(self.lm.tr('info', "Bilgi"), f"{self.lm.tr('template_created', 'Şablon oluşturuldu')}: {path}")
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('template_create_error', "Şablon oluşturulamadı"))
        def _apply_data(d, year):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
            mgr = TCFDManager(db_path)
            data = {}
            for k in ['scope1_emissions','scope2_emissions','scope3_emissions','total_energy_consumption','renewable_energy_pct','internal_carbon_price']:
                if k in d and d.get(k) not in (None, ''):
                    try:
                        data[k] = float(d.get(k))
                    except Exception:
                        data[k] = d.get(k)
            other = {}
            if 'current_energy_price' in d:
                other['current_energy_price'] = d.get('current_energy_price')
            if other:
                try:
                    data['other_metrics'] = json.dumps(other)
                except Exception:
                    data['other_metrics'] = None
            ok, msg = mgr.save_metrics(self.company_id, int(year), data)
            if ok:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), msg)
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), msg)
        def _import_file():
            fp = filedialog.askopenfilename(
                title=self.lm.tr('select_data_file', "Veri Dosyası Seç"),
                filetypes=[(self.lm.tr('data_files', 'Veri Dosyaları'),'*.xlsx;*.csv;*.json')]
            )
            if not fp:
                return
            y = year_var.get() or str(datetime.now().year)
            try:
                if fp.lower().endswith('.json'):
                    with open(fp, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                elif fp.lower().endswith('.csv'):
                    df = pd.read_csv(fp)
                    d = {c: df.iloc[0][c] for c in df.columns}
                else:
                    df = pd.read_excel(fp)
                    d = {c: df.iloc[0][c] for c in df.columns}
                _apply_data(d, y)
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('import_error', 'İçe aktarma hatası')}: {e}")
        def _fetch_url():
            u = url_var.get().strip()
            if not u:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('enter_url', "URL girin"))
                return
            y = year_var.get() or str(datetime.now().year)
            try:
                with urllib.request.urlopen(u, timeout=10) as resp:
                    data_bytes = resp.read()
                import json as _json
                d = _json.loads(data_bytes.decode('utf-8'))
                _apply_data(d, y)
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('url_fetch_error', 'URL’den veri alınamadı')}: {e}")
        ttk.Button(btns, text=self.lm.tr('create_template_xlsx', "Şablon Oluştur (XLSX)"), style='Primary.TButton', command=_create_template).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('import_data', "İçe Aktar"), style='Primary.TButton', command=_import_file).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('fetch_from_url', "URL’den Getir"), style='Primary.TButton', command=_fetch_url).pack(side='left', padx=5)

    def create_report_tab(self, parent):
        """Raporlama tab'ını oluştur"""
        # Rapor oluşturma
        report_frame = tk.LabelFrame(parent, text=self.lm.tr('create_issb_report', "ISSB Raporu Oluştur"),
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        report_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(report_frame, text=self.lm.tr('report_period', "Raporlama Dönemi:"), bg='white').grid(row=0, column=0,
                                                                         sticky='w', padx=10, pady=10)
        self.report_period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
        period_entry = tk.Entry(report_frame, textvariable=self.report_period_var, width=20)
        period_entry.grid(row=0, column=1, padx=10, pady=10)
        try:
            add_tooltip(period_entry, TOOLTIP_TEXTS.get('report_period', self.lm.tr('tooltip_report_period', 'Raporlama dönemi (yıl veya çeyrek)')))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        gen_btn = ttk.Button(report_frame, text=self.lm.tr('generate_report', "Rapor Oluştur"), style='Primary.TButton', command=self.generate_report)
        gen_btn.grid(row=0, column=2, padx=10, pady=10)
        docx_btn = ttk.Button(report_frame, text=self.lm.tr('export_docx', "DOCX’e Aktar"), style='Primary.TButton', command=self.export_docx_report)
        docx_btn.grid(row=0, column=3, padx=10, pady=10)
        xlsx_btn = ttk.Button(report_frame, text=self.lm.tr('excel_action_plan', "Excel Aksiyon Planı"), style='Primary.TButton', command=self.export_excel_action_plan)
        xlsx_btn.grid(row=0, column=4, padx=10, pady=10)
        pdf_btn = ttk.Button(report_frame, text=self.lm.tr('pdf_action_plan', "PDF Aksiyon Planı"), style='Primary.TButton', command=self.export_pdf_action_plan)
        pdf_btn.grid(row=0, column=5, padx=10, pady=10)
        try:
            add_tooltip(gen_btn, self.lm.tr('tooltip_generate_report', 'ISSB rapor özetini oluşturur'))
            add_tooltip(docx_btn, self.lm.tr('tooltip_export_docx', 'Aksiyon Planı ekli DOCX rapor üretir'))
            add_tooltip(xlsx_btn, self.lm.tr('tooltip_export_excel', 'ISSB Gap Aksiyon Planını Excel’e aktarır'))
            add_tooltip(pdf_btn, self.lm.tr('tooltip_export_pdf', 'ISSB Gap Aksiyon Planını PDF’e aktarır'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        shortcut_frame = tk.LabelFrame(parent, text=self.lm.tr('shortcuts', "Kısayollar"), font=('Segoe UI', 12, 'bold'), bg='white')
        shortcut_frame.pack(fill='x', padx=20, pady=10)
        tk.Button(shortcut_frame, text=self.lm.tr('ungc_cop_pdf', "UNGC COP (PDF)"), command=self._open_cop_generator, bg='#1e3a8a', fg='white').pack(side='left', padx=8, pady=8)
        tk.Button(shortcut_frame, text=self.lm.tr('esrs_form', "ESRS Formu"), command=self._open_esrs_form, bg='#0ea5e9', fg='white').pack(side='left', padx=8, pady=8)
        try:
            add_tooltip(shortcut_frame, self.lm.tr('tooltip_shortcuts', 'UNGC COP ve ESRS formları için hızlı erişim'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        preview_open_frame = tk.Frame(parent, bg='white')
        preview_open_frame.pack(fill='x', padx=20, pady=(0, 20))
        tk.Button(preview_open_frame, text=self.lm.tr('preview_and_outputs', "Önizleme ve Çıkışlar"), command=self.open_preview_window, bg='#0ea5e9', fg='white').pack(side='left')

    def _save_preview_text(self):
        try:
            content = self.report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('preview_empty', 'Önizleme içeriği boş'))
                return
            fp = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.txt',
                filetypes=[(self.lm.tr('text_file', 'Metin'),'*.txt')],
                initialfile=f"issb_report_{self.company_id}_{self.report_period_var.get()}.txt"
            )
            if not fp:
                return
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            self._last_saved_report_text_path = fp
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('report_text_saved', 'Rapor metni kaydedildi')}: {fp}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def _export_preview_docx(self):
        try:
            period = self.report_period_var.get().strip()
            year = self._validate_year(period)
            if year is None:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('enter_valid_year', 'Geçerli bir yıl girin (örn. 2025)'))
                return
            from modules.issb.issb_report_generator import ISSBReportGenerator
            gen = ISSBReportGenerator()
            report = self.manager.generate_issb_report(self.company_id, str(year))
            fp = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.docx',
                filetypes=[(self.lm.tr('word_files', 'Word Dosyaları'),'*.docx')],
                initialfile=f"issb_report_{self.company_id}_{year}.docx"
            )
            if not fp:
                return
            ok = gen.generate_docx_report(fp, report, self.company_id, int(year))
            if ok:
                self.last_issb_report_path = fp
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('docx_created', 'DOCX raporu oluşturuldu')}: {fp}")
            else:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('docx_failed', 'DOCX oluşturulamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('docx_error', 'DOCX oluşturma hatası')}: {e}")

    def _print_preview_text(self):
        try:
            import os
            import tempfile
            content = self.report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('preview_empty', 'Önizleme içeriği boş'))
                return
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"issb_preview_{self.company_id}_{self.report_period_var.get()}.txt")
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp_path, 'print')
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('print_started', 'Yazdırma başlatıldı'))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_error', 'Yazdırma hatası')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_prep_error', 'Yazdırmaya hazırlık hatası')}: {e}")

    def _copy_preview_to_clipboard(self):
        try:
            content = self.report_text.get('1.0', tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('preview_copied', 'Önizleme metni panoya kopyalandı'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _open_last_report(self):
        try:
            path = getattr(self, 'last_issb_report_path', None)
            if path and os.path.exists(path):
                os.startfile(path)
                return
            path_txt = getattr(self, '_last_saved_report_text_path', None)
            if path_txt and os.path.exists(path_txt):
                os.startfile(path_txt)
                return
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('report_not_found', 'Açılacak rapor bulunamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('open_error', 'Açma hatası')}: {e}")


    def _share_dialog(self):
        try:
            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('share', 'Paylaş'))
            dialog.geometry('360x180')
            dialog.grab_set()
            tk.Label(dialog, text=self.lm.tr('share_options', 'Paylaşım Seçenekleri'), font=('Segoe UI', 12, 'bold')).pack(pady=10)
            btns = tk.Frame(dialog)
            btns.pack(pady=10)
            def copy_path():
                path = getattr(self, 'last_issb_report_path', None) or getattr(self, '_last_saved_report_text_path', None)
                if path and os.path.exists(path):
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(path)
                    messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('path_copied', 'Dosya yolu panoya kopyalandı'))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('file_not_found', 'Paylaşılacak dosya bulunamadı'))
            def open_folder():
                path = getattr(self, 'last_issb_report_path', None) or getattr(self, '_last_saved_report_text_path', None)
                if path and os.path.exists(path):
                    os.startfile(os.path.dirname(path))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('folder_open_error', 'Klasör açılamadı'))
            def copy_text():
                content = self.report_text.get('1.0', tk.END)
                self.parent.clipboard_clear()
                self.parent.clipboard_append(content)
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('preview_copied', 'Önizleme metni panoya kopyalandı'))
            tk.Button(btns, text=self.lm.tr('copy_path', 'Dosya Yolunu Kopyala'), command=copy_path, bg='#0ea5e9', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr('open_folder', 'Klasörü Aç'), command=open_folder, bg='#2563eb', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr('copy_preview_text', 'Önizleme Metnini Kopyala'), command=copy_text, bg='#6b7280', fg='white').pack(side='left', padx=6)
            tk.Button(dialog, text=self.lm.tr('btn_close', 'Kapat'), command=dialog.destroy).pack(pady=8)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('share_error', 'Paylaşım hatası')}: {e}")

    def open_preview_window(self):
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('issb_preview_title', 'ISSB Önizleme ve Çıkışlar'))
            win.geometry('900x600')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            ttk.Button(top, text=self.lm.tr('btn_back', 'Geri'), command=win.destroy, style='Primary.TButton').pack(side='left')
            status_frame = tk.Frame(win, bg='white')
            status_frame.pack(fill='x', padx=10, pady=6)
            self.plan_status_label = tk.Label(status_frame, text=self.lm.tr('action_plan_status_missing', 'Aksiyon Planı Durumu: (Excel bulunamadı)'), bg='white')
            self.plan_status_label.pack(side='left')
            ttk.Button(status_frame, text=self.lm.tr('update_status', 'Durumu Güncelle'), command=self.refresh_action_plan_status, style='Primary.TButton').pack(side='left', padx=8)
            self.report_text = tk.Text(win, height=20, wrap='word')
            report_scrollbar = ttk.Scrollbar(win, orient='vertical', command=self.report_text.yview)
            self.report_text.configure(yscrollcommand=report_scrollbar.set)
            self.report_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            report_scrollbar.pack(side='right', fill='y', pady=10)
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', padx=10, pady=(0,10))
            ttk.Button(tools, text=self.lm.tr('save_txt', 'Kaydet (.txt)'), command=self._save_preview_text, style='Primary.TButton').pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('save_as_docx', 'Farklı Kaydet (DOCX)'), command=self._export_preview_docx, style='Primary.TButton').pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('print', 'Yazdır'), command=self._print_preview_text, style='Primary.TButton').pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('copy_to_clipboard', 'Panoya Kopyala'), command=self._copy_preview_to_clipboard, style='Primary.TButton').pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('open', 'Aç'), command=self._open_last_report, style='Primary.TButton').pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('share', 'Paylaş'), command=self._share_dialog, style='Primary.TButton').pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('preview_window_error', 'Önizleme penceresi hatası')}: {e}")

    def _open_cop_generator(self):
        try:
            period = self.report_period_var.get().strip() if hasattr(self, 'report_period_var') else datetime.now().strftime('%Y')
            generator = UNGCCOPGenerator(self.db_path)
            out = filedialog.asksaveasfilename(
                title=self.lm.tr('save_pdf', 'PDF Kaydet'),
                defaultextension='.pdf',
                filetypes=[(self.lm.tr('pdf_files', 'PDF Dosyaları'),'*.pdf')]
            )
            if not out:
                return
            generator.manager.create_tables()
            fp = generator.generate_report(self.company_id, period, ceo_statement="")
            try:
                if fp and os.path.exists(fp):
                    import shutil
                    shutil.copyfile(fp, out)
                    messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('cop_pdf_created', 'COP PDF oluşturuldu')}: {out}")
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('cop_pdf_failed', 'COP PDF oluşturulamadı'))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _open_esrs_form(self):
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('esrs_form_title', 'ESRS Formu'))
            ESRSGUI(win, company_id=self.company_id, db_path=self.db_path)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _validate_year(self, y: str):
        try:
            y = (y or "").strip()
            if not (y.isdigit() and len(y) == 4):
                return None
            val = int(y)
            if 1990 <= val <= 2100:
                return val
            return None
        except Exception:
            return None

    def _validate_metrics_schema(self, d: Dict) -> List[str]:
        try:
            errs = []
            allowed = {
                'scope1_emissions','scope2_emissions','scope3_emissions','total_emissions',
                'emissions_intensity','intensity_metric',
                'total_energy_consumption','renewable_energy_pct','energy_intensity',
                'water_consumption','water_intensity',
                'internal_carbon_price','carbon_price_coverage',
                'climate_related_revenue','climate_related_opex','climate_related_capex',
                'other_metrics','current_energy_price'
            }
            numeric_keys = {
                'scope1_emissions','scope2_emissions','scope3_emissions','total_emissions',
                'emissions_intensity',
                'total_energy_consumption','renewable_energy_pct','energy_intensity',
                'water_consumption','water_intensity',
                'internal_carbon_price','carbon_price_coverage',
                'climate_related_revenue','climate_related_opex','climate_related_capex'
            }
            for k in d.keys():
                if k not in allowed:
                    errs.append(f"Desteklenmeyen alan: {k}")
            for k in numeric_keys:
                v = d.get(k)
                if v not in (None, ''):
                    try:
                        float(str(v))
                    except Exception:
                        errs.append(f"Sayısal olmayan değer: {k} = {v}")
            return errs
        except Exception as e:
            return [f"Şema doğrulama hatası: {e}"]

    def refresh_action_plan_status(self):
        try:
            from modules.issb.issb_report_generator import ISSBReportGenerator
            gen = ISSBReportGenerator()
            period = self.report_period_var.get()
            year = self._validate_year(period)
            if year is None:
                self.plan_status_label.config(text=self.lm.tr('ap_status_enter_year', "Aksiyon Planı Durumu: Geçerli yıl girin"))
                return
            summary = gen.get_action_plan_status_summary(self.company_id, int(year))
            txt = self.lm.tr('ap_status_summary', "Aksiyon Planı Durumu: Tamamlanan {tamamlanan} | Devam {devam} | Beklemede {beklemede} | Son Tarihi Geçmiş {son_tarih_gecmis}").format(**summary)
            self.plan_status_label.config(text=txt)
        except Exception as e:
            self.plan_status_label.config(text=f"{self.lm.tr('ap_status_error', 'Aksiyon Planı Durumu: Hata')} ({e})")

    def create_action_plan_tab(self, parent):
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(filter_frame, text=self.lm.tr('year_label', "Yıl:"), bg='white').pack(side='left')
        self.action_year_var = tk.StringVar(value=self.report_period_var.get())
        tk.Entry(filter_frame, textvariable=self.action_year_var, width=8).pack(side='left', padx=6)
        tk.Label(filter_frame, text=self.lm.tr('status_label', "Durum:"), bg='white').pack(side='left', padx=(10,0))
        self.action_status_var = tk.StringVar(value="")
        self.action_status_combo = ttk.Combobox(filter_frame, textvariable=self.action_status_var, values=["", "Beklemede", "Devam", "Tamamlandı"], width=16)
        self.action_status_combo.pack(side='left')
        try:
            add_tooltip(self.action_status_combo, self.lm.tr('status_filter_tooltip', 'Duruma göre filtreleyin: Beklemede/Devam/Tamamlandı'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        tk.Label(filter_frame, text=self.lm.tr('department_label', "Departman:"), bg='white').pack(side='left', padx=(10,0))
        self.action_department_var = tk.StringVar(value="")
        self.action_dept_combo = ttk.Combobox(filter_frame, textvariable=self.action_department_var, values=[""], width=18)
        self.action_dept_combo.pack(side='left')
        try:
            add_tooltip(self.action_dept_combo, self.lm.tr('department_filter_tooltip', 'Departmana göre filtreleyin'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        tk.Label(filter_frame, text=self.lm.tr('responsible_label', "Sorumlu:"), bg='white').pack(side='left', padx=(10,0))
        self.action_responsible_var = tk.StringVar(value="")
        self.action_resp_combo = ttk.Combobox(filter_frame, textvariable=self.action_responsible_var, values=[""], width=18)
        self.action_resp_combo.pack(side='left')
        try:
            add_tooltip(self.action_resp_combo, self.lm.tr('responsible_filter_tooltip', 'Sorumlu kişiye göre filtreleyin'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        ttk.Button(filter_frame, text=self.lm.tr('load', "Yükle"), command=self._load_action_plan).pack(side='left', padx=8)
        ttk.Button(filter_frame, text=self.lm.tr('export_excel', "Excel’e Aktar"), command=self._export_action_plan_excel).pack(side='left', padx=4)
        ttk.Button(filter_frame, text=self.lm.tr('import_excel', "Excel’den Al"), command=self._import_action_plan_excel).pack(side='left', padx=4)

        columns = ('gap_item', 'standard', 'module', 'department', 'responsible', 'action_step', 'due_date', 'status', 'dependencies')
        headers = {
            'gap_item': self.lm.tr('col_gap_item', 'Eksik Kalem'),
            'standard': self.lm.tr('col_standard', 'Standard'),
            'module': self.lm.tr('col_module', 'Sorumlu Modül'),
            'department': self.lm.tr('col_department', 'Departman'),
            'responsible': self.lm.tr('col_responsible', 'Sorumlu'),
            'action_step': self.lm.tr('col_action_step', 'Önerilen Adım'),
            'due_date': self.lm.tr('col_due_date', 'Hedef Tarih'),
            'status': self.lm.tr('col_status', 'Durum'),
            'dependencies': self.lm.tr('col_dependencies', 'Bağımlılıklar')
        }
        self.action_plan_tv = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        for col in columns:
            self.action_plan_tv.heading(col, text=headers.get(col, col))
            self.action_plan_tv.column(col, width=140)
        self.action_plan_tv.pack(side='left', fill='both', expand=True, padx=(20,0), pady=(0,20))
        ap_scroll = ttk.Scrollbar(parent, orient='vertical', command=self.action_plan_tv.yview)
        self.action_plan_tv.configure(yscrollcommand=ap_scroll.set)
        ap_scroll.pack(side='right', fill='y', pady=(0,20))
        self.action_item_ids = {}

        actions = tk.Frame(parent, bg='white')
        actions.pack(fill='x', padx=20, pady=(0, 20))
        tk.Button(actions, text=self.lm.tr('new', "Yeni"), command=self._add_action_item_dialog, bg='#10b981', fg='white').pack(side='left', padx=5)
        tk.Button(actions, text=self.lm.tr('btn_edit', "Düzenle"), command=self._edit_action_item_dialog, bg='#3b82f6', fg='white').pack(side='left', padx=5)
        tk.Button(actions, text=self.lm.tr('btn_delete', "Sil"), command=self._delete_action_item, bg='#ef4444', fg='white').pack(side='left', padx=5)

    def _load_action_plan(self):
        try:
            y = self.action_year_var.get().strip()
            year = self._validate_year(y)
            if year is None:
                return
            filters = {
                'status': self.action_status_var.get().strip(),
                'department': self.action_department_var.get().strip(),
                'responsible': self.action_responsible_var.get().strip(),
            }
            mgr = ISSBManager(self.db_path)
            items = mgr.list_action_items(self.company_id, int(year), filters)
            self.action_plan_tv.delete(*self.action_plan_tv.get_children())
            self.action_item_ids.clear()
            depts = set()
            resps = set()
            for it in items:
                iid = self.action_plan_tv.insert('', 'end', values=(
                    it.get('gap_item') or '', it.get('standard') or '', it.get('module') or '',
                    it.get('department') or '', it.get('responsible') or '', it.get('action_step') or '',
                    it.get('due_date') or '', it.get('status') or '', it.get('dependencies') or ''
                ))
                if it.get('id') is not None:
                    self.action_item_ids[iid] = it.get('id')
                if it.get('department'):
                    depts.add(it.get('department'))
                if it.get('responsible'):
                    resps.add(it.get('responsible'))
            self.action_dept_combo['values'] = [""] + sorted(list(depts))
            self.action_resp_combo['values'] = [""] + sorted(list(resps))
            self.action_department_var.set("")
            self.action_responsible_var.set("")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _export_action_plan_excel(self):
        try:
            y = self.action_year_var.get().strip()
            year = self._validate_year(y)
            if year is None:
                return
            generator = ISSBReportGenerator()
            fp = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.xlsx',
                initialfile=f"issb_action_plan_{self.company_id}_{int(year)}.xlsx",
                filetypes=[(self.lm.tr('excel_files', 'Excel Dosyaları'), '*.xlsx'), (self.lm.tr('all_files', 'Tüm Dosyalar'), '*.*')]
            )
            if not fp:
                return
            generator.export_excel_action_plan(fp, self.company_id, int(year))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _import_action_plan_excel(self):
        try:
            y = self.action_year_var.get().strip()
            year = self._validate_year(y)
            if year is None:
                return
            fp = filedialog.askopenfilename(
                title=self.lm.tr('select_excel_file', "Excel Dosyası Seç"),
                filetypes=[(self.lm.tr('excel_files', 'Excel Dosyaları'),'*.xlsx'), (self.lm.tr('all_files', 'Tüm Dosyalar'), '*.*')]
            )
            if not fp:
                return
            mgr = ISSBManager(self.db_path)
            mgr.import_action_plan_from_excel(fp, self.company_id, int(year))
            self._load_action_plan()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _add_action_item_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('new_action', "Yeni Aksiyon"))
        entries = {}
        # Text entries
        for label, key in [(self.lm.tr('col_gap_item', 'Eksik Kalem'),'gap_item'),
                           (self.lm.tr('col_standard', 'Standard'),'standard'),
                           (self.lm.tr('col_module', 'Sorumlu Modül'),'module'),
                           (self.lm.tr('col_action_step', 'Önerilen Adım'),'action_step'),
                           (self.lm.tr('col_dependencies', 'Bağımlılıklar'),'dependencies')]:
            row = tk.Frame(dialog)
            row.pack(fill='x', padx=10, pady=4)
            tk.Label(row, text=label, width=18, anchor='w').pack(side='left')
            e = tk.Entry(row)
            e.pack(side='left', fill='x', expand=True)
            entries[key] = e
        # Department combobox (dynamic from current list)
        r1 = tk.Frame(dialog)
        r1.pack(fill='x', padx=10, pady=4)
        tk.Label(r1, text=self.lm.tr('col_department', 'Departman'), width=18, anchor='w').pack(side='left')
        dept_cb = ttk.Combobox(r1, values=self.action_dept_combo['values'], width=20)
        dept_cb.pack(side='left', fill='x', expand=True)
        entries['department'] = dept_cb
        # Responsible combobox (dynamic)
        r2 = tk.Frame(dialog)
        r2.pack(fill='x', padx=10, pady=4)
        tk.Label(r2, text=self.lm.tr('col_responsible', 'Sorumlu'), width=18, anchor='w').pack(side='left')
        resp_cb = ttk.Combobox(r2, values=self.action_resp_combo['values'], width=20)
        resp_cb.pack(side='left', fill='x', expand=True)
        entries['responsible'] = resp_cb
        # Due date entry with ISO format hint
        r3 = tk.Frame(dialog)
        r3.pack(fill='x', padx=10, pady=4)
        tk.Label(r3, text=self.lm.tr('col_due_date', 'Hedef Tarih'), width=18, anchor='w').pack(side='left')
        due_e = tk.Entry(r3)
        due_e.insert(0, 'YYYY-MM-DD')
        due_e.pack(side='left', fill='x', expand=True)
        entries['due_date'] = due_e
        # Status combobox
        r4 = tk.Frame(dialog)
        r4.pack(fill='x', padx=10, pady=4)
        tk.Label(r4, text=self.lm.tr('col_status', 'Durum'), width=18, anchor='w').pack(side='left')
        status_cb = ttk.Combobox(r4, values=["Beklemede","Devam","Tamamlandı"], width=20)
        status_cb.pack(side='left', fill='x', expand=True)
        entries['status'] = status_cb
        def save():
            y = self.action_year_var.get().strip()
            if self._validate_year(y) is None:
                dialog.destroy()
                return
            data = {k: (v.get() if hasattr(v, 'get') else v.get()) for k, v in entries.items()}
            dv = data.get('due_date') or ''
            if dv:
                try:
                    from datetime import datetime
                    datetime.strptime(dv, '%Y-%m-%d')
                except Exception:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('invalid_date_format', 'Hedef Tarih formatı geçersiz. Örnek: 2025-12-31'))
                    return
            st = data.get('status')
            if st and st not in ['Beklemede','Devam','Tamamlandı']:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('invalid_status_value', 'Durum değeri geçersiz'))
                return
            mgr = ISSBManager(self.db_path)
            mgr.add_action_item(self.company_id, int(self._validate_year(y)), data)
            dialog.destroy()
            self._load_action_plan()
            try:
                self.refresh_action_plan_status()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        tk.Button(dialog, text=self.lm.tr('btn_save', "Kaydet"), command=save).pack(pady=8)

    def _edit_action_item_dialog(self):
        sel = self.action_plan_tv.selection()
        if not sel:
            return
        values = self.action_plan_tv.item(sel[0], 'values')
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('edit_action', "Aksiyon Düzenle"))
        entries = {}
        def add_entry(label, initial):
            r = tk.Frame(dialog)
            r.pack(fill='x', padx=10, pady=4)
            tk.Label(r, text=label, width=18, anchor='w').pack(side='left')
            e = tk.Entry(r)
            e.insert(0, initial)
            e.pack(side='left', fill='x', expand=True)
            return e
        entries['gap_item'] = add_entry(self.lm.tr('col_gap_item', 'Eksik Kalem'), values[0])
        entries['standard'] = add_entry(self.lm.tr('col_standard', 'Standard'), values[1])
        entries['module'] = add_entry(self.lm.tr('col_module', 'Sorumlu Modül'), values[2])
        r1 = tk.Frame(dialog)
        r1.pack(fill='x', padx=10, pady=4)
        tk.Label(r1, text=self.lm.tr('col_department', 'Departman'), width=18, anchor='w').pack(side='left')
        dept_cb = ttk.Combobox(r1, values=self.action_dept_combo['values'], width=20)
        dept_cb.set(values[3])
        dept_cb.pack(side='left', fill='x', expand=True)
        entries['department'] = dept_cb
        r2 = tk.Frame(dialog)
        r2.pack(fill='x', padx=10, pady=4)
        tk.Label(r2, text=self.lm.tr('col_responsible', 'Sorumlu'), width=18, anchor='w').pack(side='left')
        resp_cb = ttk.Combobox(r2, values=self.action_resp_combo['values'], width=20)
        resp_cb.set(values[4])
        resp_cb.pack(side='left', fill='x', expand=True)
        entries['responsible'] = resp_cb
        entries['action_step'] = add_entry(self.lm.tr('col_action_step', 'Önerilen Adım'), values[5])
        r3 = tk.Frame(dialog)
        r3.pack(fill='x', padx=10, pady=4)
        tk.Label(r3, text=self.lm.tr('col_due_date', 'Hedef Tarih'), width=18, anchor='w').pack(side='left')
        due_e = tk.Entry(r3)
        due_e.insert(0, values[6])
        due_e.pack(side='left', fill='x', expand=True)
        entries['due_date'] = due_e
        r4 = tk.Frame(dialog)
        r4.pack(fill='x', padx=10, pady=4)
        tk.Label(r4, text=self.lm.tr('col_status', 'Durum'), width=18, anchor='w').pack(side='left')
        status_cb = ttk.Combobox(r4, values=["Beklemede","Devam","Tamamlandı"], width=20)
        status_cb.set(values[7])
        status_cb.pack(side='left', fill='x', expand=True)
        entries['status'] = status_cb
        entries['dependencies'] = add_entry(self.lm.tr('col_dependencies', 'Bağımlılıklar'), values[8])
        def save():
            y = self.action_year_var.get().strip()
            if self._validate_year(y) is None:
                dialog.destroy()
                return
            data = {k: (v.get() if hasattr(v, 'get') else v.get()) for k, v in entries.items()}
            dv = data.get('due_date') or ''
            if dv:
                try:
                    from datetime import datetime
                    datetime.strptime(dv, '%Y-%m-%d')
                except Exception:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('invalid_date_format', 'Hedef Tarih formatı geçersiz. Örnek: 2025-12-31'))
                    return
            st = data.get('status')
            if st and st not in ['Beklemede','Devam','Tamamlandı']:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('invalid_status_value', 'Durum değeri geçersiz'))
                return
            mgr = ISSBManager(self.db_path)
            iid = sel[0]
            item_id = self.action_item_ids.get(iid)
            if item_id:
                mgr.update_action_item(item_id, data)
            else:
                mgr.add_action_item(self.company_id, int(self._validate_year(y)), data)
            dialog.destroy()
            self._load_action_plan()
            try:
                self.refresh_action_plan_status()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        tk.Button(dialog, text=self.lm.tr('btn_save', "Kaydet"), command=save).pack(pady=8)

    def _delete_action_item(self):
        sel = self.action_plan_tv.selection()
        if not sel:
            return
        iid = sel[0]
        item_id = self.action_item_ids.get(iid)
        if not item_id:
            return
        mgr = ISSBManager(self.db_path)
        mgr.delete_action_item(item_id)
        self._load_action_plan()
        try:
            self.refresh_action_plan_status()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def load_data(self):
        """Verileri yükle"""
        self.load_s1_data()
        self.load_s2_data()
        self.update_status_cards()

    def load_s1_data(self):
        """IFRS S1 verilerini yükle"""
        try:
            # Mevcut öğeleri temizle
            for item in self.s1_tree.get_children():
                self.s1_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT requirement_code, requirement_title, category, subcategory,
                       status, last_updated
                FROM ifrs_s1_requirements
                WHERE company_id = ?
                ORDER BY requirement_code
                """,
                (self.company_id,)
            )

            requirements = cursor.fetchall()
            conn.close()

            for req in requirements:
                self.s1_tree.insert('', 'end', values=req)

        except Exception as e:
            logging.error(f"IFRS S1 veri yükleme hatası: {e}")

    def load_s2_data(self):
        """IFRS S2 verilerini yükle"""
        try:
            # Mevcut öğeleri temizle
            for item in self.s2_tree.get_children():
                self.s2_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT disclosure_code, disclosure_title, category, subcategory,
                       status, last_updated
                FROM ifrs_s2_climate
                WHERE company_id = ?
                ORDER BY disclosure_code
                """,
                (self.company_id,)
            )

            disclosures = cursor.fetchall()
            conn.close()

            for disc in disclosures:
                self.s2_tree.insert('', 'end', values=disc)

        except Exception as e:
            logging.error(f"IFRS S2 veri yükleme hatası: {e}")

    def update_status_cards(self):
        """Durum kartlarını güncelle"""
        try:
            status = self.manager.get_company_issb_status(self.company_id)

            s1_rate = status['ifrs_s1']['compliance_rate']
            s2_rate = status['ifrs_s2']['compliance_rate']
            overall_rate = (s1_rate + s2_rate) / 2

            self.s1_compliance_label.config(text=f"{s1_rate:.1f}%")
            self.s2_compliance_label.config(text=f"{s2_rate:.1f}%")
            self.overall_compliance_label.config(text=f"{overall_rate:.1f}%")

        except Exception as e:
            logging.error(f"Durum kartları güncelleme hatası: {e}")

    def filter_s1_data(self):
        """IFRS S1 verilerini filtrele"""
        # Basit filtreleme - gerçek uygulamada daha gelişmiş olabilir
        self.load_s1_data()

    def filter_s2_data(self):
        """IFRS S2 verilerini filtrele"""
        # Basit filtreleme - gerçek uygulamada daha gelişmiş olabilir
        self.load_s2_data()

    def update_s1_status(self):
        """IFRS S1 durumunu güncelle"""
        selected = self.s1_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_requirement_update', "Lütfen güncellenecek gereksinimi seçin!"))
            return

        # Durum güncelleme dialog'u
        self.show_status_update_dialog('s1', selected[0])

    def update_s2_status(self):
        """IFRS S2 durumunu güncelle"""
        selected = self.s2_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_disclosure_update', "Lütfen güncellenecek açıklamayı seçin!"))
            return

        # Durum güncelleme dialog'u
        self.show_status_update_dialog('s2', selected[0])

    def show_status_update_dialog(self, standard_type, item_id):
        """Durum güncelleme dialog'unu göster"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('update_status', "Durum Güncelle"))
        dialog.geometry("400x300")
        dialog.grab_set()

        tk.Label(dialog, text=self.lm.tr('new_status', "Yeni Durum:"), font=('Segoe UI', 12, 'bold')).pack(pady=10)

        status_var = tk.StringVar(value="In Progress")
        status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                  values=["Not Started", "In Progress", "Completed"])
        status_combo.pack(pady=5)
        try:
            add_rich_tooltip(status_combo, title=self.lm.tr('status', "Durum"),
                              text=self.lm.tr('status_tooltip', "Gereksinim/açıklama ilerleme durumunu seçin."),
                              example=self.lm.tr('status_example', "Örn: In Progress"))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        tk.Label(dialog, text=self.lm.tr('notes', "Notlar:"), font=('Segoe UI', 12, 'bold')).pack(pady=(20, 5))
        notes_text = tk.Text(dialog, height=8, width=40)
        notes_text.pack(pady=5, padx=20, fill='both', expand=True)
        try:
            add_rich_tooltip(notes_text, title=self.lm.tr('notes', "Notlar"),
                              text=self.lm.tr('notes_tooltip', "Kısa açıklama ekleyin. Tamamlanan için kanıt/detay önerilir."),
                              example=self.lm.tr('notes_example', "Örn: Politika yayımlandı, link: ..."))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        def save_status():
            status = status_var.get()
            notes = notes_text.get("1.0", tk.END).strip()
            if status not in {"Not Started", "In Progress", "Completed"}:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_valid_status', "Geçerli bir durum seçin."))
                return
            if status == "Completed" and not notes:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('add_note_for_completed', "Tamamlanan durum için kısaca bir not ekleyin."))
                return
            if len(notes) > 2000:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('notes_too_long', "Notlar 2000 karakteri aşmamalıdır."))
                return
            try:
                if standard_type == 's1':
                    vals = self.s1_tree.item(item_id, 'values')
                    code = vals[0] if vals else None
                    if not code:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('code_read_error', "Kod okunamadı"))
                        return
                    import sqlite3
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()
                    row = cur.execute("SELECT id FROM ifrs_s1_requirements WHERE company_id=? AND requirement_code=?", (self.company_id, code)).fetchone()
                    conn.close()
                    if not row:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('requirement_not_found', "Gereksinim bulunamadı"))
                        return
                    req_id = int(row[0])
                    ok = self.manager.update_requirement_status(self.company_id, req_id, status, notes)
                    if not ok:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('status_update_failed', "Durum güncellenemedi"))
                        return
                else:
                    vals = self.s2_tree.item(item_id, 'values')
                    code = vals[0] if vals else None
                    if not code:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('code_read_error', "Kod okunamadı"))
                        return
                    import sqlite3
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()
                    row = cur.execute("SELECT id FROM ifrs_s2_climate WHERE company_id=? AND disclosure_code=?", (self.company_id, code)).fetchone()
                    conn.close()
                    if not row:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('disclosure_not_found', "Açıklama bulunamadı"))
                        return
                    disc_id = int(row[0])
                    ok = self.manager.update_disclosure_status(self.company_id, disc_id, status, notes)
                    if not ok:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('status_update_failed', "Durum güncellenemedi"))
                        return
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('status_updated', "Durum güncellendi!"))
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('update_error', 'Güncelleme hatası')}: {e}")

        tk.Button(dialog, text=self.lm.tr('btn_save', "Kaydet"), command=save_status,
                 bg='#10b981', fg='white').pack(pady=10)

    def show_hover_tooltip(self, widget, text, x_root, y_root):
        try:
            if hasattr(self, '_hover_tip') and self._hover_tip:
                self._hover_tip.destroy()
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.wm_geometry(f"+{x_root+12}+{y_root+12}")
            frame = tk.Frame(tip, background="#ffffe0", relief='solid', borderwidth=1)
            frame.pack()
            label = tk.Label(frame, text=text, background="#ffffe0", font=('Segoe UI', 9), justify='left', wraplength=300)
            label.pack(padx=8, pady=6)
            self._hover_tip = tip
            widget.after(1500, self.hide_hover_tooltip)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def hide_hover_tooltip(self):
        try:
            if hasattr(self, '_hover_tip') and self._hover_tip:
                self._hover_tip.destroy()
                self._hover_tip = None
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def show_s1_detail(self):
        """IFRS S1 detayını göster"""
        selected = self.s1_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_requirement_detail', "Lütfen detayını görmek istediğiniz gereksinimi seçin!"))
            return

        messagebox.showinfo(self.lm.tr('detail', "Detay"), self.lm.tr('s1_detail_info', "IFRS S1 detay bilgileri gösterilecek"))

    def show_s2_detail(self):
        """IFRS S2 detayını göster"""
        selected = self.s2_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_disclosure_detail', "Lütfen detayını görmek istediğiniz açıklamayı seçin!"))
            return

        messagebox.showinfo(self.lm.tr('detail', "Detay"), self.lm.tr('s2_detail_info', "IFRS S2 detay bilgileri gösterilecek"))

    def generate_report(self):
        """ISSB raporu oluştur"""
        try:
            period = self.report_period_var.get()
            year = self._validate_year(period)
            if year is None:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('enter_valid_year', "Lütfen geçerli bir raporlama yılı girin (örn. 2025)."))
                return
            report = self.manager.generate_issb_report(self.company_id, str(year))

            # Raporu text widget'a yaz
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", f"{self.lm.tr('issb_report_title', 'ISSB RAPORU')} - {year}\n")
            self.report_text.insert(tk.END, "=" * 50 + "\n\n")

            self.report_text.insert(tk.END, f"{self.lm.tr('report_date', 'Rapor Tarihi')}: {report.get('generation_date', 'N/A')}\n")
            self.report_text.insert(tk.END, f"{self.lm.tr('overall_compliance', 'Genel Uyumluluk')}: {report.get('overall_compliance', 0):.1f}%\n")
            self.report_text.insert(tk.END, f"{self.lm.tr('readiness_level', 'Hazırlık Seviyesi')}: {report.get('readiness_level', 'N/A')}\n\n")

            self.report_text.insert(tk.END, f"{self.lm.tr('ifrs_s1_title', 'IFRS S1 - Genel Gereksinimler')}:\n")
            s1_data = report.get('ifrs_s1_compliance', {})
            self.report_text.insert(tk.END, f"  {self.lm.tr('compliance_rate', 'Uyumluluk Oranı')}: {s1_data.get('compliance_rate', 0):.1f}%\n")
            self.report_text.insert(tk.END, f"  {self.lm.tr('completed_status', 'Tamamlanan')}: {s1_data.get('completed', 0)}\n")
            self.report_text.insert(tk.END, f"  {self.lm.tr('in_progress_status', 'Devam Eden')}: {s1_data.get('in_progress', 0)}\n")
            self.report_text.insert(tk.END, f"  {self.lm.tr('not_started_status', 'Başlanmayan')}: {s1_data.get('not_started', 0)}\n\n")

            self.report_text.insert(tk.END, f"{self.lm.tr('ifrs_s2_title', 'IFRS S2 - İklim Açıklamaları')}:\n")
            s2_data = report.get('ifrs_s2_compliance', {})
            self.report_text.insert(tk.END, f"  {self.lm.tr('compliance_rate', 'Uyumluluk Oranı')}: {s2_data.get('compliance_rate', 0):.1f}%\n")
            self.report_text.insert(tk.END, f"  {self.lm.tr('completed_status', 'Tamamlanan')}: {s2_data.get('completed', 0)}\n")
            self.report_text.insert(tk.END, f"  {self.lm.tr('in_progress_status', 'Devam Eden')}: {s2_data.get('in_progress', 0)}\n")
            self.report_text.insert(tk.END, f"  {self.lm.tr('not_started_status', 'Başlanmayan')}: {s2_data.get('not_started', 0)}\n")

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('report_generated', "ISSB raporu oluşturuldu!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_error', 'Rapor oluşturma hatası')}: {e}")

    def export_docx_report(self):
        """ISSB raporunu DOCX olarak dışa aktar (Ek: Aksiyon Planı)."""
        try:
            period = self.report_period_var.get()
            year = self._validate_year(period)
            if year is None:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('enter_valid_year_docx', "DOCX için geçerli bir yıl girin (örn. 2025)."))
                return
            report = self.manager.generate_issb_report(self.company_id, str(year))
            generator = ISSBReportGenerator()
            out_dir = os.path.join("data", "reports", "issb")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"issb_{self.company_id}_{year}.docx")
            ok = generator.generate_docx_report(out_path, report, self.company_id, int(year))
            if ok:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('docx_saved', 'DOCX kaydedildi')}: {out_path}")
                self.report_text.insert(tk.END, f"\n{self.lm.tr('docx_saved', 'DOCX kaydedildi')}: {out_path}\n")
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('docx_error', "DOCX oluşturulamadı (kütüphane eksik veya hata)."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('docx_export_error', 'DOCX dışa aktarım hatası')}: {e}")

    def export_excel_action_plan(self):
        """ISSB Gap Aksiyon Planını Excel olarak dışa aktar."""
        try:
            period = self.report_period_var.get()
            year = self._validate_year(period)
            if year is None:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('enter_valid_year_excel', "Excel için geçerli bir yıl girin (örn. 2025)."))
                return
            generator = ISSBReportGenerator()
            out_dir = os.path.join("data", "reports", "issb")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"issb_action_plan_{self.company_id}_{year}.xlsx")
            ok = generator.export_excel_action_plan(out_path, self.company_id, int(year))
            if ok:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('excel_saved', 'Excel kaydedildi')}: {out_path}")
                self.report_text.insert(tk.END, f"\n{self.lm.tr('excel_saved', 'Excel kaydedildi')}: {out_path}\n")
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('excel_error', "Excel oluşturulamadı (kütüphane eksik veya hata)."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('excel_export_error', 'Excel dışa aktarım hatası')}: {e}")

    def export_pdf_action_plan(self):
        try:
            period = self.report_period_var.get()
            year = self._validate_year(period)
            if year is None:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('enter_valid_year_pdf', "PDF için geçerli bir yıl girin (örn. 2025)."))
                return
            generator = ISSBReportGenerator()
            out_dir = os.path.join("data", "reports", "issb")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"issb_action_plan_{self.company_id}_{year}.pdf")
            ok = generator.export_pdf_action_plan(out_path, self.company_id, int(year))
            if ok:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('pdf_saved', 'PDF kaydedildi')}: {out_path}")
                self.report_text.insert(tk.END, f"\n{self.lm.tr('pdf_saved', 'PDF kaydedildi')}: {out_path}\n")
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('pdf_error', "PDF oluşturulamadı (kütüphane eksik veya hata)."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('pdf_export_error', 'PDF dışa aktarım hatası')}: {e}")
