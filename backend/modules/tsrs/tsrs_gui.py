import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS (Türkiye Sürdürülebilirlik Raporlama Standardı) GUI
TSRS standartları, göstergeleri ve raporlama arayüzü
"""

import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable, Optional

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme
from config.icons import Icons

try:
    from utils.progress_engine import STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED
    from utils.progress_engine import ProgressEngine as _ProgressEngine
    ProgressEngineCls: Optional[type] = _ProgressEngine
except Exception:
    ProgressEngineCls = None
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
try:
    from utils.tooltip import add_rich_tooltip as _add_rich_tooltip
    add_rich_tooltip: Optional[Callable[..., None]] = _add_rich_tooltip
except Exception:
    add_rich_tooltip = None

from .tsrs_esrs_forms import (
    ClimateRiskAssessmentWindow,
    DoubleMaterialityWindow,
    ESRSRequirementsWindow,
    EUTaxonomyWindow,
    ValueChainAnalysisWindow,
)
from .tsrs_integration_gui import TSRSIntegrationGUI
from .tsrs_manager import TSRSManager
from .tsrs_reporting_gui import TSRSReportingGUI
from config.icons import Icons


class TSRSGUI:
    """TSRS Modülü GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.tsrs_manager = TSRSManager()
        try:
            import os as _os
            # c:\SDG\modules\tsrs\tsrs_gui.py -> c:\SDG
            base_dir = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..', '..'))
            self.db_path: Optional[str] = _os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        except Exception:
            self.db_path = None
        self._pe = ProgressEngineCls(self.db_path) if ProgressEngineCls and self.db_path else None
        self._steps = [
            ('tsrs_start', self.lm.tr('step_start', 'Başlangıç')),
            ('tsrs_requirements', self.lm.tr('step_requirements', 'Gereklilikler')),
            ('tsrs_double_materiality', self.lm.tr('step_double_materiality', 'Çift Önemlilik')),
            ('tsrs_reporting', self.lm.tr('step_reporting', 'Raporlama')),
            ('tsrs_complete', self.lm.tr('step_complete', 'Tamamla'))
        ]

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()
        try:
            if self._pe:
                self._pe.initialize_steps(user_id=1, company_id=self.company_id, module_code='tsrs', steps=self._steps)
                self._pe.set_progress(1, self.company_id, 'tsrs', 'tsrs_start', 'Başlangıç', STATUS_IN_PROGRESS)
                self._update_guided_header()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def setup_ui(self) -> None:
        """TSRS modülü arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("tsrs_title", "TSRS - Türkiye Sürdürülebilirlik Raporlama Standardı"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr("btn_report_center", "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_tsrs).pack(side='left', padx=6)
        ttk.Button(toolbar, text=self.lm.tr("btn_refresh", "Yenile"), style='Primary.TButton', command=self.load_data).pack(side='left', padx=6)
        ttk.Label(toolbar, text=self.lm.tr("year_label", "Yıl:")).pack(side='left', padx=(10,0))
        self.period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        period_combo = ttk.Combobox(toolbar, textvariable=self.period_var, values=years, width=8, state='readonly')
        period_combo.pack(side='left', padx=6)
        def _validate_year(y: str) -> bool:
            try:
                y = (y or '').strip()
                return y.isdigit() and len(y) == 4 and 1990 <= int(y) <= 2100
            except Exception:
                return False
        def _on_period_change(*args):
            if not _validate_year(self.period_var.get()):
                # messagebox.showwarning("Uyarı", "Geçersiz yıl seçimi")
                return
            try:
                self.load_data()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        try:
            self.period_var.trace_add('write', _on_period_change)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        guided = tk.Frame(main_frame, bg='#f8fafc', height=50)
        guided.pack(fill='x', pady=(0, 10))
        guided.pack_propagate(False)
        self._guided_frame = guided
        try:
            self._progress_var = tk.DoubleVar(value=0.0)
            pb = ttk.Progressbar(guided, maximum=100.0, variable=self._progress_var)
            pb.pack(side='left', fill='x', expand=True, padx=10, pady=10)
            self._step_info = tk.Label(guided, text=f"{self.lm.tr('step_label', 'Adım')}: {self.lm.tr('step_start', 'Başlangıç')}", font=('Segoe UI', 10, 'bold'), bg='#f8fafc', fg='#334155')
            self._step_info.pack(side='left', padx=10)
            try:
                if add_rich_tooltip is not None:
                    add_rich_tooltip(self._step_info, "Bu adımda ne yapmalı?", "TSRS modülünde gereklilikleri, çift önemlilik analizi ve raporlamayı tamamlayın.")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
            def _next_step():
                try:
                    if not self._pe:
                        return
                    progress = self._pe.get_module_progress(self.company_id, 'tsrs', user_id=1)
                    order = [sid for sid, _ in self._steps]
                    current_sid = None
                    for p in progress:
                        if p['status'] == STATUS_IN_PROGRESS:
                            current_sid = p['step_id']
                            break
                    if current_sid is None:
                        current_sid = order[0]
                    idx = order.index(current_sid)
                    self._pe.set_progress(1, self.company_id, 'tsrs', current_sid,
                                          dict(self._steps)[current_sid], STATUS_COMPLETED)
                    if idx + 1 < len(order):
                        next_sid = order[idx + 1]
                        self._pe.set_progress(1, self.company_id, 'tsrs', next_sid,
                                              dict(self._steps)[next_sid], STATUS_IN_PROGRESS)
                    self._update_guided_header()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            ttk.Button(guided, text=self.lm.tr('next_step', 'Sonraki Adım'), style='Primary.TButton', command=_next_step).pack(side='right', padx=10)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # İstatistik kartları
        self.create_stats_frame(main_frame)
        self.create_quick_actions_frame(main_frame)

        # Ana içerik - Notebook (Sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Standartlar sekmesi
        self.standards_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.standards_frame, text=f" {self.lm.tr('tsrs_tab_standards', 'TSRS Standartları')}")

        # Raporlama sekmesi
        self.reporting_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.reporting_frame, text=f" {self.lm.tr('tsrs_tab_reporting', 'Raporlama')}")

        # Entegrasyon sekmesi
        self.integration_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.integration_frame, text=f" {self.lm.tr('tsrs_tab_integration', 'GRI-SDG Entegrasyon')}")

        # Standartlar sekmesi içeriği
        standards_content = tk.Frame(self.standards_frame, bg='#f5f5f5')
        standards_content.pack(fill='both', expand=True)

        # İki panel yan yana
        content_frame = tk.Frame(standards_content, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sol panel - TSRS Kategorileri
        left_panel = tk.Frame(content_frame, bg='#f8f9fa', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)

        # Kategori başlığı
        cat_title = tk.Label(left_panel, text=self.lm.tr("tsrs_categories", "TSRS Kategorileri"),
                           font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        cat_title.pack(pady=15)

        # Kategori butonları
        self.create_category_buttons(left_panel)

        # Sağ panel - İçerik
        right_panel = tk.Frame(content_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True)

        # İçerik başlığı
        self.content_title = tk.Label(right_panel, text=self.lm.tr("tsrs_welcome_title", "TSRS Standartlarına Hoş Geldiniz"),
                                    font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white')
        self.content_title.pack(pady=20)

        # İçerik alanı
        self.create_content_area(right_panel)

        # Raporlama sekmesi içeriği
        TSRSReportingGUI(self.reporting_frame, self.company_id)

        # Entegrasyon sekmesi içeriği
        TSRSIntegrationGUI(self.integration_frame, self.company_id)

        # Varsayılan hoş geldin içeriği
        self.show_welcome_content()

    def open_report_center_tsrs(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('tsrs')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for tsrs: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_center_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def _update_guided_header(self) -> None:
        try:
            if not self._pe:
                return
            percent = self._pe.get_completion_percentage(self.company_id, 'tsrs', self._steps, user_id=1)
            self._progress_var.set(percent)
            progress = self._pe.get_module_progress(self.company_id, 'tsrs', user_id=1)
            active = None
            for p in progress:
                if p['status'] == STATUS_IN_PROGRESS:
                    active = p
                    break
            step_text = f"{self.lm.tr('step_label', 'Adım')}: {active['step_title']}" if active else f"{self.lm.tr('step_label', 'Adım')}: -"
            self._step_info.configure(text=step_text)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def create_stats_frame(self, parent) -> None:
        """İstatistik kartlarını oluştur"""
        stats_frame = tk.Frame(parent, bg='#f5f5f5')
        stats_frame.pack(fill='x', pady=(0, 10))

        self.stats_labels = {}

        stats_data = [
            (self.lm.tr('tsrs_stats_total', "Toplam Standart"), "total_standards", "#3498db"),
            (self.lm.tr('tsrs_stats_indicators', "Toplam Gösterge"), "total_indicators", "#f39c12"),
            (self.lm.tr('tsrs_stats_answered', "Yanıtlanan Gösterge"), "answered_indicators", "#e74c3c"),
            (self.lm.tr('tsrs_stats_percent', "Yanıt Yüzdesi"), "response_percentage", "#2ecc71")
        ]

        for i, (title, key, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='x', expand=True, padx=(0, 5) if i < len(stats_data)-1 else 0)

            card_content = tk.Frame(card, bg=color)
            card_content.pack(fill='both', expand=True, padx=15, pady=10)

            title_label = tk.Label(card_content, text=title, font=('Segoe UI', 9, 'bold'),
                                  fg='white', bg=color)
            title_label.pack()

            value_label = tk.Label(card_content, text="0", font=('Segoe UI', 12, 'bold'),
                                  fg='white', bg=color)
            value_label.pack()

            self.stats_labels[key] = value_label

    def create_category_buttons(self, parent) -> None:
        """TSRS kategori butonlarını oluştur"""
        categories = [
            ("🏛️", self.lm.tr('tsrs_cat_governance', "Yönetişim"), "governance", "#3498db"),
            ("🎯", self.lm.tr('tsrs_cat_strategy', "Strateji"), "strategy", "#f39c12"),
            (Icons.WARNING, self.lm.tr('tsrs_cat_risk', "Risk Yönetimi"), "risk", "#e74c3c"),
            (Icons.REPORT, self.lm.tr('tsrs_cat_metrics', "Metrikler"), "metrics", "#2ecc71")
        ]

        from functools import partial
        for icon, name, key, color in categories:
            btn = tk.Button(parent, text=f"{icon}  {name}",
                           font=('Segoe UI', 12, 'bold'), fg='white', bg=color,
                           relief='flat', bd=0, cursor='hand2', padx=20, pady=12,
                           command=partial(self.show_category, key))
            btn.pack(fill='x', pady=8, padx=15)

    def create_quick_actions_frame(self, parent) -> None:
        """Eksik özellikler için hızlı aksiyon butonları"""
        qa = tk.Frame(parent, bg='#f5f5f5')
        qa.pack(fill='x', pady=(0, 10))

        tk.Label(qa, text=self.lm.tr('quick_actions', "Hızlı Aksiyonlar"), font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#f5f5f5').pack(anchor='w')

        buttons_frame = tk.Frame(qa, bg='#f5f5f5')
        buttons_frame.pack(fill='x', pady=6)

        def make_btn(text, color, cmd) -> tk.Button:
            b = tk.Button(buttons_frame, text=text, font=('Segoe UI', 10, 'bold'), fg='white', bg=color,
                          relief='flat', padx=12, pady=8, cursor='hand2', command=cmd)
            return b

        btns = [
            make_btn(self.lm.tr('btn_double_materiality', " Çift Önemlilik"), '#8e44ad', self.open_double_materiality),
            make_btn(self.lm.tr('btn_esrs_req', " ESRS Gereklilikleri"), '#34495e', self.open_esrs_requirements),
            make_btn(self.lm.tr('btn_eu_taxonomy', "️ AB Taksonomisi"), '#16a085', self.open_eu_taxonomy),
            make_btn(self.lm.tr('btn_value_chain', " Değer Zinciri Analizi"), '#2980b9', self.open_value_chain),
            make_btn(self.lm.tr('btn_climate_risk', "️ İklim Riski"), '#c0392b', self.open_climate_risk),
            make_btn(self.lm.tr('btn_seed_env', " Çevresel Göstergeleri Ekle"), '#2ecc71', self.seed_environmental_indicators),
        ]

        for i, b in enumerate(btns):
            b.pack(side='left', padx=(0, 6) if i < len(btns)-1 else 0)

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

    def open_double_materiality(self) -> None:
        try:
            DoubleMaterialityWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('double_materiality_error', 'Çift önemlilik formu açılamadı')}: {e}")

    def open_esrs_requirements(self) -> None:
        try:
            ESRSRequirementsWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('esrs_req_error', 'ESRS gereklilikleri formu açılamadı')}: {e}")

    def open_eu_taxonomy(self) -> None:
        try:
            EUTaxonomyWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('eu_taxonomy_error', 'AB Taksonomisi formu açılamadı')}: {e}")

    def open_value_chain(self) -> None:
        try:
            ValueChainAnalysisWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('value_chain_error', 'Değer zinciri analizi açılamadı')}: {e}")

    def open_climate_risk(self) -> None:
        try:
            ClimateRiskAssessmentWindow(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('climate_risk_error', 'İklim riski formu açılamadı')}: {e}")

    def seed_environmental_indicators(self) -> None:
        try:
            mgr = TSRSManager()
            mgr.create_tables()
            mgr.create_default_tsrs_data(sample=False)
            messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('tsrs_env_added', "Çevresel TSRS göstergeleri eklendi veya zaten mevcut."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('tsrs_add_error', 'Göstergeler eklenemedi')}: {e}")

    def create_content_area(self, parent) -> None:
        """İçerik alanını oluştur"""
        # Canvas ve scrollbar
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)

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

    def show_welcome_content(self) -> None:
        """Hoş geldin içeriğini göster"""
        # Mevcut içeriği temizle (scrollable_frame içinde)
        try:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # Hoş geldin mesajı
        welcome_frame = tk.Frame(self.scrollable_frame, bg='white')
        welcome_frame.pack(fill='both', expand=True, padx=50, pady=50)

        welcome_text = self.lm.tr('tsrs_welcome_msg',
                               "TSRS Modülüne Hoş Geldiniz!\n\n"
                               "Türkiye Sürdürülebilirlik Raporlama Standardı (TSRS) ile\n"
                               "sürdürülebilirlik performansınızı raporlayabilirsiniz.\n\n"
                               "Sol panelden kategorileri seçerek başlayabilirsiniz.")

        welcome_label = tk.Label(welcome_frame,
                               text=welcome_text,
                               font=('Segoe UI', 14), fg='#7f8c8d', bg='white', justify='center')
        welcome_label.pack(expand=True)

        # TSRS bilgi kartları
        info_frame = tk.Frame(welcome_frame, bg='white')
        info_frame.pack(fill='x', pady=20)

        info_cards = [
            ("", self.lm.tr('tsrs_cat_governance', "Yönetişim"), self.lm.tr('tsrs_card_gov_desc', "Sürdürülebilirlik yönetişim yapısı ve sorumluluklar")),
            ("", self.lm.tr('tsrs_cat_strategy', "Strateji"), self.lm.tr('tsrs_card_strat_desc', "Sürdürülebilirlik stratejisi ve uzun vadeli hedefler")),
            ("️", self.lm.tr('tsrs_cat_risk', "Risk Yönetimi"), self.lm.tr('tsrs_card_risk_desc', "Çevresel ve sosyal risklerin değerlendirilmesi")),
            ("", self.lm.tr('tsrs_cat_metrics', "Metrikler"), self.lm.tr('tsrs_card_met_desc', "Performans göstergeleri ve hedef takibi"))
        ]

        for i, (icon, title, desc) in enumerate(info_cards):
            card = tk.Frame(info_frame, bg='#f8f9fa', relief='solid', bd=1)
            card.pack(side='left', fill='both', expand=True, padx=5)

            card_content = tk.Frame(card, bg='#f8f9fa')
            card_content.pack(fill='both', expand=True, padx=15, pady=15)

            icon_label = tk.Label(card_content, text=icon, font=('Segoe UI', 20),
                                 bg='#f8f9fa')
            icon_label.pack()

            title_label = tk.Label(card_content, text=title, font=('Segoe UI', 12, 'bold'),
                                  fg='#2c3e50', bg='#f8f9fa')
            title_label.pack()

            desc_label = tk.Label(card_content, text=desc, font=('Segoe UI', 9),
                                 fg='#7f8c8d', bg='#f8f9fa', wraplength=150, justify='center')
            desc_label.pack()

    def show_category(self, category_key: str) -> None:
        """Kategoriyi göster"""
        # İçerik başlığını güncelle
        category_names = {
            'governance': self.lm.tr('tsrs_cat_governance', 'Yönetişim'),
            'strategy': self.lm.tr('tsrs_cat_strategy', 'Strateji'),
            'risk': self.lm.tr('tsrs_cat_risk', 'Risk Yönetimi'),
            'metrics': self.lm.tr('tsrs_cat_metrics', 'Metrikler')
        }

        self.content_title.config(text=f"TSRS {category_names.get(category_key, category_key)}")

        # İçerik alanını temizle
        try:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # DB kategori eşlemesi ve TSRS standartlarını getir
        db_category_map = {
            'governance': 'Yönetişim',
            'strategy': 'Strateji',
            'risk': 'Risk Yönetimi',
            'metrics': 'Metrikler'
        }
        db_category = db_category_map.get(category_key, category_key)
        standards = self.tsrs_manager.get_tsrs_standards(db_category)

        if not standards:
            try:
                # Güvenli widget oluşturma
                if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
                    msg = self.lm.tr('tsrs_no_standard_msg', '{category} kategorisinde standart bulunamadı.')
                    # .format usage might be risky if translation lacks placeholder, but simple concatenation is safer or handle format error
                    # safer approach:
                    final_msg = msg.replace('{category}', category_names.get(category_key, category_key))
                    
                    no_data_label = tk.Label(self.scrollable_frame,
                                           text=final_msg,
                                           font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
                    no_data_label.pack(pady=50)
            except Exception as e:
                logging.error(f"TSRS widget hatası: {e}")
            return

        # Standartları göster
        for standard in standards:
            self.create_standard_card(standard)

    def create_standard_card(self, standard) -> None:
        """TSRS standart kartı oluştur"""
        card_frame = tk.Frame(self.scrollable_frame, bg='#f8f9fa', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=20, pady=10)

        # Kart başlığı
        header_frame = tk.Frame(card_frame, bg='#2c3e50')
        header_frame.pack(fill='x')

        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(fill='x', padx=15, pady=10)

        code_label = tk.Label(title_frame, text=standard['code'],
                             font=('Segoe UI', 12, 'bold'), fg='white', bg='#2c3e50')
        code_label.pack(side='left')

        req_label = tk.Label(title_frame, text=standard['requirement_level'],
                            font=('Segoe UI', 9), fg='#f39c12', bg='#2c3e50')
        req_label.pack(side='right')

        # Kart içeriği
        content_frame = tk.Frame(card_frame, bg='#f8f9fa')
        content_frame.pack(fill='x', padx=15, pady=10)

        title_label = tk.Label(content_frame, text=standard['title'],
                              font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa')
        title_label.pack(anchor='w')

        desc_label = tk.Label(content_frame, text=standard['description'],
                             font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa',
                             wraplength=600, justify='left')
        desc_label.pack(anchor='w', pady=(5, 0))

        # Alt bilgiler
        info_frame = tk.Frame(content_frame, bg='#f8f9fa')
        info_frame.pack(fill='x', pady=(10, 0))

        subcat_label = tk.Label(info_frame, text=f"{self.lm.tr('subcategory', 'Alt Kategori')}: {standard.get('subcategory', self.lm.tr('no_data', 'Veri Yok'))}",
                               font=('Segoe UI', 9), fg='#95a5a6', bg='#f8f9fa')
        subcat_label.pack(side='left')

        freq_label = tk.Label(info_frame, text=f"{self.lm.tr('reporting_frequency', 'Raporlama')}: {standard.get('reporting_frequency', self.lm.tr('no_data', 'Veri Yok'))}",
                             font=('Segoe UI', 9), fg='#95a5a6', bg='#f8f9fa')
        freq_label.pack(side='right')

        # Butonlar
        button_frame = tk.Frame(content_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(10, 0))

        indicators_btn = tk.Button(button_frame, text=self.lm.tr('view_indicators', "Göstergeleri Görüntüle"),
                                  font=('Segoe UI', 10), bg='#3498db', fg='white',
                                  relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                                  command=lambda: self.show_indicators(standard['id'], standard['title']))
        indicators_btn.pack(side='left')

        detail_btn = tk.Button(button_frame, text=self.lm.tr('details', "Detay"),
                              font=('Segoe UI', 10), bg='#3498db', fg='white',
                              relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                              command=lambda: self.show_tsrs_detail(standard['id'], standard['code'], is_standard=True))
        detail_btn.pack(side='left', padx=(10, 0))

        respond_btn = tk.Button(button_frame, text=self.lm.tr('respond', "Yanıtla"),
                               font=('Segoe UI', 10), bg='#27ae60', fg='white',
                               relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                               command=lambda: self.respond_to_standard(standard['id'], standard['code']))
        respond_btn.pack(side='left', padx=(10, 0))

    def show_indicators(self, standard_id, standard_title) -> None:
        """Göstergeleri göster"""
        # İçerik başlığını güncelle
        self.content_title.config(text=f"{self.lm.tr('tsrs_indicators', 'TSRS Göstergeleri')} - {standard_title}")

        # İçerik alanını temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Göstergeleri getir
        indicators = self.tsrs_manager.get_tsrs_indicators_by_standard(standard_id)

        if not indicators:
            no_data_label = tk.Label(self.scrollable_frame,
                                   text=self.lm.tr('no_indicators_found', "Bu standart için gösterge bulunamadı."),
                                   font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
            no_data_label.pack(pady=50)
            return

        # Göstergeleri listele
        for indicator in indicators:
            self.create_indicator_card(indicator)

    def create_indicator_card(self, indicator) -> None:
        """TSRS gösterge kartı oluştur"""
        card_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=20, pady=5)

        # Kart içeriği
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=15, pady=10)

        # Başlık satırı
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x')

        code_label = tk.Label(header_frame, text=indicator['code'],
                             font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='white')
        code_label.pack(side='left')

        if indicator['is_mandatory']:
            mandatory_label = tk.Label(header_frame, text=self.lm.tr('tsrs_mandatory', "Zorunlu"),
                                      font=('Segoe UI', 8), fg='#e74c3c', bg='white')
            mandatory_label.pack(side='right')

        title_label = tk.Label(content_frame, text=indicator['title'],
                              font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(anchor='w', pady=(5, 0))

        desc_label = tk.Label(content_frame, text=indicator['description'],
                             font=('Segoe UI', 9), fg='#7f8c8d', bg='white',
                             wraplength=500, justify='left')
        desc_label.pack(anchor='w', pady=(5, 0))

        # Alt bilgiler
        info_frame = tk.Frame(content_frame, bg='white')
        info_frame.pack(fill='x', pady=(10, 0))

        if indicator['unit']:
            unit_label = tk.Label(info_frame, text=f"Birim: {indicator['unit']}",
                                 font=('Segoe UI', 9), fg='#95a5a6', bg='white')
            unit_label.pack(side='left')

        type_label = tk.Label(info_frame, text=f"Tip: {indicator['data_type']}",
                             font=('Segoe UI', 9), fg='#95a5a6', bg='white')
        type_label.pack(side='right')

        # Butonlar
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))

        detail_btn = tk.Button(button_frame, text=self.lm.tr('btn_detail', "Detay"),
                              font=('Segoe UI', 9), bg='#3498db', fg='white',
                              relief='flat', bd=0, cursor='hand2', padx=10, pady=3,
                              command=lambda: self.show_tsrs_detail(indicator['id'], indicator['code'], is_standard=False))
        detail_btn.pack(side='left')

        respond_btn = tk.Button(button_frame, text=self.lm.tr('tsrs_btn_respond', "Yanıtla"),
                               font=('Segoe UI', 9), bg='#27ae60', fg='white',
                               relief='flat', bd=0, cursor='hand2', padx=10, pady=3,
                               command=lambda: self.respond_to_indicator(indicator['id'], indicator['code']))
        respond_btn.pack(side='left', padx=(10, 0))

    def respond_to_standard(self, standard_id, standard_code) -> None:
        """Standart için yanıt yerine ilgili göstergeleri aç"""
        try:
            standards = self.tsrs_manager.get_tsrs_standards()
            standard = next((s for s in standards if s['id'] == standard_id), None)
            standard_title = standard['title'] if standard else standard_code
            # Standart bazında doğrudan yanıt desteklenmediğinden göstergeleri aç
            self.show_indicators(standard_id, standard_title)
        except Exception:
            # Hata halinde kullanıcıya bilgi ver ve yine göstergeleri aç
            messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('tsrs_msg_standard_response_not_supported', "Standart bazında yanıt desteklenmiyor. Lütfen ilgili göstergeleri yanıtlayın."))
            self.show_indicators(standard_id, standard_code)

    def respond_to_indicator(self, indicator_id, indicator_code) -> None:
        """Gösterge için yanıt formu göster"""
        self.show_tsrs_response_form(indicator_id, indicator_code, is_standard=False)

    def show_tsrs_response_form(self, item_id, item_code, is_standard=False) -> None:
        """TSRS yanıt formu göster"""
        # Yanıt penceresi oluştur
        response_window = tk.Toplevel(self.parent)
        item_type = self.lm.tr('standard', "Standart") if is_standard else self.lm.tr('indicator', "Gösterge")
        response_window.title(f"TSRS {item_code} {item_type} {self.lm.tr('response', 'Yanıtı')}")
        response_window.geometry("600x700")
        response_window.configure(bg='white')

        # Başlık
        title_label = tk.Label(response_window, text=f"TSRS {item_code} - {item_type} {self.lm.tr('response', 'Yanıtı')}",
                              font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=20)

        # Form frame
        form_frame = tk.Frame(response_window, bg='white')
        form_frame.pack(fill='both', expand=True, padx=30, pady=20)

        # Form alanları
        from typing import Dict
        fields: Dict[str, Any] = {}

        # Veri tipine göre dinamik form için gösterge bilgilerini getir
        indicator_info = None
        indicator_unit = ''
        indicator_dtype = 'text'
        if not is_standard:
            try:
                indicators = self.tsrs_manager.get_tsrs_indicators()
                indicator_info = next((i for i in indicators if i['id'] == item_id), None)
                if indicator_info:
                    indicator_unit = indicator_info.get('unit') or ''
                    indicator_dtype = (indicator_info.get('data_type') or 'text').lower()
            except Exception:
                indicator_info = None

        # Raporlama Dönemi
        tk.Label(form_frame, text=f"{self.lm.tr('reporting_period', 'Raporlama Dönemi')}:", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        fields['reporting_period'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        fields['reporting_period'].insert(0, "2024")  # Varsayılan değer
        fields['reporting_period'].pack(pady=(0, 15))

        # Veri tipine göre dinamik alanlar
        # Ortak olarak her tipte kullanılabilecek alanları hazırla
        # Yanıt/metin alanı (sadece text tipi için)
        if indicator_dtype in ['text', 'string', 'metin']:
            tk.Label(form_frame, text=f"{self.lm.tr('response_value_text', 'Yanıt Değeri (Metin)')}:", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
            fields['response_value'] = tk.Text(form_frame, height=4, width=50, font=('Segoe UI', 10))
            fields['response_value'].pack(pady=(0, 15))
        else:
            # Diğer tiplerde response_value isteğe bağlı açıklama alanı olarak sunulabilir
            tk.Label(form_frame, text=f"{self.lm.tr('description_optional', 'Açıklama (İsteğe bağlı)')}:", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
            fields['response_value'] = tk.Text(form_frame, height=3, width=50, font=('Segoe UI', 10))
            fields['response_value'].pack(pady=(0, 15))

        # Numeric / yüzdelik / para birimi gibi sayısal veri tipleri
        if indicator_dtype in ['numeric', 'number', 'percentage', 'percent', 'currency']:
            tk.Label(form_frame, text=f"{self.lm.tr('numerical_value', 'Sayısal Değer')}:", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
            fields['numerical_value'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
            fields['numerical_value'].pack(pady=(0, 10))

            tk.Label(form_frame, text=f"{self.lm.tr('unit', 'Birim')}:", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
            fields['unit'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
            if indicator_unit:
                fields['unit'].insert(0, indicator_unit)
            fields['unit'].pack(pady=(0, 15))
        elif indicator_dtype in ['boolean', 'bool']:
            # Boolean seçim alanı
            tk.Label(form_frame, text=f"{self.lm.tr('value_yes_no', 'Değer (Evet/Hayır)')}:", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
            fields['boolean_value'] = tk.StringVar(value='')
            bool_frame = tk.Frame(form_frame, bg='white')
            bool_frame.pack(fill='x', pady=(0, 15))
            tk.Radiobutton(bool_frame, text=self.lm.tr('yes', "Evet"), variable=fields['boolean_value'], value="Evet", bg='white').pack(side='left')
            tk.Radiobutton(bool_frame, text=self.lm.tr('no', "Hayır"), variable=fields['boolean_value'], value="Hayır", bg='white').pack(side='left', padx=(20, 0))
            # Birim alanı boolean için gerekli değil
            fields['numerical_value'] = tk.Entry(form_frame)
            fields['unit'] = tk.Entry(form_frame)
        elif indicator_dtype in ['file', 'dosya']:
            # Dosya seçimi → evidence_url alanını doldurur
            tk.Label(form_frame, text=f"{self.lm.tr('file_evidence', 'Dosya Kanıtı')}:", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
            file_frame = tk.Frame(form_frame, bg='white')
            file_frame.pack(fill='x', pady=(0, 10))
            fields['evidence_url'] = tk.Entry(file_frame, font=('Segoe UI', 10), width=40)
            fields['evidence_url'].pack(side='left', padx=(0, 10))

            def select_file() -> None:
                path = filedialog.askopenfilename(title=self.lm.tr('select_evidence_file', "Kanıt Dosyası Seç"))
                if path:
                    fields['evidence_url'].delete(0, tk.END)
                    fields['evidence_url'].insert(0, path)

            tk.Button(file_frame, text=self.lm.tr('select_file', "Dosya Seç"), font=('Segoe UI', 9), bg='#3498db', fg='white', relief='flat', padx=10, command=select_file).pack(side='left')
            # Numerik/birim alanlarını placeholder olarak oluştur (kaydetme sırasında boş bırakılabilir)
            fields['numerical_value'] = tk.Entry(form_frame)
            fields['unit'] = tk.Entry(form_frame)
        else:
            # Varsayılan: metin alanı zaten eklendi, numerik/birim alanları isteğe bağlı boş
            fields['numerical_value'] = tk.Entry(form_frame)
            fields['unit'] = tk.Entry(form_frame)

        # Metodoloji
        tk.Label(form_frame, text=f"{self.lm.tr('methodology_used', 'Kullanılan Metodoloji')}:", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
        fields['methodology_used'] = tk.Text(form_frame, height=3, width=50, font=('Segoe UI', 10))
        fields['methodology_used'].pack(pady=(0, 15))

        # Veri Kaynağı
        tk.Label(form_frame, text=f"{self.lm.tr('data_source', 'Veri Kaynağı')}:", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
        fields['data_source'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        fields['data_source'].pack(pady=(0, 15))

        # Raporlama Durumu
        tk.Label(form_frame, text=f"{self.lm.tr('reporting_status', 'Raporlama Durumu')}:", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
        status_frame = tk.Frame(form_frame, bg='white')
        status_frame.pack(fill='x', pady=(0, 15))
        fields['reporting_status'] = tk.StringVar(value="Draft")
        tk.Radiobutton(status_frame, text=self.lm.tr('draft', "Taslak"), variable=fields['reporting_status'], value="Draft", bg='white').pack(side='left')
        tk.Radiobutton(status_frame, text=self.lm.tr('approved', "Onaylanmış"), variable=fields['reporting_status'], value="Approved", bg='white').pack(side='left', padx=(20, 0))

        # Kanıt URL'si (dosya tipi için yukarıda oluşturulduysa tekrar oluşturma)
        if 'evidence_url' not in fields:
            tk.Label(form_frame, text=self.lm.tr('evidence_url', "Kanıt URL'si") + ":", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
            fields['evidence_url'] = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
            fields['evidence_url'].pack(pady=(0, 15))

        # Notlar
        tk.Label(form_frame, text=f"{self.lm.tr('notes', 'Notlar')}:", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(10, 5))
        fields['notes'] = tk.Text(form_frame, height=3, width=50, font=('Segoe UI', 10))
        fields['notes'].pack(pady=(0, 20))

        # Butonlar
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill='x', pady=20)

        def save_response() -> None:
            try:
                # Standart için yanıt kaydı desteklenmiyor
                if is_standard:
                    messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('tsrs_standard_response_error', "Standart bazında yanıt kaydı desteklenmiyor. Lütfen ilgili göstergeleri yanıtlayın."))
                    return
                # Form verilerini topla
                def _val(w: Any) -> str:
                    try:
                        if isinstance(w, tk.Text):
                            return w.get('1.0', tk.END).strip()
                        if isinstance(w, tk.Entry):
                            return w.get().strip()
                        if isinstance(w, tk.StringVar) or isinstance(w, tk.IntVar):
                            return str(w.get()).strip()
                    except Exception:
                        return ''
                    return ''

                from typing import Any as _Any
                from typing import Dict as _Dict
                response_data: _Dict[str, _Any] = {
                    'response_value': _val(fields.get('response_value')),
                    'numerical_value': _val(fields.get('numerical_value')),
                    'unit': _val(fields.get('unit')),
                    'methodology_used': _val(fields.get('methodology_used')),
                    'data_source': _val(fields.get('data_source')),
                    'reporting_status': _val(fields.get('reporting_status')),
                    'evidence_url': _val(fields.get('evidence_url')),
                    'notes': _val(fields.get('notes'))
                }

                rp = fields['reporting_period'].get()
                yr = self._validate_year(rp)
                if yr is None:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('invalid_reporting_period', "Raporlama dönemi geçersiz. Lütfen 4 haneli yıl girin."))
                    return


                # Veri tipine göre zorunlu alanları kontrol et
                dtype = indicator_dtype
                if dtype in ['text', 'string', 'metin']:
                    if not response_data['response_value']:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('enter_text_response', "Lütfen metin yanıtını girin."))
                        return
                elif dtype in ['numeric', 'number', 'percentage', 'percent', 'currency']:
                    if not response_data['numerical_value']:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('enter_numerical_value', "Lütfen sayısal değeri girin."))
                        return
                    try:
                        response_data['numerical_value'] = float(response_data['numerical_value'])
                    except Exception:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('invalid_numeric_format', "Sayısal değer formatı geçersiz."))
                        return
                    if not (response_data['unit'] or indicator_unit):
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('unit_required', "Birim bilgisi gerekli."))
                        return
                elif dtype in ['boolean', 'bool']:
                    # Boolean için numerical/unit kullanılmaz, response_value'ı Evet/Hayır olarak doldur
                    selected = fields['boolean_value'].get() if 'boolean_value' in fields else ''
                    if not selected:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('select_yes_no', "Lütfen Evet/Hayır seçimi yapın."))
                        return
                    response_data['response_value'] = selected
                    response_data['numerical_value'] = ''
                    response_data['unit'] = ''
                elif dtype in ['file', 'dosya']:
                    if not response_data['evidence_url']:
                        messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('select_evidence', "Lütfen kanıt dosyasını seçin veya URL girin."))
                        return

                # TSRS manager ile yanıtı kaydet
                success = self.tsrs_manager.save_tsrs_response(
                    company_id=self.company_id,
                    indicator_id=item_id,
                    reporting_period=str(yr),
                    response_data=response_data
                )

                if success:
                    messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"TSRS {item_code} {item_type} {self.lm.tr('response_saved', 'yanıtı başarıyla kaydedildi!')}")
                    response_window.destroy()
                    self.load_data()  # İstatistikleri yenile
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('response_save_error', "Yanıt kaydedilemedi!"))

            except Exception as e:
                logging.error(f"TSRS yanıt kaydetme hatası: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('response_save_error', 'Yanıt kaydedilemedi')}: {e}")

        tk.Button(button_frame, text=self.lm.tr('btn_save', "Kaydet"), font=('Segoe UI', 10, 'bold'), bg='#27ae60',
                 fg='white', relief='flat', padx=20, pady=5, command=save_response).pack(side='left', padx=5)

        tk.Button(button_frame, text=self.lm.tr('btn_cancel', "İptal"), font=('Segoe UI', 10, 'bold'), bg='#95a5a6',
                 fg='white', relief='flat', padx=20, pady=5, command=response_window.destroy).pack(side='left', padx=5)

    def show_tsrs_detail(self, item_id, item_code, is_standard=False) -> None:
        """TSRS detay penceresi göster"""
        # Detay penceresi oluştur
        detail_window = tk.Toplevel(self.parent)
        item_type = self.lm.tr('standard', "Standart") if is_standard else self.lm.tr('indicator', "Gösterge")
        detail_window.title(f"TSRS {item_code} {item_type} {self.lm.tr('detail', 'Detayı')}")
        detail_window.geometry("700x500")
        detail_window.configure(bg='white')

        # Başlık
        title_label = tk.Label(detail_window, text=f"TSRS {item_code} - {item_type} {self.lm.tr('detail', 'Detayı')}",
                              font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=20)

        # Detay içeriği
        content_frame = tk.Frame(detail_window, bg='white')
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)

        # TSRS manager'dan detayları getir
        try:
            if is_standard:
                # Standart detayları
                standards = self.tsrs_manager.get_tsrs_standards()
                standard_data = next((s for s in standards if s['id'] == item_id), None)

                if standard_data:
                    detail_text = f"""
