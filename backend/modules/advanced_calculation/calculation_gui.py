#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculation GUI
Tkinter interface for Emission Calculations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

try:
    from .emission_calculator import EmissionCalculator
except ImportError:
    # Fallback for direct execution
    from backend.modules.advanced_calculation.emission_calculator import EmissionCalculator

class CalculationGUI(ttk.Frame):
    """
    Emisyon Hesaplama Arayüzü
    """

    def __init__(self, parent, company_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.company_id = company_id
        self.calculator = EmissionCalculator()
        
        self._init_ui()

    def _init_ui(self):
        """Arayüz bileşenlerini oluştur"""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Emisyon Hesaplama", font=('Segoe UI', 14, 'bold')).pack(side='left')
        
        # Sekmeli yapı
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        self._create_scope1_tab(notebook)
        self._create_scope2_tab(notebook)
        self._create_scope3_tab(notebook)

    def _create_scope1_tab(self, notebook):
        """Scope 1 Hesaplama"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Scope 1 (Doğrudan)")
        
        ttk.Label(tab, text="Yakıt Tüketimi").pack(pady=5)
        
        form_frame = ttk.Frame(tab)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="Yakıt Türü:").grid(row=0, column=0, padx=5, pady=5)
        fuel_type = tk.StringVar(value='diesel')
        fuel_combo = ttk.Combobox(form_frame, textvariable=fuel_type, values=['diesel', 'petrol', 'natural_gas', 'coal'])
        fuel_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Miktar:").grid(row=1, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(form_frame)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        result_label = ttk.Label(tab, text="Sonuç: -", font=('Segoe UI', 10, 'bold'))
        result_label.pack(pady=10)
        
        def calculate():
            try:
                amt = float(amount_entry.get())
                data = [{'type': fuel_type.get(), 'amount': amt}]
                res = self.calculator.calculate_scope1(data)
                result_label.config(text=f"Sonuç: {res['total']} kg CO2e")
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir miktar girin!")
                
        ttk.Button(tab, text="Hesapla", command=calculate).pack(pady=5)

    def _create_scope2_tab(self, notebook):
        """Scope 2 Hesaplama"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Scope 2 (Enerji)")
        
        ttk.Label(tab, text="Elektrik Tüketimi (kWh)").pack(pady=5)
        
        form_frame = ttk.Frame(tab)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="Tüketim (kWh):").grid(row=0, column=0, padx=5, pady=5)
        kwh_entry = ttk.Entry(form_frame)
        kwh_entry.grid(row=0, column=1, padx=5, pady=5)
        
        result_label = ttk.Label(tab, text="Sonuç: -", font=('Segoe UI', 10, 'bold'))
        result_label.pack(pady=10)
        
        def calculate():
            try:
                kwh = float(kwh_entry.get())
                data = {'consumption_kwh': kwh, 'source': 'grid'}
                res = self.calculator.calculate_scope2(data)
                result_label.config(text=f"Location Based: {res['location_based']} kg CO2e")
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir tüketim girin!")
                
        ttk.Button(tab, text="Hesapla", command=calculate).pack(pady=5)

    def _create_scope3_tab(self, notebook):
        """Scope 3 Hesaplama"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Scope 3 (Diğer)")
        
        ttk.Label(tab, text="Diğer Aktiviteler").pack(pady=5)
        
        # Basit bir placeholder
        ttk.Label(tab, text="Detaylı Scope 3 hesaplaması için veri girişi gereklidir.").pack(pady=10)
