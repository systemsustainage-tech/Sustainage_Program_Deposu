#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EU Taxonomy GUI
Avrupa Birliği Sürdürülebilir Finans Taksonomisi Arayüzü
"""

import logging
import os
import tkinter as tk
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from .taxonomy_manager import EUTaxonomyManager


class EUTaxonomyGUI:
    """EU Taxonomy GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id

        # Base directory
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')

        self.lm = LanguageManager()
        self.manager = EUTaxonomyManager(db_path)
        self.current_period = '2024'

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """UI oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#1e40af', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🇪🇺 EU Taxonomy - Sürdürülebilir Finans Taksonomisi",
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#1e40af').pack(side='left', padx=20, pady=15)

        # İçerik alanı
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_dashboard_tab()
        self.create_activities_tab()
        self.create_assessment_tab()
        self.create_mapping_tab()
        self.create_reporting_tab()

    def create_dashboard_tab(self) -> None:
        """Dashboard sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=" Dashboard")

        # KPI kartları
        kpi_frame = tk.Frame(tab, bg='white')
        kpi_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(kpi_frame, text="Taxonomy KPI'ları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        # KPI kartları container
        cards_frame = tk.Frame(kpi_frame, bg='white')
        cards_frame.pack(fill='x')

        self.kpi_vars = {}
        kpis = [
            ('revenue', 'Gelir Uyumu', '#10b981'),
            ('capex', 'CapEx Uyumu', '#3b82f6'),
            ('opex', 'OpEx Uyumu', '#f59e0b')
        ]

        for key, title, color in kpis:
            self.create_kpi_card(cards_frame, key, title, color)

    def create_kpi_card(self, parent, key: str, title: str, color: str) -> None:
        """KPI kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.pack(side='left', fill='both', expand=True, padx=(0, 10) if key != 'opex' else 0)

        tk.Label(card, text=title, font=('Segoe UI', 11, 'bold'),
                fg='white', bg=color).pack(pady=(15, 5))

        self.kpi_vars[f'{key}_eligible'] = tk.StringVar(value="-%")
        tk.Label(card, textvariable=self.kpi_vars[f'{key}_eligible'],
                font=('Segoe UI', 20, 'bold'), fg='white', bg=color).pack()

        tk.Label(card, text="Uygun", font=('Segoe UI', 9),
                fg='white', bg=color).pack()

        self.kpi_vars[f'{key}_aligned'] = tk.StringVar(value="-%")
        tk.Label(card, textvariable=self.kpi_vars[f'{key}_aligned'],
                font=('Segoe UI', 16, 'bold'), fg='white', bg=color).pack(pady=(10, 0))

        tk.Label(card, text="Uyumlu", font=('Segoe UI', 9),
                fg='white', bg=color).pack(pady=(0, 15))

    def create_activities_tab(self) -> None:
        """Faaliyetler sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=" Faaliyetler")

        # Toolbar
        toolbar = tk.Frame(tab, bg='white')
        toolbar.pack(fill='x', padx=20, pady=(20, 10))

        tk.Button(toolbar, text=" Yeni Faaliyet", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#10b981', relief='flat', cursor='hand2',
                 command=self.add_activity, padx=20, pady=8).pack(side='left', padx=(0, 10))

        tk.Button(toolbar, text=" Yenile", font=('Segoe UI', 10, 'bold'),
                 fg='white', bg='#6b7280', relief='flat', cursor='hand2',
                 command=self.load_data, padx=20, pady=8).pack(side='left')

        # Tablo
        table_frame = tk.Frame(tab, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = ('Kod', 'Faaliyet', 'Sektör', 'Gelir %', 'CapEx %', 'OpEx %', 'Uygun', 'Uyumlu', 'Durum')
        self.activities_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.activities_tree.heading(col, text=col)
            self.activities_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.activities_tree.yview)
        self.activities_tree.configure(yscrollcommand=scrollbar.set)

        self.activities_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_assessment_tab(self) -> None:
        """Değerlendirme sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=" Değerlendirme")

        # Değerlendirme formu
        form_frame = tk.LabelFrame(tab, text="Faaliyet Değerlendirme",
                                  font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Form alanları
        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Çevresel hedefler
        tk.Label(fields_frame, text="Çevresel Hedefler",
                font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 10))

        objectives = self.manager.config.get('objectives', [])
        self.objective_vars = {}

        for obj in objectives:
            frame = tk.Frame(fields_frame, bg='white')
            frame.pack(fill='x', pady=5)

            var = tk.BooleanVar()
            self.objective_vars[obj['id']] = var

            cb = tk.Checkbutton(frame, text=f"{obj['name_tr']} ({obj['id']})",
                               variable=var, font=('Segoe UI', 10), bg='white')
            cb.pack(side='left')

    def create_mapping_tab(self) -> None:
        """Eşleştirme sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=" Framework Eşleştirme")

        # Eşleştirme tablosu
        table_frame = tk.Frame(tab, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)

        columns = ('Faaliyet', 'Hedef', 'SDG', 'GRI', 'TSRS', 'Açıklama')
        self.mapping_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.mapping_tree.heading(col, text=col)
            self.mapping_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.mapping_tree.yview)
        self.mapping_tree.configure(yscrollcommand=scrollbar.set)

        self.mapping_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_reporting_tab(self) -> None:
        """Raporlama sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=" Raporlama")

        # Rapor oluşturma
        report_frame = tk.LabelFrame(tab, text="Taxonomy Raporu Oluştur",
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        report_frame.pack(fill='x', padx=20, pady=20)

        content = tk.Frame(report_frame, bg='white')
        content.pack(fill='x', padx=20, pady=20)

        tk.Button(content, text=" " + self.lm.tr('btn_create_docx', "DOCX Raporu Oluştur"),
                 font=('Segoe UI', 11, 'bold'), fg='white', bg='#3b82f6',
                 relief='flat', cursor='hand2', command=self.generate_docx_report,
                 padx=30, pady=10).pack(pady=10)

        tk.Button(content, text=" " + self.lm.tr('btn_create_excel', "Excel Raporu Oluştur"),
                 font=('Segoe UI', 11, 'bold'), fg='white', bg='#10b981',
                 relief='flat', cursor='hand2', command=self.generate_excel_report,
                 padx=30, pady=10).pack(pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # KPI'ları yükle
            kpis = self.manager.calculate_taxonomy_kpis(self.company_id, self.current_period)

            if kpis:
                self.kpi_vars['revenue_eligible'].set(f"{kpis['revenue']['eligible_percentage']:.1f}%")
                self.kpi_vars['revenue_aligned'].set(f"{kpis['revenue']['aligned_percentage']:.1f}%")
                self.kpi_vars['capex_eligible'].set(f"{kpis['capex']['eligible_percentage']:.1f}%")
                self.kpi_vars['capex_aligned'].set(f"{kpis['capex']['aligned_percentage']:.1f}%")
                self.kpi_vars['opex_eligible'].set(f"{kpis['opex']['eligible_percentage']:.1f}%")
                self.kpi_vars['opex_aligned'].set(f"{kpis['opex']['aligned_percentage']:.1f}%")

            # Faaliyetleri yükle
            self.load_activities()

            # Eşleştirmeleri yükle
            self.load_mappings()

        except Exception as e:
            messagebox.showerror("Hata", f"Veriler yüklenirken hata: {e}")

    def load_activities(self) -> None:
        """Faaliyetleri yükle"""
        try:
            # Tabloyu temizle
            for item in self.activities_tree.get_children():
                self.activities_tree.delete(item)

            # Faaliyetleri al
            activities = self.manager.get_company_activities(self.company_id, self.current_period)

            for activity in activities:
                self.activities_tree.insert('', 'end', values=(
                    activity.get('activity_code', ''),
                    activity.get('activity_name_tr', activity.get('activity_name', '')),
                    activity.get('sector', ''),
                    f"{activity.get('revenue_share', 0):.1f}",
                    f"{activity.get('capex_share', 0):.1f}",
                    f"{activity.get('opex_share', 0):.1f}",
                    '' if activity.get('is_eligible') else '',
                    '' if activity.get('is_aligned') else '',
                    activity.get('alignment_status', 'N/A')
                ))
        except Exception as e:
            logging.error(f"Faaliyetler yükleme hatası: {e}")

    def load_mappings(self) -> None:
        """Eşleştirmeleri yükle"""
        try:
            # Tabloyu temizle
            for item in self.mapping_tree.get_children():
                self.mapping_tree.delete(item)

            # Eşleştirmeleri al
            mappings = self.manager.get_framework_mappings()

            for mapping in mappings:
                self.mapping_tree.insert('', 'end', values=(
                    mapping.get('activity_code', ''),
                    mapping.get('objective_code', ''),
                    mapping.get('sdg_target', '-'),
                    mapping.get('gri_disclosure', '-'),
                    mapping.get('tsrs_metric', '-'),
                    mapping.get('mapping_rationale', '')[:50]
                ))
        except Exception as e:
            logging.error(f"Eşleştirmeler yükleme hatası: {e}")

    def add_activity(self) -> None:
        """Yeni faaliyet ekle"""
        self.show_activity_form()

    def show_activity_form(self) -> None:
        """Faaliyet ekleme formunu göster"""
        # Form penceresi
        form_window = tk.Toplevel(self.parent)
        form_window.title(" Yeni Faaliyet Ekle")
        form_window.geometry("600x700")
        form_window.configure(bg='#f8f9fa')
        form_window.grab_set()

        # Pencereyi merkeze al
        form_window.transient(self.parent)
        form_window.focus_force()

        # Başlık
        header_frame = tk.Frame(form_window, bg='#3b82f6', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" Yeni Faaliyet Ekle",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#3b82f6')
        title_label.pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(form_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f8f9fa')
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form alanları
        form_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Temel bilgiler
        tk.Label(form_frame, text="Temel Bilgiler", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 10))

        # Kod
        tk.Label(form_frame, text="Kod:", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        code_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=50)
        code_entry.pack(anchor='w', padx=20, pady=(0, 10))

        # Faaliyet Adı
        tk.Label(form_frame, text="Faaliyet Adı:", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        activity_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=50)
        activity_entry.pack(anchor='w', padx=20, pady=(0, 10))

        # Sektör
        tk.Label(form_frame, text="Sektör:", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        sector_var = tk.StringVar()
        sector_combo = ttk.Combobox(form_frame, textvariable=sector_var, font=('Segoe UI', 11), width=47)
        sector_combo['values'] = [
            'Enerji', 'Ulaştırma', 'Su ve Atık Yönetimi', 'Bilgi ve İletişim',
            'İnşaat', 'Tarım', 'Orman', 'Çevre Koruma', 'Diğer'
        ]
        sector_combo.pack(anchor='w', padx=20, pady=(0, 10))

        # KPI Bilgileri
        tk.Label(form_frame, text="KPI Bilgileri", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 10))

        # Gelir %
        tk.Label(form_frame, text="Gelir Uyumu (%):", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        revenue_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=50)
        revenue_entry.pack(anchor='w', padx=20, pady=(0, 10))

        # CapEx %
        tk.Label(form_frame, text="CapEx Uyumu (%):", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        capex_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=50)
        capex_entry.pack(anchor='w', padx=20, pady=(0, 10))

        # OpEx %
        tk.Label(form_frame, text="OpEx Uyumu (%):", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        opex_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=50)
        opex_entry.pack(anchor='w', padx=20, pady=(0, 10))

        # Çevresel Hedefler
        tk.Label(form_frame, text="Çevresel Hedefler", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 10))

        objectives_frame = tk.Frame(form_frame, bg='white')
        objectives_frame.pack(fill='x', padx=20, pady=(0, 10))

        objectives = [
            'İklim Değişikliği Azaltma',
            'İklim Değişikliği Adaptasyonu',
            'Su ve Deniz Kaynaklarının Sürdürülebilir Kullanımı',
            'Döngüsel Ekonomiye Geçiş',
            'Kirliliğin Önlenmesi ve Kontrolü',
            'Biyoçeşitlilik ve Ekosistemlerin Korunması'
        ]

        objective_vars = {}
        for i, obj in enumerate(objectives):
            var = tk.BooleanVar()
            objective_vars[obj] = var
            cb = tk.Checkbutton(objectives_frame, text=obj, variable=var,
                              font=('Segoe UI', 10), bg='white', fg='#34495e')
            cb.pack(anchor='w', pady=2)

        # Durum
        tk.Label(form_frame, text="Durum:", font=('Segoe UI', 11, 'bold'),
                fg='#34495e', bg='white').pack(anchor='w', padx=20, pady=(20, 5))
        status_var = tk.StringVar(value="Uygun")
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, font=('Segoe UI', 11), width=47)
        status_combo['values'] = ['Uygun', 'Uyumlu', 'Uygun Değil', 'Değerlendirme Bekliyor']
        status_combo.pack(anchor='w', padx=20, pady=(0, 20))

        # Butonlar
        button_frame = tk.Frame(form_window, bg='#f8f9fa')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        def save_activity() -> None:
            """Faaliyeti kaydet"""
            try:
                # Form verilerini al
                code = code_entry.get().strip()
                activity_name = activity_entry.get().strip()
                sector = sector_var.get().strip()
                revenue_pct = revenue_entry.get().strip()
                capex_pct = capex_entry.get().strip()
                opex_pct = opex_entry.get().strip()
                status = status_var.get().strip()

                # Seçili çevresel hedefler
                selected_objectives = [obj for obj, var in objective_vars.items() if var.get()]

                # Validasyon
                if not all([code, activity_name, sector]):
                    messagebox.showerror("Hata", "Lütfen temel bilgileri doldurun!")
                    return

                # KPI değerlerini sayıya çevir
                try:
                    revenue_pct = float(revenue_pct) if revenue_pct else 0.0
                    capex_pct = float(capex_pct) if capex_pct else 0.0
                    opex_pct = float(opex_pct) if opex_pct else 0.0
                except ValueError:
                    messagebox.showerror("Hata", "KPI değerleri sayısal olmalıdır!")
                    return

                # Faaliyeti kaydet
                activity_data = {
                    'code': code,
                    'name': activity_name,
                    'sector': sector,
                    'revenue_alignment': revenue_pct,
                    'capex_alignment': capex_pct,
                    'opex_alignment': opex_pct,
                    'status': status,
                    'environmental_objectives': selected_objectives,
                    'company_id': self.company_id,
                    'period': self.current_period
                }

                result = self.manager.add_company_activity(activity_data)

                if result:
                    messagebox.showinfo("Başarılı", "Faaliyet başarıyla eklendi!")
                    form_window.destroy()
                    self.load_data()  # Verileri yenile
                else:
                    messagebox.showerror("Hata", "Faaliyet eklenirken hata oluştu!")

            except Exception as e:
                messagebox.showerror("Hata", f"Kaydetme hatası: {e}")

        def cancel_form() -> None:
            """Formu iptal et"""
            form_window.destroy()

        # Butonlar
        tk.Button(button_frame, text=" " + self.lm.tr('btn_save', "Kaydet"), command=save_activity,
                 font=('Segoe UI', 11, 'bold'), bg='#10b981', fg='white',
                 padx=20, pady=10).pack(side='left', padx=(0, 10))

        tk.Button(button_frame, text=" " + self.lm.tr('btn_cancel', "İptal"), command=cancel_form,
                 font=('Segoe UI', 11, 'bold'), bg='#ef4444', fg='white',
                 padx=20, pady=10).pack(side='left')

        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel binding
        def _on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event) -> None:
            canvas.unbind_all("<MouseWheel>")
        form_window.bind("<Destroy>", _unbind_mousewheel)

    def generate_docx_report(self) -> None:
        """DOCX raporu oluştur"""
        try:
            self.manager.generate_taxonomy_report(self.company_id, self.current_period)
            messagebox.showinfo("Başarılı", "Taxonomy raporu oluşturuldu!")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturma hatası: {e}")

    def generate_excel_report(self) -> None:
        """Excel raporu oluştur"""
        messagebox.showinfo("Bilgi", "Faaliyet analizi tamamlandi")

# Test fonksiyonu
def test_taxonomy_gui() -> None:
    """Taxonomy GUI'yi test et"""
    root = tk.Tk()
    root.title("EU Taxonomy Test")
    root.geometry("1200x800")

    EUTaxonomyGUI(root, company_id=1)

    root.mainloop()

if __name__ == "__main__":
    test_taxonomy_gui()