TSRS {item_type} {self.lm.tr('detail', 'Detayı')}

{self.lm.tr('code', 'Kod')}: {standard_data.get('code', '')}
{self.lm.tr('title', 'Başlık')}: {standard_data.get('title', '')}
{self.lm.tr('description', 'Açıklama')}: {standard_data.get('description', '')}
{self.lm.tr('category', 'Kategori')}: {standard_data.get('category', '')}
{self.lm.tr('subcategory', 'Alt Kategori')}: {standard_data.get('subcategory', '')}
{self.lm.tr('requirement_level', 'Gereklilik Seviyesi')}: {standard_data.get('requirement_level', '')}
{self.lm.tr('reporting_frequency', 'Raporlama Sıklığı')}: {standard_data.get('reporting_frequency', '')}
{self.lm.tr('effective_date', 'Yürürlük Tarihi')}: {standard_data.get('effective_date', '')}
                    """
                else:
                    detail_text = f"TSRS {item_code} {self.lm.tr('standard_not_found', 'standartı bulunamadı.')}"
            else:
                # Gösterge detayları
                indicators = self.tsrs_manager.get_tsrs_indicators()
                indicator_data = next((i for i in indicators if i['id'] == item_id), None)

                if indicator_data:
                    detail_text = f"""
TSRS {item_type} {self.lm.tr('detail', 'Detayı')}

