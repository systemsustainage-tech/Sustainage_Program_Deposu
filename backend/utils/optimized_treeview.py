#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimize Edilmiş Treeview
Büyük veri setleri için performans optimizasyonlu Treeview wrapper
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List


class OptimizedTreeview:
    """
    Büyük veri setleri için optimize edilmiş Treeview
    
    Özellikler:
    - Lazy loading (sayfalama)
    - Sanal scrolling
    - Hızlı arama/filtreleme
    - Bellek optimizasyonu
    """

    def __init__(self, parent, columns: List[str], headings: List[str],
                 page_size: int = 100, **kwargs):
        """
        Optimize edilmiş Treeview oluştur
        
        Args:
            parent: Tkinter parent widget
            columns: Kolon isimleri
            headings: Kolon başlıkları
            page_size: Sayfa başına kayıt (varsayılan: 100)
        """
        self.parent = parent
        self.columns = columns
        self.headings = headings
        self.page_size = page_size
        self.current_page = 0
        self.total_items = 0
        self.all_data = []  # Tüm veri (hafızada)
        self.filtered_data = []  # Filtrelenmiş veri
        self.filter_active = False

        # Treeview oluştur
        self.tree = ttk.Treeview(parent, columns=columns, show='tree headings', **kwargs)

        # Kolonları ayarla
        self.tree.column('#0', width=0, stretch=False)  # Gizle
        for i, (col, heading) in enumerate(zip(columns, headings)):
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=120, anchor='w')

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Sayfalama kontrolleri
        self.control_frame = tk.Frame(parent, bg='white')
        self.page_label = tk.Label(self.control_frame, text="Sayfa: 1/1",
                                   font=('Segoe UI', 9), bg='white')
        self.prev_btn = tk.Button(self.control_frame, text="◀ Önceki",
                                  command=self.prev_page, state='disabled')
        self.next_btn = tk.Button(self.control_frame, text="Sonraki ▶",
                                  command=self.next_page, state='disabled')

        # Arama
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.on_search_change())
        self.search_entry = tk.Entry(self.control_frame, textvariable=self.search_var,
                                     width=30, font=('Segoe UI', 9))
        self.search_label = tk.Label(self.control_frame, text=" Ara:",
                                     font=('Segoe UI', 9), bg='white')

        # Info label
        self.info_label = tk.Label(self.control_frame,
                                   text="Toplam: 0 kayıt",
                                   font=('Segoe UI', 9), bg='white', fg='#666')

    def pack(self, **kwargs) -> None:
        """Widget'ları yerleştir"""
        # Kontroller (üstte)
        self.control_frame.pack(fill='x', padx=10, pady=5)

        self.search_label.pack(side='left', padx=5)
        self.search_entry.pack(side='left', padx=5)

        self.info_label.pack(side='left', padx=20)

        self.page_label.pack(side='right', padx=5)
        self.next_btn.pack(side='right', padx=2)
        self.prev_btn.pack(side='right', padx=2)

        # Treeview
        self.tree.pack(side='left', fill='both', expand=True, **kwargs)
        self.scrollbar.pack(side='right', fill='y')

    def load_data(self, data: List[Dict], clear: bool = True) -> None:
        """
        Veri yükle (sayfalama ile)
        
        Args:
            data: Veri listesi
            clear: Mevcut veriyi temizle
        """
        if clear:
            self.all_data = data
            self.filtered_data = data
            self.current_page = 0
            self.filter_active = False

        self.total_items = len(self.filtered_data)
        self._render_current_page()
        self._update_controls()

    def _render_current_page(self) -> None:
        """Mevcut sayfayı render et"""
        # Mevcut kayıtları temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sayfa hesapla
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, self.total_items)

        # Sadece mevcut sayfayı göster
        page_data = self.filtered_data[start_idx:end_idx]

        for row in page_data:
            values = [row.get(col, '') for col in self.columns]
            self.tree.insert('', 'end', values=values)

        # Bellek temizliği için force garbage collection
        if self.total_items > 1000:
            import gc
            gc.collect()

    def _update_controls(self) -> None:
        """Kontrol butonlarını güncelle"""
        total_pages = (self.total_items + self.page_size - 1) // self.page_size
        total_pages = max(1, total_pages)

        # Sayfa label
        self.page_label.config(text=f"Sayfa: {self.current_page + 1}/{total_pages}")

        # Info label
        start_idx = self.current_page * self.page_size + 1
        end_idx = min((self.current_page + 1) * self.page_size, self.total_items)

        if self.filter_active:
            self.info_label.config(
                text=f"Gösterilen: {start_idx}-{end_idx} / {self.total_items} "
                     f"(Toplam: {len(self.all_data)} kayıt - Filtrelendi)"
            )
        else:
            self.info_label.config(text=f"Toplam: {self.total_items} kayıt ({start_idx}-{end_idx})")

        # Butonlar
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < total_pages - 1 else 'disabled')

    def next_page(self) -> None:
        """Sonraki sayfa"""
        total_pages = (self.total_items + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._render_current_page()
            self._update_controls()

    def prev_page(self) -> None:
        """Önceki sayfa"""
        if self.current_page > 0:
            self.current_page -= 1
            self._render_current_page()
            self._update_controls()

    def on_search_change(self) -> None:
        """Arama değiştiğinde"""
        search_text = self.search_var.get().lower().strip()

        if not search_text:
            # Filtre kaldır
            self.filtered_data = self.all_data
            self.filter_active = False
        else:
            # Filtrele (tüm kolonlarda ara)
            self.filtered_data = [
                row for row in self.all_data
                if any(search_text in str(row.get(col, '')).lower() for col in self.columns)
            ]
            self.filter_active = True

        # İlk sayfaya dön
        self.current_page = 0
        self.total_items = len(self.filtered_data)
        self._render_current_page()
        self._update_controls()

    def sort_column(self, col: str) -> None:
        """Kolona göre sırala"""
        # Mevcut sıralamayı tersine çevir
        reverse = getattr(self, f'_sort_{col}_reverse', False)

        try:
            # Sayısal sıralama dene
            self.filtered_data.sort(
                key=lambda x: float(x.get(col, 0)) if x.get(col) else 0,
                reverse=reverse
            )
        except (ValueError, TypeError):
            # String sıralama
            self.filtered_data.sort(
                key=lambda x: str(x.get(col, '')).lower(),
                reverse=reverse
            )

        # Sıralama yönünü değiştir
        setattr(self, f'_sort_{col}_reverse', not reverse)

        # Render
        self._render_current_page()

    def bind(self, event: str, callback: Callable) -> None:
        """Event binding"""
        self.tree.bind(event, callback)

    def selection(self) -> None:
        """Seçili öğeleri al"""
        return self.tree.selection()

    def item(self, item_id: str, option: str = None) -> None:
        """Öğe bilgisi al"""
        return self.tree.item(item_id, option)

    def get_page_info(self) -> Dict:
        """Sayfalama bilgisi"""
        return {
            'current_page': self.current_page,
            'page_size': self.page_size,
            'total_items': self.total_items,
            'total_pages': (self.total_items + self.page_size - 1) // self.page_size,
            'filter_active': self.filter_active
        }

