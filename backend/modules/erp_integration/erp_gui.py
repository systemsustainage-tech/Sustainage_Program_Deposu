#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ERP GUI"""
import tkinter as tk
from tkinter import scrolledtext, ttk


class ERPGUI:
    def __init__(self, parent, company_id: int = 1):
        self.parent = parent
        self.company_id = company_id
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="ERP Entegrasyon Modulu", font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))

        text = """
ERP ENTEGRASYON MODULU

Desteklenen Sistemler:
- SAP ERP
- Oracle ERP
- Microsoft Dynamics
- Diger ERP sistemleri

Ozellikler:
- Veri cekme (import)
- Veri gonderme (export)
- Otomatik senkronizasyon
- Veri esleme

DURUM: Modul aktif
Baglanti: Simdilik simulasyon modu
"""

        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')

