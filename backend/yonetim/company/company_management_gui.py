#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from utils.language_manager import LanguageManager


class CompanyManagementGUI:
    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(self.base_dir, "data", "sdg_desktop.sqlite")
        self.setup_ui()
        self.load_companies()

    def setup_ui(self) -> None:
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        title_frame = tk.Frame(main_frame, bg='#2F6DB2', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        title_label = ttk.Label(title_frame, text=" Firma Yönetimi")
        title_label.pack(side='left', padx=12)
        actions_frame = tk.Frame(title_frame, bg='#2c3e50')
        actions_frame.pack(side='right', padx=10)
        content_frame = tk.Frame(main_frame, bg='#ffffff', relief='ridge', bd=1)
        content_frame.pack(fill='both', expand=True)
        toolbar = tk.Frame(content_frame, bg='white')
        toolbar.pack(fill='x', padx=15, pady=10)
        tk.Button(toolbar, text=" Yeni Firma", command=self.add_company).pack(side='left', padx=5)
        tk.Button(toolbar, text=" Firma Düzenle", command=self.edit_company).pack(side='left', padx=5)
        tk.Button(toolbar, text=" Firma Sil", command=self.delete_company).pack(side='left', padx=5)
        tk.Button(toolbar, text=" Firma Detayları", command=self.show_company_details).pack(side='left', padx=5)
        list_frame = tk.Frame(content_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        columns = ('ID', 'Firma Adı', 'Sektör', 'Aktif', 'Oluşturulma')
        self.company_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.company_tree.heading(col, text=col)
            self.company_tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.company_tree.yview)
        self.company_tree.configure(yscrollcommand=scrollbar.set)
        self.company_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def load_companies(self) -> None:
        try:
            for item in self.company_tree.get_children():
                self.company_tree.delete(item)
            
            from modules.company.company_manager import CompanyManager
            manager = CompanyManager(self.db_path)
            
            # CompanyManager üzerinden şirketleri çek (Tutarlılık için)
            # get_all_companies: [(id, name, active), ...] döner (basit liste)
            # Ancak detaylı bilgi için doğrudan sorgu veya manager'a yeni metod eklemeliyiz.
            # Şimdilik manager.get_all_companies() kullanıp, eksik bilgileri (sektör) ayrıca alalım veya
            # manager sınıfını geliştirelim.
            # Pratik çözüm: Burada sorguyu düzeltmek.
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sektör kolonu kontrolü (sektor vs sektor_kod)
            try:
                cursor.execute("SELECT sektor FROM company_info LIMIT 1")
                sector_col = "sektor"
            except:
                sector_col = "sektor_kod"

            # company_info tablosundan verileri çek
            # aktif ve created_at (companies tablosundan join ile) alalım
            query = f"""
                SELECT 
                    ci.company_id, 
                    COALESCE(ci.ticari_unvan, ci.sirket_adi, 'Firma'), 
                    ci.{sector_col},
                    ci.aktif,
                    c.created_at
                FROM company_info ci
                LEFT JOIN companies c ON ci.company_id = c.id
                ORDER BY ci.company_id
            """
            cursor.execute(query)
            companies = cursor.fetchall()
            conn.close()
            
            for company in companies:
                company_id, name, sector, active, created_at = company
                
                # Formatlama
                active_str = "Evet" if active else "Hayır"
                created_str = created_at if created_at else "Bilinmiyor"
                
                self.company_tree.insert('', 'end', values=(
                    company_id,
                    name or 'Bilinmiyor',
                    sector or 'Belirtilmemiş',
                    active_str,
                    created_str
                ))
        except Exception as e:
            messagebox.showerror("Hata", f"Firmalar yüklenemedi: {e}")

    def add_company(self) -> None:
        dialog = tk.Toplevel(self.parent)
        dialog.title("Yeni Firma Ekle")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()
        title_label = tk.Label(dialog, text="Yeni Firma Ekle", font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)
        tk.Label(form_frame, text="Firma Adı:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        tk.Label(form_frame, text="Sektör:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        sector_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        sector_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        def save_company():
            name = name_entry.get().strip()
            sector = sector_entry.get().strip()
            if not name:
                messagebox.showerror("Hata", "Firma adı gereklidir!")
                return
            try:
                # Use CompanyManager for consistent creation
                from modules.company.company_manager import CompanyManager
                manager = CompanyManager(self.db_path)
                
                # create_company syncs with companies table and initializes modules
                cid = manager.create_company({
                    'sirket_adi': name,
                    'ticari_unvan': name,
                    'sektor': sector,
                    'aktif': 1
                })
                
                if cid:
                    messagebox.showinfo("Başarılı", "Firma başarıyla eklendi!")
                    dialog.destroy()
                    self.load_companies()
                else:
                    messagebox.showerror("Hata", "Firma oluşturulamadı. Logları kontrol edin.")
                    
            except Exception as e:
                messagebox.showerror("Hata", f"Firma ekleme hatası: {e}")
        save_btn = tk.Button(button_frame, text=self.lm.tr("btn_save", "Kaydet"), command=save_company, bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)
        cancel_btn = tk.Button(button_frame, text=self.lm.tr("btn_cancel", "İptal"), command=dialog.destroy, bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def edit_company(self) -> None:
        selected = self.company_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir firma seçin!")
            return
        item = self.company_tree.item(selected[0])
        company_data = item['values']
        company_id, name, sector, is_active, created_at = company_data
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Firma Düzenle: {name}")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()
        title_label = tk.Label(dialog, text=f"Firma Düzenle: {name}", font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=30, pady=20, fill='both', expand=True)
        tk.Label(form_frame, text="Firma Adı:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        tk.Label(form_frame, text="Sektör:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        sector_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        sector_entry.insert(0, sector)
        sector_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # company_info tablosunda aktiflik durumu olmadığı için bu alanı gizleyebiliriz veya pasif bırakabiliriz
        # Ancak basitlik için sadece kaldırıyoruz
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        def update_company():
            new_name = name_entry.get().strip()
            new_sector = sector_entry.get().strip()
            
            if not new_name:
                messagebox.showerror("Hata", "Firma adı gereklidir!")
                return
            try:
                from modules.company.company_manager import CompanyManager
                manager = CompanyManager(self.db_path)
                
                success = manager.update_company(company_id, {
                    'sirket_adi': new_name,
                    'ticari_unvan': new_name,
                    'sektor': new_sector
                })
                
                if success:
                    messagebox.showinfo("Başarılı", "Firma başarıyla güncellendi!")
                    dialog.destroy()
                    self.load_companies()
                else:
                    messagebox.showerror("Hata", "Güncelleme başarısız.")
            except Exception as e:
                messagebox.showerror("Hata", f"Firma güncelleme hatası: {e}")
        save_btn = tk.Button(button_frame, text=self.lm.tr("btn_update", "Güncelle"), command=update_company, bg='#28a745', fg='white', font=('Segoe UI', 10), padx=20)
        save_btn.pack(side='left', padx=5)
        cancel_btn = tk.Button(button_frame, text=self.lm.tr("btn_cancel", "İptal"), command=dialog.destroy, bg='#dc3545', fg='white', font=('Segoe UI', 10), padx=20)
        cancel_btn.pack(side='left', padx=5)

    def delete_company(self) -> None:
        selected = self.company_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir firma seçin!")
            return
        item = self.company_tree.item(selected[0])
        company_data = item['values']
        company_id, name, sector, is_active, created_at = company_data
        
        warning_msg = (
            f"{name} firmasını silmek istediğinizden emin misiniz?\n\n"
            "DİKKAT: Bu işlem geri alınamaz!\n\n"
            "Bu şirkete ait TÜM VERİLER (Kullanıcılar, raporlar, enerji kayıtları vb.) "
            "kalıcı olarak SİLİNECEKTİR!"
        )
        
        if messagebox.askyesno("Kritik İşlem Onayı", warning_msg, icon='warning'):
            try:
                from modules.company.company_manager import CompanyManager
                manager = CompanyManager(self.db_path)
                
                if manager.hard_delete_company(company_id):
                    messagebox.showinfo("Başarılı", f"{name} firması ve tüm verileri silindi!")
                    self.load_companies()
                else:
                    # Hata durumu (örn: varsayılan şirket)
                    messagebox.showerror("Hata", "Firma silinemedi! (Varsayılan şirket silinemez veya bir hata oluştu)")
                    
            except Exception as e:
                messagebox.showerror("Hata", f"Firma silme hatası: {e}")

    def show_company_details(self) -> None:
        selected = self.company_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir firma seçin!")
            return
        item = self.company_tree.item(selected[0])
        company_data = item['values']
        company_id, name, sector, is_active, created_at = company_data
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Firma Detayları: {name}")
        dialog.geometry("500x400")
        dialog.grab_set()
        title_label = tk.Label(dialog, text=f"Firma Detayları: {name}", font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        details_text = f"""
FIRMA BİLGİLERİ
================

Firma Adı: {name}
Sektör: {sector}
Durum: {is_active}
Oluşturulma Tarihi: {created_at}

KULLANICI İSTATİSTİKLERİ
========================
"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE company_id = ?", (company_id,))
            user_count = cursor.fetchone()[0]
            details_text += f"Toplam Kullanıcı: {user_count}\n"
            conn.close()
        except Exception as e:
            details_text += f"Hata: {e}\n"
        text_widget = tk.Text(content_frame, font=('Consolas', 10), wrap='word')
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', details_text)
        text_widget.config(state='disabled')
