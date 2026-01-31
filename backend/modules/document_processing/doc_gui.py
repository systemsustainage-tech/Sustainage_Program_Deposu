#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Belge Isleme GUI"""
import tkinter as tk
from tkinter import scrolledtext, ttk


class DocProcessingGUI:
    def __init__(self, parent, company_id: int = 1):
        self.parent = parent
        self.company_id = company_id
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Belge Isleme Modulu", font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))

        text = """
BELGE ISLEME MODULU

Ozellikler:
- PDF metin cikartma
- OCR (Optical Character Recognition)
- Belge analizi
- Veri cikartma

Desteklenen Formatlar:
- PDF
- JPEG, PNG
- Word belgeler
- Excel dosyalari

DURUM: Modul aktif
OCR: Simdilik simulasyon modu
"""

        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')