{self.lm.tr('code', 'Kod')}: {indicator_data.get('code', '')}
{self.lm.tr('title', 'Başlık')}: {indicator_data.get('title', '')}
{self.lm.tr('description', 'Açıklama')}: {indicator_data.get('description', '')}
{self.lm.tr('unit', 'Birim')}: {indicator_data.get('unit', '')}
{self.lm.tr('methodology', 'Metodoloji')}: {indicator_data.get('methodology', '')}
{self.lm.tr('data_type', 'Veri Tipi')}: {indicator_data.get('data_type', '')}
{self.lm.tr('is_mandatory', 'Zorunlu mu?')}: {indicator_data.get('is_mandatory', '')}
{self.lm.tr('is_quantitative', 'Sayısal mı?')}: {indicator_data.get('is_quantitative', '')}
{self.lm.tr('baseline_year', 'Baz Yıl')}: {indicator_data.get('baseline_year', '')}
{self.lm.tr('target_year', 'Hedef Yıl')}: {indicator_data.get('target_year', '')}
{self.lm.tr('standard_id', 'Standart ID')}: {indicator_data.get('standard_id', '')}
                    """
                else:
                    detail_text = f"TSRS {item_code} {self.lm.tr('indicator_not_found', 'göstergesi bulunamadı.')}"

            # Detay metnini göster
            detail_label = tk.Label(content_frame, text=detail_text,
                                   font=('Segoe UI', 10), fg='#2c3e50', bg='white',
                                   justify='left', wraplength=650)
            detail_label.pack(pady=20)

        except Exception as e:
            logging.error(f"TSRS detay getirme hatası: {e}")
            error_label = tk.Label(content_frame, text=f"{self.lm.tr('details_fetch_error', 'Detay bilgileri getirilemedi')}: {e}",
                                  font=('Segoe UI', 10), fg='#e74c3c', bg='white')
            error_label.pack(pady=20)

        # Kapat butonu
        close_btn = tk.Button(content_frame, text=self.lm.tr('btn_close', "Kapat"), font=('Segoe UI', 10, 'bold'),
                             bg='#95a5a6', fg='white', relief='flat', padx=20, pady=5,
                             command=detail_window.destroy)
        close_btn.pack(pady=20)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # TSRS istatistiklerini güncelle
            stats = self.tsrs_manager.get_tsrs_statistics(self.company_id)
            self.update_stats(stats)
            # Eğer sistemde hiç standart yoksa varsayılan veriyi yükle ve tekrar istatistikleri çek
            if stats.get('total_standards', 0) == 0:
                try:
                    # Varsayılan standartları yükle (Sample=False olarak, gerçek standart tanımları)
                    self.tsrs_manager.create_default_tsrs_data(sample=False)
                    stats = self.tsrs_manager.get_tsrs_statistics(self.company_id)
                    self.update_stats(stats)
                except Exception as se:
                    logging.info(f"Varsayılan TSRS verisi yüklenemedi: {se}")
        except Exception as e:
            logging.error(f"TSRS verileri yüklenirken hata: {e}")

    def update_stats(self, stats) -> None:
        """İstatistikleri güncelle"""
        self.stats_labels['total_standards'].config(text=str(stats.get('total_standards', 0)))
        self.stats_labels['total_indicators'].config(text=str(stats.get('total_indicators', 0)))
        self.stats_labels['answered_indicators'].config(text=str(stats.get('answered_indicators', 0)))
        self.stats_labels['response_percentage'].config(text=f"%{stats.get('response_percentage', 0)}")
