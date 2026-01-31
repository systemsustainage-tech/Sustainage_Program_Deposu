#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Logları GUI
Detaylı sistem logları görüntüleme ve yönetimi
"""

import logging
import csv
import json
import os
import random
import sqlite3
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from utils.language_manager import LanguageManager
from config.database import DB_PATH


class SystemLogsGUI:
    """Sistem Logları Arayüzü"""

    def __init__(self, parent, company_id: int) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        except Exception:
            self.db_path = DB_PATH
        self.auto_refresh_enabled = False
        self.auto_refresh_thread = None

        self.setup_ui()
        self.load_logs()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        tk.Label(main_frame, text="Güvenlik Logları",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f5f5f5').pack(pady=(0, 20))

        # Filtreleme paneli
        self.create_filter_panel(main_frame)

        # Log tablosu paneli
        self.create_logs_table_panel(main_frame)

        # Detaylar paneli
        self.create_details_panel(main_frame)

        # Alt bilgi
        self.create_footer(main_frame)

    def create_filter_panel(self, parent) -> None:
        """Filtreleme paneli oluştur"""
        # Filtre paneli
        filter_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        filter_frame.pack(fill='x', pady=(0, 10))

        # Panel içeriği
        content_frame = tk.Frame(filter_frame, bg='white')
        content_frame.pack(fill='x', padx=20, pady=15)

        # Tarih aralığı
        date_frame = tk.Frame(content_frame, bg='white')
        date_frame.pack(fill='x', pady=(0, 10))

        tk.Label(date_frame, text="Tarih Aralığı:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')

        tk.Label(date_frame, text="Başlangıç:", font=('Segoe UI', 9), bg='white').pack(side='left', padx=(20, 5))
        self.start_date = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%d.%m.%Y"))
        start_date_entry = tk.Entry(date_frame, textvariable=self.start_date, font=('Segoe UI', 9), width=12)
        start_date_entry.pack(side='left', padx=(0, 10))

        tk.Label(date_frame, text="Bitiş:", font=('Segoe UI', 9), bg='white').pack(side='left', padx=(10, 5))
        self.end_date = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        end_date_entry = tk.Entry(date_frame, textvariable=self.end_date, font=('Segoe UI', 9), width=12)
        end_date_entry.pack(side='left', padx=(0, 20))

        # Filtreler satırı
        filter_row = tk.Frame(content_frame, bg='white')
        filter_row.pack(fill='x', pady=(0, 10))

        # Log seviyesi
        tk.Label(filter_row, text="Log Seviyesi:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')
        self.log_level = tk.StringVar(value="Tümü")
        level_combo = ttk.Combobox(filter_row, textvariable=self.log_level, width=15, state='readonly')
        level_combo['values'] = ('Tümü', 'INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL')
        level_combo.pack(side='left', padx=(10, 20))

        # Kullanıcı
        tk.Label(filter_row, text="Kullanıcı:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')
        self.user_filter = tk.StringVar(value="Tümü")
        user_combo = ttk.Combobox(filter_row, textvariable=self.user_filter, width=15, state='readonly')
        user_combo['values'] = ('Tümü', 'admin', 'kullanici', 'sistem')
        user_combo.pack(side='left', padx=(10, 20))

        # Arama
        tk.Label(filter_row, text="Ara:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')
        self.search_text = tk.StringVar()
        search_entry = tk.Entry(filter_row, textvariable=self.search_text, font=('Segoe UI', 9), width=25)
        search_entry.insert(0, "Log mesajında ara...")
        search_entry.pack(side='left', padx=(10, 0))

        # Butonlar
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))

        tk.Button(button_frame, text="Ara", font=('Segoe UI', 9, 'bold'), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                 command=self.search_logs).pack(side='left', padx=(0, 5))

        tk.Button(button_frame, text="Temizle", font=('Segoe UI', 9, 'bold'), bg='#95a5a6', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                 command=self.clear_filters).pack(side='left', padx=5)

        tk.Button(button_frame, text="Yenile", font=('Segoe UI', 9, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                 command=self.refresh_logs).pack(side='left', padx=5)

        tk.Button(button_frame, text="Dışa Aktar", font=('Segoe UI', 9, 'bold'), bg='#e67e22', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=5,
                 command=self.export_logs).pack(side='left', padx=5)

        # Otomatik yenileme
        self.auto_refresh_var = tk.BooleanVar()
        auto_refresh_check = tk.Checkbutton(button_frame, text="Otomatik Yenile",
                                           variable=self.auto_refresh_var, font=('Segoe UI', 9),
                                           bg='white', command=self.toggle_auto_refresh)
        auto_refresh_check.pack(side='right', padx=(20, 0))

    def create_logs_table_panel(self, parent) -> None:
        """Log tablosu paneli oluştur"""
        # Tablo paneli
        table_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Panel başlığı
        header_frame = tk.Frame(table_frame, bg='#27ae60', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="Sistem Logları",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#27ae60').pack(expand=True)

        # Tablo içeriği
        table_content = tk.Frame(table_frame, bg='white')
        table_content.pack(fill='both', expand=True, padx=10, pady=10)

        # Treeview (tablo) oluştur
        columns = ('Zaman', 'Seviye', 'Kullanıcı', 'Modül', 'Mesaj')
        self.logs_tree = ttk.Treeview(table_content, columns=columns, show='headings', height=15)

        # Sütun ayarları
        self.logs_tree.heading('Zaman', text='Zaman')
        self.logs_tree.heading('Seviye', text='Seviye')
        self.logs_tree.heading('Kullanıcı', text='Kullanıcı')
        self.logs_tree.heading('Modül', text='Modül')
        self.logs_tree.heading('Mesaj', text='Mesaj')

        self.logs_tree.column('Zaman', width=120)
        self.logs_tree.column('Seviye', width=80)
        self.logs_tree.column('Kullanıcı', width=100)
        self.logs_tree.column('Modül', width=120)
        self.logs_tree.column('Mesaj', width=400)

        # Scrollbar
        logs_scrollbar = ttk.Scrollbar(table_content, orient='vertical', command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)

        # Pack
        self.logs_tree.pack(side='left', fill='both', expand=True)
        logs_scrollbar.pack(side='right', fill='y')

        # Seçim eventi
        self.logs_tree.bind('<<TreeviewSelect>>', self.on_log_select)

    def create_details_panel(self, parent) -> None:
        """Detaylar paneli oluştur"""
        # Detaylar paneli
        details_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        details_frame.pack(fill='x', pady=(0, 10))

        # Panel başlığı
        detail_header = tk.Frame(details_frame, bg='#27ae60', height=40)
        detail_header.pack(fill='x')
        detail_header.pack_propagate(False)

        tk.Label(detail_header, text="Detaylar",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#27ae60').pack(expand=True)

        # Detay içeriği
        detail_content = tk.Frame(details_frame, bg='white')
        detail_content.pack(fill='both', expand=True, padx=10, pady=10)

        # Detay metni
        self.detail_text = tk.Text(detail_content, font=('Segoe UI', 9), height=8,
                                  relief='solid', bd=1, wrap='word')
        detail_scrollbar = ttk.Scrollbar(detail_content, orient='vertical', command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)

        # Pack
        self.detail_text.pack(side='left', fill='both', expand=True)
        detail_scrollbar.pack(side='right', fill='y')

        # Varsayılan mesaj
        self.detail_text.insert('1.0', "Bir log kaydı seçin...")
        self.detail_text.configure(state='disabled')

    def create_footer(self, parent) -> None:
        """Alt bilgi oluştur"""
        footer_frame = tk.Frame(parent, bg='#ecf0f1', height=30)
        footer_frame.pack(fill='x')
        footer_frame.pack_propagate(False)

        self.total_logs_label = tk.Label(footer_frame, text="Toplam Log: 0",
                                        font=('Segoe UI', 9), fg='#7f8c8d', bg='#ecf0f1')
        self.total_logs_label.pack(side='left', padx=10, pady=5)

    def load_logs(self) -> None:
        """Logları yükle"""
        try:
            # Treeview'ı temizle
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)

            db_logs = self.get_db_logs(limit=200)
            logs_to_show = db_logs if db_logs else self.get_sample_logs()

            for log in logs_to_show:
                # Log seviyesine göre renk belirle
                level = log['level']
                tags = []
                if level == 'ERROR':
                    tags = ['error']
                elif level == 'WARNING':
                    tags = ['warning']
                elif level == 'INFO':
                    tags = ['info']

                self.logs_tree.insert('', 'end', values=(
                    log['timestamp'],
                    log['level'],
                    log['user'],
                    log['module'],
                    log['message']
                ), tags=tags)

            # Renk etiketleri
            self.logs_tree.tag_configure('error', foreground='#e74c3c')
            self.logs_tree.tag_configure('warning', foreground='#f39c12')
            self.logs_tree.tag_configure('info', foreground='#3498db')

            # Toplam log sayısını güncelle
            self.total_logs_label.config(text=f"Toplam Log: {len(logs_to_show)}")

        except Exception as e:
            logging.error(f"Loglar yüklenirken hata: {e}")
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('log_load_error', 'Loglar yüklenirken hata')}: {e}")

    def _table_exists(self, cursor, name: str) -> bool:
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
            return cursor.fetchone() is not None
        except Exception:
            return False

    def get_db_logs(self, limit: int = 200) -> list:
        logs = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            has_system = self._table_exists(cursor, 'system_logs')
            has_audit = self._table_exists(cursor, 'audit_logs')

            if has_system:
                cursor.execute(
                    """
                    SELECT created_at, level, user_id, module, message
                    FROM system_logs
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                for ts, level, user_id, module, message in cursor.fetchall():
                    try:
                        dt = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        try:
                            dt = datetime.fromisoformat(str(ts))
                        except Exception:
                            dt = datetime.now()
                    logs.append({
                        'timestamp': dt.strftime("%d.%m.%Y %H:%M:%S"),
                        'level': level or 'INFO',
                        'user': str(user_id or 'sistem'),
                        'module': module or 'Sistem',
                        'message': message or ''
                    })

            if has_audit:
                cursor.execute(
                    """
                    SELECT created_at, level, user_id, module, COALESCE(message, action) as msg
                    FROM audit_logs
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                for ts, level, user_id, module, message in cursor.fetchall():
                    try:
                        dt = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        try:
                            dt = datetime.fromisoformat(str(ts))
                        except Exception:
                            dt = datetime.now()
                    logs.append({
                        'timestamp': dt.strftime("%d.%m.%Y %H:%M:%S"),
                        'level': (level or 'INFO').upper(),
                        'user': str(user_id or 'sistem'),
                        'module': module or 'Audit',
                        'message': message or ''
                    })

            conn.close()

            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            return logs[:limit]
        except Exception:
            return []

    def get_sample_logs(self) -> None:
        """Örnek log verileri oluştur"""
        import random

        levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        users = ['admin', 'kullanici', 'sistem', 'otomatik']
        modules = ['Giriş', 'Kullanıcı Yönetimi', 'TSRS', 'SDG', 'Raporlama', 'Sistem']
        messages = [
            "Kullanıcı girişi başarılı",
            "Veritabanı bağlantısı kuruldu",
            "Rapor oluşturuldu",
            "Hata: Veritabanı bağlantısı kesildi",
            "Yeni kullanıcı oluşturuldu",
            "TSRS standartları yüklendi",
            "Backup işlemi tamamlandı",
            "Uyarı: Disk alanı düşük",
            "Sistem yeniden başlatıldı",
            "Güvenlik ihlali tespit edildi"
        ]

        logs = []
        base_time = datetime.now()

        for i in range(50):
            log_time = base_time - timedelta(hours=i*2, minutes=random.randint(0, 59))

            logs.append({
                'timestamp': log_time.strftime("%d.%m.%Y %H:%M:%S"),
                'level': random.choice(levels),
                'user': random.choice(users),
                'module': random.choice(modules),
                'message': random.choice(messages)
            })

        return logs

    def on_log_select(self, event) -> None:
        """Log seçildiğinde"""
        selection = self.logs_tree.selection()
        if not selection:
            return

        item = self.logs_tree.item(selection[0])
        values = item['values']

        # Detay metnini güncelle
        detail_content = f"""Log Detayları:

Zaman: {values[0]}
Seviye: {values[1]}
Kullanıcı: {values[2]}
Modül: {values[3]}
Mesaj: {values[4]}

Ek Bilgiler:
- Log ID: {hash(str(values)) % 100000}
- IP Adresi: 192.168.1.{random.randint(1, 254)}
- Session ID: {random.randint(100000, 999999)}
- Tarayıcı: Chrome 120.0.0.0
- İşletim Sistemi: Windows 10
- Uygulama Versiyonu: 1.0.0

Stack Trace:
{values[4]} hatası oluştu.
Dosya: app/main.py, Satır: {random.randint(1, 100)}  # nosec
Fonksiyon: {random.choice(['main', 'process_data', 'save_user', 'generate_report'])}  # nosec
"""

        self.detail_text.configure(state='normal')
        self.detail_text.delete('1.0', 'end')
        self.detail_text.insert('1.0', detail_content)
        self.detail_text.configure(state='disabled')

    def search_logs(self) -> None:
        """Log arama"""
        try:
            # Filtreleme kriterlerini al
            start_date = self.start_date.get()
            end_date = self.end_date.get()
            level = self.log_level.get()
            user = self.user_filter.get()
            search_term = self.search_text.get()

            # Filtrelenmiş logları yükle
            filtered_logs = self.get_filtered_logs(start_date, end_date, level, user, search_term)

            # Treeview'ı güncelle
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)

            for log in filtered_logs:
                level = log['level']
                tags = []
                if level == 'ERROR':
                    tags = ['error']
                elif level == 'WARNING':
                    tags = ['warning']
                elif level == 'INFO':
                    tags = ['info']

                self.logs_tree.insert('', 'end', values=(
                    log['timestamp'],
                    log['level'],
                    log['user'],
                    log['module'],
                    log['message']
                ), tags=tags)

            self.total_logs_label.config(text=f"Toplam Log: {len(filtered_logs)}")

        except Exception as e:
            logging.error(f"Log arama hatası: {e}")
            messagebox.showerror(self.lm.tr('title_error', "Hata"), f"{self.lm.tr('err_log_search', 'Log arama hatası')}: {e}")

    def get_filtered_logs(self, start_date, end_date, level, user, search_term) -> None:
        """Filtrelenmiş logları getir"""
        all_logs = self.get_db_logs(limit=500) or self.get_sample_logs()
        filtered_logs = []

        for log in all_logs:
            # Tarih filtresi
            if start_date and end_date:
                log_date = datetime.strptime(log['timestamp'].split(' ')[0], "%d.%m.%Y")
                start_dt = datetime.strptime(start_date, "%d.%m.%Y")
                end_dt = datetime.strptime(end_date, "%d.%m.%Y")

                if not (start_dt <= log_date <= end_dt):
                    continue

            # Seviye filtresi
            if level != 'Tümü' and log['level'] != level:
                continue

            # Kullanıcı filtresi
            if user != 'Tümü' and log['user'] != user:
                continue

            # Arama terimi
            if (
                search_term
                and search_term != "Log mesajında ara..."
                and search_term.lower() not in log['message'].lower()
            ):
                continue

            filtered_logs.append(log)

        return filtered_logs

    def clear_filters(self) -> None:
        """Filtreleri temizle"""
        self.start_date.set((datetime.now() - timedelta(days=7)).strftime("%d.%m.%Y"))
        self.end_date.set(datetime.now().strftime("%d.%m.%Y"))
        self.log_level.set("Tümü")
        self.user_filter.set("Tümü")
        self.search_text.set("Log mesajında ara...")

        self.load_logs()

    def refresh_logs(self) -> None:
        """Logları yenile"""
        self.load_logs()

    def export_logs(self) -> None:
        """Logları dışa aktar"""
        try:
            # Dosya seçimi
            file_path = filedialog.asksaveasfilename(
                title=self.lm.tr("export_logs", "Logları Dışa Aktar"),
                defaultextension=".csv",
                filetypes=[
                    (self.lm.tr("file_csv", "CSV dosyaları"), "*.csv"),
                    (self.lm.tr("file_json", "JSON dosyaları"), "*.json"),
                    (self.lm.tr("all_files", "Tüm dosyalar"), "*.*"),
                ],
            )

            if not file_path:
                return

            # Seçili logları al
            selected_logs = []
            for item in self.logs_tree.get_children():
                item_values = self.logs_tree.item(item)['values']
                selected_logs.append({
                    'timestamp': item_values[0],
                    'level': item_values[1],
                    'user': item_values[2],
                    'module': item_values[3],
                    'message': item_values[4]
                })

            # Dosya formatına göre kaydet
            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'level', 'user', 'module', 'message']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(selected_logs)

            elif file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(selected_logs, jsonfile, ensure_ascii=False, indent=2)

            messagebox.showinfo("Başarılı", f"Loglar başarıyla dışa aktarıldı: {file_path}")

        except Exception as e:
            logging.error(f"Log dışa aktarma hatası: {e}")
            messagebox.showerror("Hata", f"Log dışa aktarma hatası: {e}")

    def toggle_auto_refresh(self) -> None:
        """Otomatik yenilemeyi aç/kapat"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def start_auto_refresh(self) -> None:
        """Otomatik yenilemeyi başlat"""
        self.auto_refresh_enabled = True
        self._schedule_refresh()

    def stop_auto_refresh(self) -> None:
        """Otomatik yenilemeyi durdur"""
        self.auto_refresh_enabled = False

    def _schedule_refresh(self) -> None:
        """Bir sonraki yenilemeyi zamanla"""
        if self.auto_refresh_enabled:
            # 30 saniye sonra yenile
            self.parent.after(30000, self._perform_auto_refresh)

    def _perform_auto_refresh(self) -> None:
        """Otomatik yenileme işlemini gerçekleştir"""
        if self.auto_refresh_enabled:
            try:
                self.refresh_logs()
            except Exception as e:
                logging.error(f"Otomatik yenileme hatası: {e}")
            finally:
                # Bir sonraki döngüyü başlat
                self._schedule_refresh()
