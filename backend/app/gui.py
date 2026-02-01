#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit masaüstü GUI iskeleti (Tkinter)
- Modül menüsü: SDG, GRI, TSRS, KARBON, EŞLEŞTİRME, RAPORLAMA, YÖNETİM
- SDG → Hedef seçimi, veri girişi, ilerleme
- RAPORLAMA → 3 rapor tipi butonları
"""
import tkinter as tk
import sys
import os
from tkinter import messagebox, ttk

# Add parent directory to path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.language_manager import LanguageManager


class SDGDesktopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.lm = LanguageManager()
        self.title(self.lm.tr("app_title_desktop", "SDG Desktop"))
        self.geometry("1000x650")
        self._build_menu()
        self._build_main()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        mod = tk.Menu(menubar, tearoff=0)
        
        modules = [
            ("SDG", "module_sdg"),
            ("GRI", "module_gri"),
            ("TSRS", "module_tsrs"),
            ("KARBON", "module_carbon"),
            ("EŞLEŞTİRME", "module_mapping"),
            ("RAPORLAMA", "module_reporting"),
            ("YÖNETİM", "module_management")
        ]
        
        for m_text, m_key in modules:
            label = self.lm.tr(m_key, m_text)
            mod.add_command(label=label, command=lambda x=label: self._switch_module(x))
            
        menubar.add_cascade(label=self.lm.tr("menu_modules", "Modüller"), menu=mod)
        self.config(menu=menubar)

    def _build_main(self) -> None:
        self.tabs = ttk.Notebook(self)
        # SDG sekmesi
        self.tab_sdg = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_sdg, text=self.lm.tr("sdg_tab_title", "SDG"))
        ttk.Label(self.tab_sdg, text=self.lm.tr("sdg_selection_label", "SDG Hedef/Alt Hedef/Gösterge Seçimi")).pack(anchor="w", padx=10, pady=10)
        ttk.Button(self.tab_sdg, text=self.lm.tr("btn_data_collection", "Veri Toplama"), command=lambda: messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("msg_data_collection", "Veri toplama ekranı (placeholder)"))).pack(padx=10,pady=5)
        ttk.Button(self.tab_sdg, text=self.lm.tr("btn_progress_view", "İlerleme Görünümü"), command=lambda: messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("msg_progress_view", "İlerleme ekranı (placeholder)"))).pack(padx=10,pady=5)

        # RAPORLAMA sekmesi
        self.tab_rep = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_rep, text=self.lm.tr("rep_tab_title", "RAPORLAMA"))
        ttk.Label(self.tab_rep, text=self.lm.tr("rep_types_label", "Rapor Tipleri")).pack(anchor="w", padx=10, pady=10)
        ttk.Button(self.tab_rep, text=self.lm.tr("btn_sdg_report", "SDG Raporu"), command=lambda: messagebox.showinfo(self.lm.tr("report_label", "Rapor"), self.lm.tr("msg_sdg_report", "SDG raporu üret (placeholder)"))).pack(padx=10,pady=5)
        ttk.Button(self.tab_rep, text=self.lm.tr("btn_sdg_gri_report", "SDG + GRI Raporu"), command=lambda: messagebox.showinfo(self.lm.tr("report_label", "Rapor"), self.lm.tr("msg_sdg_gri_report", "SDG+GRI raporu (placeholder)"))).pack(padx=10,pady=5)
        ttk.Button(self.tab_rep, text=self.lm.tr("btn_sdg_gri_tsrs_report", "SDG + GRI + TSRS Raporu"), command=lambda: messagebox.showinfo(self.lm.tr("report_label", "Rapor"), self.lm.tr("msg_sdg_gri_tsrs_report", "SDG+GRI+TSRS raporu (placeholder)"))).pack(padx=10,pady=5)

        # UI Etiketleri (Durum/Kategori) önizleme alanı
        preview_frame = ttk.LabelFrame(self.tab_rep, text=self.lm.tr("preview_frame_title", "UI Etiket Önizleme"))
        preview_frame.pack(fill="x", padx=10, pady=10)

        # Durum etiketleri
        ttk.Label(preview_frame, text=self.lm.tr("lbl_status_tags", "Durum Etiketleri:")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        
        status_labels = [
            self.lm.tr("status_full", "TAM FONKSİYONEL"),
            self.lm.tr("status_partial", "KISMİ TAMAMLANDI"),
            self.lm.tr("status_planned", "PLANLANDI"),
            self.lm.tr("status_missing", "EKSİK"),
            self.lm.tr("status_pending", "BEKLEMEDE")
        ]
        status_values = ", ".join(status_labels)
        ttk.Label(preview_frame, text=status_values).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        # Kategori etiketleri
        ttk.Label(preview_frame, text=self.lm.tr("lbl_category_tags", "Kategori Etiketleri:")).grid(row=0, column=1, sticky="w", padx=8, pady=(8, 2))
        
        category_labels = [
            self.lm.tr("category_innovation", "İnovasyon"),
            self.lm.tr("category_quality", "Kalite"),
            self.lm.tr("category_prioritization", "Önceliklendirme"),
            self.lm.tr("category_module", "Modül"),
            self.lm.tr("category_database", "Veritabanı"),
            self.lm.tr("category_reporting", "Raporlama")
        ]
        category_values = ", ".join(category_labels)
        ttk.Label(preview_frame, text=category_values).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))

        # Rapor başlık örneği
        ttk.Label(preview_frame, text=self.lm.tr("lbl_report_title", "Rapor Başlığı:")).grid(row=2, column=0, sticky="w", padx=8, pady=(2, 2))
        ttk.Label(preview_frame, text=self.lm.tr("title_gui_missing_files", "EKSİK GUI DOSYALARI")).grid(row=3, column=0, sticky="w", padx=8, pady=(0, 8))

        # YÖNETİM sekmesi
        self.tab_mgmt = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_mgmt, text=self.lm.tr("mgmt_tab_title", "YÖNETİM"))
        ttk.Label(self.tab_mgmt, text=self.lm.tr("mgmt_control_label", "Kullanıcı / Rol / Lisans / Modül Kontrol")).pack(anchor="w", padx=10, pady=10)
        ttk.Button(self.tab_mgmt, text=self.lm.tr("btn_role_matrix", "Rol/İzin Matrisi"), command=lambda: messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("msg_role_matrix", "CSV matrisi: yonetim/settings/role_permission_matrix.csv"))).pack(padx=10,pady=5)

        self.tabs.pack(expand=True, fill="both")

    def _switch_module(self, name) -> None:
        messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("module_selected", "{} modülü seçildi (placeholder).").format(name))

if __name__ == "__main__":
    app = SDGDesktopApp()
    app.mainloop()
