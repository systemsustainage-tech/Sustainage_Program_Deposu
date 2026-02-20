#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Inventory GUI
Tkinter interface for Inventory Management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

try:
    from .inventory_manager import InventoryManager
except ImportError:
    # Fallback for direct execution
    from backend.modules.advanced_inventory.inventory_manager import InventoryManager

class InventoryGUI(ttk.Frame):
    """
    Envanter Yönetimi Arayüzü
    """

    def __init__(self, parent, db_path: str = None, company_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.company_id = company_id
        self.manager = InventoryManager(db_path, company_id)
        
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """Arayüz bileşenlerini oluştur"""
        # Başlık
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Envanter Yönetimi", font=('Segoe UI', 14, 'bold')).pack(side='left')
        
        # Araç çubuğu
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Yeni Ekle", command=self._add_item_dialog).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Yenile", command=self._load_data).pack(side='left', padx=5)

        # Liste
        columns = ('ID', 'Ad', 'Kategori', 'Miktar', 'Birim', 'Konum')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _load_data(self):
        """Verileri yükle"""
        # Temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.company_id:
            return

        items = self.manager.get_inventory(self.company_id)
        for item in items:
            self.tree.insert('', 'end', values=(
                item.get('id'),
                item.get('name'),
                item.get('category'),
                item.get('quantity'),
                item.get('unit'),
                item.get('location')
            ))

    def _add_item_dialog(self):
        """Yeni ekleme penceresi (Basit)"""
        if not self.company_id:
            messagebox.showwarning("Uyarı", "Şirket seçilmedi!")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Yeni Envanter Kalemi")
        dialog.geometry("300x250")
        
        # Form alanları
        tk.Label(dialog, text="Ad:").pack()
        name_entry = tk.Entry(dialog)
        name_entry.pack()
        
        tk.Label(dialog, text="Kategori:").pack()
        cat_entry = tk.Entry(dialog)
        cat_entry.pack()
        
        tk.Label(dialog, text="Miktar:").pack()
        qty_entry = tk.Entry(dialog)
        qty_entry.pack()

        def save():
            name = name_entry.get()
            cat = cat_entry.get()
            try:
                qty = float(qty_entry.get())
            except ValueError:
                messagebox.showerror("Hata", "Miktar sayı olmalı!")
                return
                
            if name:
                self.manager.add_item(self.company_id, name, cat, qty, "adet")
                self._load_data()
                dialog.destroy()
        
        tk.Button(dialog, text="Kaydet", command=save).pack(pady=10)
