#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Library GUI
Kurumsal Sürdürülebilirlik Politika Kütüphanesi Arayüzü
"""

import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .policy_manager import PolicyLibraryManager
from config.icons import Icons


class PolicyLibraryGUI:
    """Politika Kütüphanesi GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()

        # Base directory
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')

        self.manager = PolicyLibraryManager(db_path)

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """UI oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#6366f1', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=self.lm.tr('policy_lib_title', "Politika Kütüphanesi - Kurumsal Sürdürülebilirlik Politikaları"),
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#6366f1').pack(side='left', padx=20, pady=15)

        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text=self.lm.tr('btn_report_center', "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_policy).pack(side='left', padx=6, pady=6)
        # İçerik alanı
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_library_tab()
        self.create_company_policies_tab()
        self.create_compliance_matrix_tab()
        self.create_templates_tab()

    def create_library_tab(self) -> None:
        """Kütüphane sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('policy_tab_library', "Politika Kütüphanesi"))

        # Kategoriler ve şablonlar
        paned = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg='white')
        paned.pack(fill='both', expand=True, padx=20, pady=20)

        # Sol panel - Kategoriler
        left_panel = tk.LabelFrame(paned, text=self.lm.tr('policy_lbl_categories', "Kategoriler"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        paned.add(left_panel, width=250)

        # Kategori listesi
        self.category_listbox = tk.Listbox(left_panel, font=('Segoe UI', 11), height=20)
        self.category_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        # Sağ panel - Şablonlar
        right_panel = tk.LabelFrame(paned, text=self.lm.tr('policy_lbl_templates', "Politika Şablonları"),
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        paned.add(right_panel)

        # Toolbar
        toolbar = tk.Frame(right_panel, bg='white')
        toolbar.pack(fill='x', padx=10, pady=10)

        ttk.Button(toolbar, text=self.lm.tr('policy_btn_new_template', "Yeni Şablon"), style='Primary.TButton', command=self.add_template).pack(side='left', padx=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('policy_btn_create_from_template', "Şablondan Politika Oluştur"), style='Primary.TButton', command=self.create_policy_from_template).pack(side='left')

        # Şablon tablosu
        table_frame = tk.Frame(right_panel, bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        columns = (self.lm.tr('policy_col_code', 'Kod'), self.lm.tr('policy_col_template_name', 'Şablon Adı'), self.lm.tr('policy_col_category', 'Kategori'), self.lm.tr('policy_col_version', 'Versiyon'), self.lm.tr('policy_col_lang', 'Dil'))
        self.templates_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.templates_tree.heading(col, text=col)
            self.templates_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=scrollbar.set)

        self.templates_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_company_policies_tab(self) -> None:
        """Şirket politikaları sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('policy_tab_company', "Şirket Politikaları"))

        # Toolbar
        toolbar = tk.Frame(tab, bg='white')
        toolbar.pack(fill='x', padx=20, pady=(20, 10))

        ttk.Button(toolbar, text=self.lm.tr('policy_btn_new_policy', "Yeni Politika"), style='Primary.TButton', command=self.add_company_policy).pack(side='left', padx=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('policy_btn_edit', "Düzenle"), style='Primary.TButton', command=self.edit_company_policy).pack(side='left', padx=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('policy_btn_map_module', "Modüle Bağla"), style='Primary.TButton', command=self.map_to_module).pack(side='left', padx=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('policy_btn_refresh', "Yenile"), style='Primary.TButton', command=self.load_company_policies).pack(side='left')

        # Tablo
        table_frame = tk.Frame(tab, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = (self.lm.tr('policy_col_id', 'ID'), self.lm.tr('policy_col_policy_name', 'Politika Adı'), self.lm.tr('policy_col_code', 'Kod'), self.lm.tr('policy_col_category', 'Kategori'), self.lm.tr('policy_col_version', 'Versiyon'), self.lm.tr('policy_col_status', 'Durum'), self.lm.tr('policy_col_approval_date', 'Onay Tarihi'), self.lm.tr('policy_col_update', 'Güncelleme'))
        self.policies_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Kolon başlıkları
        for col in columns:
            self.policies_tree.heading(col, text=col)
            if col == self.lm.tr('policy_col_id', 'ID'):
                self.policies_tree.column(col, width=0, stretch=False)
            else:
                self.policies_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.policies_tree.yview)
        self.policies_tree.configure(yscrollcommand=scrollbar.set)

        self.policies_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_compliance_matrix_tab(self) -> None:
        """Uyum matrisi sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('policy_tab_compliance', "Uyum Matrisi"))

        # Açıklama
        desc_frame = tk.Frame(tab, bg='#e0f2fe', relief='solid', bd=1)
        desc_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(desc_frame, text=f"{Icons.INFO} {self.lm.tr('policy_lbl_compliance_title', 'Uyum Matrisi')}", font=('Segoe UI', 12, 'bold'),
                fg='#0369a1', bg='#e0f2fe').pack(anchor='w', padx=15, pady=(10, 5))

        tk.Label(desc_frame,
                text=self.lm.tr('policy_lbl_compliance_desc', "Politika gereksinimlerinin modül metrikleri ile eşleştirilmesi ve uyum durumunun takibi"),
                font=('Segoe UI', 10), fg='#0c4a6e', bg='#e0f2fe', wraplength=800).pack(anchor='w', padx=15, pady=(0, 10))

        # Toolbar
        toolbar = tk.Frame(tab, bg='white')
        toolbar.pack(fill='x', padx=20, pady=(0, 10))

        ttk.Button(toolbar, text=self.lm.tr('policy_btn_new_requirement', "Yeni Gereksinim"), style='Primary.TButton', command=self.add_compliance_requirement).pack(side='left', padx=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('policy_btn_update_status', "Durum Güncelle"), style='Primary.TButton', command=self.update_compliance_status).pack(side='left', padx=(0, 10))
        ttk.Button(toolbar, text=self.lm.tr('policy_btn_refresh', "Yenile"), style='Primary.TButton', command=self.load_compliance_matrix).pack(side='left')

        # Tablo
        table_frame = tk.Frame(tab, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = (self.lm.tr('policy_col_id', 'ID'), self.lm.tr('policy_col_policy_name', 'Politika'), self.lm.tr('policy_col_requirement', 'Gereksinim'), self.lm.tr('policy_col_module', 'Modül'), self.lm.tr('policy_col_metric', 'Metrik'), self.lm.tr('policy_col_target', 'Hedef'), self.lm.tr('policy_col_current', 'Mevcut'), self.lm.tr('policy_col_status', 'Durum'), self.lm.tr('policy_col_responsible', 'Sorumlu'))
        self.compliance_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Kolon başlıkları
        for col in columns:
            self.compliance_tree.heading(col, text=col)
            if col == self.lm.tr('policy_col_id', 'ID'):
                self.compliance_tree.column(col, width=0, stretch=False)
            else:
                self.compliance_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.compliance_tree.yview)
        self.compliance_tree.configure(yscrollcommand=scrollbar.set)

        self.compliance_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_templates_tab(self) -> None:
        """Şablon yönetimi sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('policy_tab_template_mgmt', "️ Şablon Yönetimi"))

        # Şablon yükleme
        upload_frame = tk.LabelFrame(tab, text=self.lm.tr('policy_lbl_template_upload', "Şablon Yükleme"),
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        upload_frame.pack(fill='x', padx=20, pady=20)

        content = tk.Frame(upload_frame, bg='white')
        content.pack(fill='x', padx=20, pady=20)

        tk.Label(content, text=self.lm.tr('policy_lbl_upload_desc', "Politika şablonlarını (DOCX, PDF) yükleyebilirsiniz:"),
                font=('Segoe UI', 11), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        ttk.Button(content, text=self.lm.tr('policy_btn_select_file', " Dosya Seç ve Yükle"), style='Primary.TButton', command=self.upload_template_file).pack(anchor='w')

        # Varsayılan şablonlar
        defaults_frame = tk.LabelFrame(tab, text=self.lm.tr('policy_lbl_default_templates', "Varsayılan Şablonlar"),
                                      font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        defaults_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        defaults_content = tk.Frame(defaults_frame, bg='white')
        defaults_content.pack(fill='both', expand=True, padx=20, pady=20)

        # Varsayılan şablon listesi
        default_templates = [
            (self.lm.tr('policy_tpl_env', " Çevre Politikası"), self.lm.tr('policy_tpl_env_desc', "Çevresel sürdürülebilirlik taahhütleri")),
            (self.lm.tr('policy_tpl_social', " Sosyal Sorumluluk Politikası"), self.lm.tr('policy_tpl_social_desc', "Sosyal etki ve toplum ilişkileri")),
            (self.lm.tr('policy_tpl_ethics', "️ Etik Kurallar"), self.lm.tr('policy_tpl_ethics_desc', "İş etiği ve davranış kuralları")),
            (self.lm.tr('policy_tpl_supply', " Tedarik Zinciri Politikası"), self.lm.tr('policy_tpl_supply_desc', "Sorumlu tedarik zinciri yönetimi")),
            (self.lm.tr('policy_tpl_hr', " İnsan Kaynakları Politikası"), self.lm.tr('policy_tpl_hr_desc', "Çalışan hakları ve İSG")),
            (self.lm.tr('policy_tpl_quality', f"{Icons.STAR} Kalite Politikası"), self.lm.tr('policy_tpl_quality_desc', "Kalite yönetim sistemi")),
            (self.lm.tr('policy_tpl_risk', "️ Risk Yönetimi Politikası"), self.lm.tr('policy_tpl_risk_desc', "Kurumsal risk yönetimi")),
            (self.lm.tr('policy_tpl_data', " Veri Gizliliği Politikası"), self.lm.tr('policy_tpl_data_desc', "Kişisel verilerin korunması"))
        ]

        for i, (title, desc) in enumerate(default_templates):
            template_card = tk.Frame(defaults_content, bg='#f8f9fa', relief='solid', bd=1)
            template_card.pack(fill='x', pady=5)

            tk.Label(template_card, text=title, font=('Segoe UI', 11, 'bold'),
                    fg='#2c3e50', bg='#f8f9fa').pack(anchor='w', padx=15, pady=(10, 5))

            tk.Label(template_card, text=desc, font=('Segoe UI', 9),
                    fg='#6b7280', bg='#f8f9fa').pack(anchor='w', padx=15, pady=(0, 10))

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_categories()
        self.load_templates()
        self.load_company_policies()
        self.load_compliance_matrix()

    def load_categories(self) -> None:
        """Kategorileri yükle"""
        try:
            self.category_listbox.delete(0, tk.END)

            categories = self.manager.get_categories()
            for cat in categories:
                icon = cat.get('icon', '')
                name = cat.get('category_name_tr', cat.get('category_name', ''))
                self.category_listbox.insert(tk.END, f"{icon} {name}")

            # İlk kategoriyi seç
            if categories:
                self.category_listbox.selection_set(0)
                self.on_category_select(None)

        except Exception as e:
            logging.error(f"Kategoriler yükleme hatası: {e}")

    def load_templates(self, category_id: int = None) -> None:
        """Şablonları yükle"""
        try:
            # Tabloyu temizle
            for item in self.templates_tree.get_children():
                self.templates_tree.delete(item)

            # Şablonları al
            templates = self.manager.get_templates(category_id)

            for template in templates:
                self.templates_tree.insert('', 'end', values=(
                    template.get('template_code', ''),
                    template.get('template_name_tr', template.get('template_name', '')),
                    template.get('category_name_tr', ''),
                    template.get('version', '1.0'),
                    template.get('language', 'tr').upper()
                ))
        except Exception as e:
            logging.error(f"Şablonlar yükleme hatası: {e}")

    def load_company_policies(self) -> None:
        """Şirket politikalarını yükle"""
        try:
            # Tabloyu temizle
            for item in self.policies_tree.get_children():
                self.policies_tree.delete(item)

            # Politikaları al
            policies = self.manager.get_company_policies(self.company_id)

            for policy in policies:
                self.policies_tree.insert('', 'end', values=(
                    policy.get('id', ''),
                    policy.get('policy_name', ''),
                    policy.get('policy_code', ''),
                    policy.get('category_name_tr', ''),
                    policy.get('version', '1.0'),
                    policy.get('status', 'Draft'),
                    policy.get('approval_date', '-'),
                    policy.get('updated_at', '')[:10] if policy.get('updated_at') else '-'
                ))
        except Exception as e:
            logging.error(f"Şirket politikaları yükleme hatası: {e}")

    def load_compliance_matrix(self) -> None:
        """Uyum matrisini yükle"""
        try:
            # Tabloyu temizle
            for item in self.compliance_tree.get_children():
                self.compliance_tree.delete(item)

            # Matrisi al
            matrix = self.manager.get_compliance_matrix(self.company_id)

            for item in matrix:
                self.compliance_tree.insert('', 'end', values=(
                    item.get('id', ''),
                    item.get('policy_name', '')[:20],
                    item.get('requirement', '')[:30],
                    item.get('module_name', ''),
                    item.get('metric_name', '')[:20],
                    item.get('target_value', ''),
                    item.get('current_value', ''),
                    item.get('compliance_status', ''),
                    item.get('responsible_person', '')
                ))
        except Exception as e:
            logging.error(f"Uyum matrisi yükleme hatası: {e}")

    def on_category_select(self, event) -> None:
        """Kategori seçildiğinde"""
        selection = self.category_listbox.curselection()
        if selection:
            # Kategori ID'sini al (basitleştirilmiş)
            self.load_templates()

    def add_template(self) -> None:
        """Yeni şablon ekle"""
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), "Yeni şablon ekleme formu açılacak")

    def create_policy_from_template(self) -> None:
        """Şablondan politika oluştur"""
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), "Şablondan politika oluşturma formu açılacak")

    def add_company_policy(self) -> None:
        """Yeni şirket politikası ekle - İŞLEVSEL"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('policy_title_add_new', "Yeni Politika Ekle"))
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Başlık
        tk.Label(dialog, text=self.lm.tr('policy_title_add_new', " Yeni Politika Ekle"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50').pack(pady=20)

        # Form alanları
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Politika Adı
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_policy_name', "Politika Adı:"), font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.policy_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.policy_name_var, width=40).grid(row=0, column=1, sticky='ew', pady=5)

        # Politika Kodu
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_policy_code', "Politika Kodu:"), font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.policy_code_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.policy_code_var, width=40).grid(row=1, column=1, sticky='ew', pady=5)

        # Kategori
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_category', "Kategori:"), font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var,
                                    values=["Etik ve Uyum", "Kalite", "Risk Yönetimi", "Sosyal Politika",
                                           "Tedarik Zinciri", "Yönetişim Politikası", "Çevre Politikası", "İnsan Kaynakları"])
        category_combo.grid(row=2, column=1, sticky='ew', pady=5)

        # Versiyon
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_version', "Versiyon:"), font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        self.version_var = tk.StringVar(value="1.0")
        tk.Entry(form_frame, textvariable=self.version_var, width=40).grid(row=3, column=1, sticky='ew', pady=5)

        # Durum
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_status', "Durum:"), font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.status_var = tk.StringVar(value="Draft")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var,
                                  values=["Draft", "Review", "Approved", "Active", "Archived"])
        status_combo.grid(row=4, column=1, sticky='ew', pady=5)

        # Açıklama
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_description', "Açıklama:"), font=('Segoe UI', 10, 'bold')).grid(row=5, column=0, sticky='nw', pady=5)
        self.description_text = tk.Text(form_frame, height=4, width=40, wrap=tk.WORD)
        self.description_text.grid(row=5, column=1, sticky='ew', pady=5)

        # Grid yapılandırması
        form_frame.grid_columnconfigure(1, weight=1)

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(button_frame, text=self.lm.tr('btn_save', " Kaydet"), style='Primary.TButton', command=lambda: self.save_policy(dialog)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=dialog.destroy).pack(side='left')

    def save_policy(self, dialog) -> None:
        """Politikayı kaydet"""
        try:
            # Veri doğrulama
            if not self.policy_name_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_policy_name_empty', "Politika adı boş olamaz!"))
                return

            if not self.policy_code_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_policy_code_empty', "Politika kodu boş olamaz!"))
                return

            # Veri hazırla
            policy_data = {
                'name': self.policy_name_var.get().strip(),
                'code': self.policy_code_var.get().strip(),
                'category': self.category_var.get().strip(),
                'version': self.version_var.get().strip(),
                'status': self.status_var.get().strip(),
                'description': self.description_text.get('1.0', tk.END).strip(),
                'company_id': self.company_id
            }

            # Veritabanına kaydet
            success = self.manager.add_company_policy(policy_data)

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_policy_saved', "Politika başarıyla kaydedildi!"))
                dialog.destroy()
                self.load_data()  # Verileri yenile
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_policy_save_failed', "Politika kaydedilemedi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('err_policy_save_exception', 'Politika kaydedilirken hata oluştu')}: {e}")

    def edit_company_policy(self) -> None:
        """Şirket politikasını düzenle"""
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_policy_edit_form', "Politika düzenleme formu açılacak"))

    def map_to_module(self) -> None:
        """Politikayı modüle bağla"""
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_policy_map_form', "Modül eşleştirme formu açılacak"))

    def add_compliance_requirement(self) -> None:
        """Yeni uyum gereksinimi ekle - İŞLEVSEL"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('policy_title_add_requirement', "Yeni Uyum Gereksinimi Ekle"))
        dialog.geometry("700x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Başlık
        tk.Label(dialog, text=self.lm.tr('policy_title_add_requirement', " Yeni Uyum Gereksinimi Ekle"),
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50').pack(pady=20)

        # Form alanları
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Politika
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_policy', "Politika:"), font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.requirement_policy_var = tk.StringVar()
        policy_combo = ttk.Combobox(form_frame, textvariable=self.requirement_policy_var,
                                  values=["Test Çevre Politikası", "Etik Kurallar", "Kalite Politikası"])
        policy_combo.grid(row=0, column=1, sticky='ew', pady=5)

        # Gereksinim
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_name', "Gereksinim:"), font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.requirement_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.requirement_name_var, width=50).grid(row=1, column=1, sticky='ew', pady=5)

        # Modül
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_module', "Modül:"), font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.requirement_module_var = tk.StringVar()
        module_combo = ttk.Combobox(form_frame, textvariable=self.requirement_module_var,
                                  values=["SDG", "GRI", "TCFD", "SASB", "UNGC", "ISSB", "Çevre", "Sosyal", "Yönetişim"])
        module_combo.grid(row=2, column=1, sticky='ew', pady=5)

        # Metrik
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_metric', "Metrik:"), font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        self.requirement_metric_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.requirement_metric_var, width=50).grid(row=3, column=1, sticky='ew', pady=5)

        # Hedef
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_target', "Hedef:"), font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.requirement_target_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.requirement_target_var, width=50).grid(row=4, column=1, sticky='ew', pady=5)

        # Mevcut Değer
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_current', "Mevcut Değer:"), font=('Segoe UI', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=5)
        self.requirement_current_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.requirement_current_var, width=50).grid(row=5, column=1, sticky='ew', pady=5)

        # Durum
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_status', "Durum:"), font=('Segoe UI', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=5)
        self.requirement_status_var = tk.StringVar(value="Uyumlu")
        status_combo = ttk.Combobox(form_frame, textvariable=self.requirement_status_var,
                                  values=["Uyumlu", "Kısmen Uyumlu", "Uyumsuz", "Değerlendiriliyor"])
        status_combo.grid(row=6, column=1, sticky='ew', pady=5)

        # Sorumlu
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_req_responsible', "Sorumlu:"), font=('Segoe UI', 10, 'bold')).grid(row=7, column=0, sticky='w', pady=5)
        self.requirement_responsible_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.requirement_responsible_var, width=50).grid(row=7, column=1, sticky='ew', pady=5)

        # Açıklama
        tk.Label(form_frame, text=self.lm.tr('policy_lbl_description', "Açıklama:"), font=('Segoe UI', 10, 'bold')).grid(row=8, column=0, sticky='nw', pady=5)
        self.requirement_description_text = tk.Text(form_frame, height=3, width=50, wrap=tk.WORD)
        self.requirement_description_text.grid(row=8, column=1, sticky='ew', pady=5)

        # Grid yapılandırması
        form_frame.grid_columnconfigure(1, weight=1)

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(button_frame, text=self.lm.tr('btn_save', " Kaydet"), style='Primary.TButton', command=lambda: self.save_compliance_requirement(dialog)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=dialog.destroy).pack(side='left')

    def open_report_center_policy(self) -> None:
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
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_report_center_open', "Rapor Merkezi açılamadı:\n{}").format(e))
            logging.error(f"Error opening report center: {e}")

    def save_compliance_requirement(self, dialog) -> None:
        """Uyum gereksinimini kaydet"""
        try:
            # Veri doğrulama
            if not self.requirement_name_var.get().strip():
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_req_name_empty', "Gereksinim adı boş olamaz!"))
                return

            # Veri hazırla
            requirement_data = {
                'policy': self.requirement_policy_var.get().strip(),
                'requirement': self.requirement_name_var.get().strip(),
                'module': self.requirement_module_var.get().strip(),
                'metric': self.requirement_metric_var.get().strip(),
                'target': self.requirement_target_var.get().strip(),
                'current': self.requirement_current_var.get().strip(),
                'status': self.requirement_status_var.get().strip(),
                'responsible': self.requirement_responsible_var.get().strip(),
                'description': self.requirement_description_text.get('1.0', tk.END).strip(),
                'company_id': self.company_id
            }

            # Veritabanına kaydet
            success = self.manager.add_compliance_requirement(requirement_data)

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_req_saved', "Uyum gereksinimi başarıyla kaydedildi!"))
                dialog.destroy()
                self.load_data()  # Verileri yenile
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('err_req_save_failed', "Uyum gereksinimi kaydedilemedi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('err_req_save_exception', 'Uyum gereksinimi kaydedilirken hata oluştu')}: {e}")

    def update_compliance_status(self) -> None:
        """Uyum durumunu güncelle"""
        messagebox.showinfo(self.lm.tr('info', "Bilgi"), self.lm.tr('msg_req_update_form', "Uyum durumu güncelleme formu açılacak"))

    def upload_template_file(self) -> None:
        """Şablon dosyası yükle"""
        filename = filedialog.askopenfilename(
            title=self.lm.tr('title_select_template', "Politika Şablonu Seç"),
            filetypes=[(self.lm.tr('file_word', "Word Dosyaları"), "*.docx"), (self.lm.tr('file_pdf', "PDF Dosyaları"), "*.pdf"), (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")]
        )

        if filename:
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_file_selected', f"Dosya seçildi: {os.path.basename(filename)}\n\nŞablon yükleme işlemi tamamlanacak.").format(os.path.basename(filename)))

# Test fonksiyonu
def test_policy_gui() -> None:
    """Policy GUI'yi test et"""
    root = tk.Tk()
    root.title("Politika Kütüphanesi Test")
    root.geometry("1200x800")

    PolicyLibraryGUI(root, company_id=1)

    root.mainloop()

if __name__ == "__main__":
    test_policy_gui()
