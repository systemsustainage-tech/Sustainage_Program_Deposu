import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

try:
    from utils.progress_engine import STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED, ProgressEngine
except Exception:
    ProgressEngine = None
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
import os
from datetime import datetime

from utils.tooltip import add_rich_tooltip

try:
    from .gri_forms import (
        ContentIndexWindow,
        GRI1FoundationForm,
        GRI2DisclosuresForm,
        MaterialityForm,
        SectorStandardsWindow,
    )
    from .gri_manager import GRIManager
    from .gri_reporting import GRIReporting
except ImportError:
    # Handle the case where the script is run directly or relative imports fail
    try:
        from gri_forms import (
            ContentIndexWindow,
            GRI1FoundationForm,
            GRI2DisclosuresForm,
            MaterialityForm,
            SectorStandardsWindow,
        )
        from gri_manager import GRIManager
        from gri_reporting import GRIReporting
    except ImportError as e:
        # If both fail, it's likely a path issue or missing dependencies
        # This often happens when running the module directly instead of via main_app
        logging.error(f"Critical ImportError in gri_gui: {e}")
        # We don't raise here to allow the file to be imported, 
        # but usage of GRIGUI will likely fail if these are missing.



class GRIGUI:
    """GRI Modülü GUI - Global Reporting Initiative standartları"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.gri_manager = GRIManager()
        self.gri_manager.company_id = company_id
        self.reporting = GRIReporting()
        self.last_gri_report_path = None
        try:
            import os as _os
            # c:\SDG\modules\gri\gri_gui.py -> c:\SDG
            base_dir = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..', '..'))
            self.db_path = _os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        except Exception:
            self.db_path = None
        self._pe = ProgressEngine(self.db_path) if ProgressEngine else None
        self._steps = [
            ('gri_start', self.lm.tr('gri_start', 'Başlangıç')),
            ('gri_disclosures', self.lm.tr('gri_disclosures', 'Açıklamalar')),
            ('gri_materiality', self.lm.tr('gri_materiality', 'Materyalite')),
            ('gri_content_index', self.lm.tr('gri_content_index', 'İçerik İndeksi')),
            ('gri_complete', self.lm.tr('gri_complete', 'Tamamla'))
        ]

        # Eşleştirme modülünü yükle
        try:
            from mapping.sdg_gri_mapping import SDGGRIMapping
            self.mapping = SDGGRIMapping()
        except Exception as e:
            logging.info(f"Eşleştirme modülü yüklenemedi: {e}")
            self.mapping = None

        # UI bileşenlerini başlat
        self.content_area = None
        self.scrollable_frame = None

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()
        try:
            if self._pe:
                self._pe.initialize_steps(user_id=1, company_id=self.company_id, module_code='gri', steps=self._steps)
                self._pe.set_progress(1, self.company_id, 'gri', 'gri_start', self.lm.tr('gri_start', 'Başlangıç'), STATUS_IN_PROGRESS)
                self._update_guided_header()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def setup_ui(self) -> None:
        """GRI modülü arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık ve çıkış butonu
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        # Navigasyon
        nav_frame = tk.Frame(header_frame, bg='#2c3e50')
        nav_frame.pack(side='left', padx=20, pady=20)
        tk.Button(nav_frame, text=self.lm.tr('btn_back', "← Geri"), bg='#34495e', fg='white', relief='flat', command=self._go_back).pack(side='left', padx=(0, 6))
        tk.Button(nav_frame, text=self.lm.tr('btn_close', "✕ Kapat"), bg='#c0392b', fg='white', relief='flat', command=self._close_view).pack(side='left')

        # Başlık ve çıkış butonu yan yana
        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

        title_label = tk.Label(title_frame, text=self.lm.tr('gri_title', "GRI Standartları"),
                              font=('Segoe UI', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text=self.lm.tr('gri_full_name', "Global Reporting Initiative"),
                                 font=('Segoe UI', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack(side='left', padx=(10, 0))

        # SDG seçimine göre filtreleme butonu
        actions_frame = tk.Frame(header_frame, bg='#2c3e50')
        actions_frame.pack(side='right', padx=20, pady=20)

        # Dışa aktarma butonu
        ttk.Button(actions_frame, text=self.lm.tr('export_csv', "CSV Dışa Aktar"), style='Primary.TButton',
                   command=self.export_gri_indicators_csv).pack(side='right', padx=(10,0))

        # İçerik İndeksi
        ttk.Button(actions_frame, text=self.lm.tr('gri_content_index', "İçerik İndeksi"), style='Primary.TButton',
                   command=self.open_content_index).pack(side='right', padx=(10,0))

        # Materyalite
        ttk.Button(actions_frame, text=self.lm.tr('gri_materiality', "Materyalite"), style='Primary.TButton',
                   command=self.open_materiality).pack(side='right', padx=(10,0))

        # GRI 2
        ttk.Button(actions_frame, text=self.lm.tr('gri_2_disclosures', "GRI 2 Açıklamalar"), style='Primary.TButton',
                   command=self.open_gri2).pack(side='right', padx=(10,0))

        # GRI 1
        ttk.Button(actions_frame, text=self.lm.tr('gri_1_foundation', "GRI 1 Temel"), style='Primary.TButton',
                   command=self.open_gri1).pack(side='right', padx=(10,0))

        # Sektör
        ttk.Button(actions_frame, text=self.lm.tr('sector_standards', "Sektör Standartları"), style='Primary.TButton',
                   command=self.open_sector).pack(side='right', padx=(10,0))

        # SDG seçimine göre filtreleme butonu
        self.filter_btn = ttk.Button(actions_frame, text=self.lm.tr('filter_by_sdg', "SDG Seçimine Göre Filtrele"), style='Primary.TButton',
                                     command=self.toggle_sdg_filter)
        self.filter_btn.pack(side='right')
        ttk.Button(actions_frame, text=self.lm.tr('btn_report_center', "Rapor Merkezi"), style='Primary.TButton',
                   command=self.open_report_center_gri).pack(side='right', padx=(10,0))

        self.sdg_filter_active = False

        # İstatistik kartları
        self.create_stats_frame(main_frame)

        guided = tk.Frame(main_frame, bg='#f8fafc', height=50)
        guided.pack(fill='x', pady=(0, 10))
        guided.pack_propagate(False)
        self._guided_frame = guided
        try:
            self._progress_var = tk.DoubleVar(value=0.0)
            pb = ttk.Progressbar(guided, maximum=100.0, variable=self._progress_var)
            pb.pack(side='left', fill='x', expand=True, padx=10, pady=10)
            self._step_info = tk.Label(guided, text=f"{self.lm.tr('step', 'Adım')}: {self.lm.tr('step_start', 'Başlangıç')}", font=('Segoe UI', 10, 'bold'), bg='#f8fafc', fg='#334155')
            self._step_info.pack(side='left', padx=10)
            try:
                add_rich_tooltip(self._step_info, self.lm.tr('what_to_do_in_this_step', "Bu adımda ne yapmalı?"), self.lm.tr('gri_step_desc', "GRI modülünde sırasıyla açıklamalar, materyalite ve içerik indeksini tamamlayın."))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            def _next_step():
                try:
                    if not self._pe:
                        return
                    progress = self._pe.get_module_progress(self.company_id, 'gri', user_id=1)
                    order = [sid for sid, _ in self._steps]
                    current_sid = None
                    for p in progress:
                        if p['status'] == STATUS_IN_PROGRESS:
                            current_sid = p['step_id']
                            break
                    if current_sid is None:
                        current_sid = order[0]
                    idx = order.index(current_sid)
                    self._pe.set_progress(1, self.company_id, 'gri', current_sid,
                                          dict(self._steps)[current_sid], STATUS_COMPLETED)
                    if idx + 1 < len(order):
                        next_sid = order[idx + 1]
                        self._pe.set_progress(1, self.company_id, 'gri', next_sid,
                                              dict(self._steps)[next_sid], STATUS_IN_PROGRESS)
                    self._update_guided_header()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            ttk.Button(guided, text=self.lm.tr('next_step', " Sonraki Adım"), style='Primary.TButton', command=_next_step).pack(side='right', padx=10)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Ana içerik - Basit ve temiz
        content_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        content_frame.pack(fill='both', expand=True)

        # Sol panel - Kategoriler
        left_panel = tk.Frame(content_frame, bg='#f8f9fa', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 1))
        left_panel.pack_propagate(False)
        # Grid yapılandırması: scroll alanının dikeyde genişlemesi için
        left_panel.grid_rowconfigure(2, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Kategori başlığı
        cat_title = tk.Label(left_panel, text=self.lm.tr('gri_categories', "GRI Kategorileri"),
                           font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        cat_title.grid(row=0, column=0, columnspan=2, pady=15, sticky='ew')

        # Arama ve filtreleme
        search_frame = tk.Frame(left_panel, bg='#f8f9fa')
        search_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=15, pady=(0, 10))

        search_label = tk.Label(search_frame, text=self.lm.tr('search_and_filter', "Arama ve Filtreleme"),
                               font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        search_label.pack(anchor='w', pady=(0, 5))

        # Arama kutusu
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=('Segoe UI', 10), relief='solid', bd=1)
        search_entry.pack(fill='x', pady=(0, 5))
        search_entry.insert(0, self.lm.tr('search_placeholder', "Kod veya başlık ara..."))
        search_entry.bind('<FocusIn>', self.on_search_focus_in)
        search_entry.bind('<FocusOut>', self.on_search_focus_out)

        # Filtre seçenekleri
        filter_frame = tk.Frame(search_frame, bg='#f8f9fa')
        filter_frame.pack(fill='x', pady=(5, 0))

        # Öncelik filtresi
        priority_label = tk.Label(filter_frame, text=self.lm.tr('priority', "Öncelik:"),
                                 font=('Segoe UI', 9), fg='#2c3e50', bg='#f8f9fa')
        priority_label.pack(anchor='w')

        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_var,
                                     values=[self.lm.tr('priority_all', 'Tümü'), 
                                             self.lm.tr('priority_critical', 'Kritik'), 
                                             self.lm.tr('priority_high', 'Yüksek'), 
                                             self.lm.tr('priority_medium', 'Orta'), 
                                             self.lm.tr('priority_low', 'Düşük')],
                                     state='readonly', width=15)
        priority_combo.pack(fill='x', pady=(0, 5))
        priority_combo.set(self.lm.tr('priority_all', 'Tümü'))
        priority_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Gereklilik filtresi
        requirement_label = tk.Label(filter_frame, text=self.lm.tr('requirement', "Gereklilik:"),
                                    font=('Segoe UI', 9), fg='#2c3e50', bg='#f8f9fa')
        requirement_label.pack(anchor='w')

        self.requirement_var = tk.StringVar()
        requirement_combo = ttk.Combobox(filter_frame, textvariable=self.requirement_var,
                                        values=[self.lm.tr('req_all', 'Tümü'), 
                                                self.lm.tr('req_mandatory', 'Zorunlu'), 
                                                self.lm.tr('req_recommended', 'Önerilen'), 
                                                self.lm.tr('req_optional', 'İsteğe Bağlı')],
                                        state='readonly', width=15)
        requirement_combo.pack(fill='x', pady=(0, 5))
        requirement_combo.set(self.lm.tr('req_all', 'Tümü'))
        requirement_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Temizle butonu
        ttk.Button(filter_frame, text=self.lm.tr('clear_filters', "Filtreleri Temizle"), style='Primary.TButton',
                   command=self.clear_filters).pack(fill='x', pady=(5, 0))

        # Kategori butonları için scroll yapısı
        cat_canvas = tk.Canvas(left_panel, bg='#f8f9fa', highlightthickness=0)
        cat_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=cat_canvas.yview)
        cat_scrollable_frame = tk.Frame(cat_canvas, bg='#f8f9fa')

        cat_scrollable_frame.bind(
            "<Configure>",
            lambda e: cat_canvas.configure(scrollregion=cat_canvas.bbox("all"))
        )

        cat_canvas.create_window((0, 0), window=cat_scrollable_frame, anchor="nw")
        cat_canvas.configure(yscrollcommand=cat_scrollbar.set)

        # Grid ile yerleştir: scroll alanı kalan yüksekliği doldurur
        cat_canvas.grid(row=2, column=0, sticky='nsew')
        cat_scrollbar.grid(row=2, column=1, sticky='ns')

        # Mouse wheel desteği
        def _on_mousewheel(event) -> None:
            try:
                cat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        # Mouse wheel olaylarını sol panelde de yakala
        cat_canvas.bind("<MouseWheel>", _on_mousewheel)
        cat_scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        left_panel.bind("<MouseWheel>", _on_mousewheel)

        # Kategori butonları
        self._nav_stack = []
        self._current_view = None
        self.category_buttons = {}
        self.create_category_buttons(cat_scrollable_frame)

        # Sağ panel - İçerik
        right_panel = tk.Frame(content_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True)

        # İçerik başlığı
        self.content_title = tk.Label(right_panel, text=self.lm.tr('gri_welcome_title', "GRI Standartlarına Hoş Geldiniz"),
                                    font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white')
        self.content_title.pack(pady=20)

        # İçerik alanı - Scrollable
        self.create_content_area(right_panel)
        self._current_view = (self.show_welcome_content, tuple(), {})

        report_open_frame = tk.Frame(main_frame, bg='white')
        report_open_frame.pack(fill='x', padx=15, pady=(10, 0))
        ttk.Button(report_open_frame, text=self.lm.tr('btn_preview_outputs', 'Önizleme ve Çıkışlar'), style='Primary.TButton', command=self._gri_open_preview_window).pack(side='left')


    def _gri_open_preview_window(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('gri_preview_window_title', 'GRI Önizleme ve Çıkışlar'))
            win.geometry('900x600')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            ttk.Button(top, text=self.lm.tr('btn_back', 'Geri'), command=win.destroy).pack(side='left')
            top_controls = tk.Frame(win, bg='white')
            top_controls.pack(fill='x', padx=10, pady=6)
            tk.Label(top_controls, text=self.lm.tr('reporting_period', 'Raporlama Dönemi:'), bg='white').pack(side='left')
            self.gri_report_period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
            period_entry = tk.Entry(top_controls, textvariable=self.gri_report_period_var, width=10)
            period_entry.pack(side='left', padx=8)
            try:
                add_rich_tooltip(period_entry, title=self.lm.tr('report_year_tooltip_title', 'Rapor Yılı'), text=self.lm.tr('report_year_tooltip_text', 'GRI rapor yılı (YYYY).'), example='Örn: 2025')
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            self.gri_report_text = tk.Text(win, height=20, wrap='word')
            r_scroll = ttk.Scrollbar(win, orient='vertical', command=self.gri_report_text.yview)
            self.gri_report_text.configure(yscrollcommand=r_scroll.set)
            self.gri_report_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            r_scroll.pack(side='right', fill='y', pady=10)
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', padx=10, pady=(0,10))
            ttk.Button(tools, text=self.lm.tr('fill_preview', 'Önizlemeyi Doldur'), style='Primary.TButton', command=self._gri_fill_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('open', 'Aç'), style='Primary.TButton', command=self._gri_open_last_report).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('save_txt', 'Kaydet (.txt)'), style='Primary.TButton', command=self._gri_save_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('save_docx', 'Farklı Kaydet (DOCX)'), style='Primary.TButton', command=self._gri_export_docx).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('save_pdf', 'Farklı Kaydet (PDF)'), style='Primary.TButton', command=self._gri_export_pdf).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('print', 'Yazdır'), style='Primary.TButton', command=self._gri_print_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('copy_to_clipboard', 'Panoya Kopyala'), style='Primary.TButton', command=self._gri_copy_preview_to_clipboard).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('share', 'Paylaş'), style='Primary.TButton', command=self._gri_share_dialog).pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('preview_error', 'Önizleme penceresi hatası')}: {e}")

    def open_report_center_gri(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('gri')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"{self.lm.tr('gri_report_filter_error', 'GRI raporları filtrelenirken hata')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'HATA'), f"{self.lm.tr('report_center_open_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"{self.lm.tr('report_center_open_error_log', 'Rapor merkezi açma hatası')}: {e}")

    def _update_guided_header(self) -> None:
        try:
            if not self._pe:
                return
            percent = self._pe.get_completion_percentage(self.company_id, 'gri', self._steps, user_id=1)
            self._progress_var.set(percent)
            progress = self._pe.get_module_progress(self.company_id, 'gri', user_id=1)
            active = None
            for p in progress:
                if p['status'] == STATUS_IN_PROGRESS:
                    active = p
                    break
            step_text = f"Adım: {active['step_title']}" if active else "Adım: -"
            self._step_info.configure(text=step_text)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def open_gri1(self) -> None:
        try:
            GRI1FoundationForm(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('gri1_form_error', 'GRI 1 formu açılamadı')}: {e}")

    def open_gri2(self) -> None:
        try:
            GRI2DisclosuresForm(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('gri2_form_error', 'GRI 2 formu açılamadı')}: {e}")

    def open_materiality(self) -> None:
        try:
            MaterialityForm(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('materiality_form_error', 'Materyalite formu açılamadı')}: {e}")

    def open_content_index(self) -> None:
        try:
            ContentIndexWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('content_index_error', 'İçerik indeksi penceresi açılamadı')}: {e}")

    def open_sector(self) -> None:
        try:
            SectorStandardsWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('sector_standards_error', 'Sektör standartları penceresi açılamadı')}: {e}")

    def create_content_area(self, parent) -> None:
        """İçerik alanını oluştur"""
        # Canvas ve scrollbar
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)

        # content_area'yi canvas olarak ayarla
        self.content_area = canvas
        self.scrollable_frame = tk.Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel desteği
        def _on_mousewheel(event) -> None:
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Başlangıç içeriği
        self.show_welcome_content()

    def setup_content_area(self, parent) -> None:
        """Mevcut içerik alanı içinde yeni scrollable frame oluştur"""
        try:
            # Canvas ise tüm öğeleri temizle
            if isinstance(parent, tk.Canvas):
                for item in parent.find_all():
                    parent.delete(item)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Yeni scrollable frame kur
        self.scrollable_frame = tk.Frame(parent, bg='white')
        try:
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: parent.configure(scrollregion=parent.bbox("all"))
            )
            parent.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        except Exception:
            # parent Canvas değilse, direkt pack ile ekle
            self.scrollable_frame.pack(fill='both', expand=True)

    def show_welcome_content(self) -> None:
        """Hoş geldin içeriğini göster"""
        # Content area'yı temizle
        try:
            for widget in self.content_area.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Content area'yı yeniden oluştur
        self.setup_content_area(self.content_area)

        # Hoş geldin metni
        welcome_text = self.lm.tr('gri_welcome_text', """
GRI (Global Reporting Initiative) Standartları

GRI Standartları, sürdürülebilirlik raporlaması için en yaygın kullanılan küresel standartlardır. 
Bu modülde GRI standartlarını inceleyebilir ve şirketiniz için uygun olanları seçebilirsiniz.

Kategoriler:
• Universal Standards: Tüm şirketler için temel standartlar
• Economic: Ekonomik performans standartları  
• Environmental: Çevresel etki standartları
• Social: Sosyal etki standartları

Sol menüden bir kategori seçerek detayları inceleyebilirsiniz.
        """)

        welcome_label = tk.Label(self.scrollable_frame, text=welcome_text.strip(),
                               font=('Segoe UI', 11), fg='#2c3e50', bg='white',
                               justify='left', wraplength=600)
        welcome_label.pack(pady=20, padx=20)

    def _go_back(self) -> None:
        try:
            if getattr(self, '_nav_stack', None):
                prev = self._nav_stack.pop()
                fn, args, kwargs = prev
                fn(*args, **kwargs)
                self._current_view = (fn, args, kwargs)
            else:
                # Ana uygulamaya (Dashboard) dön
                if hasattr(self, 'main_app') and self.main_app:
                    try:
                        self.main_app.show_dashboard()
                        return
                    except Exception as e:
                        logging.error(f"Dashboard'a dönme hatası: {e}")

                self.show_welcome_content()
                self._current_view = (self.show_welcome_content, tuple(), {})
        except Exception:
            self.show_welcome_content()
            self._current_view = (self.show_welcome_content, tuple(), {})

    def _navigate_to(self, fn, *args, **kwargs) -> None:
        try:
            cur = getattr(self, '_current_view', None)
            if cur and (cur[0] is not fn or cur[1] != args or cur[2] != kwargs):
                self._nav_stack.append(cur)
            fn(*args, **kwargs)
            self._current_view = (fn, args, kwargs)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _close_view(self) -> None:
        try:
            self.show_welcome_content()
            self._current_view = (self.show_welcome_content, tuple(), {})
            if hasattr(self, '_nav_stack'):
                self._nav_stack.clear()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def show_category(self, category_key) -> None:
        """Kategori içeriğini göster"""
        try:
            # Mevcut kategoriyi kaydet
            self.current_category = category_key

            # İçerik alanını temizle
            try:
                for widget in self.content_area.winfo_children():
                    widget.destroy()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

            # Content area'yı yeniden oluştur
            self.setup_content_area(self.content_area)

            # Kategori başlığını güncelle
            category_names = {
                "universal": self.lm.tr('gri_cat_universal', "Universal Standards"),
                "economic": self.lm.tr('gri_cat_economic', "Economic Standards"),
                "environmental": self.lm.tr('gri_cat_environmental', "Environmental Standards"),
                "social": self.lm.tr('gri_cat_social', "Social Standards"),
                "sector": self.lm.tr('gri_cat_sector', "Sector-Specific Standards")
            }

            self.content_title.config(text=category_names.get(category_key, self.lm.tr('gri_title', "GRI Standartları")))

            # Kategori butonlarını güncelle
            for key, btn in self.category_buttons.items():
                if key == category_key:
                    btn.config(bg='#34495e', fg='white')
                else:
                    colors = {"universal": "#3498db", "economic": "#f39c12",
                             "environmental": "#27ae60", "social": "#e74c3c", "sector": "#9b59b6"}
                    btn.config(bg=colors[key], fg='white')

            # Kategori verilerini getir ve göster
            category_data = self.get_filtered_data(category_key)
            self.display_category_data(category_key, category_data)

        except Exception as e:
            logging.error(f"Kategori gösterilirken hata: {e}")

    def display_category_data(self, category_name, data) -> None:
        """Kategori verilerini göster"""
        # Content area'yı temizle
        try:
            for widget in self.content_area.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Content area'yı yeniden oluştur
        self.setup_content_area(self.content_area)

        # Sektörel standartlar için özel handling
        if category_name == "sector":
            self.display_sectoral_standards()
            return

        if not data or not data.get('indicators'):
            no_data_label = tk.Label(self.scrollable_frame,
                                   text=self.lm.tr('category_no_data', "{category} kategorisinde veri bulunamadı.").format(category=category_name),
                                   font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
            no_data_label.pack(pady=50)
            return

        # Kategori başlığı
        category_names = {
            "universal": self.lm.tr('cat_universal', "Universal Standards"),
            "economic": self.lm.tr('cat_economic', "Economic Standards"),
            "environmental": self.lm.tr('cat_environmental', "Environmental Standards"),
            "social": self.lm.tr('cat_social', "Social Standards"),
            "sector": self.lm.tr('cat_sector', "Sector-Specific Standards")
        }

        title_label = tk.Label(self.scrollable_frame,
                              text=category_names.get(category_name, category_name),
                              font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=(10, 20))

        # Göstergeleri listele
        for indicator in data['indicators']:
            self.create_indicator_card(self.scrollable_frame, indicator)

    def display_sectoral_standards(self) -> None:
        """Sektörel standartları göster"""
        try:
            # Sektörel standartlar manager'ını import et
            from modules.standards.gri_sectoral_standards import GRISectoralStandardsManager

            manager = GRISectoralStandardsManager()
            standards = manager.get_sectoral_standards()

            # Başlık
            title_label = tk.Label(self.scrollable_frame,
                                  text=f" {self.lm.tr('gri_sectoral_standards', 'GRI Sektörel Standartları')}",
                                  font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='white')
            title_label.pack(pady=(10, 20))

            # Açıklama
            desc_label = tk.Label(self.scrollable_frame,
                                 text=self.lm.tr('gri_sectoral_desc', "Sektöre özgü GRI standartları ve uygulamaları"),
                                 font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
            desc_label.pack(pady=(0, 20))

            # Sektörel standartlar butonları
            for standard in standards:
                self.create_sectoral_standard_card(self.scrollable_frame, standard, manager)

        except Exception as e:
            error_label = tk.Label(self.scrollable_frame,
                                  text=f"{self.lm.tr('sectoral_load_error', 'Sektörel standartlar yüklenirken hata')}: {e}",
                                  font=('Segoe UI', 12), fg='#e74c3c', bg='white')
            error_label.pack(pady=50)

    def create_sectoral_standard_card(self, parent, standard, manager) -> None:
        """Sektörel standart kartı oluştur"""
        # Ana kart frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=10, pady=5)

        # Kart içeriği
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=15)

        # Başlık satırı
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 10))

        # Standart kodu ve adı
        title_text = f"{standard['standard_code']} - {standard['standard_name']}"
        title_label = tk.Label(header_frame, text=title_text,
                              font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(side='left')

        # Yıl
        year_label = tk.Label(header_frame, text=f"({standard['year']})",
                             font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
        year_label.pack(side='right')

        # Açıklama
        desc_label = tk.Label(content_frame, text=standard['description'],
                             font=('Segoe UI', 10), fg='#34495e', bg='white', wraplength=600, justify='left')
        desc_label.pack(anchor='w', pady=(0, 10))

        # Sektör bilgisi
        sector_label = tk.Label(content_frame, text=f"{self.lm.tr('sector', 'Sektör')}: {standard['sector']}",
                               font=('Segoe UI', 10, 'bold'), fg='#27ae60', bg='white')
        sector_label.pack(anchor='w', pady=(0, 10))

        # Uygulanabilir sektörler
        if standard.get('applicable_sectors'):
            applicable_label = tk.Label(content_frame,
                                       text=f"{self.lm.tr('applicable_sectors', 'Uygulanabilir Sektörler')}: {standard['applicable_sectors']}",
                                       font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
            applicable_label.pack(anchor='w', pady=(0, 10))

        # Alt panel - Butonlar
        btn_frame = tk.Frame(content_frame, bg='white')
        btn_frame.pack(fill='x', pady=(10, 0))

        # Detayları görüntüle butonu
        def show_standard_details():
            self.show_sectoral_standard_details(standard['standard_code'], manager)

        ttk.Button(btn_frame, text=f" {self.lm.tr('view_details', 'Detayları Görüntüle')}", style='Primary.TButton',
                   command=show_standard_details).pack(side='left', padx=(0, 10))

        # Uyumluluk durumu butonu
        def show_compliance():
            self.show_sectoral_compliance(standard['standard_code'], manager)

        ttk.Button(btn_frame, text=f" {self.lm.tr('compliance_status', 'Uyumluluk Durumu')}", style='Primary.TButton',
                   command=show_compliance).pack(side='left', padx=(0, 10))

        # Rapor oluştur butonu
        def generate_report():
            self.generate_sectoral_report(standard['standard_code'], manager)

        ttk.Button(btn_frame, text=f" {self.lm.tr('create_report', 'Rapor Oluştur')}", style='Primary.TButton',
                   command=generate_report).pack(side='left')

    def show_sectoral_standard_details(self, standard_code, manager) -> None:
        """Sektörel standart detaylarını göster"""
        try:
            topics = manager.get_standard_topics(standard_code, self.company_id)

            # Detay penceresi
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"{standard_code} - {self.lm.tr('details', 'Detaylar')}")
            detail_window.geometry("800x600")
            detail_window.configure(bg='white')

            # Başlık
            tk.Label(detail_window, text=f"{standard_code} {self.lm.tr('topics', 'Konuları')}",
                    font=('Segoe UI', 16, 'bold'), bg='white').pack(pady=10)

            # Konular listesi
            topics_frame = tk.Frame(detail_window, bg='white')
            topics_frame.pack(fill='both', expand=True, padx=20, pady=10)

            for topic in topics:
                topic_frame = tk.Frame(topics_frame, bg='#f8f9fa', relief='solid', bd=1)
                topic_frame.pack(fill='x', pady=5)

                # Konu başlığı
                tk.Label(topic_frame, text=topic.get('topic_name', ''),
                        font=('Segoe UI', 12, 'bold'), bg='#f8f9fa').pack(anchor='w', padx=10, pady=5)

                # Konu açıklaması
                tk.Label(topic_frame, text=topic.get('topic_description', ''),
                        font=('Segoe UI', 10), bg='#f8f9fa', wraplength=700, justify='left').pack(anchor='w', padx=10, pady=(0, 5))

                # Uyumluluk durumu
                status = topic.get('compliance_status', 'Not Started')
                status_color = {'Compliant': '#27ae60', 'In Progress': '#f39c12',
                               'Not Started': '#e74c3c', 'Not Applicable': '#95a5a6'}.get(status, '#95a5a6')
                
                status_tr = {
                    'Compliant': self.lm.tr('status_compliant', 'Uyumlu'),
                    'In Progress': self.lm.tr('status_in_progress', 'Devam Ediyor'),
                    'Not Started': self.lm.tr('status_not_started', 'Başlanmadı'),
                    'Not Applicable': self.lm.tr('status_not_applicable', 'Uygulanamaz')
                }.get(status, status)

                tk.Label(topic_frame, text=f"{self.lm.tr('status', 'Durum')}: {status_tr}",
                        font=('Segoe UI', 10, 'bold'), fg=status_color, bg='#f8f9fa').pack(anchor='w', padx=10, pady=(0, 10))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('details_error', 'Standart detayları gösterilirken hata')}: {e}")

    def show_sectoral_compliance(self, standard_code, manager) -> None:
        """Sektörel standart uyumluluk durumunu göster"""
        try:
            win = tk.Toplevel(self.parent)
            win.title(f"{standard_code} {self.lm.tr('compliance_status', 'Uyumluluk Durumu')}")
            win.geometry("800x600")

            main_frame = tk.Frame(win, bg='white')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)

            tk.Label(main_frame, text=f"{standard_code} {self.lm.tr('compliance_status', 'Uyumluluk Durumu')}",
                    font=('Segoe UI', 16, 'bold'), bg='white').pack(pady=10)

            # Uyumluluk verilerini göster
            import sqlite3
            conn = sqlite3.connect(manager.db_path)
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT disclosure_number, disclosure_title, reporting_status
                    FROM gri_2_general_disclosures
                    WHERE company_id = ? AND disclosure_number LIKE ?
                    ORDER BY disclosure_number
                """, (self.company_id, f"{standard_code}%"))

                columns = (self.lm.tr('disclosure', 'Disclosure'), self.lm.tr('title', 'Başlık'), self.lm.tr('status', 'Durum'))
                tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)

                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=200)

                tree.pack(fill='both', expand=True, pady=10)

                for row in cursor.fetchall():
                    tree.insert('', 'end', values=row)
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('compliance_data_error', 'Uyumluluk verileri yüklenemedi')}: {e}")
            finally:
                conn.close()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('compliance_show_error', 'Uyumluluk durumu gösterilemedi')}: {e}")

    def generate_sectoral_report(self, standard_code, manager) -> None:
        """Sektörel standart raporu oluştur"""
        try:
            from tkinter import filedialog

            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr('pdf_files', "PDF Dosyaları"), "*.pdf"), (self.lm.tr('excel_files', "Excel Dosyaları"), "*.xlsx"), (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")],
                title=f"{standard_code} {self.lm.tr('save_report', 'Raporu Kaydet')}",
                initialfile=f"{standard_code}_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
            )

            if save_path:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{standard_code} {self.lm.tr('report_created', 'raporu oluşturuldu')}:\n{save_path}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_create_error', 'Rapor oluşturulamadı')}: {e}")

    def _gri_fill_preview_text(self) -> None:
        try:
            period = self.gri_report_period_var.get().strip()
            if period and (not period.isdigit() or len(period) != 4):
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('invalid_year_error', "Geçerli bir yıl girin (YYYY)"))
                return
            data = self.reporting.get_gri_data(self.company_id, period or None)
            if 'error' in data:
                messagebox.showerror(self.lm.tr('error', 'Hata'), data['error'])
                return
            self.gri_report_text.delete('1.0', tk.END)
            self.gri_report_text.insert(tk.END, f"{self.lm.tr('gri_content_index_report', 'GRI İçerik İndeksi ve Rapor')}\n")
            self.gri_report_text.insert(tk.END, f"{self.lm.tr('company', 'Şirket')}: {data['company']['name']}\n")
            if period:
                self.gri_report_text.insert(tk.END, f"{self.lm.tr('period', 'Dönem')}: {period}\n")
            self.gri_report_text.insert(tk.END, f"{self.lm.tr('selected_indicators_count', 'Seçilen Gösterge Sayısı')}: {len(data['selections'])}\n")
            self.gri_report_text.insert(tk.END, f"{self.lm.tr('answered_indicators_count', 'Cevaplanan Gösterge Sayısı')}: {len(data['responses'])}\n\n")
            for scode, icode, ititle, tsrs in data.get('content_rows', []):
                self.gri_report_text.insert(tk.END, f"{scode} - {icode}: {ititle}\n")
                self.gri_report_text.insert(tk.END, f"  TSRS: {tsrs}\n\n")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('preview_error', 'Önizleme hatası')}: {e}")

    def _gri_save_preview_text(self) -> None:
        try:
            content = self.gri_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('preview_empty', 'Önizleme içeriği boş'))
                return
            period = self.gri_report_period_var.get().strip()
            fp = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.txt',
                filetypes=[(self.lm.tr('text_file', 'Metin Dosyası'), '*.txt')],
                initialfile=f"gri_report_{self.company_id}_{period or datetime.now().strftime('%Y')}.txt"
            )
            if not fp:
                return
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('report_text_saved', 'Rapor metni kaydedildi')}: {fp}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def _gri_export_docx(self) -> None:
        try:
            period = self.gri_report_period_var.get().strip()
            if period and (not period.isdigit() or len(period) != 4):
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('invalid_year_error', 'Geçerli bir yıl girin (YYYY)'))
                return
            out = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.docx',
                filetypes=[(self.lm.tr('word_file', 'Word Dosyası'),'*.docx')],
                initialfile=f"gri_report_{self.company_id}_{period or datetime.now().strftime('%Y')}.docx"
            )
            if not out:
                return
            ok = self.reporting.create_docx_report(self.company_id, out, period or None)
            if ok:
                self.last_gri_report_path = out
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('docx_created', 'DOCX raporu oluşturuldu')}: {out}")
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('docx_create_failed', 'DOCX oluşturulamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('docx_create_error', 'DOCX oluşturma hatası')}: {e}")

    def _gri_export_pdf(self) -> None:
        try:
            period = self.gri_report_period_var.get().strip()
            if period and (not period.isdigit() or len(period) != 4):
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('invalid_year_error', 'Geçerli bir yıl girin (YYYY)'))
                return
            out = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.pdf',
                filetypes=[(self.lm.tr('pdf_file', 'PDF Dosyası'),'*.pdf')],
                initialfile=f"gri_report_{self.company_id}_{period or datetime.now().strftime('%Y')}.pdf"
            )
            if not out:
                return
            ok = self.reporting.create_pdf_report(self.company_id, out, period or None)
            if ok:
                self.last_gri_report_path = out
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('pdf_created', 'PDF raporu oluşturuldu')}: {out}")
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('pdf_create_failed', 'PDF oluşturulamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('pdf_create_error', 'PDF oluşturma hatası')}: {e}")

    def _gri_print_preview_text(self) -> None:
        try:
            import tempfile
            content = self.gri_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('preview_empty', 'Önizleme içeriği boş'))
                return
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"gri_preview_{self.company_id}_{self.gri_report_period_var.get() or datetime.now().strftime('%Y')}.txt")
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp_path, 'print')
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('print_started', 'Yazdırma başlatıldı'))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_error', 'Yazdırma hatası')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_prep_error', 'Yazdırmaya hazırlık hatası')}: {e}")

    def _gri_open_last_report(self) -> None:
        try:
            if self.last_gri_report_path and os.path.exists(self.last_gri_report_path):
                os.startfile(self.last_gri_report_path)
            else:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('report_not_found', 'Açılacak rapor bulunamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('open_error', 'Açma hatası')}: {e}")

    def _gri_copy_preview_to_clipboard(self) -> None:
        try:
            content = self.gri_report_text.get('1.0', tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('preview_copied', 'Önizleme metni panoya kopyalandı'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _gri_share_dialog(self) -> None:
        try:
            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('share', 'Paylaş'))
            dialog.geometry('360x180')
            dialog.grab_set()
            tk.Label(dialog, text=self.lm.tr('share_options', 'Paylaşım Seçenekleri'), font=('Segoe UI', 12, 'bold')).pack(pady=10)
            btns = tk.Frame(dialog)
            btns.pack(pady=10)
            def copy_path():
                path = self.last_gri_report_path
                if path and os.path.exists(path):
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(path)
                    messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('path_copied', 'Dosya yolu panoya kopyalandı'))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('share_file_not_found', 'Paylaşılacak dosya bulunamadı'))
            def open_folder():
                path = self.last_gri_report_path
                if path and os.path.exists(path):
                    os.startfile(os.path.dirname(path))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('folder_open_error', 'Klasör açılamadı'))
            def copy_text():
                content = self.gri_report_text.get('1.0', tk.END)
                self.parent.clipboard_clear()
                self.parent.clipboard_append(content)
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('preview_copied', 'Önizleme metni panoya kopyalandı'))
            ttk.Button(btns, text=self.lm.tr('copy_path', 'Dosya Yolunu Kopyala'), style='Primary.TButton', command=copy_path).pack(side='left', padx=6)
            ttk.Button(btns, text=self.lm.tr('open_folder', 'Klasörü Aç'), style='Primary.TButton', command=open_folder).pack(side='left', padx=6)
            ttk.Button(btns, text=self.lm.tr('copy_preview', 'Önizleme Metnini Kopyala'), style='Primary.TButton', command=copy_text).pack(side='left', padx=6)
            ttk.Button(dialog, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=dialog.destroy).pack(pady=8)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('share_error', 'Paylaşım hatası')}: {e}")

    def create_indicator_card(self, parent, indicator) -> None:
        """Gösterge kartı oluştur"""
        # Ana kart frame
        card_frame = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=10, pady=5)

        # Kart içeriği
        content_frame = tk.Frame(card_frame, bg='#f8f9fa')
        content_frame.pack(fill='x', padx=15, pady=10)

        # Başlık satırı
        header_frame = tk.Frame(content_frame, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=(0, 5))

        # Gösterge kodu
        code_label = tk.Label(header_frame, text=indicator.get('code', ''),
                             font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        code_label.pack(side='left')

        # Birim
        unit = indicator.get('unit', '')
        if unit:
            unit_label = tk.Label(header_frame, text=f"[{unit}]",
                                 font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa')
            unit_label.pack(side='left', padx=(10, 0))

        # Başlık
        title_label = tk.Label(content_frame, text=indicator.get('title', ''),
                              font=('Segoe UI', 11), fg='#2c3e50', bg='#f8f9fa',
                              wraplength=600, justify='left')
        title_label.pack(anchor='w', pady=(0, 5))

        # Detaylar
        details_frame = tk.Frame(content_frame, bg='#f8f9fa')
        details_frame.pack(fill='x', pady=(0, 5))

        # Metodoloji
        methodology = indicator.get('methodology', '')
        if methodology:
            method_label = tk.Label(details_frame, text=f"{self.lm.tr('methodology', 'Metodoloji')}: {methodology}",
                                   font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa')
            method_label.pack(anchor='w')

        # Gereklilik
        requirement = indicator.get('reporting_requirement', '')
        if requirement:
            req_label = tk.Label(details_frame, text=f"{self.lm.tr('requirement', 'Gereklilik')}: {requirement}",
                                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa')
            req_label.pack(anchor='w')

        # Öncelik
        priority = indicator.get('priority', '')
        if priority:
            priority_label = tk.Label(details_frame, text=f"{self.lm.tr('priority', 'Öncelik')}: {priority}",
                                     font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa')
            priority_label.pack(anchor='w')

        # Aksiyon butonları
        actions_frame = tk.Frame(content_frame, bg='#f8f9fa')
        actions_frame.pack(fill='x', pady=(5, 0))

        # Detay butonu
        ttk.Button(actions_frame, text=self.lm.tr('detail', "Detay"), style='Primary.TButton',
                   command=lambda: self.show_indicator_detail(indicator)).pack(side='left', padx=(0, 5))

        # Yanıtla butonu
        ttk.Button(actions_frame, text=self.lm.tr('respond', "Yanıtla"), style='Primary.TButton',
                   command=lambda: self.respond_to_indicator(indicator)).pack(side='left')

    def show_indicator_detail(self, indicator) -> None:
        """Gösterge detayını göster"""
        # Detay penceresi oluştur (basit versiyon)
        detail_window = tk.Toplevel(self.parent)
        code = indicator.get('code') or indicator.get('indicator_code') or ''
        detail_window.title(f"GRI {code} {self.lm.tr('detail', 'Detayı')}")
        detail_window.geometry("600x400")
        detail_window.configure(bg='white')

        # Detay içeriği
        title = indicator.get('title') or indicator.get('indicator_title') or ''
        unit = indicator.get('unit') or indicator.get('unit_name') or ''
        methodology = indicator.get('methodology') or indicator.get('methodology_detail') or ''
        requirement = indicator.get('reporting_requirement') or indicator.get('requirement') or ''
        priority = indicator.get('priority') or ''
        detail_text = f"""
