#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yedekleme ve Kurtarma GUI
Otomatik backup, restore ve yapılandırma arayüzü
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from .backup_recovery_manager import BackupRecoveryManager


class BackupGUI:
    """Yedekleme ve kurtarma arayüzü"""
    
    def __init__(self, parent, db_path: str) -> None:
        self.parent = parent
        self.db_path = db_path
        self.backup_manager = BackupRecoveryManager(db_path)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Başlık
        header = tk.Frame(self.parent, bg='#e67e22', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=" Yedekleme ve Kurtarma Sistemi",
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#e67e22').pack(side='left', padx=20, pady=20)
        
        # Notebook
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Sekmeler
        self.backup_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.backup_frame, text=" Yedekleme")
        
        self.restore_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.restore_frame, text=" Geri Yükleme")
        
        self.config_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.config_frame, text="️ Ayarlar")
        
        self.build_backup_tab()
        self.build_restore_tab()
        self.build_config_tab()
    
    def build_backup_tab(self) -> None:
        """Yedekleme sekmesi"""
        # İstatistikler
        stats_frame = tk.Frame(self.backup_frame, bg='white')
        stats_frame.pack(fill='x', padx=20, pady=20)
        
        self.stat_labels = {}
        stats = [
            ('total', 'Toplam Yedek', '#3498db'),
            ('successful', 'Başarılı', '#27ae60'),
            ('failed', 'Başarısız', '#e74c3c'),
            ('size', 'Toplam Boyut', '#9b59b6')
        ]
        
        for key, label, color in stats:
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='both', expand=True, padx=5)
            
            tk.Label(card, text=label, font=('Segoe UI', 9, 'bold'),
                    bg=color, fg='white').pack(pady=(10, 5))
            
            value = tk.Label(card, text="0", font=('Segoe UI', 16, 'bold'),
                           bg=color, fg='white')
            value.pack(pady=(0, 10))
            self.stat_labels[key] = value
        
        # Butonlar
        button_frame = tk.Frame(self.backup_frame, bg='white')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(button_frame, text=" Tam Yedekleme Oluştur", 
                 font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', cursor='hand2', padx=20, pady=10,
                 command=lambda: self.create_backup('full')).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="️ Sadece Veritabanı",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=lambda: self.create_backup('database_only')).pack(side='left', padx=5)
        
        tk.Button(button_frame, text=" Yenile",
                 font=('Segoe UI', 10), bg='#95a5a6', fg='white',
                 relief='flat', cursor='hand2', padx=15, pady=8,
                 command=self.load_data).pack(side='left', padx=5)
        
        # Yedek listesi
        list_frame = tk.LabelFrame(self.backup_frame, text=" Yedek Geçmişi",
                                   bg='white', font=('Segoe UI', 11, 'bold'))
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        columns = ('ID', 'Adı', 'Tür', 'Boyut (MB)', 'Tarih', 'Durum', 'Oluşturan')
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.backup_tree.heading(col, text=col)
            if col == 'Adı':
                self.backup_tree.column(col, width=250)
            elif col == 'Tarih':
                self.backup_tree.column(col, width=150)
            else:
                self.backup_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
    
    def build_restore_tab(self) -> None:
        """Geri yükleme sekmesi"""
        # Uyarı
        warning = tk.Frame(self.restore_frame, bg='#fff3cd', relief='solid', bd=2)
        warning.pack(fill='x', padx=20, pady=20)
        
        tk.Label(warning, text="️ DİKKAT: Geri yükleme mevcut verilerin üzerine yazacaktır!",
                font=('Segoe UI', 11, 'bold'), bg='#fff3cd', fg='#856404').pack(pady=15)
        tk.Label(warning, text="Geri yükleme öncesi otomatik güvenlik yedeği alınacaktır.",
                font=('Segoe UI', 9), bg='#fff3cd', fg='#856404').pack(pady=(0, 15))
        
        # Yedek seçimi
        select_frame = tk.LabelFrame(self.restore_frame, text="1️⃣ Yedek Seçin",
                                     bg='white', font=('Segoe UI', 11, 'bold'))
        select_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        columns = ('ID', 'Adı', 'Tarih', 'Boyut', 'Durum')
        self.restore_tree = ttk.Treeview(select_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.restore_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(select_frame, orient='vertical', command=self.restore_tree.yview)
        self.restore_tree.configure(yscrollcommand=scrollbar.set)
        
        self.restore_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Geri yükleme butonu
        restore_btn_frame = tk.Frame(self.restore_frame, bg='white')
        restore_btn_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(restore_btn_frame, text=" SEÇİLİ YEDEĞİ GERİ YÜKLE",
                 font=('Segoe UI', 12, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', cursor='hand2', padx=30, pady=15,
                 command=self.restore_selected).pack()
    
    def build_config_tab(self) -> None:
        """Ayarlar sekmesi"""
        config = self.backup_manager.get_backup_config()
        
        form_frame = tk.Frame(self.config_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Otomatik yedekleme
        auto_frame = tk.LabelFrame(form_frame, text=" Otomatik Yedekleme",
                                   bg='white', font=('Segoe UI', 11, 'bold'))
        auto_frame.pack(fill='x', pady=(0, 20))
        
        self.auto_enabled_var = tk.BooleanVar(value=config.get('auto_backup_enabled', True))
        tk.Checkbutton(auto_frame, text="Otomatik yedeklemeyi aktifleştir",
                      variable=self.auto_enabled_var, font=('Segoe UI', 10),
                      bg='white').pack(anchor='w', padx=15, pady=10)
        
        # Sıklık
        freq_frame = tk.Frame(auto_frame, bg='white')
        freq_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(freq_frame, text="Sıklık:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.frequency_var = tk.StringVar(value=config.get('backup_frequency', 'daily'))
        freq_combo = ttk.Combobox(freq_frame, textvariable=self.frequency_var,
                                 values=['daily (Günlük)', 'weekly (Haftalık)', 'monthly (Aylık)'],
                                 state='readonly', width=20)
        freq_combo.pack(side='left', padx=10)
        
        # Zaman
        time_frame = tk.Frame(auto_frame, bg='white')
        time_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        tk.Label(time_frame, text="Saat:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.time_var = tk.StringVar(value=config.get('backup_time', '02:00'))
        time_entry = tk.Entry(time_frame, textvariable=self.time_var, width=10)
        time_entry.pack(side='left', padx=10)
        tk.Label(time_frame, text="(HH:MM format)", font=('Segoe UI', 8),
                bg='white', fg='#666').pack(side='left')
        
        # Maksimum yedek
        max_frame = tk.LabelFrame(form_frame, text="️ Yedek Saklama",
                                  bg='white', font=('Segoe UI', 11, 'bold'))
        max_frame.pack(fill='x', pady=(0, 20))
        
        max_inner = tk.Frame(max_frame, bg='white')
        max_inner.pack(fill='x', padx=15, pady=15)
        
        tk.Label(max_inner, text="Maksimum yedek sayısı:", 
                font=('Segoe UI', 10), bg='white').pack(side='left')
        self.max_backups_var = tk.IntVar(value=config.get('max_backups', 30))
        tk.Spinbox(max_inner, from_=5, to=100, textvariable=self.max_backups_var,
                  width=10).pack(side='left', padx=10)
        
        # Kaydet butonu
        tk.Button(form_frame, text=" Ayarları Kaydet",
                 font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', cursor='hand2', padx=30, pady=12,
                 command=self.save_config).pack(pady=20)
    
    def load_data(self) -> None:
        """Verileri yükle"""
        # İstatistikler
        stats = self.backup_manager.get_backup_statistics()
        
        self.stat_labels['total'].config(text=str(stats['total_backups']))
        self.stat_labels['successful'].config(text=str(stats['successful_backups']))
        self.stat_labels['failed'].config(text=str(stats['failed_backups']))
        self.stat_labels['size'].config(text=f"{stats['total_size_mb']} MB")
        
        # Yedek listesi
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        for item in self.restore_tree.get_children():
            self.restore_tree.delete(item)
        
        backups = self.backup_manager.get_backup_list(50)
        for backup in backups:
            size_mb = round(backup['size'] / (1024 * 1024), 2) if backup['size'] else 0
            
            # Tarih formatla
            try:
                dt = datetime.fromisoformat(backup['date'])
                date_str = dt.strftime('%d.%m.%Y %H:%M')
            except Exception:
                date_str = backup['date']
            
            values = (backup['id'], backup['name'], backup['type'], 
                     size_mb, date_str, backup['status'], backup['created_by'])
            
            self.backup_tree.insert('', 'end', values=values)
            
            # Sadece başarılı yedekler restore edilebilir
            if backup['status'] == 'completed':
                self.restore_tree.insert('', 'end', values=values[:5] + (backup['status'],))
    
    def create_backup(self, backup_type: str) -> None:
        """Yedekleme oluştur"""
        if messagebox.askyesno("Onay", f"{backup_type.title()} yedekleme oluşturulsun mu?"):
            try:
                success, message = self.backup_manager.create_backup(
                    backup_type=backup_type,
                    created_by='user',
                    include_files=True
                )
                
                if success:
                    messagebox.showinfo("Başarılı", f"Yedekleme oluşturuldu!\n\n{message}")
                    self.load_data()
                else:
                    # Hata mesajını daha kullanıcı dostu hale getir
                    if "Permission denied" in message or "Erişim engellendi" in message:
                        error_msg = "Dosya izin hatası!\n\n" \
                                  "Çözüm önerileri:\n" \
                                  "• Uygulamayı yönetici olarak çalıştırın\n" \
                                  "• Antivirus programını geçici olarak kapatın\n" \
                                  "• Dosyaların başka program tarafından kullanılmadığından emin olun\n\n" \
                                  f"Teknik detay: {message}"
                    else:
                        error_msg = f"Yedekleme hatası:\n\n{message}"
                    messagebox.showerror("Yedekleme Hatası", error_msg)
            
            except Exception as e:
                error_msg = f"Beklenmeyen hata:\n\n{str(e)}\n\n" \
                          "Lütfen uygulamayı yeniden başlatın ve tekrar deneyin."
                messagebox.showerror("Sistem Hatası", error_msg)
    
    def restore_selected(self) -> None:
        """Seçili yedeği geri yükle"""
        selection = self.restore_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen geri yüklenecek yedeği seçin")
            return
        
        values = self.restore_tree.item(selection[0], 'values')
        backup_name = values[1]
        backup_date = values[4]
        
        # Çok katı onay
        confirm_text = f"""
UYARI: GERİ YÜKLEME İŞLEMİ!

Seçili Yedek: {backup_name}
Tarih: {backup_date}

Bu işlem:
 Mevcut veritabanının yedeğini alacak
 Seçili yedeği geri yükleyecek
 Mevcut veriler değişecek

DEVAM ETMEK İSTEDİĞİNİZDEN EMİN MİSİNİZ?
"""
        
        if messagebox.askyesno("️ ÖNEMLİ ONAY", confirm_text):
            # İkinci onay
            if messagebox.askyesno("Son Onay", "Bu işlemi gerçekten yapmak istiyor musunuz?"):
                try:
                    # Backup dosya yolunu bul
                    backups = self.backup_manager.get_backup_list(100)
                    backup_id = int(values[0])
                    backup_path = next((b['path'] for b in backups if b['id'] == backup_id), None)
                    
                    if not backup_path:
                        messagebox.showerror("Hata", "Yedek dosyası bulunamadı")
                        return
                    
                    success, message = self.backup_manager.restore_backup(backup_path, 'user')
                    
                    if success:
                        messagebox.showinfo("Başarılı", 
                                          f"Geri yükleme başarılı!\n\n{message}\n\n"
                                          "Değişikliklerin geçerli olması için uygulamayı yeniden başlatın.")
                    else:
                        messagebox.showerror("Hata", message)
                
                except Exception as e:
                    messagebox.showerror("Hata", f"Geri yükleme hatası: {e}")
    
    def save_config(self) -> None:
        """Yapılandırmayı kaydet"""
        try:
            freq = self.frequency_var.get().split('(')[0].strip()
            
            config = {
                'auto_backup_enabled': self.auto_enabled_var.get(),
                'backup_frequency': freq,
                'backup_time': self.time_var.get(),
                'max_backups': self.max_backups_var.get(),
                'compress_backups': True,
                'include_files': True
            }
            
            if self.backup_manager.update_backup_config(config):
                messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            else:
                messagebox.showerror("Hata", "Ayarlar kaydedilemedi")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")

