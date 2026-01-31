#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dosya Yönetimi GUI
Merkezi dosya yönetimi sistemi
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from utils.language_manager import LanguageManager
from config.icons import Icons


class FileManagerGUI:
    """Dosya Yönetimi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.current_user_id = current_user_id
        self.current_path = os.path.abspath(".")

        self.setup_ui()
        self.refresh_files()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık ve toolbar
        header_frame = tk.Frame(main_frame, bg='#34495e', height=50)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="📁 Dosya Yöneticisi",
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#34495e').pack(side='left', padx=15, pady=12)

        # Toolbar butonları
        toolbar = tk.Frame(header_frame, bg='#34495e')
        toolbar.pack(side='right', padx=15, pady=8)

        tk.Button(toolbar, text=Icons.LOADING, font=('Segoe UI', 10), bg='#2ecc71', fg='white',
                 relief='flat', padx=8, pady=3, command=self.refresh_files).pack(side='left', padx=2)

        tk.Button(toolbar, text="📁 Yeni Klasör", font=('Segoe UI', 9), bg='#3498db', fg='white',
                 relief='flat', padx=10, pady=3, command=self.create_folder).pack(side='left', padx=2)

        tk.Button(toolbar, text=f"{Icons.OUTBOX} Yükle", font=('Segoe UI', 9), bg='#9b59b6', fg='white',
                 relief='flat', padx=10, pady=3, command=self.upload_file).pack(side='left', padx=2)

        # Yol gösterici
        path_frame = tk.Frame(main_frame, bg='#ecf0f1', relief='sunken', bd=2)
        path_frame.pack(fill='x', pady=(0, 10))

        tk.Label(path_frame, text="📍 Konum:", font=('Segoe UI', 10, 'bold'),
                bg='#ecf0f1').pack(side='left', padx=10, pady=5)

        self.path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=self.path_var, font=('Segoe UI', 10),
                             state='readonly', bg='white')
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), pady=5)

        # Ana içerik bölümü - Panedwindow
        paned = tk.PanedWindow(main_frame, orient='horizontal', sashrelief='raised')
        paned.pack(fill='both', expand=True)

        # Sol panel - Dosya listesi
        left_frame = tk.Frame(paned, bg='white', relief='sunken', bd=2)
        paned.add(left_frame, minsize=400)

        # Dosya listesi (Treeview)
        columns = ('Ad', 'Tür', 'Boyut', 'Değiştirilme')
        self.file_tree = ttk.Treeview(left_frame, columns=columns, show='tree headings')

        # Sütun ayarları
        self.file_tree.heading('#0', text=Icons.FOLDER_OPEN)
        self.file_tree.heading('Ad', text='Dosya Adı')
        self.file_tree.heading('Tür', text='Tür')
        self.file_tree.heading('Boyut', text='Boyut')
        self.file_tree.heading('Değiştirilme', text='Değiştirilme Tarihi')

        self.file_tree.column('#0', width=30, minwidth=30)
        self.file_tree.column('Ad', width=200)
        self.file_tree.column('Tür', width=80)
        self.file_tree.column('Boyut', width=100)
        self.file_tree.column('Değiştirilme', width=150)

        # Scrollbar
        file_scroll = ttk.Scrollbar(left_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll.set)

        self.file_tree.pack(side='left', fill='both', expand=True)
        file_scroll.pack(side='right', fill='y')

        # Event bindings
        self.file_tree.bind('<Double-1>', self.on_double_click)
        self.file_tree.bind('<Button-3>', self.show_context_menu)

        # Sağ panel - Dosya detayları
        right_frame = tk.Frame(paned, bg='white', relief='sunken', bd=2)
        paned.add(right_frame, minsize=300)

        # Detay başlığı
        detail_header = tk.Frame(right_frame, bg='#bdc3c7')
        detail_header.pack(fill='x')

        tk.Label(detail_header, text=f"{Icons.CLIPBOARD} Dosya Detayları",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#bdc3c7').pack(pady=10)

        # Detay içeriği
        self.detail_frame = tk.Frame(right_frame, bg='white')
        self.detail_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # İlk durumda boş mesaj
        tk.Label(self.detail_frame, text="Dosya detaylarını görmek için\nbir dosya seçin",
                font=('Segoe UI', 11), fg='#7f8c8d', bg='white').pack(expand=True)

        # Alt durum çubuğu
        status_frame = tk.Frame(main_frame, bg='#95a5a6', height=25)
        status_frame.pack(fill='x', side='bottom', pady=(10, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text=f"{Icons.FOLDER_OPEN} Hazır",
                                   font=('Segoe UI', 9), bg='#95a5a6', anchor='w')
        self.status_label.pack(side='left', padx=10, pady=3)

    def refresh_files(self):
        """Dosya listesini yenile"""
        # Ağacı temizle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Mevcut yolu güncelle
        self.path_var.set(self.current_path)

        try:
            # Dizin içeriğini al
            items = os.listdir(self.current_path)

            # Önce klasörler
            folders = [item for item in items if os.path.isdir(os.path.join(self.current_path, item))]
            folders.sort()

            for folder in folders:
                full_path = os.path.join(self.current_path, folder)
                try:
                    stat = os.stat(full_path)
                    mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y %H:%M')

                    self.file_tree.insert('', 'end', text='📁', values=(
                        folder, 'Klasör', '-', mod_time
                    ))
                except Exception:
                    self.file_tree.insert('', 'end', text='📁', values=(
                        folder, 'Klasör', '-', 'Bilinmiyor'
                    ))

            # Sonra dosyalar
            files = [item for item in items if os.path.isfile(os.path.join(self.current_path, item))]
            files.sort()

            for file in files:
                full_path = os.path.join(self.current_path, file)
                try:
                    stat = os.stat(full_path)
                    size = self.format_size(stat.st_size)
                    mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y %H:%M')
                    ext = os.path.splitext(file)[1].lower()

                    # Dosya simgesi
                    if ext in ['.txt', '.log']:
                        icon = Icons.FILE
                    elif ext in ['.xlsx', '.xls', '.csv']:
                        icon = Icons.REPORT
                    elif ext in ['.pdf']:
                        icon = '📕'
                    elif ext in ['.jpg', '.png', '.gif']:
                        icon = '🖼️'
                    else:
                        icon = Icons.FILE

                    self.file_tree.insert('', 'end', text=icon, values=(
                        file, ext.upper() if ext else 'Dosya', size, mod_time
                    ))
                except Exception:
                    self.file_tree.insert('', 'end', text=Icons.FILE, values=(
                        file, 'Dosya', 'Bilinmiyor', 'Bilinmiyor'
                    ))

            self.status_label.config(text=f"{Icons.FOLDER_OPEN} {len(folders)} klasör, {len(files)} dosya")

        except PermissionError:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("permission_error", "Bu klasöre erişim izniniz yok!"))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('file_load_error', 'Dosyalar yüklenirken hata')}: {e}")

    def format_size(self, size_bytes):
        """Dosya boyutunu formatla"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024*1024*1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"

    def on_double_click(self, event):
        """Çift tıklama olayı"""
        selection = self.file_tree.selection()
        if not selection:
            return

        item = self.file_tree.item(selection[0])
        name = item['values'][0]
        type_col = item['values'][1]

        if type_col == 'Klasör':
            # Klasöre gir
            new_path = os.path.join(self.current_path, name)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_path = new_path
                self.refresh_files()

    def show_context_menu(self, event):
        """Sağ tık menüsü"""
        try:
            menu = tk.Menu(self.parent, tearoff=0)
            menu.add_command(label="Yeni Klasör", command=self.create_folder)
            menu.add_command(label="Dosya Yükle", command=self.upload_file)
            menu.add_separator()
            menu.add_command(label="Yenile", command=self.refresh_files)
            menu.add_command(label="Özellikler", command=lambda: messagebox.showinfo("Özellikler", "Dosya özellikleri"))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        except Exception as e:
            messagebox.showerror("Hata", f"Menü gösterilemedi: {e}")

    def create_folder(self):
        """Yeni klasör oluştur"""
        try:
            from tkinter import simpledialog
            folder_name = simpledialog.askstring(
                self.lm.tr("new_folder", "Yeni Klasör"), 
                self.lm.tr("folder_name", "Klasör adı:")
            )
            if folder_name:
                new_path = os.path.join(self.current_path, folder_name)
                os.makedirs(new_path, exist_ok=True)
                self.refresh_files()
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('folder_created', 'Klasör oluşturuldu')}: {folder_name}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('folder_create_error', 'Klasör oluşturulamadı')}: {e}")

    def upload_file(self):
        """Dosya yükle"""
        try:
            file_path = filedialog.askopenfilename(
                title=self.lm.tr("select_file", "Dosya Seç"),
                filetypes=[(self.lm.tr("all_files", "Tüm dosyalar"), "*.*")]
            )
            if file_path:
                dest_path = os.path.join(self.current_path, os.path.basename(file_path))
                import shutil
                shutil.copy2(file_path, dest_path)
                self.refresh_files()
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('file_uploaded', 'Dosya yüklendi')}: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('file_upload_error', 'Dosya yüklenemedi')}: {e}")