GRI {self.lm.tr('indicator_detail', 'Gösterge Detayı')}

{self.lm.tr('code', 'Kod')}: {code}
{self.lm.tr('title', 'Başlık')}: {title}
{self.lm.tr('unit', 'Birim')}: {unit}
{self.lm.tr('methodology', 'Metodoloji')}: {methodology}
{self.lm.tr('requirement', 'Gereklilik')}: {requirement}
{self.lm.tr('priority', 'Öncelik')}: {priority}
{self.lm.tr('data_quality', 'Veri Kalitesi')}: {indicator.get('data_quality', '')}
{self.lm.tr('audit_required', 'Denetim Gereksinimi')}: {indicator.get('audit_required', '')}
{self.lm.tr('validation_required', 'Validasyon Gereksinimi')}: {indicator.get('validation_required', '')}
{self.lm.tr('digitalization_status', 'Dijitalleşme Durumu')}: {indicator.get('digitalization_status', '')}
{self.lm.tr('cost_level', 'Maliyet Seviyesi')}: {indicator.get('cost_level', '')}
{self.lm.tr('time_requirement', 'Zaman Gereksinimi')}: {indicator.get('time_requirement', '')}
{self.lm.tr('expertise_requirement', 'Uzmanlık Gereksinimi')}: {indicator.get('expertise_requirement', '')}
{self.lm.tr('risk_level', 'Risk Seviyesi')}: {indicator.get('risk_level', '')}
{self.lm.tr('sustainability_impact', 'Sürdürülebilirlik Etkisi')}: {indicator.get('sustainability_impact', '')}
{self.lm.tr('legal_compliance', 'Yasal Uyumluluk')}: {indicator.get('legal_compliance', '')}
        """

        detail_label = tk.Label(detail_window, text=detail_text,
                               font=('Segoe UI', 10), fg='#2c3e50', bg='white',
                               justify='left', wraplength=550)
        detail_label.pack(pady=20, padx=20)

    def respond_to_indicator(self, indicator) -> None:
        """Göstergeye yanıt ver"""
        # Yanıt penceresi oluştur (basit versiyon)
        response_window = tk.Toplevel(self.parent)
        response_window.title(f"GRI {indicator.get('indicator_code', '')} {self.lm.tr('response', 'Yanıtı')}")
        response_window.geometry("500x400")
        response_window.configure(bg='white')

        # Yanıt formu
        tk.Label(response_window, text=f"GRI {indicator.get('indicator_code', '')} - {indicator.get('indicator_title', '')}",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Yanıt metni
        tk.Label(response_window, text=f"{self.lm.tr('response', 'Yanıt')}:", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20)

        response_text = tk.Text(response_window, height=10, width=50, font=('Segoe UI', 10))
        response_text.pack(pady=5, padx=20, fill='both', expand=True)

        # Kaydet butonu
        ttk.Button(response_window, text=self.lm.tr('btn_save', "Kaydet"), style='Primary.TButton',
                   command=lambda: self.save_indicator_response(indicator, response_text.get('1.0', tk.END))).pack(pady=10)

    def save_indicator_response(self, indicator, response) -> None:
        """Gösterge yanıtını kaydet"""
        try:
            # Yanıtı veritabanına kaydet
            indicator_code = indicator.get('indicator_code', '') or indicator.get('code', '')
            indicator_id = indicator.get('id', '')

            if not indicator_code:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('indicator_code_not_found', "Gösterge kodu bulunamadı!"))
                return

            # GRI manager ile yanıtı kaydet
            success = self.gri_manager.save_indicator_response(
                indicator_code=indicator_code,
                response_text=response.strip(),
                indicator_id=indicator_id,
                company_id=self.company_id
            )

            if success:
                logging.info(f"Yanıt kaydedildi - {indicator_code}: {response}")
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('gri_response_saved', "GRI {code} gösterge yanıtı başarıyla kaydedildi!").format(code=indicator_code))
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('response_save_failed', "Yanıt kaydedilemedi!"))

        except Exception as e:
            logging.error(f"Yanıt kaydetme hatası: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('response_save_error', "Yanıt kaydedilemedi: {e}").format(e=e))

    def export_gri_indicators_csv(self) -> None:
        """Mevcut GRI göstergelerini CSV olarak dışa aktar"""
        try:
            # Dosya seçimi
            import csv
            from datetime import datetime
            from tkinter import filedialog, messagebox

            # Varsayılan dosya adı - tarih ile
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"gri_indikatorler_{timestamp}.csv"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[(self.lm.tr('csv_file', "CSV Dosyası"), "*.csv")],
                initialfile=default_name,
                title=self.lm.tr('export_gri_indicators', "GRI Göstergelerini dışa aktar")
            )
            if not file_path:
                # GUI ortamında dosya seçimi iptal edilirse, varsayılan klasöre yaz
                export_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'data', 'exports')
                os.makedirs(export_dir, exist_ok=True)
                file_path = os.path.join(export_dir, default_name)

            # Tüm göstergeleri çek
            logging.info("GRI göstergeleri çekiliyor...")
            indicators = self.gri_manager.get_gri_indicators()
            logging.info(f"Toplam {len(indicators)} gösterge bulundu")

            if not indicators:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('no_gri_indicator_to_export', "Dışa aktarılacak GRI göstergesi bulunamadı!"))
                return

            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')  # Noktalı virgül ile ayır

                # Başlık satırı
                headers = [
                    self.lm.tr('col_standard_code', "Standart Kod"), 
                    self.lm.tr('col_standard_title', "Standart Başlık"), 
                    self.lm.tr('col_indicator_code', "Gösterge Kod"), 
                    self.lm.tr('col_indicator_title', "Gösterge Başlık"),
                    self.lm.tr('col_description', "Açıklama"), 
                    self.lm.tr('col_unit', "Birim"), 
                    self.lm.tr('col_methodology', "Metodoloji"), 
                    self.lm.tr('col_reporting_req', "Raporlama Gerekliliği"),
                    self.lm.tr('col_priority', "Öncelik"), 
                    self.lm.tr('col_req_level', "Gereklilik Seviyesi"), 
                    self.lm.tr('col_data_quality', "Veri Kalitesi"), 
                    self.lm.tr('col_audit_req', "Denetim Gereksinimi"),
                    self.lm.tr('col_validation_req', "Validasyon Gereksinimi"), 
                    self.lm.tr('col_digitalization', "Dijitalleşme Durumu"), 
                    self.lm.tr('col_cost_level', "Maliyet Seviyesi"),
                    self.lm.tr('col_time_req', "Zaman Gereksinimi"), 
                    self.lm.tr('col_expertise_req', "Uzmanlık Gereksinimi"), 
                    self.lm.tr('col_sustainability_impact', "Sürdürülebilirlik Etkisi"),
                    self.lm.tr('col_legal_compliance', "Yasal Uyumluluk"), 
                    self.lm.tr('col_sector_specific', "Sektör Spesifik"), 
                    self.lm.tr('col_international_std', "Uluslararası Standart"),
                    self.lm.tr('col_metric_type', "Metrik Tipi"), 
                    self.lm.tr('col_scale_unit', "Ölçek Birimi"), 
                    self.lm.tr('col_data_source', "Veri Kaynağı Sistemi"), 
                    self.lm.tr('col_reporting_fmt', "Raporlama Formatı")
                ]
                writer.writerow(headers)

                # Veri satırları
                for ind in indicators:
                    # Kodları metin olarak zorla (Excel'in tarih formatına çevirmemesi için)
                    standard_code = ind.get('standard_code', '')
                    if standard_code:
                        standard_code = f"'{standard_code}"

                    indicator_code = ind.get('code', '')
                    if indicator_code:
                        indicator_code = f"'{indicator_code}"

                    row = [
                        standard_code,  # Metin formatında standart kodu
                        ind.get('standard_title', ''),
                        indicator_code,  # Metin formatında gösterge kodu
                        ind.get('title', ''),
                        ind.get('description', ''),
                        ind.get('unit', ''),
                        ind.get('methodology', ''),
                        ind.get('reporting_requirement', ''),
                        ind.get('priority', ''),
                        ind.get('requirement_level', ''),
                        ind.get('data_quality', ''),
                        ind.get('audit_required', ''),
                        ind.get('validation_required', ''),
                        ind.get('digitalization_status', ''),
                        ind.get('cost_level', ''),
                        ind.get('time_requirement', ''),
                        ind.get('expertise_requirement', ''),
                        ind.get('sustainability_impact', ''),
                        ind.get('legal_compliance', ''),
                        ind.get('sector_specific', ''),
                        ind.get('international_standard', ''),
                        ind.get('metric_type', ''),
                        ind.get('scale_unit', ''),
                        ind.get('data_source_system', ''),
                        ind.get('reporting_format', '')
                    ]
                    writer.writerow(row)

            messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                f"{self.lm.tr('gri_export_success', 'GRI göstergeleri başarıyla dışa aktarıldı!')}\n\n"
                f"{self.lm.tr('file', 'Dosya')}: {file_path}\n"
                f"{self.lm.tr('total_indicators', 'Toplam gösterge')}: {len(indicators)}")
        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('csv_export_error', 'CSV dışa aktarımında hata')}: {e}")
            except Exception:
                logging.error(f"{self.lm.tr('csv_export_error_log', 'CSV dışa aktarımında hata')}: {e}")

    def load_category_standards(self, category_key) -> None:
        """Kategori standartlarını yükle ve göster"""
        try:
            # Veritabanından standartları al
            standards = self.gri_manager.get_standards_by_category(category_key)

            if not standards:
                # Veri yoksa bilgi göster
                no_data_label = tk.Label(self.content_area,
                                       text=self.lm.tr('gri_no_standards_in_category', "{category} kategorisinde henüz standart bulunmuyor.\n\nVeritabanına standartlar eklendikçe burada görünecektir.").format(category=category_key.title()),
                                       font=('Segoe UI', 11), fg='#7f8c8d', bg='white',
                                       justify='center')
                no_data_label.pack(pady=50)
                return

            # Standartları göster
            for i, standard in enumerate(standards):
                self.create_standard_card(standard, i)

        except Exception as e:
            error_label = tk.Label(self.content_area,
                                 text=self.lm.tr('gri_data_load_error', "Veri yüklenirken hata oluştu: {error}").format(error=str(e)),
                                 font=('Segoe UI', 11), fg='#e74c3c', bg='white',
                                 justify='center')
            error_label.pack(pady=50)

    def create_standard_card(self, standard, index) -> None:
        """Standart kartı oluştur"""
        # Kart çerçevesi
        card_frame = tk.Frame(self.content_area, bg='#f8f9fa', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=20, pady=10)

        # Kart içeriği
        content_frame = tk.Frame(card_frame, bg='#f8f9fa')
        content_frame.pack(fill='x', padx=15, pady=15)

        # Başlık
        no_data = self.lm.tr('no_data', 'Veri Yok')
        title_label = tk.Label(content_frame, text=f"{standard.get('code', no_data)} - {standard.get('title', no_data)}",
                              font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                              anchor='w')
        title_label.pack(fill='x', pady=(0, 5))

        # Açıklama
        if standard.get('description_tr') or standard.get('description_en'):
            desc_text = standard.get('description_tr') or standard.get('description_en', '')
            desc_label = tk.Label(content_frame, text=desc_text,
                                 font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa',
                                 anchor='w', wraplength=500)
            desc_label.pack(fill='x', pady=(0, 10))

        # Alt bilgi
        info_frame = tk.Frame(content_frame, bg='#f8f9fa')
        info_frame.pack(fill='x')

        # Kategori
        category_label = tk.Label(info_frame, text=f"Kategori: {standard.get('category', 'Veri Yok')}",
                                 font=('Segoe UI', 9), fg='#95a5a6', bg='#f8f9fa')
        category_label.pack(side='left')

        # Tip
        type_label = tk.Label(info_frame, text=self.lm.tr('type_label', "Tip: {type}").format(type=standard.get('type', no_data)),
                             font=('Segoe UI', 9), fg='#95a5a6', bg='#f8f9fa')
        type_label.pack(side='right')

    def create_stats_frame(self, parent) -> None:
        """İstatistik kartlarını oluştur"""
        stats_frame = tk.Frame(parent, bg='#f5f5f5')
        stats_frame.pack(fill='x', pady=(0, 10))

        # İstatistik kartları
        self.stats_cards = {}

        stats_data = [
            (self.lm.tr('total_standards', "Toplam Standart"), "total_standards", "#3498db"),
            (self.lm.tr('total_indicators', "Toplam Gösterge"), "total_indicators", "#2ecc71"),
            (self.lm.tr('answered_indicators', "Cevaplanan Gösterge"), "answered_indicators", "#f39c12"),
            (self.lm.tr('completion_percentage', "Tamamlanma %"), "answer_percentage", "#e74c3c")
        ]

        for i, (title, key, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='x', expand=True, padx=(0 if i == 0 else 5, 0))

            title_label = tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                                 fg='white', bg=color)
            title_label.pack(pady=(10, 5))

            value_label = tk.Label(card, text="0", font=('Segoe UI', 16, 'bold'),
                                 fg='white', bg=color)
            value_label.pack(pady=(0, 10))

            self.stats_cards[key] = value_label

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            if self.sdg_filter_active:
                # SDG seçimlerine göre filtreli görünüm
                self.show_sdg_filtered_view()
            else:
                # Varsayılan kategori bazlı görünüm
                self.show_default_view()
        except Exception as e:
            logging.error(f"GRI verileri yüklenirken hata: {e}")
            # Varsayılan istatistikler
            default_stats = {
                'total_standards': 0,
                'total_indicators': 0,
                'answered_indicators': 0,
                'answer_percentage': 0.0
            }
            self.update_stats(default_stats)

    def toggle_sdg_filter(self) -> None:
        """SDG filtresini aç/kapat"""
        self.sdg_filter_active = not self.sdg_filter_active

        if self.sdg_filter_active:
            self.filter_btn.config(text=self.lm.tr('gri_filter_all', "Tüm GRI Standartları"), bg='#95a5a6')
        else:
            self.filter_btn.config(text=self.lm.tr('gri_filter_sdg', "SDG Seçimine Göre Filtrele"), bg='#e67e22')

        self.load_data()

    def show_default_view(self) -> None:
        """Varsayılan kategori bazlı görünümü göster"""
        # İçerik alanını temizle
        try:
            for widget in self.content_area.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Content area'yı yeniden oluştur
        self.setup_content_area(self.content_area)

        # Varsayılan GRI istatistikleri
        stats = self.gri_manager.get_gri_statistics(self.company_id)
        self.update_stats(stats)

        # Varsayılan kategori olarak Universal'i göster
        self.current_category = "universal"
        category_data = self.get_filtered_data("universal")
        self.display_category_data("universal", category_data)

    def show_sdg_filtered_view(self) -> None:
        """SDG seçimlerine göre filtreli görünümü göster"""
        try:
            # SDG seçimlerine göre GRI standartlarını al
            standards_by_category = self.gri_manager.get_gri_standards_for_sdg_selection(self.company_id)

            if not standards_by_category:
                # İçerik alanını temizle
                for widget in self.content_area.winfo_children():
                    widget.destroy()

                # Content area'yı yeniden oluştur
                self.setup_content_area(self.content_area)

                no_data_label = tk.Label(self.scrollable_frame,
                                       text=self.lm.tr('gri_no_sdg_mapping', "Seçilen SDG hedeflerine göre GRI eşleştirmesi bulunamadı.\nLütfen önce SDG modülünden hedef seçimi yapın."),
                                       font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
                no_data_label.pack(expand=True)
                return

            # İçerik alanını temizle
            for widget in self.content_area.winfo_children():
                widget.destroy()

            # Başlık
            title_label = tk.Label(self.content_area,
                                 text=self.lm.tr('gri_sdg_filtered_title', "SDG Seçimlerine Göre GRI Standartları"),
                                 font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
            title_label.pack(pady=(0, 20))

            # Scrollable frame
            canvas = tk.Canvas(self.content_area, bg='white')
            scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Her kategori için standartları göster
            for category, standards in standards_by_category.items():
                self.create_category_section(scrollable_frame, category, standards)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            logging.error(f"SDG filtrelenmiş görünüm gösterilirken hata: {e}")

    def create_category_buttons(self, parent=None) -> None:
        """İçerik alanında kategori butonları şeridi oluştur"""
        # Canvas içine doğrudan pack yapılmaması için scrollable_frame'i kullan
        if parent is None:
            parent = self.scrollable_frame
        try:
            # Ana frame oluştur
            main_frame = tk.Frame(parent, bg='#f8f9fa')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Başlık (sadece içerik alanında göster)
            if parent == self.content_area:
                title = tk.Label(main_frame, text=self.lm.tr('gri_categories_title', "GRI Kategorileri"), font=('Segoe UI', 16, 'bold'),
                                 fg='#2c3e50', bg='white')
                title.pack(pady=(0, 20))

            # Kategori butonları verisi
            categories = [
                ("", "Universal Standards", "universal", "#3498db"),
                ("", "Economic Standards", "economic", "#f39c12"),
                ("", "Environmental Standards", "environmental", "#27ae60"),
                ("", "Social Standards", "social", "#e74c3c"),
                ("", "Sector-Specific Standards", "sector", "#9b59b6")
            ]

            # Butonları oluştur
            for icon, name, key, color in categories:
                btn = ttk.Button(main_frame, text=f"{icon}  {name}",
                                  style='Primary.TButton',
                                  command=lambda k=key: self._navigate_to(self.show_category, k))
                btn.pack(fill='x', pady=8)

                # Sol panelde oluşturuluyorsa butonları haritaya ekle
                if parent != self.scrollable_frame:
                    self.category_buttons[key] = btn

            # Bilgi notu
            info = tk.Label(main_frame,
                            text=self.lm.tr('gri_category_info', "Yukarıdaki butonlardan bir kategori seçerek GRI standartlarını görüntüleyebilirsiniz."),
                            font=('Segoe UI', 10), fg='#7f8c8d', bg='white', wraplength=600, justify='center')
            info.pack(pady=(20, 0))

        except Exception as e:
            error_label = tk.Label(self.scrollable_frame, text=f"Kategori butonları oluşturulamadı: {e}",
                                   font=('Segoe UI', 11), fg='#e74c3c', bg='white')
            error_label.pack(pady=40)

    def create_category_section(self, parent, category, standards) -> None:
        """Kategori bölümü oluştur"""
        # Kategori başlığı
        category_frame = tk.Frame(parent, bg='#ecf0f1', relief='solid', bd=1)
        category_frame.pack(fill='x', padx=10, pady=5)

        category_label = tk.Label(category_frame, text=category.title(),
                                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        category_label.pack(pady=10)

        # Standartlar
        for standard in standards:
            self.create_standard_card_view(parent, standard)

    def create_standard_card_view(self, parent, standard) -> None:
        """GRI standart kartı oluştur"""
        # Standart kartı
        card_frame = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=20, pady=5)

        # Standart başlığı
        header_frame = tk.Frame(card_frame, bg='#3498db', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=f"{standard['code']}: {standard['title']}",
                             font=('Segoe UI', 11, 'bold'), fg='white', bg='#3498db')
        title_label.pack(expand=True)

        # Göstergeler
        indicators_frame = tk.Frame(card_frame, bg='#f8f9fa')
        indicators_frame.pack(fill='x', padx=10, pady=10)

        for indicator in standard['indicators']:
            self.create_indicator_item(indicators_frame, indicator)

    def create_indicator_item(self, parent, indicator) -> None:
        """GRI gösterge öğesi oluştur"""
        # Gösterge çerçevesi
        indicator_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        indicator_frame.pack(fill='x', pady=2)

        # Gösterge başlığı
        title_frame = tk.Frame(indicator_frame, bg='#e8f5e8')
        title_frame.pack(fill='x')

        title_label = tk.Label(title_frame, text=f"{indicator['code']}: {indicator['title']}",
                             font=('Segoe UI', 10, 'bold'), fg='#27ae60', bg='#e8f5e8')
        title_label.pack(anchor='w', padx=10, pady=5)

        # Açıklama
        if indicator['description']:
            desc_label = tk.Label(indicator_frame, text=indicator['description'],
                                font=('Segoe UI', 9), fg='#2c3e50', bg='white', wraplength=800)
            desc_label.pack(anchor='w', padx=10, pady=(0, 5))

        # Eşleştirmeler
        mappings_frame = tk.Frame(indicator_frame, bg='#fff3cd')
        mappings_frame.pack(fill='x', padx=10, pady=(0, 5))

        # SDG eşleştirmeleri
        if indicator['mapped_sdg_indicators']:
            sdg_label = tk.Label(mappings_frame, text=self.lm.tr('gri_sdg_mappings', "SDG Eşleştirmeleri:"),
                               font=('Segoe UI', 9, 'bold'), fg='#856404', bg='#fff3cd')
            sdg_label.pack(anchor='w', padx=5, pady=2)

            sdg_text = ", ".join(indicator['mapped_sdg_indicators'])
            sdg_value_label = tk.Label(mappings_frame, text=sdg_text,
                                     font=('Segoe UI', 9), fg='#2c3e50', bg='#fff3cd')
            sdg_value_label.pack(anchor='w', padx=20, pady=(0, 2))

        # TSRS eşleştirmeleri
        if indicator['mapped_tsrs']:
            tsrs_label = tk.Label(mappings_frame, text=self.lm.tr('gri_tsrs_mappings', "TSRS Eşleştirmeleri:"),
                                font=('Segoe UI', 9, 'bold'), fg='#856404', bg='#fff3cd')
            tsrs_label.pack(anchor='w', padx=5, pady=2)

            for tsrs in indicator['mapped_tsrs']:
                tsrs_text = f"{tsrs['section']} / {tsrs['metric']}"
                tsrs_value_label = tk.Label(mappings_frame, text=tsrs_text,
                                          font=('Segoe UI', 9), fg='#2c3e50', bg='#fff3cd')
                tsrs_value_label.pack(anchor='w', padx=20, pady=(0, 2))

    def update_stats(self, stats) -> None:
        """İstatistikleri güncelle"""
        self.stats_cards['total_standards'].config(text=str(stats['total_standards']))
        self.stats_cards['total_indicators'].config(text=str(stats['total_indicators']))
        self.stats_cards['answered_indicators'].config(text=str(stats['answered_indicators']))
        self.stats_cards['answer_percentage'].config(text=f"{stats['answer_percentage']:.1f}%")

    def load_standards(self) -> None:
        """GRI standartlarını yükle - Yeni tasarım için güncellendi"""
        # Bu metod artık kullanılmıyor, show_category kullanılıyor
        pass

    def filter_standards(self, event=None) -> None:
        """Standartları filtrele - Yeni tasarım için güncellendi"""
        # Bu metod artık kullanılmıyor, show_category kullanılıyor
        pass

    def on_standard_select(self, event) -> None:
        """Standart seçildiğinde - Yeni tasarım için güncellendi"""
        # Bu metod artık kullanılmıyor, show_category kullanılıyor
        pass

    def show_standard_details(self, standard_text) -> None:
        """Standart detaylarını göster"""
        # Mevcut detayları temizle
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Standart bilgilerini al
        standards = self.gri_manager.get_gri_standards()
        selected_standard = None
        for standard in standards:
            if f"{standard['code']}: {standard['title']}" == standard_text:
                selected_standard = standard
                break

        if not selected_standard:
            return

        # Standart başlığı
        title_label = tk.Label(self.detail_frame, text=selected_standard['code'],
                              font=('Segoe UI', 14, 'bold'), bg='white', fg='#27ae60')
        title_label.pack(pady=(0, 5))

        # Standart açıklaması
        desc_label = tk.Label(self.detail_frame, text=selected_standard['title'],
                             font=('Segoe UI', 12), bg='white', fg='#2c3e50')
        desc_label.pack(pady=(0, 10))

        # Kategori
        category_label = tk.Label(self.detail_frame, text=f"Kategori: {selected_standard['category']}",
                                 font=('Segoe UI', 10), bg='white', fg='#7f8c8d')
        category_label.pack(pady=(0, 10))

        # Göstergeleri göster
        self.show_indicators_for_standard(selected_standard['id'])

    def show_indicators_for_standard(self, standard_id) -> None:
        """Belirli standart için göstergeleri göster"""
        indicators = self.gri_manager.get_gri_indicators(standard_id)

        # Scrollable frame
        canvas = tk.Canvas(self.detail_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.detail_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for indicator in indicators:
            self.create_indicator_card_v2(scrollable_frame, indicator)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_indicator_card_v2(self, parent, indicator) -> None:
        """Gösterge kartı oluştur (iki veri şemasıyla uyumlu)"""
        # Şema uyumluluğu: code/indicator_code, title/indicator_title vb.
        code = indicator.get('code') or indicator.get('indicator_code') or ''
        title = indicator.get('title') or indicator.get('indicator_title') or ''
        description = indicator.get('description') or indicator.get('indicator_description') or ''
        unit = indicator.get('unit') or indicator.get('unit_name') or ''
        methodology = indicator.get('methodology') or indicator.get('methodology_detail') or ''
        requirement = indicator.get('reporting_requirement') or indicator.get('requirement') or ''

        card_frame = tk.Frame(parent, bg='#f8f9fa', relief='raised', bd=1)
        card_frame.pack(fill='x', pady=2, padx=5)

        # Gösterge başlığı
        title_frame = tk.Frame(card_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', padx=10, pady=5)

        title_label = tk.Label(title_frame, text=f"{code}: {title}",
                              font=('Segoe UI', 10, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title_label.pack(side='left')

        # Aksiyon butonları
        detail_btn = tk.Button(title_frame, text=self.lm.tr('btn_detail', "Detay"), font=('Segoe UI', 9),
                               bg='#3498db', fg='white', relief='flat', bd=0,
                               command=lambda: self.show_indicator_detail(indicator))
        detail_btn.pack(side='right', padx=(0, 5))

        response_btn = tk.Button(title_frame, text=self.lm.tr('btn_answer', "Cevap Ver"), font=('Segoe UI', 9),
                                 bg='#27ae60', fg='white', relief='flat', bd=0,
                                 command=lambda: self.show_response_form(indicator))
        response_btn.pack(side='right')

        # Gösterge detayları
        details_text = f"Açıklama: {description}\n"
        details_text += f"Birim: {unit or 'Belirtilmemiş'}\n"
        details_text += f"Metodoloji: {methodology or 'Genel'}\n"
        details_text += f"Raporlama: {requirement}\n"

        # Eşleştirme bilgileri (SDG↔GRI ve GRI↔TSRS)
        try:
            maps = self.gri_manager.get_mappings_for_gri_indicator(code)
            sdg_links = maps.get('sdg_gri', [])
            tsrs_links = maps.get('gri_tsrs', [])
            if sdg_links:
                sdg_codes = ", ".join(sorted({m['sdg_indicator_code'] for m in sdg_links}))
                details_text += f"\nSDG eşleşmeleri: {sdg_codes}"
            if tsrs_links:
                tsrs_metrics = ", ".join(sorted({m['tsrs_section'] + ':' + m['tsrs_metric'] for m in tsrs_links}))
                details_text += f"\nTSRS eşleşmeleri: {tsrs_metrics}"
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        details_label = tk.Label(card_frame, text=details_text, font=('Segoe UI', 9),
                               bg='#f8f9fa', fg='#7f8c8d', justify='left')
        details_label.pack(anchor='w', padx=10, pady=(0, 5))

    def show_response_form(self, indicator) -> None:
        """Cevap formunu göster"""
        # Cevap formu penceresi
        response_window = tk.Toplevel(self.parent)
        code = indicator.get('code') or indicator.get('indicator_code') or ''
        title = indicator.get('title') or indicator.get('indicator_title') or ''
        response_window.title(f"GRI Cevap Ver - {code}")
        response_window.state('zoomed')  # Tam ekran
        response_window.configure(bg='#f5f5f5')

        # Başlık
        title_frame = tk.Frame(response_window, bg='#27ae60', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=f"GRI Gösterge: {code} - {title}",
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#27ae60')
        title_label.pack(expand=True)

        # Form içeriği
        form_frame = tk.Frame(response_window, bg='#f5f5f5')
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Dönem seçimi
        period_frame = tk.Frame(form_frame, bg='#f5f5f5')
        period_frame.pack(fill='x', pady=(0, 20))

        tk.Label(period_frame, text=self.lm.tr('label_period', "Dönem:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(side='left')

        period_var = tk.StringVar(value=datetime.now().year)
        period_entry = tk.Entry(period_frame, textvariable=period_var, font=('Segoe UI', 12))
        period_entry.pack(side='left', padx=(10, 0))

        # Cevap metni
        response_frame = tk.Frame(form_frame, bg='#f5f5f5')
        response_frame.pack(fill='x', pady=10)

        tk.Label(response_frame, text=self.lm.tr('label_answer', "Cevap:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w')

        response_text = tk.Text(response_frame, height=4, font=('Segoe UI', 11))
        response_text.pack(fill='x', pady=(5, 0))

        # Sayısal değer
        value_frame = tk.Frame(form_frame, bg='#f5f5f5')
        value_frame.pack(fill='x', pady=10)

        tk.Label(value_frame, text=self.lm.tr('label_numeric_value', "Sayısal Değer:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(side='left')

        value_var = tk.StringVar()
        value_entry = tk.Entry(value_frame, textvariable=value_var, font=('Segoe UI', 12))
        value_entry.pack(side='left', padx=(10, 0))

        unit = indicator.get('unit') or indicator.get('unit_name') or ''
        if unit:
            tk.Label(value_frame, text=f"({unit})", font=('Segoe UI', 10),
                    bg='#f5f5f5', fg='#7f8c8d').pack(side='left', padx=(5, 0))

        # Metodoloji
        methodology_frame = tk.Frame(form_frame, bg='#f5f5f5')
        methodology_frame.pack(fill='x', pady=10)

        tk.Label(methodology_frame, text=self.lm.tr('label_methodology', "Metodoloji:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w')

        methodology_text = tk.Text(methodology_frame, height=2, font=('Segoe UI', 11))
        methodology_text.pack(fill='x', pady=(5, 0))

        # Kanıt URL
        evidence_frame = tk.Frame(form_frame, bg='#f5f5f5')
        evidence_frame.pack(fill='x', pady=10)

        tk.Label(evidence_frame, text=self.lm.tr('label_evidence_url', "Kanıt URL:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w')

        evidence_var = tk.StringVar()
        evidence_entry = tk.Entry(evidence_frame, textvariable=evidence_var, font=('Segoe UI', 11))
        evidence_entry.pack(fill='x', pady=(5, 0))

        # Notlar
        notes_frame = tk.Frame(form_frame, bg='#f5f5f5')
        notes_frame.pack(fill='both', expand=True, pady=10)

        tk.Label(notes_frame, text=self.lm.tr('label_notes', "Notlar:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w')

        notes_text = tk.Text(notes_frame, height=3, font=('Segoe UI', 11))
        notes_text.pack(fill='both', expand=True, pady=(5, 0))

        # Butonlar
        button_frame = tk.Frame(response_window, bg='#f5f5f5')
        button_frame.pack(fill='x', padx=20, pady=10)

        save_btn = tk.Button(button_frame, text=self.lm.tr('btn_save', "Kaydet"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=lambda: self.save_response(indicator, period_var.get(),
                                                           response_text.get("1.0", tk.END).strip(),
                                                           value_var.get(), methodology_text.get("1.0", tk.END).strip(),
                                                           evidence_var.get(), notes_text.get("1.0", tk.END).strip(),
                                                           response_window))
        save_btn.pack(side='right')

        cancel_btn = tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), font=('Segoe UI', 12),
                             bg='#95a5a6', fg='white', relief='flat', bd=0,
                             command=response_window.destroy)
        cancel_btn.pack(side='right', padx=(0, 10))

    def save_response(self, indicator, period, response_value, numerical_value,
                     methodology, evidence_url, notes, window):
        """Cevabı kaydet"""
        try:
            numerical_val = float(numerical_value) if numerical_value else None
        except ValueError:
            numerical_val = None

        success = self.gri_manager.save_gri_response(
            self.company_id, indicator['id'], period, response_value, numerical_val,
            indicator['unit'], methodology, evidence_url, notes
        )

        if success:
            messagebox.showinfo(self.lm.tr('msg_success', "Başarılı"), self.lm.tr('msg_gri_saved', "GRI cevabı kaydedildi"))
            window.destroy()
            # İstatistikleri güncelle
            stats = self.gri_manager.get_gri_statistics(self.company_id)
            self.update_stats(stats)
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('gri_response_save_error', "GRI cevabı kaydedilemedi"))

    def get_selected_sdg_goals(self) -> None:
        """Seçilen SDG hedeflerini getir"""
        try:
            from sdg.sdg_manager import SDGManager
            sdg_manager = SDGManager()
            return sdg_manager.get_selected_goals(self.company_id)
        except Exception as e:
            logging.error(f"Seçilen SDG hedefleri getirilirken hata: {e}")
            return []

    def show_sdg_gri_mapping(self, selected_goal_ids) -> None:
        """Seçilen SDG hedeflerine göre GRI eşleştirmelerini göster"""
        try:
            # Eşleştirme verilerini al
            mapping_data = self.mapping.get_gri_mapping_for_goals(selected_goal_ids)

            # İçerik alanını temizle
            for widget in self.content_area.winfo_children():
                widget.destroy()

            # Başlık
            title_label = tk.Label(self.content_area,
                                 text=self.lm.tr('sdg_gri_mapping_title', "Seçilen SDG Hedeflerine Göre GRI Eşleştirmeleri"),
                                 font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa')
            title_label.pack(pady=(0, 20))

            # Scrollable frame
            canvas = tk.Canvas(self.content_area, bg='#f8f9fa')
            scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Her SDG hedefi için GRI eşleştirmelerini göster
            for sdg_no, data in mapping_data.items():
                self.create_sdg_gri_section(scrollable_frame, sdg_no, data)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            logging.error(f"GRI eşleştirmeleri gösterilirken hata: {e}")

    def create_sdg_gri_section(self, parent, sdg_no, data) -> None:
        """SDG hedefi için GRI bölümü oluştur"""
        # SDG hedefi başlığı
        sdg_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        sdg_frame.pack(fill='x', padx=10, pady=5)

        # SDG başlığı
        title_frame = tk.Frame(sdg_frame, bg='#3498db', height=40)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=f"SDG {sdg_no}: {data['sdg_title']}",
                             font=('Segoe UI', 12, 'bold'), fg='white', bg='#3498db')
        title_label.pack(expand=True)

        # GRI standartları
        if data['gri_standards']:
            gri_frame = tk.Frame(sdg_frame, bg='#e8f5e8')
            gri_frame.pack(fill='x', padx=10, pady=5)

            gri_label = tk.Label(gri_frame, text=self.lm.tr('gri_standards', "GRI Standartları:"),
                               font=('Segoe UI', 10, 'bold'), fg='#27ae60', bg='#e8f5e8')
            gri_label.pack(anchor='w')

            for gri_standard in data['gri_standards']:
                gri_item = tk.Label(gri_frame, text=f"• {gri_standard}",
                                  font=('Segoe UI', 9), fg='#2c3e50', bg='#e8f5e8')
                gri_item.pack(anchor='w', padx=20)

        # TSRS standartları
        if data['tsrs_standards']:
            tsrs_frame = tk.Frame(sdg_frame, bg='#fff3cd')
            tsrs_frame.pack(fill='x', padx=10, pady=5)

            tsrs_label = tk.Label(tsrs_frame, text=self.lm.tr('tsrs_standards', "TSRS Standartları:"),
                                font=('Segoe UI', 10, 'bold'), fg='#856404', bg='#fff3cd')
            tsrs_label.pack(anchor='w')

            for tsrs_standard in data['tsrs_standards']:
                tsrs_item = tk.Label(tsrs_frame, text=f"• {tsrs_standard}",
                                   font=('Segoe UI', 9), fg='#2c3e50', bg='#fff3cd')
                tsrs_item.pack(anchor='w', padx=20)

        # Göstergeler
        indicators_frame = tk.Frame(sdg_frame, bg='#f8f9fa')
        indicators_frame.pack(fill='x', padx=10, pady=5)

        indicators_label = tk.Label(indicators_frame, text=f"Göstergeler ({len(data['indicators'])} adet):",
                                  font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        indicators_label.pack(anchor='w')

        for indicator in data['indicators']:
            indicator_text = f"• {indicator['indicator_code']}: {indicator['indicator_title']}"
            indicator_label = tk.Label(indicators_frame, text=indicator_text,
                                     font=('Segoe UI', 9), fg='#6c757d', bg='#f8f9fa', wraplength=800)
            indicator_label.pack(anchor='w', padx=20)

    # create_category_buttons çift tanımı kaldırıldı; tek tanım yukarıda (parent=None)

    def on_search_focus_in(self, event) -> None:
        """Arama kutusu odaklandığında"""
        if self.search_var.get() == "Kod veya başlık ara...":
            self.search_var.set("")

    def on_search_focus_out(self, event) -> None:
        """Arama kutusu odak kaybettiğinde"""
        if not self.search_var.get():
            self.search_var.set(self.lm.tr('search_placeholder', "Kod veya başlık ara..."))

    def on_search_change(self, *args) -> None:
        """Arama değiştiğinde"""
        if hasattr(self, 'current_category'):
            self.apply_filters()

    def on_filter_change(self, event=None) -> None:
        """Filtre değiştiğinde"""
        # Eğer kategori seçiliyse filtreleri uygula
        if hasattr(self, 'current_category') and self.current_category:
            self.apply_filters()
        else:
            # Hoş geldin sayfasındaysa varsayılan görünümü göster
            self.show_welcome_content()

    def clear_filters(self) -> None:
        """Filtreleri temizle"""
        self.search_var.set(self.lm.tr('search_placeholder', "Kod veya başlık ara..."))
        self.priority_var.set(self.lm.tr('priority_all', 'Tümü'))
        self.requirement_var.set(self.lm.tr('req_all', 'Tümü'))
        if hasattr(self, 'current_category'):
            self.apply_filters()

    def apply_filters(self) -> None:
        """Filtreleri uygula"""
        if not hasattr(self, 'current_category'):
            return

        search_term = self.search_var.get()
        if search_term == self.lm.tr('search_placeholder', "Kod veya başlık ara..."):
            search_term = ""

        priority_filter = self.priority_var.get()
        requirement_filter = self.requirement_var.get()

        # Mevcut verileri filtrele
        filtered_data = self.get_filtered_data(self.current_category, search_term, priority_filter, requirement_filter)

        # UI'yi güncelle
        self.display_category_data(self.current_category, filtered_data)
        try:
            logging.info(f"Filtre uygulandı: arama='{search_term}', öncelik='{priority_filter}', gereklilik='{requirement_filter}', sonuç={len(filtered_data.get('indicators', []))}")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def get_filtered_data(self, category, search_term="", priority_filter="Tümü", requirement_filter="Tümü") -> None:
        """Filtrelenmiş veriyi getir"""
        try:
            # Kategori verilerini al
            if category == "universal":
                data = self.gri_manager.get_standards_by_category("Universal")
            elif category == "economic":
                data = self.gri_manager.get_standards_by_category("Economic")
            elif category == "environmental":
                data = self.gri_manager.get_standards_by_category("Environmental")
            elif category == "social":
                data = self.gri_manager.get_standards_by_category("Social")
            elif category == "sector":
                data = self.gri_manager.get_standards_by_category("Sector-Specific")
            else:
                data = {'standards': [], 'indicators': []}

            # Arama filtresi uygula
            if search_term:
                filtered_indicators = []
                for indicator in data.get('indicators', []):
                    if (search_term.lower() in indicator.get('indicator_code', '').lower() or
                        search_term.lower() in indicator.get('indicator_title', '').lower()):
                        filtered_indicators.append(indicator)
                data['indicators'] = filtered_indicators

            # Öncelik filtresi uygula (Çoklu dil desteği ile)
            if priority_filter != self.lm.tr('priority_all', 'Tümü'):
                # Seçilen yerel dil değerini İngilizce/DB değerine çevir
                pf_en = priority_filter # Varsayılan
                if priority_filter == self.lm.tr('priority_critical', 'Kritik'): pf_en = 'Critical'
                elif priority_filter == self.lm.tr('priority_high', 'Yüksek'): pf_en = 'High'
                elif priority_filter == self.lm.tr('priority_medium', 'Orta'): pf_en = 'Medium'
                elif priority_filter == self.lm.tr('priority_low', 'Düşük'): pf_en = 'Low'
                
                # Ayrıca eski statik haritalamayı da koru (yedek olarak)
                priority_map = {'Kritik': 'Critical', 'Yüksek': 'High', 'Orta': 'Medium', 'Düşük': 'Low'}
                pf_alt = priority_map.get(priority_filter, priority_filter)
                
                filtered_indicators = []
                for indicator in data.get('indicators', []):
                    text = str(indicator.get('priority') or '').lower()
                    if pf_en.lower() in text or pf_alt.lower() in text or priority_filter.lower() in text:
                        filtered_indicators.append(indicator)
                data['indicators'] = filtered_indicators

            # Gereklilik filtresi uygula (Çoklu dil desteği ile)
            if requirement_filter != self.lm.tr('req_all', 'Tümü'):
                # Seçilen yerel dil değerini İngilizce/DB değerine çevir
                rf_en = requirement_filter # Varsayılan
                if requirement_filter == self.lm.tr('req_mandatory', 'Zorunlu'): rf_en = 'Mandatory'
                elif requirement_filter == self.lm.tr('req_recommended', 'Önerilen'): rf_en = 'Recommended'
                elif requirement_filter == self.lm.tr('req_optional', 'İsteğe Bağlı'): rf_en = 'Optional'
                
                # Eski statik haritalama
                requirement_map = {'Zorunlu': 'Mandatory', 'Önerilen': 'Recommended', 'İsteğe Bağlı': 'Optional'}
                rf_alt = requirement_map.get(requirement_filter, requirement_filter)
                
                filtered_indicators = []
                for indicator in data.get('indicators', []):
                    text = str(indicator.get('reporting_requirement') or '').lower()
                    if rf_en.lower() in text or rf_alt.lower() in text or requirement_filter.lower() in text:
                        filtered_indicators.append(indicator)
                data['indicators'] = filtered_indicators

            return data

        except Exception as e:
            logging.error(f"Filtreleme hatası: {e}")
            return {'standards': [], 'indicators': []}

    # go_to_dashboard fonksiyonu kaldırıldı
