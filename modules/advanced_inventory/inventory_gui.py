import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gelismis Envanter GUI"""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme


class InventoryGUI:
    def __init__(self, parent, company_id: int = 1):
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.setup_ui()

    def setup_ui(self):
        apply_theme(self.parent)
        main_frame = ttk.Frame(self.parent, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        header = ttk.Frame(main_frame, style='Toolbar.TFrame')
        header.pack(fill='x')
        ttk.Label(header, text=self.lm.tr('adv_inv_title', "Gelismis Envanter"), style='Header.TLabel').pack(side='left', padx=12)
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(10, 10))
        ttk.Button(toolbar, text=self.lm.tr('btn_report_center', "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center).pack(side='left', padx=6)
        ttk.Button(toolbar, text=self.lm.tr('btn_refresh', "Yenile"), style='Primary.TButton', command=self.refresh_view).pack(side='left', padx=6)
        ttk.Label(toolbar, text=self.lm.tr('lbl_year', "Yıl:")).pack(side='left', padx=(10,0))
        self.period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        period_combo = ttk.Combobox(toolbar, textvariable=self.period_var, values=years, width=8, state='readonly')
        period_combo.pack(side='left', padx=6)
        def _validate_year(y: str):
            try:
                y = (y or '').strip()
                return y.isdigit() and len(y) == 4 and 1990 <= int(y) <= 2100
            except Exception:
                return False
        def _on_period_change(*args):
            if not _validate_year(self.period_var.get()):
                messagebox.showwarning(self.lm.tr('warn_title', 'Uyarı'), self.lm.tr('warn_valid_year', 'Geçerli bir yıl seçin (1990-2100)'))
                return
            try:
                self.refresh_view()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        try:
            self.period_var.trace_add('write', _on_period_change)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        ttk.Label(main_frame, text=self.lm.tr('adv_inv_header', "Gelismis Envanter"), font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))

        text = self.lm.tr('adv_inv_info', """
GELISMIS ENVANTER MODULU

Ozellikler:
- Detayli envanter takibi
- Stok yonetimi
- Hareket kayitlari
- Envanter degerleme
- Dashboard

Raporlama:
- Envanter ozeti
- Hareket raporu
- Deger analizi
- Grafik gosterimler

DURUM: Modul aktif
Envanter: Simdilik simulasyon modu
""")

        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')

    def open_report_center(self) -> None:
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

    def refresh_view(self) -> None:
        try:
            _ = self.period_var.get()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

