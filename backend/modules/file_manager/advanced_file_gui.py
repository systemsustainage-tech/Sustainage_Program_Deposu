#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Dosya Yönetimi GUI
Çoklu dosya yükleme, klasör yapısı, etiketleme, versiyon kontrolü arayüzü
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from utils.language_manager import LanguageManager
from .advanced_file_manager import AdvancedFileManager


class AdvancedFileGUI:
    """Gelişmiş dosya yönetimi arayüzü"""

    def __init__(self, parent, db_path: str, company_id: int = 1, user_id: Optional[int] = None) -> None:
        """
        Args:
            parent: Ana pencere
            db_path: Veritabanı yolu
            company_id: Şirket ID
            user_id: Kullanıcı ID
        """
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.user_id = user_id
        self.lm = LanguageManager()
        self.file_manager = AdvancedFileManager(db_path)
        self.current_folder_id = None
        self.folder_breadcrumbs = []

        self.setup_gui()
        self.load_files()

    def setup_gui(self) -> None:
        """GUI bileşenlerini oluştur"""
        # Ana başlık
        title_frame = tk.Frame(self.parent, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text=" Gelişmiş Dosya Yönetimi",
            font=('Segoe UI', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Yükleme butonları
        upload_btn = tk.Button(
            title_frame,
            text=" Dosya Yükle",
            command=self.upload_files,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=15,
            pady=8
        )
        upload_btn.pack(side=tk.RIGHT, padx=5, pady=12)

        folder_btn = tk.Button(
            title_frame,
            text=self.lm.tr("create_folder", " Klasör Oluştur"),
            command=self.create_folder,
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=15,
            pady=8
        )
        folder_btn.pack(side=tk.RIGHT, padx=5, pady=12)

        # Toolbar
        toolbar_frame = tk.Frame(self.parent, bg='#ecf0f1', height=45)
        toolbar_frame.pack(fill=tk.X)
        toolbar_frame.pack_propagate(False)

        # Breadcrumb navigation
        self.breadcrumb_frame = tk.Frame(toolbar_frame, bg='#ecf0f1')
        self.breadcrumb_frame.pack(side=tk.LEFT, padx=20, pady=10)

        self.update_breadcrumbs()

        # Arama
        search_frame = tk.Frame(toolbar_frame, bg='#ecf0f1')
        search_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Label(search_frame, text="", bg='#ecf0f1', font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 10), width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.load_files())

        tk.Button(
            search_frame,
            text="Ara",
            command=self.load_files,
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 9),
            cursor='hand2',
            padx=10,
            pady=2
        ).pack(side=tk.LEFT)

        # Ana içerik alanı
        content_frame = tk.Frame(self.parent, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Sol panel: Klasör ağacı
        left_frame = tk.Frame(content_frame, bg='white', width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0), pady=20)

        tk.Label(
            left_frame,
            text=" Klasörler",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 10))

        # Klasör ağacı
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.folder_tree = ttk.Treeview(
            tree_frame,
            show='tree',
            yscrollcommand=scrollbar.set
        )
        self.folder_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.folder_tree.yview)

        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_select)
        self.folder_tree.bind('<Button-3>', self.show_folder_context_menu)

        self.load_folder_tree()

        # Sağ panel: Dosya listesi
        right_frame = tk.Frame(content_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Filtre ve görünüm
        filter_frame = tk.Frame(right_frame, bg='white')
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_frame, text="Etiket Filtresi:", bg='white', font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.tag_filter_var = tk.StringVar(value="Tümü")
        tag_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.tag_filter_var,
            state='readonly',
            width=20
        )
        tag_combo['values'] = ['Tümü'] + [tag['name'] for tag in self.file_manager.get_all_tags()]
        tag_combo.pack(side=tk.LEFT, padx=(0, 10))
        tag_combo.bind('<<ComboboxSelected>>', lambda e: self.load_files())

        # Dosya listesi (Treeview)
        list_frame = tk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.file_tree = ttk.Treeview(
            list_frame,
            columns=('name', 'size', 'type', 'version', 'tags', 'date'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.file_tree.yview)
        h_scrollbar.config(command=self.file_tree.xview)

        # Sütun başlıkları
        self.file_tree.heading('name', text=self.lm.tr("file_name", 'Dosya Adı'))
        self.file_tree.heading('size', text=self.lm.tr("size", 'Boyut'))
        self.file_tree.heading('type', text=self.lm.tr("type", 'Tür'))
        self.file_tree.heading('version', text=self.lm.tr("version", 'Versiyon'))
        self.file_tree.heading('tags', text=self.lm.tr("tags", 'Etiketler'))
        self.file_tree.heading('date', text=self.lm.tr("upload_date", 'Yüklenme Tarihi'))

        self.file_tree.column('name', width=250, anchor='w')
        self.file_tree.column('size', width=80, anchor='center')
        self.file_tree.column('type', width=60, anchor='center')
        self.file_tree.column('version', width=70, anchor='center')
        self.file_tree.column('tags', width=150, anchor='w')
        self.file_tree.column('date', width=120, anchor='center')

        self.file_tree.bind('<Double-Button-1>', self.on_file_double_click)
        self.file_tree.bind('<Button-3>', self.show_file_context_menu)

        # Durum çubuğu
        status_frame = tk.Frame(self.parent, bg='#34495e', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text=self.lm.tr("status_ready", "Hazır"),
            bg='#34495e',
            fg='white',
            font=('Segoe UI', 9),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def update_breadcrumbs(self) -> None:
        """Breadcrumb navigasyonunu güncelle"""
        # Temizle
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()

        # Kök
        root_btn = tk.Button(
            self.breadcrumb_frame,
            text=" " + self.lm.tr("root_folder", "Kök"),
            command=lambda: self.navigate_to_folder(None),
            bg='#ecf0f1',
            relief=tk.FLAT,
            font=('Segoe UI', 9),
            cursor='hand2'
        )
        root_btn.pack(side=tk.LEFT)

        # Yol
        for i, (folder_id, folder_name) in enumerate(self.folder_breadcrumbs):
            tk.Label(self.breadcrumb_frame, text="▸", bg='#ecf0f1', font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)

            btn = tk.Button(
                self.breadcrumb_frame,
                text=folder_name,
                command=lambda fid=folder_id: self.navigate_to_folder(fid),
                bg='#ecf0f1',
                relief=tk.FLAT,
                font=('Segoe UI', 9),
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT)

    def navigate_to_folder(self, folder_id: Optional[int]) -> None:
        """Klasöre git"""
        self.current_folder_id = folder_id

        # Breadcrumb'ı güncelle
        if folder_id is None:
            self.folder_breadcrumbs = []
        else:
            # Seçilen klasöre kadar breadcrumb'ı kırp
            found = False
            for i, (fid, fname) in enumerate(self.folder_breadcrumbs):
                if fid == folder_id:
                    self.folder_breadcrumbs = self.folder_breadcrumbs[:i+1]
                    found = True
                    break

            if not found:
                # Yeni klasör ekle (basit implementasyon)
                # Gerçek uygulamada klasör bilgisini veritabanından çekmeli
                pass

        self.update_breadcrumbs()
        self.load_files()

    def load_folder_tree(self) -> None:
        """Klasör ağacını yükle"""
        # Temizle
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        # Kök klasörleri yükle
        folders = self.file_manager.list_folders(self.company_id, None)

        for folder in folders:
            node = self.folder_tree.insert(
                '',
                tk.END,
                text=f" {folder['name']} ({folder['file_count']})",
                values=(folder['id'],)
            )

            # Alt klasörleri ekle (placeholder)
            self.folder_tree.insert(node, tk.END, text="...")

    def on_folder_select(self, event) -> None:
        """Klasör seçildiğinde"""
        selected = self.folder_tree.selection()
        if not selected:
            return

        values = self.folder_tree.item(selected[0], 'values')
        if values and values[0]:
            folder_id = values[0]
            self.navigate_to_folder(folder_id)

    def load_files(self) -> None:
        """Dosyaları yükle"""
        # Temizle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Filtreleri al
        search_term = self.search_var.get()
        tag_filter = self.tag_filter_var.get()
        tags = [tag_filter] if tag_filter != "Tümü" else None

        # Dosyaları getir
        files = self.file_manager.list_files(
            company_id=self.company_id,
            folder_id=self.current_folder_id,
            tags=tags,
            search_term=search_term
        )

        # Listeye ekle
        for file in files:
            # Boyutu formatla
            size_kb = file['size'] / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"

            # Etiketleri formatla
            tags_str = ', '.join([f"️{tag['name']}" for tag in file['tags']])

            # Versiyon
            version_str = f"v{file['version']}" + (f" (+{file['version_count']-1})" if file['version_count'] > 1 else "")

            # Tarihi formatla
            date_str = file['uploaded_at'][:10] if file['uploaded_at'] else ''

            self.file_tree.insert('', tk.END, values=(
                file['name'],
                size_str,
                file['type'],
                version_str,
                tags_str,
                date_str
            ), tags=(file['id'],))

        # Durum çubuğu
        self.status_label.config(text=f"{len(files)} {self.lm.tr('file_count_suffix', 'dosya')}")

    def create_folder(self) -> None:
        """Yeni klasör oluştur"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("new_folder", "Yeni Klasör"))
        dialog.geometry("450x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)  # Boyut değiştirilemez

        # Başlık
        tk.Label(
            dialog,
            text=self.lm.tr("create_new_folder", " Yeni Klasör Oluştur"),
            font=('Segoe UI', 14, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(fill=tk.X, pady=10)

        # Form
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr("folder_name", "Klasör Adı:"), font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=40)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()

        tk.Label(form_frame, text=self.lm.tr("description_optional", "Açıklama (Opsiyonel):"), font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        desc_text = tk.Text(form_frame, font=('Segoe UI', 10), height=4, wrap=tk.WORD)
        desc_text.pack(fill=tk.X)

        # Butonlar - Daha belirgin hale getirildi
        button_frame = tk.Frame(dialog, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=20, pady=(20, 20))

        def create() -> None:
            folder_name = name_entry.get().strip()
            if not folder_name:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("enter_folder_name", "Lütfen klasör adı girin"), parent=dialog)
                return

            description = desc_text.get('1.0', tk.END).strip()

            folder_id = self.file_manager.create_folder(
                company_id=self.company_id,
                folder_name=folder_name,
                parent_folder_id=self.current_folder_id,
                description=description,
                created_by=self.user_id
            )

            if folder_id:
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("folder_created_success", "Klasör başarıyla oluşturuldu!"), parent=dialog)
                dialog.destroy()
                self.load_folder_tree()
                self.load_files()
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("folder_create_error", "Klasör oluşturulamadı"), parent=dialog)

        # Oluştur butonu - Daha büyük ve belirgin
        create_btn = tk.Button(
            button_frame,
            text=self.lm.tr("btn_save", " KAYDET"),
            command=create,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            cursor='hand2',
            padx=30,
            pady=10,
            relief='raised',
            bd=2
        )
        create_btn.pack(side=tk.LEFT, padx=(0, 10))

        # İptal butonu
        cancel_btn = tk.Button(
            button_frame,
            text=self.lm.tr("btn_cancel", " İPTAL"),
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            cursor='hand2',
            padx=30,
            pady=10,
            relief='raised',
            bd=2
        )
        cancel_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Enter tuşu ile kaydetme
        def on_enter(event):
            create()

        name_entry.bind('<Return>', on_enter)
        desc_text.bind('<Control-Return>', on_enter)

    def upload_files(self) -> None:
        """Dosya yükle"""
        file_paths = filedialog.askopenfilenames(
            title=self.lm.tr("select_file", "Dosya Seç"),
            filetypes=[(self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
        )

        if not file_paths:
            return

        # Etiket seçimi dialogu
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("file_upload_title", "Dosya Yükleme"))
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=f" {len(file_paths)} {self.lm.tr('files_uploading', 'Dosya Yükleniyor')}",
            font=('Segoe UI', 14, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(fill=tk.X, pady=10)

        # Etiketler
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form_frame, text=self.lm.tr("tags_input", "Etiketler (virgülle ayırın):"), font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        tags_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        tags_entry.pack(fill=tk.X, pady=(0, 15))

        # Mevcut etiketler
        tk.Label(form_frame, text=self.lm.tr("existing_tags", "Mevcut Etiketler:"), font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        tags_frame = tk.Frame(form_frame)
        tags_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(tags_frame, height=100)
        scrollbar = ttk.Scrollbar(tags_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Etiketleri göster
        for tag in self.file_manager.get_all_tags():
            btn = tk.Button(
                scrollable_frame,
                text=f"️ {tag['name']} ({tag['usage_count']})",
                command=lambda t=tag['name']: tags_entry.insert(tk.END, f"{t}, "),
                bg=tag['color'],
                fg='white',
                font=('Segoe UI', 9),
                cursor='hand2',
                relief=tk.FLAT,
                padx=8,
                pady=4
            )
            btn.pack(side=tk.LEFT, padx=3, pady=3)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # İlerleme
        progress_frame = tk.Frame(dialog)
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=len(file_paths))
        progress_bar.pack(fill=tk.X)

        progress_label = tk.Label(progress_frame, text="", font=('Segoe UI', 9))
        progress_label.pack()

        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        def upload() -> None:
            tags_str = tags_entry.get().strip()
            tags = [t.strip() for t in tags_str.split(',') if t.strip()]

            uploaded_count = 0
            for i, file_path in enumerate(file_paths):
                progress_label.config(text=f"{self.lm.tr('uploading', 'Yükleniyor')}: {os.path.basename(file_path)}")
                progress_bar['value'] = i
                dialog.update()

                file_id = self.file_manager.upload_file(
                    company_id=self.company_id,
                    source_path=file_path,
                    folder_id=self.current_folder_id,
                    tags=tags,
                    uploaded_by=self.user_id
                )

                if file_id:
                    uploaded_count += 1

            progress_bar['value'] = len(file_paths)
            progress_label.config(text=f" {uploaded_count}/{len(file_paths)} {self.lm.tr('files_uploaded_count_short', 'dosya yüklendi')}")

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{uploaded_count} {self.lm.tr('files_uploaded_success', 'dosya başarıyla yüklendi!')}", parent=dialog)
            dialog.destroy()
            self.load_files()

        tk.Button(
            button_frame,
            text=self.lm.tr("upload", " Yükle"),
            command=upload,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text=self.lm.tr("btn_cancel", " İptal"),
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def on_file_double_click(self, event) -> None:
        """Dosyaya çift tıklandığında"""
        selected = self.file_tree.selection()
        if not selected:
            return

        file_id = self.file_tree.item(selected[0])['tags'][0]
        self.show_file_info(file_id)

    def show_file_info(self, file_id: int) -> None:
        """Dosya bilgilerini göster"""
        file_info = self.file_manager.get_file_info(file_id)
        if not file_info:
            messagebox.showerror("Hata", "Dosya bilgileri alınamadı")
            return

        # Bilgi penceresi
        dialog = tk.Toplevel(self.parent)
        dialog.title("Dosya Bilgileri")
        dialog.geometry("600x500")

        # ... (Dosya bilgi detayları için UI)

        messagebox.showinfo("Bilgi", f"Dosya: {file_info['name']}\n\nDetaylı bilgi penceresi yakında eklenecek", parent=dialog)

    def show_file_context_menu(self, event) -> None:
        """Dosya sağ tık menüsü"""
        # Context menu implementasyonu
        pass

    def show_folder_context_menu(self, event) -> None:
        """Klasör sağ tık menüsü"""
        # Context menu implementasyonu
        pass

