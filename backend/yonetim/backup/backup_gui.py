#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yedekleme GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import datetime
from typing import Optional, List
from utils.language_manager import LanguageManager
from config.icons import Icons

class BackupGUI:
    """Yedekleme Yönetimi GUI"""
    
    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana container
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = tk.Label(main_frame, text=f"{Icons.SAVE} Yedekleme Merkezi",
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))
        
        # Hızlı Aksiyon Paneli
        action_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        action_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(action_frame, text="Hızlı İşlemler", 
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)
        
        btn_container = tk.Frame(action_frame, bg='white')
        btn_container.pack(pady=(0, 10))
        
        # Hızlı yedekleme butonları
        tk.Button(btn_container, text="📦 Hızlı Yedek Al", font=('Segoe UI', 10, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', padx=15, pady=5,
                 command=self.quick_backup).pack(side='left', padx=5)
        
        tk.Button(btn_container, text=f"{Icons.FOLDER_OPEN} Klasör Seç", font=('Segoe UI', 10),
                 bg='#3498db', fg='white', relief='flat', padx=15, pady=5,
                 command=self.select_backup_folder).pack(side='left', padx=5)
        
        tk.Button(btn_container, text=f"{Icons.LOADING} Geri Yükle", font=('Segoe UI', 10),
                 bg='#f39c12', fg='white', relief='flat', padx=15, pady=5,
                 command=self.restore_backup).pack(side='left', padx=5)
        
        # Notebook (Ana sekmeler)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Yedekleme Sekmesi
        backup_frame = tk.Frame(notebook, bg='white')
        notebook.add(backup_frame, text=f"{Icons.SAVE} Yedekleme")
        self.create_backup_tab(backup_frame)
        
        # Geri Yükleme Sekmesi  
        restore_frame = tk.Frame(notebook, bg='white')
        notebook.add(restore_frame, text=f"{Icons.LOADING} Geri Yükleme")
        self.create_restore_tab(restore_frame)
        
        # Otomatik Yedekleme Sekmesi
        auto_frame = tk.Frame(notebook, bg='white')
        notebook.add(auto_frame, text=f"{Icons.TIME} Otomatik")
        self.create_auto_backup_tab(auto_frame)
        
        # Geçmiş Sekmesi
        history_frame = tk.Frame(notebook, bg='white')
        notebook.add(history_frame, text="📜 Geçmiş")
        self.create_history_tab(history_frame)
    
    def create_backup_tab(self, parent):
        """Yedekleme sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Yedekleme seçenekleri
        tk.Label(container, text="Yedekleme Seçenekleri", 
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))
        
        # Seçenekler
        self.backup_db_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text=f"{Icons.REPORT} Veritabanı", variable=self.backup_db_var, 
                      bg='white', font=('Segoe UI', 11)).pack(anchor='w', pady=3)
        
        self.backup_files_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="📁 Dosyalar ve Raporlar", variable=self.backup_files_var,
                      bg='white', font=('Segoe UI', 11)).pack(anchor='w', pady=3)
        
        self.backup_config_var = tk.BooleanVar(value=False)
        tk.Checkbutton(container, text=f"{Icons.SETTINGS} Yapılandırma Dosyaları", variable=self.backup_config_var,
                      bg='white', font=('Segoe UI', 11)).pack(anchor='w', pady=3)
        
        # Hedef klasör
        tk.Label(container, text="\nHedef Klasör:", font=('Segoe UI', 11, 'bold'), bg='white').pack(anchor='w')
        
        folder_frame = tk.Frame(container, bg='white')
        folder_frame.pack(fill='x', pady=5)
        
        # Default backup path in user's home directory
        default_backup_path = os.path.join(os.path.expanduser("~"), "SDG_Backup")
        self.backup_path_var = tk.StringVar(value=default_backup_path)
        tk.Entry(folder_frame, textvariable=self.backup_path_var, width=50).pack(side='left')
        tk.Button(folder_frame, text=Icons.FOLDER_OPEN, command=self.select_backup_folder).pack(side='left', padx=5)
        
        # Yedekleme Butonu
        tk.Button(container, text=f"{Icons.SAVE} Yedekleme Başlat", font=('Segoe UI', 12, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', bd=0, cursor='hand2',
                 padx=30, pady=10, command=self.start_backup).pack(pady=20)
        
        # Progress bar
        self.backup_progress = ttk.Progressbar(container, mode='determinate')
        self.backup_progress.pack(fill='x', pady=10)
        
        # Status
        self.backup_status = tk.Label(container, text="Hazır", font=('Segoe UI', 10), 
                                     fg='#7f8c8d', bg='white')
        self.backup_status.pack()
    
    def create_restore_tab(self, parent):
        """Geri yükleme sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text=f"{Icons.LOADING} Geri Yükleme İşlemleri", 
                 font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))

        # Uyarı
        warning_frame = tk.Frame(container, bg='#fff3cd', padx=15, pady=10, relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(warning_frame, text=f"{Icons.WARNING} Dikkat: Geri yükleme işlemi mevcut verileri değiştirecektir!", 
                font=('Segoe UI', 10, 'bold'), fg='#856404', bg='#fff3cd').pack(side='left')

        # Yedek seçimi
        select_frame = tk.Frame(container, bg='white')
        select_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(select_frame, text="Yedek Dosyası Seç...", command=self.select_backup_file,
                 font=('Segoe UI', 10), bg='#3498db', fg='white', relief='flat', padx=15, pady=8).pack(side='left', padx=(0, 10))
                 
        self.selected_backup_label = tk.Label(select_frame, text="Dosya seçilmedi", font=('Segoe UI', 10, 'italic'), fg='#7f8c8d', bg='white')
        self.selected_backup_label.pack(side='left')

        # Geri yükle butonu
        tk.Button(container, text=f"{Icons.LOADING} Geri Yükle", font=('Segoe UI', 12, 'bold'),
                 bg='#e67e22', fg='white', relief='flat', padx=20, pady=12,
                 command=self.start_restore).pack(anchor='e', pady=10)
    
    def create_auto_backup_tab(self, parent):
        """Otomatik yedekleme sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text=f"{Icons.TIME} Otomatik Yedekleme Ayarları", 
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))
        
        # Otomatik yedekleme aktif/pasif
        self.auto_backup_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Otomatik yedekleme aktif", 
                      variable=self.auto_backup_enabled, bg='white', 
                      font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=10)
        
        # Sıklık seçenekleri
        tk.Label(container, text="Yedekleme Sıklığı:", font=('Segoe UI', 11, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        self.backup_frequency = tk.StringVar(value="Günlük")
        frequencies = ["Saatlik", "Günlük", "Haftalık", "Aylık"]
        for freq in frequencies:
            tk.Radiobutton(container, text=freq, variable=self.backup_frequency, 
                          value=freq, bg='white').pack(anchor='w', padx=20, pady=2)
        
        # Saklama süresi
        tk.Label(container, text="Yedekleri Saklama Süresi:", font=('Segoe UI', 11, 'bold'), bg='white').pack(anchor='w', pady=(15, 5))
        
        retention_frame = tk.Frame(container, bg='white')
        retention_frame.pack(anchor='w')
        
        self.retention_days = tk.StringVar(value="30")
        tk.Entry(retention_frame, textvariable=self.retention_days, width=10).pack(side='left')
        tk.Label(retention_frame, text="gün", bg='white').pack(side='left', padx=5)
        
        # Kaydet butonu
        tk.Button(container, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Ayarları Kaydet')}", font=('Segoe UI', 11),
                 bg='#3498db', fg='white', relief='flat', padx=20, pady=5,
                 command=self.save_auto_settings).pack(pady=20)
    
    def create_history_tab(self, parent):
        """Yedekleme geçmişi sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="📜 Yedekleme Geçmişi", 
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 15))
        
        # Treeview için liste
        columns = ('Tarih', 'Tür', 'Boyut', 'Durum')
        self.history_tree = ttk.Treeview(container, columns=columns, show='headings', height=8)
        
        # Sütun başlıkları
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        self.history_tree.pack(fill='both', expand=True)
        
        # Örnek veriler
        sample_data = [
            (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'Manuel', '2.3 MB', 'Başarılı'),
            ((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M'), 'Otomatik', '2.1 MB', 'Başarılı'),
            ((datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M'), 'Manuel', '1.9 MB', 'Başarılı')
        ]
        
        for item in sample_data:
            self.history_tree.insert('', 'end', values=item)
        
        # Yenile butonu
        tk.Button(container, text=f"{Icons.LOADING} Listeyi Yenile", font=('Segoe UI', 10),
                 bg='#95a5a6', fg='white', relief='flat', padx=15, pady=5,
                 command=self.refresh_history).pack(pady=10)
    
    # Event handlers
    def quick_backup(self):
        messagebox.showinfo(self.lm.tr("quick_backup", "Hızlı Yedekleme"), self.lm.tr("quick_backup_starting", "Hızlı yedekleme başlatılıyor..."))
    
    def select_backup_folder(self):
        folder = filedialog.askdirectory(title=self.lm.tr("select_backup_folder", "Yedekleme Klasörü Seç"))
        if folder:
            self.backup_path_var.set(folder)
    
    def select_restore_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[(self.lm.tr("file_backup", "Yedek Dosyaları"), "*.backup"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")],
            title=self.lm.tr("select_restore_file", "Geri Yükleme Dosyası Seç")
        )
        if file_path:
            self.restore_file_var.set(file_path)
    
    def start_backup(self):
        messagebox.showinfo(self.lm.tr("backup", "Yedekleme"), self.lm.tr("backup_started", "Yedekleme işlemi başlatıldı!"))
        
    def start_restore(self):
        if not self.restore_file_var.get():
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_restore_file_warning", "Lütfen geri yüklenecek dosyayı seçin!"))
            return
        
        result = messagebox.askyesno(self.lm.tr("confirm", "Onay"), self.lm.tr("restore_confirm", "Geri yükleme işlemi mevcut verileri değiştirecek. Devam etmek istiyor musunuz?"))
        if result:
            messagebox.showinfo(self.lm.tr("restore", "Geri Yükleme"), self.lm.tr("restore_started", "Geri yükleme işlemi başlatıldı!"))
    
    def restore_backup(self):
        self.start_restore()
    
    def save_auto_settings(self):
        messagebox.showinfo(self.lm.tr("settings", "Ayarlar"), self.lm.tr("settings_saved", "Otomatik yedekleme ayarları kaydedildi!"))
    
    def refresh_history(self):
        messagebox.showinfo(self.lm.tr("refresh", "Yenile"), self.lm.tr("history_refreshed", "Yedekleme geçmişi yenilendi!"))
