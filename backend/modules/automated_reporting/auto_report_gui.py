#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Otomatik Raporlama GUI"""
import tkinter as tk
from tkinter import scrolledtext, ttk


class AutoReportGUI:
    def __init__(self, parent, company_id: int = 1):
        self.parent = parent
        self.company_id = company_id
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Otomatik Raporlama", font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))

        text = """
OTOMATIK RAPORLAMA MODULU

Ozellikler:
- Zamanlanmis raporlar
- Email gonderimi
- PDF oluşturma
- Excel export

Zamanlamalar:
- Gunluk
- Haftalik
- Aylik
- Yillik

DURUM: Modul aktif
Email: Simdilik simulasyon modu
"""

        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')

