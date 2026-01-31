#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Denetçi Sistemi GUI
Dış denetçi yönetimi, belge merkezi, güvence raporları arayüzü
"""

import tkinter as tk
from tkinter import messagebox, ttk

from .auditor_system import AuditorSystem


class AuditorManagementGUI:
    """Denetçi yönetimi arayüzü"""

    def __init__(self, parent, db_path: str, company_id: int) -> None:
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.auditor_system = AuditorSystem(db_path)

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Başlık
        header = tk.Frame(self.parent, bg='#8e44ad', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=" Dış Doğrulama ve Denetçi Sistemi",
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#8e44ad').pack(side='left', padx=20, pady=20)

        tk.Label(header, text="External Auditor Management & Document Center",
                font=('Segoe UI', 10), fg='#ecf0f1', bg='#8e44ad').pack(side='left')

        # Notebook
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        # Sekmeler
        self.auditors_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.auditors_frame, text=" Denetçiler")

        self.documents_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.documents_frame, text=" Belge Merkezi")

        self.comments_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.comments_frame, text=" Yorumlar")

        self.assurance_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.assurance_frame, text=" Güvence Raporları")

        self.build_auditors_tab()
        self.build_documents_tab()
        self.build_comments_tab()
        self.build_assurance_tab()

    def build_auditors_tab(self) -> None:
        """Denetçiler sekmesi"""
        # Üst panel - Butonlar
        button_frame = tk.Frame(self.auditors_frame, bg='white')
        button_frame.pack(fill='x', padx=20, pady=15)

        tk.Button(button_frame, text=" Yeni Denetçi Ekle",
                 font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=self.add_auditor).pack(side='left', padx=5)

        tk.Button(button_frame, text="️ Düzenle",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=self.edit_auditor).pack(side='left', padx=5)

        tk.Button(button_frame, text=" Yenile",
                 font=('Segoe UI', 10), bg='#95a5a6', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=self.load_data).pack(side='left', padx=5)

        # Denetçi listesi
        list_frame = tk.LabelFrame(self.auditors_frame, text=" Kayıtlı Denetçiler",
                                   bg='white', font=('Segoe UI', 11, 'bold'))
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = ('ID', 'Ad Soyad', 'Şirket', 'Email', 'Seviye', 'Sertifika', 'Durum', 'Son Giriş')
        self.auditor_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.auditor_tree.heading(col, text=col)
            if col in ['Ad Soyad', 'Şirket', 'Email']:
                self.auditor_tree.column(col, width=150)
            else:
                self.auditor_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.auditor_tree.yview)
        self.auditor_tree.configure(yscrollcommand=scrollbar.set)

        self.auditor_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def build_documents_tab(self) -> None:
        """Belge merkezi sekmesi"""
        # Belge kategorileri
        categories = ['Finansal Veriler', 'Emisyon Verileri', 'İK Verileri',
                     'Raporlar', 'Sertifikalar', 'Diğer']

        # Kategori seçimi
        cat_frame = tk.Frame(self.documents_frame, bg='white')
        cat_frame.pack(fill='x', padx=20, pady=15)

        tk.Label(cat_frame, text="Kategori:", font=('Segoe UI', 10), bg='white').pack(side='left', padx=5)
        self.doc_category_var = tk.StringVar()
        cat_combo = ttk.Combobox(cat_frame, textvariable=self.doc_category_var,
                                values=categories, state='readonly', width=25)
        cat_combo.pack(side='left', padx=5)

        tk.Button(cat_frame, text=" Belge Yükle",
                 font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=self.upload_document).pack(side='left', padx=10)

        tk.Button(cat_frame, text=" Denetçiyle Paylaş",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=self.share_with_auditor).pack(side='left', padx=5)

        # Belge listesi
        list_frame = tk.LabelFrame(self.documents_frame, text=" Belge Merkezi",
                                   bg='white', font=('Segoe UI', 11, 'bold'))
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = ('ID', 'Belge Adı', 'Kategori', 'Boyut', 'Versiyon', 'Doğrulama', 'Paylaşım', 'Tarih')
        self.doc_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.doc_tree.heading(col, text=col)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=scrollbar.set)

        self.doc_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def build_comments_tab(self) -> None:
        """Yorumlar sekmesi"""
        # Yorumlar listesi
        columns = ('ID', 'Denetçi', 'Tür', 'Yorum', 'Önem', 'Durum', 'Tarih')
        self.comment_tree = ttk.Treeview(self.comments_frame, columns=columns,
                                        show='headings', height=15)

        for col in columns:
            self.comment_tree.heading(col, text=col)
            if col == 'Yorum':
                self.comment_tree.column(col, width=300)

        scrollbar = ttk.Scrollbar(self.comments_frame, orient='vertical', command=self.comment_tree.yview)
        self.comment_tree.configure(yscrollcommand=scrollbar.set)

        self.comment_tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20)

    def build_assurance_tab(self) -> None:
        """Güvence raporları sekmesi"""
        tk.Label(self.assurance_frame,
                text=" Güvence Raporları (Assurance Reports)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=20)

        tk.Label(self.assurance_frame,
                text="Denetçiler tarafından oluşturulan bağımsız güvence beyanları",
                font=('Segoe UI', 10), bg='white', fg='#666').pack()

        # Rapor listesi
        columns = ('Yıl', 'Denetçi', 'Rapor Türü', 'Güvence Seviyesi', 'Durum', 'Tarih')
        self.assurance_tree = ttk.Treeview(self.assurance_frame, columns=columns,
                                          show='headings', height=12)

        for col in columns:
            self.assurance_tree.heading(col, text=col)

        scrollbar = ttk.Scrollbar(self.assurance_frame, orient='vertical',
                                 command=self.assurance_tree.yview)
        self.assurance_tree.configure(yscrollcommand=scrollbar.set)

        self.assurance_tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20)

    def load_data(self) -> None:
        """Verileri yükle"""
        # Denetçiler
        for item in self.auditor_tree.get_children():
            self.auditor_tree.delete(item)

        auditors = self.auditor_system.get_auditor_list()
        for auditor in auditors:
            status = ' Aktif' if auditor['is_active'] else ' Pasif'
            self.auditor_tree.insert('', 'end', values=(
                auditor['id'],
                auditor['name'],
                auditor['company'],
                auditor['email'],
                auditor['level'],
                auditor['certification'] or 'N/A',
                status,
                auditor['last_login'] or 'Hiç giriş yok'
            ))

        # Yorumlar
        for item in self.comment_tree.get_children():
            self.comment_tree.delete(item)

        comments = self.auditor_system.get_auditor_comments()
        for comment in comments[:50]:  # İlk 50
            self.comment_tree.insert('', 'end', values=(
                comment['id'],
                comment['auditor'],
                comment['type'],
                comment['text'][:50] + '...' if len(comment['text']) > 50 else comment['text'],
                comment['severity'],
                comment['status'],
                comment['date']
            ))

    def add_auditor(self) -> None:
        """Denetçi ekle"""
        messagebox.showinfo("Yeni Denetçi",
                           "Denetçi ekleme formu açılacak.\n\n"
                           "Gerekli bilgiler:\n"
                           "- Ad Soyad\n"
                           "- Denetim Şirketi\n"
                           "- Email\n"
                           "- Kullanıcı Adı ve Şifre\n"
                           "- Yetki Seviyesi\n"
                           "- Erişim Tarihleri")

    def edit_auditor(self) -> None:
        """Denetçi düzenle"""
        selection = self.auditor_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen düzenlenecek denetçiyi seçin")
            return

        messagebox.showinfo("Düzenle", "Denetçi düzenleme özelliği geliştirme aşamasında")

    def upload_document(self) -> None:
        """Belge yükle"""
        messagebox.showinfo("Belge Yükle",
                           "Denetçiler için belge yükleme:\n\n"
                           "1. Dosya seçin\n"
                           "2. Kategori belirleyin\n"
                           "3. Versiyon numarası\n"
                           "4. 'Paylaş' seçeneği ile denetçilere açın")

    def share_with_auditor(self) -> None:
        """Belgeyi denetçiyle paylaş"""
        messagebox.showinfo("Paylaş", "Seçili belge tüm aktif denetçilerle paylaşılacak")

