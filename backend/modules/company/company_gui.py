#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sirket Yonetim GUI
Yeni sirket ekleme, duzenleme, listeleme
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from utils.tooltip import bind_treeview_header_tooltips

from .company_manager import CompanyManager


class CompanyGUI:
    """Sirket yonetim arayuzu"""

    def __init__(self, parent, company_id: int = 1):
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()

        # Firma bazında veritabanı path'i oluştur
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(base_dir, "data", "sdg_desktop.sqlite")

        self.manager = CompanyManager(self.db_path)

        self.theme = {
            'primary': '#2E8B57',
            'success': '#32CD32',
            'warning': '#FFA500',
            'danger': '#DC143C'
        }

        self.setup_ui()

    def setup_ui(self):
        """Ana UI"""
        # Ana frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Baslik
        title = ttk.Label(
            main_frame,
            text=self.lm.tr("company_management_title", "Sirket Yonetimi - Cok Sirketli Sistem"),
            font=('Segoe UI', 16, 'bold')
        )
        title.pack(pady=(0, 20))

        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(0, 20))

        ttk.Button(
            btn_frame,
            text=self.lm.tr("add_new_company_btn", "Yeni Sirket Ekle"),
            command=self.show_add_company
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text=self.lm.tr("list_companies_btn", "Sirketleri Listele"),
            command=self.show_company_list
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text=self.lm.tr("refresh_btn", "Yenile"),
            command=self.refresh
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text=self.lm.tr("delete_company_btn", "Şirketi Sil"),
            command=self.delete_selected_company
        ).pack(side='left', padx=5)

        # Icerik alani
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill='both', expand=True)

        # Baslangicta liste goster
        self.show_company_list()

    def clear_content(self):
        """Icerik temizle"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_company_list(self):
        """Sirket listesi"""
        self.clear_content()

        # Treeview
        columns = ('ID', 'Sirket Adi', 'Durum')
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')

        # Kolonlar
        self.tree.heading('ID', text=self.lm.tr("id_column", "ID"))
        self.tree.heading('Sirket Adi', text=self.lm.tr("company_name_column", "Sirket Adi"))
        self.tree.heading('Durum', text=self.lm.tr("status_column", "Durum"))

        self.tree.column('ID', width=50)
        self.tree.column('Sirket Adi', width=300)
        self.tree.column('Durum', width=100)

        # Veriler
        companies = self.manager.get_all_companies()
        for company_id, name, aktif in companies:
            durum = self.lm.tr("active_status", "Aktif") if aktif else self.lm.tr("passive_status", "Pasif")
            self.tree.insert('', 'end', values=(company_id, name, durum))

        self.tree.pack(fill='both', expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        try:
            bind_treeview_header_tooltips(self.tree)
        except Exception as e:
            logging.error(f"[CompanyGUI] Failed to bind tooltips: {e}")

        # Alt bilgi
        info_label = ttk.Label(
            self.content_frame,
            text=self.lm.tr("total_companies_format", "Toplam: {count} sirket").format(count=len(companies)),
            font=('Segoe UI', 10)
        )
        info_label.pack(pady=(10, 0))

    def delete_selected_company(self):
        """Secili sirketi sil"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                self.lm.tr("warning", "Uyarı"),
                self.lm.tr("select_company_warning", "Lütfen silinecek şirketi seçiniz.")
            )
            return

        item = self.tree.item(selected_item)
        company_id = item['values'][0]
        company_name = item['values'][1]

        if company_id == 1:
            messagebox.showwarning(
                self.lm.tr("warning", "Uyarı"),
                self.lm.tr("default_company_delete_error", "Varsayılan şirket silinemez!")
            )
            return

        # Onay mesaji - Kullanicinin istedigi ozel mesaj
        confirm = messagebox.askyesno(
            self.lm.tr("confirm_delete_title", "Şirket Silme Onayı"),
            f"DIKKAT! '{company_name}' şirketini sildiğinizde, şirkete ait TÜM VERİLER (Çevresel, Sosyal, Yönetişim, Raporlar vb.) KALICI OLARAK SİLİNECEKTİR.\n\nBu işlem geri alınamaz.\n\nOnaylıyor musunuz?",
            icon='warning'
        )

        if confirm:
            success = self.manager.hard_delete_company(company_id)
            if success:
                messagebox.showinfo(
                    self.lm.tr("success", "Başarılı"),
                    self.lm.tr("company_deleted_msg", "Şirket ve ilişkili tüm veriler başarıyla silindi.")
                )
                self.refresh()
            else:
                messagebox.showerror(
                    self.lm.tr("error", "Hata"),
                    self.lm.tr("company_delete_error", "Şirket silinirken bir hata oluştu.")
                )


    def show_add_company(self):
        """Yeni sirket ekleme formu"""
        # Dialog penceresi
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("new_company_title", "Yeni Sirket Ekle"))
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form frame
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # Baslik
        ttk.Label(
            form_frame,
            text=self.lm.tr("new_company_info_title", "Yeni Sirket Bilgileri"),
            font=('Segoe UI', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Alanlar
        fields = [
            ('sirket_adi', self.lm.tr("company_name_label", "Sirket Adi *")),
            ('ticari_unvan', self.lm.tr("commercial_title_label", "Ticari Unvan")),
            ('vergi_no', self.lm.tr("tax_no_label", "Vergi No")),
            ('vergi_dairesi', self.lm.tr("tax_office_label", "Vergi Dairesi")),
            ('adres', self.lm.tr("address_label", "Adres")),
            ('il', self.lm.tr("province_label", "Il")),
            ('ilce', self.lm.tr("district_label", "Ilce")),
            ('telefon', self.lm.tr("phone_label", "Telefon")),
            ('email', self.lm.tr("email_label", "E-posta")),
            ('website', self.lm.tr("website_label", "Website")),
            ('sektor', self.lm.tr("sector_label", "Sektor")),
            ('calisan_sayisi', self.lm.tr("employee_count_label", "Calisan Sayisi"))
        ]

        entries = {}
        row = 1

        for field, label in fields:
            ttk.Label(form_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)

            if field == 'adres':
                entry = tk.Text(form_frame, height=3, width=30)
                entry.grid(row=row, column=1, sticky='ew', pady=5)
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=row, column=1, sticky='ew', pady=5)

            entries[field] = entry
            row += 1

        # Butonlar
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        def save_company():
            # Veri topla
            company_data = {}

            for field, entry in entries.items():
                if isinstance(entry, tk.Text):
                    value = entry.get('1.0', tk.END).strip()
                else:
                    value = entry.get().strip()
                company_data[field] = value

            # Zorunlu alan kontrolu
            if not company_data.get('sirket_adi'):
                messagebox.showwarning(self.lm.tr("warning", "Uyari"), self.lm.tr("company_name_required", "Sirket adi zorunludur!"))
                return

            # Calisan sayisi integer'a cevir
            try:
                company_data['calisan_sayisi'] = int(company_data.get('calisan_sayisi', 0) or 0)
            except Exception:
                company_data['calisan_sayisi'] = 0

            # Kaydet
            company_id = self.manager.create_company(company_data)

            if company_id:
                messagebox.showinfo(self.lm.tr("success", "Basarili"),
                    self.lm.tr("company_created_msg", "Yeni sirket olusturuldu!\nSirket ID: {id}\n\nSirket klasoru: data/companies/{id}/").format(id=company_id))
                dialog.destroy()
                self.show_company_list()
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("company_creation_failed", "Sirket olusturulamadi!"))

        ttk.Button(btn_frame, text=self.lm.tr("btn_save", "Kaydet"), command=save_company).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr("btn_cancel", "Iptal"), command=dialog.destroy).pack(side='left', padx=5)

    def refresh(self):
        """Listeyi yenile"""
        self.show_company_list()

