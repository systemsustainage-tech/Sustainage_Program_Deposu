#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dosya Yükleme GUI
Görevlere dosya ekleme arayüzü
"""

import os
import platform
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from utils.language_manager import LanguageManager
from .file_manager import FileManager


class FileUploadGUI:
    """
    Dosya yükleme ve yönetim arayüzü
    
    Görevlere dosya ekleme, listeleme ve silme işlemleri.
    """

    def __init__(self, parent, task_id: int, user_id: int, on_upload: Optional[callable] = None) -> None:
        """
        FileUploadGUI başlat
        
        Args:
            parent: Ana widget
            task_id: Görev ID
            user_id: Kullanıcı ID
            on_upload: Dosya yüklendiğinde çağrılacak fonksiyon
        """
        self.parent = parent
        self.task_id = task_id
        self.user_id = user_id
        self.on_upload_callback = on_upload
        self.lm = LanguageManager()
        self.file_manager = FileManager()

        self.setup_ui()
        self.load_files()

    def setup_ui(self) -> None:
        """Dosya yükleme arayüzünü oluştur"""

        # Ana frame
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#34495e', height=40)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text=" " + self.lm.tr("file_documents_title", "Dosya ve Belgeler"),
            font=('Segoe UI', 12, 'bold'),
            fg='white',
            bg='#34495e'
        ).pack(side='left', padx=15, expand=True)

        # Yükleme butonu
        upload_btn = tk.Button(
            title_frame,
            text=" " + self.lm.tr("upload_file_btn", "Dosya Yükle"),
            font=('Segoe UI', 9, 'bold'),
            bg='#3498db',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.upload_file
        )
        upload_btn.pack(side='right', padx=10)

        # Dosya listesi frame
        list_frame = tk.Frame(main_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Treeview (tablo)
        columns = ('file_name', 'size', 'uploaded_by', 'date')

        self.file_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=6
        )

        # Kolon başlıkları
        self.file_tree.heading('file_name', text=self.lm.tr("col_filename", "Dosya Adı"))
        self.file_tree.heading('size', text=self.lm.tr("col_size", "Boyut"))
        self.file_tree.heading('uploaded_by', text=self.lm.tr("col_uploaded_by", "Yükleyen"))
        self.file_tree.heading('date', text=self.lm.tr("col_date", "Tarih"))

        # Kolon genişlikleri
        self.file_tree.column('file_name', width=300)
        self.file_tree.column('size', width=100)
        self.file_tree.column('uploaded_by', width=120)
        self.file_tree.column('date', width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.file_tree.pack(side='left', fill='both', expand=True)

        # Aksiyon butonları
        action_frame = tk.Frame(main_frame, bg='white')
        action_frame.pack(fill='x', padx=10, pady=(0, 10))

        tk.Button(
            action_frame,
            text="️ Aç",
            font=('Segoe UI', 9),
            bg='#3498db',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.open_file
        ).pack(side='left', padx=(0, 5))

        tk.Button(
            action_frame,
            text=" İndir",
            font=('Segoe UI', 9),
            bg='#27ae60',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.download_file
        ).pack(side='left', padx=(0, 5))

        tk.Button(
            action_frame,
            text="️ Sil",
            font=('Segoe UI', 9),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.delete_file
        ).pack(side='left')

        # Bilgi label
        self.info_label = tk.Label(
            main_frame,
            text="İpucu: PDF, Excel, Word, resim dosyaları yükleyebilirsiniz (Max: 10 MB)",
            font=('Segoe UI', 8),
            fg='#7f8c8d',
            bg='white'
        )
        self.info_label.pack(pady=(0, 10))

    def upload_file(self) -> None:
        """Dosya yükleme dialogu aç"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr("select_file", "Dosya Seç"),
            filetypes=[
                (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*"),
                (self.lm.tr("file_pdf", "PDF Dosyaları"), "*.pdf"),
                (self.lm.tr("file_excel", "Excel Dosyaları"), "*.xlsx *.xls"),
                (self.lm.tr("file_word", "Word Dosyaları"), "*.docx *.doc"),
                (self.lm.tr("file_image", "Resim Dosyaları"), "*.png *.jpg *.jpeg"),
            ]
        )

        if not file_path:
            return

        # Dosya yükle
        file_id = self.file_manager.upload_file(
            source_path=file_path,
            task_id=self.task_id,
            uploaded_by=self.user_id
        )

        if file_id:
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("file_uploaded_success", "Dosya yüklendi!"))
            self.load_files()

            # Callback çağır
            if self.on_upload_callback:
                self.on_upload_callback()
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("file_upload_error", "Dosya yüklenemedi!"))

    def load_files(self) -> None:
        """Dosyaları yükle ve listele"""
        # Eski kayıtları temizle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Dosyaları getir
        files = self.file_manager.get_task_files(self.task_id)

        if not files:
            self.info_label.config(
                text=self.lm.tr("no_files_uploaded", "Henüz dosya yüklenmemiş. 'Dosya Yükle' butonuna tıklayarak belge ekleyebilirsiniz."),
                fg='#95a5a6'
            )
            return

        # Dosyaları ekle
        for file in files:
            # Dosya boyutunu formatla
            size_kb = (file.get('file_size', 0) or 0) / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.1f} KB"
            else:
                size_str = f"{size_kb / 1024:.2f} MB"

            # Tarihi formatla
            date_str = file.get('uploaded_at', '')[:16]  # YYYY-MM-DD HH:MM

            self.file_tree.insert(
                '',
                'end',
                values=(
                    file.get('file_name', ''),
                    size_str,
                    file.get('uploaded_by_name', 'Bilinmeyen'),
                    date_str
                ),
                tags=(str(file['id']),)
            )

        self.info_label.config(
            text=f"{len(files)} {self.lm.tr('files_uploaded_count', 'dosya yüklendi. Dosyaya çift tıklayarak açabilirsiniz.')}",
            fg='#27ae60'
        )

        # Çift tıklama ile aç
        self.file_tree.bind('<Double-1>', lambda e: self.open_file())

    def open_file(self) -> None:
        """Seçili dosyayı aç"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_file_warning", "Lütfen bir dosya seçin"))
            return

        # Dosya ID'sini al
        file_id = int(self.file_tree.item(selection[0])['tags'][0])

        # Dosya yolunu al
        file_path = self.file_manager.get_file_path(file_id)

        if not file_path or not os.path.exists(file_path):
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("file_not_found", "Dosya bulunamadı"))
            return

        # İşletim sistemine göre dosyayı aç
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('file_open_error', 'Dosya açılamadı')}: {e}")

    def download_file(self) -> None:
        """Dosyayı indir (farklı konuma kaydet)"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_file_warning", "Lütfen bir dosya seçin"))
            return

        # Dosya ID ve adını al
        file_id = int(self.file_tree.item(selection[0])['tags'][0])
        file_name = self.file_tree.item(selection[0])['values'][0]

        # Kayıt konumu sor
        save_path = filedialog.asksaveasfilename(
            title=self.lm.tr("save_file", "Dosyayı Kaydet"),
            initialfile=file_name,
            defaultextension=os.path.splitext(file_name)[1]
        )

        if not save_path:
            return

        # Dosya yolunu al
        source_path = self.file_manager.get_file_path(file_id)

        if not source_path or not os.path.exists(source_path):
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("file_not_found", "Dosya bulunamadı"))
            return

        # Kopyala
        try:
            shutil.copy2(source_path, save_path)
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('file_saved', 'Dosya kaydedildi')}:\n{save_path}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('file_save_error', 'Dosya kaydedilemedi')}: {e}")

    def delete_file(self) -> None:
        """Dosyayı sil"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_file_warning", "Lütfen bir dosya seçin"))
            return

        # Onay iste
        result = messagebox.askyesno(
            self.lm.tr("confirmation", "Onay"),
            self.lm.tr("delete_file_confirm", "Dosyayı silmek istediğinizden emin misiniz?\nBu işlem geri alınamaz.")
        )

        if not result:
            return

        # Dosya ID'sini al
        file_id = int(self.file_tree.item(selection[0])['tags'][0])

        # Sil
        if self.file_manager.delete_file(file_id):
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("file_deleted", "Dosya silindi"))
            self.load_files()
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("file_delete_error", "Dosya silinemedi"))

