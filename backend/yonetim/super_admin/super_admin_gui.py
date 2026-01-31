#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Super Admin GUI
Sistem geneli yönetim ve kontrolü
"""

import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from utils.language_manager import LanguageManager
from config.icons import Icons
from config.database import DB_PATH


class SuperAdminGUI:
    """Super Admin GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()
        self.current_frame = None
        # Erişim kontrolü
        if not self._is_super_admin():
            try:
                messagebox.showerror(self.lm.tr('access_denied', "Erişim Reddedildi"), 
                                   self.lm.tr('super_admin_access_only', "Bu panele sadece Super Admin erişebilir!"))
            except Exception as e:
                logging.error(f'Silent error in super_admin_gui.py: {str(e)}')
            return

        self.setup_main_container()
        self.show_main_page()

    def setup_main_container(self) -> None:
        """Ana container'ı oluştur"""
        self.main_container = tk.Frame(self.parent, bg='#2c3e50')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

    def clear_container(self) -> None:
        """Container'ı temizle"""
        if self.current_frame:
            self.current_frame.destroy()

    def _find_main_app(self):
        """Ana uygulamayı bul"""
        parent = self.parent
        while parent:
            if hasattr(parent, 'show_dashboard_classic'):
                return parent
            parent = getattr(parent, 'master', None)
        return None

    def close_panel(self) -> None:
        """Paneli kapat ve dashboard'a dön"""
        main_app = self._find_main_app()
        if main_app:
            main_app.show_dashboard_classic()
        else:
            # Fallback: Container'ı temizle
            self.clear_container()

    def create_header(self, parent_frame, title: str, show_back: bool = True) -> None:
        """Standart başlık ve butonları oluştur"""
        header_frame = tk.Frame(parent_frame, bg='#2c3e50', height=60)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)

        # Sol taraf - Başlık
        title_lbl = tk.Label(header_frame, text=title,
                           font=('Segoe UI', 18, 'bold'), fg='#f39c12', bg='#2c3e50')
        title_lbl.pack(side='left', padx=10)

        # Sağ taraf - Butonlar
        btn_frame = tk.Frame(header_frame, bg='#2c3e50')
        btn_frame.pack(side='right', padx=10)

        # Kapat butonu (Her zaman göster)
        close_btn = tk.Button(btn_frame, text=f"✕ {self.lm.tr('btn_close', 'Kapat')}", font=('Segoe UI', 10, 'bold'),
                             bg='#e74c3c', fg='white', relief='flat', padx=15, pady=5,
                             command=self.close_panel, cursor='hand2')
        close_btn.pack(side='right', padx=5)

        # Geri butonu (İsteğe bağlı)
        if show_back:
            back_btn = tk.Button(btn_frame, text=f"← {self.lm.tr('btn_back', 'Geri')}", font=('Segoe UI', 10, 'bold'),
                                bg='#95a5a6', fg='white', relief='flat', padx=15, pady=5,
                                command=self.show_main_page, cursor='hand2')
            back_btn.pack(side='right', padx=5)

    def show_main_page(self) -> None:
        """Ana sayfayı göster"""
        self.clear_container()

        self.current_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.current_frame.pack(fill='both', expand=True)

        # Header
        self.create_header(self.current_frame, f"👑 {self.lm.tr('super_admin_panel', 'SUPER ADMIN PANEL')}", show_back=False)

        # Uyarı mesajı
        warning_label = tk.Label(self.current_frame, text=f"{Icons.WARNING} {self.lm.tr('admin_only_warning', 'Bu panel yalnızca sistem yöneticileri içindir')} {Icons.WARNING}",
                                font=('Segoe UI', 12, 'bold'), fg='#e74c3c', bg='#2c3e50')
        warning_label.pack(pady=10)

        # İçerik alanı
        content_frame = tk.Frame(self.current_frame, bg='#34495e', relief='raised', bd=5)
        content_frame.pack(fill='both', expand=True, pady=20)

        # Yönetim butonları
        btn_frame = tk.Frame(content_frame, bg='#34495e')
        btn_frame.pack(expand=True)

        # Sistem kontrolü
        tk.Button(btn_frame, text=f"{Icons.WRENCH} {self.lm.tr('system_control', 'Sistem Kontrolü')}", font=('Segoe UI', 12, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', padx=20, pady=10, width=20,
                 command=self.show_system_control).pack(pady=10)

        # Kullanıcı yönetimi
        tk.Button(btn_frame, text=f"{Icons.USERS} {self.lm.tr('global_user_management', 'Global Kullanıcı Yönetimi')}", font=('Segoe UI', 12, 'bold'),
                 bg='#9b59b6', fg='white', relief='flat', padx=20, pady=10, width=20,
                 command=self.show_global_user_management).pack(pady=10)

        # Veritabanı yönetimi
        tk.Button(btn_frame, text=f"🗃️ {self.lm.tr('database_management', 'Veritabanı Yönetimi')}", font=('Segoe UI', 12, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', padx=20, pady=10, width=20,
                 command=self.show_database_management).pack(pady=10)

        # Sistem logları
        tk.Button(btn_frame, text=f"{Icons.REPORT} {self.lm.tr('system_logs', 'Sistem Logları')}", font=('Segoe UI', 12, 'bold'),
                 bg='#3498db', fg='white', relief='flat', padx=20, pady=10, width=20,
                 command=self.show_system_logs).pack(pady=10)

        # Alt bilgi
        info_label = tk.Label(
            self.current_frame,
            text=(
                f"{self.lm.tr('user_id', 'Kullanıcı ID')}: {self.current_user_id}\n"
                f"{self.lm.tr('access_level', 'Erişim Düzeyi')}: {self.lm.tr('super_admin', 'SÜPER YÖNETİCİ')}"
            ),
            font=('Segoe UI', 10),
            fg='#bdc3c7',
            bg='#2c3e50',
        )
        info_label.pack(side='bottom', pady=10)

    def _get_db_path(self) -> str:
        try:
            env_db = os.environ.get('SDG_DB_PATH')
            if env_db:
                return env_db
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            return os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        except Exception:
            return DB_PATH

    def _is_super_admin(self) -> bool:
        try:
            db_path = self._get_db_path()
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT username FROM users WHERE id = ?", (self.current_user_id,))
            row = cur.fetchone()
            conn.close()
            return bool(row and row[0] == '__super__')
        except Exception:
            return False

    def show_system_control(self) -> None:
        """Sistem kontrol sayfasını göster"""
        self.clear_container()

        self.current_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.current_frame.pack(fill='both', expand=True)

        # Header
        self.create_header(self.current_frame, f"{Icons.WRENCH} {self.lm.tr('system_control_title', 'SİSTEM KONTROLÜ')}")

        # İçerik alanı
        content_frame = tk.Frame(self.current_frame, bg='#ecf0f1', relief='raised', bd=3)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Sistem durumu paneli
        status_frame = tk.LabelFrame(content_frame, text=self.lm.tr('system_status', "Sistem Durumu"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        status_frame.pack(fill='x', padx=15, pady=15)

        # Sistem bilgileri
        info_frame = tk.Frame(status_frame, bg='#ecf0f1')
        info_frame.pack(fill='x', padx=10, pady=10)

        system_info = [
            (f"💻 {self.lm.tr('system_status_label', 'Sistem Durumu:')}", f"{Icons.SUCCESS} {self.lm.tr('running', 'Çalışıyor')}"),
            (f"🗃️ {self.lm.tr('database_label', 'Veritabanı:')}", f"{Icons.SUCCESS} {self.lm.tr('connected', 'Bağlı')}"),
            (f"{Icons.USERS} {self.lm.tr('active_users_label', 'Aktif Kullanıcılar:')}", f"🟢 5 {self.lm.tr('user_unit', 'Kullanıcı')}"),
            (f"{Icons.REPORT} {self.lm.tr('cpu_usage', 'CPU Kullanımı:')}", "🟢 %15"),
            (f"{Icons.SAVE} {self.lm.tr('ram_usage', 'RAM Kullanımı:')}", "🟡 %65"),
            (f"💿 {self.lm.tr('disk_usage', 'Disk Kullanımı:')}", "🟢 %45")
        ]

        for i, (label, value) in enumerate(system_info):
            row_frame = tk.Frame(info_frame, bg='#ecf0f1')
            row_frame.pack(fill='x', pady=2)

            tk.Label(row_frame, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='#ecf0f1', anchor='w', width=20).pack(side='left')
            tk.Label(row_frame, text=value, font=('Segoe UI', 10),
                    bg='#ecf0f1', anchor='w').pack(side='left')

        # Sistem kontrol butonları
        control_frame = tk.LabelFrame(content_frame, text=self.lm.tr('system_controls', "Sistem Kontrolleri"),
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        control_frame.pack(fill='x', padx=15, pady=15)

        btn_container = tk.Frame(control_frame, bg='#ecf0f1')
        btn_container.pack(pady=15)

        # Kontrol butonları
        controls = [
            (f"{Icons.LOADING} {self.lm.tr('restart_system', 'Sistemi Yeniden Başlat')}", "#e67e22", self.restart_system),
            (f"🛡️ {self.lm.tr('security_scan', 'Güvenlik Taraması')}", "#8e44ad", self.security_scan),
            (f"🧹 {self.lm.tr('clear_cache', 'Cache Temizle')}", "#3498db", self.clear_cache),
            (f"{Icons.REPORT} {self.lm.tr('performance_report', 'Performans Raporu')}", "#27ae60", self.performance_report)
        ]

        for text, color, command in controls:
            tk.Button(btn_container, text=text, font=('Segoe UI', 10, 'bold'),
                     bg=color, fg='white', relief='flat', padx=15, pady=8,
                     command=command).pack(pady=5, fill='x')

    def show_global_user_management(self) -> None:
        """Global kullanıcı yönetimi sayfasını göster"""
        self.clear_container()

        self.current_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.current_frame.pack(fill='both', expand=True)

        # Header
        self.create_header(self.current_frame, f"{Icons.USERS} {self.lm.tr('global_user_management_title', 'GLOBAL KULLANICI YÖNETİMİ')}")

        # İçerik alanı
        content_frame = tk.Frame(self.current_frame, bg='#ecf0f1', relief='raised', bd=3)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Kullanıcı istatistikleri
        stats_frame = tk.LabelFrame(content_frame, text=self.lm.tr('user_statistics', "Kullanıcı İstatistikleri"),
                                  font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        stats_frame.pack(fill='x', padx=15, pady=15)

        stats_container = tk.Frame(stats_frame, bg='#ecf0f1')
        stats_container.pack(fill='x', padx=10, pady=10)

        user_stats = [
            (f"{Icons.USERS} {self.lm.tr('total_users', 'Toplam Kullanıcı:')}", "25"),
            (f"{Icons.SUCCESS} {self.lm.tr('active_users', 'Aktif Kullanıcı:')}", "20"),
            (f"{Icons.PAUSE} {self.lm.tr('passive_users', 'Pasif Kullanıcı:')}", "3"),
            (f"🚫 {self.lm.tr('blocked_users', 'Bloklu Kullanıcı:')}", "2"),
            (f"👑 {self.lm.tr('super_admin_role', 'Super Admin:')}", "1"),
            (f"{Icons.WRENCH} {self.lm.tr('admin_role', 'Admin:')}", "4"),
            (f"{Icons.USER} {self.lm.tr('normal_user_role', 'Normal Kullanıcı:')}", "20")
        ]

        for label, value in user_stats:
            row_frame = tk.Frame(stats_container, bg='#ecf0f1')
            row_frame.pack(fill='x', pady=2)

            tk.Label(row_frame, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='#ecf0f1', anchor='w', width=20).pack(side='left')
            tk.Label(row_frame, text=value, font=('Segoe UI', 10),
                    bg='#ecf0f1', anchor='w').pack(side='left')

        # Kullanıcı yönetim araçları
        tools_frame = tk.LabelFrame(content_frame, text=self.lm.tr('management_tools', "Yönetim Araçları"),
                                  font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        tools_frame.pack(fill='x', padx=15, pady=15)

        tools_container = tk.Frame(tools_frame, bg='#ecf0f1')
        tools_container.pack(pady=15)

        tools = [
            (f"{Icons.USERS} {self.lm.tr('list_all_users', 'Tüm Kullanıcıları Listele')}", "#3498db", self.list_all_users),
            (f"{Icons.SECURE} {self.lm.tr('block_unblock_user', 'Kullanıcı Blokla/Çöz')}", "#e74c3c", self.block_unblock_user),
            (f"{Icons.KEY} {self.lm.tr('reset_password', 'Şifre Sıfırla')}", "#f39c12", self.reset_password),
            (f"{Icons.REPORT} {self.lm.tr('user_activity_report', 'Kullanıcı Aktivite Raporu')}", "#27ae60", self.user_activity_report)
        ]

        for text, color, command in tools:
            tk.Button(tools_container, text=text, font=('Segoe UI', 10, 'bold'),
                     bg=color, fg='white', relief='flat', padx=15, pady=8,
                     command=command).pack(pady=5, fill='x')

    def show_database_management(self) -> None:
        """Veritabanı yönetimi sayfasını göster"""
        self.clear_container()

        self.current_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.current_frame.pack(fill='both', expand=True)

        # Header
        self.create_header(self.current_frame, f"🗃️ {self.lm.tr('database_management_title', 'VERİTABANI YÖNETİMİ')}")

        # İçerik alanı
        content_frame = tk.Frame(self.current_frame, bg='#ecf0f1', relief='raised', bd=3)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Veritabanı bilgileri
        db_info_frame = tk.LabelFrame(content_frame, text=self.lm.tr('database_info', "Veritabanı Bilgileri"),
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        db_info_frame.pack(fill='x', padx=15, pady=15)

        info_container = tk.Frame(db_info_frame, bg='#ecf0f1')
        info_container.pack(fill='x', padx=10, pady=10)

        db_info = [
            (f"🗃️ {self.lm.tr('db_type', 'Veritabanı Türü:')}", "SQLite 3.x"),
            (f"📁 {self.lm.tr('file_size', 'Dosya Boyutu:')}", "15.2 MB"),
            (f"{Icons.REPORT} {self.lm.tr('table_count', 'Tablo Sayısı:')}", "23"),
            (f"{Icons.CLIPBOARD} {self.lm.tr('total_records', 'Toplam Kayıt:')}", "12,450"),
            (f"{Icons.LOADING} {self.lm.tr('last_backup', 'Son Yedekleme:')}", "28.10.2024 14:30"),
            (f"{Icons.SUCCESS} {self.lm.tr('status', 'Durum:')}", self.lm.tr('healthy', "Sağlıklı")),
            (f"{Icons.WRENCH} {self.lm.tr('last_maintenance', 'Son Bakım:')}", "25.10.2024")
        ]

        for label, value in db_info:
            row_frame = tk.Frame(info_container, bg='#ecf0f1')
            row_frame.pack(fill='x', pady=2)

            tk.Label(row_frame, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='#ecf0f1', anchor='w', width=20).pack(side='left')
            tk.Label(row_frame, text=value, font=('Segoe UI', 10),
                    bg='#ecf0f1', anchor='w').pack(side='left')

        # Veritabanı yönetim araçları
        db_tools_frame = tk.LabelFrame(content_frame, text=self.lm.tr('database_tools', "Veritabanı Araçları"),
                                     font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        db_tools_frame.pack(fill='x', padx=15, pady=15)

        tools_container = tk.Frame(db_tools_frame, bg='#ecf0f1')
        tools_container.pack(pady=15)

        db_tools = [
            (f"{Icons.SAVE} {self.lm.tr('manual_backup', 'Manuel Yedekleme')}", "#3498db", self.manual_backup),
            (f"{Icons.LOADING} {self.lm.tr('db_sync', 'Veritabanı Senkronizasyonu')}", "#9b59b6", self.sync_database),
            (f"🧹 {self.lm.tr('db_cleanup', 'Veritabanı Temizleme')}", "#e67e22", self.cleanup_database),
            (f"{Icons.WRENCH} {self.lm.tr('db_maintenance', 'Veritabanı Bakımı')}", "#27ae60", self.maintenance_database),
            (f"{Icons.REPORT} {self.lm.tr('performance_analysis', 'Performans Analizi')}", "#f39c12", self.performance_analysis)
        ]

        for text, color, command in db_tools:
            tk.Button(tools_container, text=text, font=('Segoe UI', 10, 'bold'),
                     bg=color, fg='white', relief='flat', padx=15, pady=8,
                     command=command).pack(pady=5, fill='x')

    def show_system_logs(self) -> None:
        """Sistem logları sayfasını göster"""
        self.clear_container()

        self.current_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.current_frame.pack(fill='both', expand=True)

        # Header
        self.create_header(self.current_frame, f"{Icons.REPORT} {self.lm.tr('system_logs_title', 'SİSTEM LOGLARI')}")

        # İçerik alanı (Container for canvas)
        content_container = tk.Frame(self.current_frame, bg='#ecf0f1', relief='raised', bd=3)
        content_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Canvas ve Scrollbar setup
        canvas = tk.Canvas(content_container, bg='#ecf0f1', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')

        # Canvas penceresi
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_window_width(event):
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_window_width)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel desteği
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        # Log istatistikleri
        log_stats_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('log_statistics', "Log İstatistikleri"),
                                      font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        log_stats_frame.pack(fill='x', padx=15, pady=15)

        stats_container = tk.Frame(log_stats_frame, bg='#ecf0f1')
        stats_container.pack(fill='x', padx=10, pady=10)

        log_stats = [
            (f"{Icons.CLIPBOARD} {self.lm.tr('total_logs', 'Toplam Log:')}", "1,245"),
            (f"{Icons.FAIL} {self.lm.tr('error_logs', 'Error Log:')}", "15"),
            (f"{Icons.WARNING} {self.lm.tr('warning_logs', 'Warning Log:')}", "89"),
            (f"{Icons.INFO} {self.lm.tr('info_logs', 'Info Log:')}", "1,141"),
            (f"{Icons.SEARCH} {self.lm.tr('debug_logs', 'Debug Log:')}", "0"),
            (f"{Icons.CALENDAR} {self.lm.tr('todays_logs', 'Bugünkü Log:')}", "142"),
            (f"🕐 {self.lm.tr('last_log', 'Son Log:')}", "14:25:33")
        ]

        for label, value in log_stats:
            row_frame = tk.Frame(stats_container, bg='#ecf0f1')
            row_frame.pack(fill='x', pady=2)

            tk.Label(row_frame, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='#ecf0f1', anchor='w', width=20).pack(side='left')
            tk.Label(row_frame, text=value, font=('Segoe UI', 10),
                    bg='#ecf0f1', anchor='w').pack(side='left')

        # Log yönetim araçları
        log_tools_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('log_management_tools', "Log Yönetim Araçları"),
                                      font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        log_tools_frame.pack(fill='x', padx=15, pady=15)

        tools_container = tk.Frame(log_tools_frame, bg='#ecf0f1')
        tools_container.pack(pady=15)

        log_tools = [
            (f"{Icons.CLIPBOARD} {self.lm.tr('view_all_logs', 'Tüm Logları Görüntüle')}", "#3498db", self.view_all_logs),
            (f"{Icons.FAIL} {self.lm.tr('filter_error_logs', 'Error Logları Filtrele')}", "#e74c3c", self.filter_error_logs),
            (f"{Icons.REPORT} {self.lm.tr('log_analysis', 'Log Analizi')}", "#9b59b6", self.analyze_logs),
            (f"{Icons.DELETE} {self.lm.tr('cleanup_old_logs', 'Eski Logları Temizle')}", "#e67e22", self.cleanup_old_logs),
            (f"{Icons.SAVE} {self.lm.tr('export_logs', 'Log Dışa Aktarma')}", "#27ae60", self.export_logs)
        ]

        for text, color, command in log_tools:
            tk.Button(tools_container, text=text, font=('Segoe UI', 10, 'bold'),
                     bg=color, fg='white', relief='flat', padx=15, pady=8,
                     command=command).pack(pady=5, fill='x')

    # ========================================================================
    # SİSTEM KONTROL FONKSİYONLARI
    # ========================================================================

    def restart_system(self):
        """Sistemi yeniden başlat"""
        try:
            result = messagebox.askyesno(self.lm.tr('restart_system_title', "Sistem Yeniden Başlatma"),
                                       self.lm.tr('restart_confirm_msg', "Sistemi yeniden başlatmak istediğinizden emin misiniz?\n\nBu işlem tüm aktif kullanıcıları etkileyecektir."))
            if result:
                messagebox.showinfo(
                    self.lm.tr('restarting', "Yeniden Başlatma"),
                    self.lm.tr('restart_countdown', "Sistem 5 saniye içinde yeniden başlatılacak..."),
                )
                
                # 1 saniye sonra simüle edilmiş restart mesajını göster
                self.parent.after(1000, lambda: messagebox.showinfo(
                    self.lm.tr('info', "Bilgi"),
                    self.lm.tr('demo_restart_msg', "Bu demo sürümde gerçek restart yapılmaz.\n\nGerçek sistemde:\n• Tüm servisler durdurulur\n• Veritabanı güvenli kapatılır\n• Sistem yeniden başlatılır"),
                ))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('restart_error', 'Sistem yeniden başlatma hatası')}: {e}")

    def security_scan(self):
        """Güvenlik taraması"""
        try:
            import random
            
            # İlerleme simülasyonu
            scan_results = {
                'threats_found': random.randint(0, 3),
                'vulnerabilities': random.randint(0, 2),
                'suspicious_activities': random.randint(0, 5)
            }

            messagebox.showinfo(
                self.lm.tr('security_scan_started', "Güvenlik Taraması Başlatıldı"),
                self.lm.tr('security_scan_msg', "Kapsamlı güvenlik taraması başlatılıyor...\n\n• Şüpheli aktivite tespiti\n• Güvenlik açığı analizi\n• Yetkisiz erişim kontrolü\n\nTarama tamamlandığında bildirilecek...")
            )
            
            def show_results():
                result_msg = f"""🛡️ {self.lm.tr('security_scan_completed', 'GÜVENLİK TARAMASI TAMAMLANDI')}

{Icons.REPORT} {self.lm.tr('results', 'SONUÇLAR')}:
• {self.lm.tr('threats_detected', 'Tespit edilen tehdit')}: {scan_results['threats_found']}
• {self.lm.tr('vulnerabilities', 'Güvenlik açığı')}: {scan_results['vulnerabilities']}  
• {self.lm.tr('suspicious_activity', 'Şüpheli aktivite')}: {scan_results['suspicious_activities']}

{f"{Icons.SUCCESS} {self.lm.tr('system_secure', 'Sistem güvenli görünüyor!')}" if sum(scan_results.values()) == 0 else f"{Icons.WARNING} {self.lm.tr('attention_needed', 'Dikkat gereken konular tespit edildi.')}"}"""

                messagebox.showinfo(self.lm.tr('security_scan_completed_title', "Güvenlik Taraması Tamamlandı"), result_msg)

            # 2 saniye sonra sonuçları göster
            self.parent.after(2000, show_results)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('security_scan_error', 'Güvenlik taraması hatası')}: {e}")

    def clear_cache(self):
        """Cache temizle"""
        try:
            result = messagebox.askyesno(self.lm.tr('clear_cache_title', "Cache Temizleme"),
                                       self.lm.tr('clear_cache_confirm', "Sistem cache'ini temizlemek istediğinizden emin misiniz?\n\n• Geçici dosyalar\n• Thumbnail cache\n• Session cache"))
            if result:
                cache_types = [
                    self.lm.tr('temp_files', "Geçici dosyalar"),
                    self.lm.tr('thumbnail_cache', "Thumbnail cache"),
                    self.lm.tr('session_cache', "Session cache"),
                    self.lm.tr('browser_cache', "Browser cache"),
                    self.lm.tr('system_cache', "System cache"),
                ]
                
                # Simülasyon fonksiyonu
                def clear_step(index=0):
                    if index < len(cache_types):
                        # Her adım için 500ms bekle
                        self.parent.after(500, lambda: clear_step(index + 1))
                    else:
                        # İşlem tamamlandı
                        success_msg = self.lm.tr('cache_cleared_success', "Sistem cache'i başarıyla temizlendi!")
                        types_msg = self.lm.tr('cache_types_cleared', 'farklı cache türü temizlendi')
                        perf_msg = self.lm.tr('perf_improved', 'Sistem performansı iyileştirildi')
                        disk_msg = self.lm.tr('disk_freed', 'Disk alanı serbest bırakıldı')

                        msg = (
                            f"{Icons.SUCCESS} {success_msg}\n\n"
                            f"• {len(cache_types)} {types_msg}\n"
                            f"• {perf_msg}\n"
                            f"• {disk_msg}"
                        )
                        messagebox.showinfo(
                            self.lm.tr('cache_cleared', "Cache Temizlendi"),
                            msg
                        )

                # İşlemi başlat
                clear_step()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('cache_clear_error', 'Cache temizleme hatası')}: {e}")

    def performance_report(self):
        """Performans raporu"""
        try:
            import random
            
            messagebox.showinfo(
                self.lm.tr('perf_analysis', "Performans Analizi"),
                self.lm.tr('perf_report_gen_msg', "Detaylı performans raporu oluşturuluyor...\n\nLütfen bekleyin..."),
            )

            def show_report():
                # Rastgele performans verileri
                cpu_usage = random.randint(10, 85)
                ram_usage = random.randint(30, 90)
                disk_io = random.randint(5, 50)
                network = random.randint(1, 30)
                
                status_normal = self.lm.tr('normal', 'Normal')
                status_high = self.lm.tr('high', 'Yüksek')
                status_critical = self.lm.tr('critical', 'Kritik')

                report = f"""{Icons.REPORT} {self.lm.tr('perf_report_title', 'PERFORMANS RAPORU')}

🖥️ {self.lm.tr('cpu_usage', 'CPU KULLANIMI')}: %{cpu_usage}
{'🟢 ' + status_normal if cpu_usage < 70 else '🟡 ' + status_high if cpu_usage < 85 else '🔴 ' + status_critical}

{Icons.SAVE} {self.lm.tr('ram_usage', 'RAM KULLANIMI')}: %{ram_usage}
{'🟢 ' + status_normal if ram_usage < 70 else '🟡 ' + status_high if ram_usage < 85 else '🔴 ' + status_critical}

💿 {self.lm.tr('disk_io', 'DİSK I/O')}: %{disk_io}
{'🟢 ' + status_normal if disk_io < 30 else '🟡 ' + status_high}

🌐 {self.lm.tr('network_traffic', 'AĞ TRAFİĞİ')}: %{network}
{'🟢 ' + status_normal if network < 20 else '🟡 ' + status_high}

{Icons.LIGHTBULB} {self.lm.tr('recommendations', 'ÖNERİLER')}:
• {self.lm.tr('rec_maintenance', 'Düzenli sistem bakımı yapın')}
• {self.lm.tr('rec_services', 'Gereksiz servisleri kapatın')}
• {self.lm.tr('rec_disk_clean', 'Disk temizliği yapın')}"""

                messagebox.showinfo(self.lm.tr('perf_report_title', "Performans Raporu"), report)

            # 1 saniye sonra raporu göster
            self.parent.after(1000, show_report)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('perf_report_error', 'Performans raporu hatası')}: {e}")

    # ========================================================================
    # KULLANICI YÖNETİM FONKSİYONLARI
    # ========================================================================

    def list_all_users(self):
        """Tüm kullanıcıları listele"""
        try:
            # Kullanıcı listesi penceresi oluştur
            user_window = tk.Toplevel()
            user_window.title(self.lm.tr('system_users', "Sistem Kullanıcıları"))
            user_window.geometry("800x600")
            user_window.configure(bg='#f5f5f5')

            # Başlık
            title_label = tk.Label(user_window, text=f"{Icons.USERS} {self.lm.tr('system_users', 'Sistem Kullanıcıları')}",
                                  font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f5f5f5')
            title_label.pack(pady=15)

            # Kullanıcı listesi (örnek veriler)

            # Treeview oluştur
            columns = ('ID', 'Kullanıcı Adı', 'Email', 'Rol', 'Durum', 'Son Giriş')
            user_tree = ttk.Treeview(user_window, columns=columns, show='headings', height=15)

            # Sütun başlıkları
            headers = [
                ('ID', 'id'),
                ('Kullanıcı Adı', 'username'),
                ('Email', 'email'),
                ('Rol', 'role'),
                ('Durum', 'status'),
                ('Son Giriş', 'last_login')
            ]
            for col, key in headers:
                user_tree.heading(col, text=self.lm.tr(key, col))
                user_tree.column(col, width=120)

            # Gerçek kullanıcı verilerini yükle
            try:
                import sqlite3
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()

                # Önce users tablosundaki sütunları kontrol et
                cursor.execute("PRAGMA table_info(users)")
                columns_info = cursor.fetchall()
                column_names = [col[1] for col in columns_info]

                # is_active sütunu var mı kontrol et
                has_is_active = 'is_active' in column_names

                # Güvenli sorgu oluştur
                if has_is_active:
                    query = """
                        SELECT id, username, 
                               COALESCE(email, '') as email,
                               COALESCE(role_name, 'Kullanıcı') as role_name,
                               CASE WHEN is_active = 1 THEN 'Aktif' ELSE 'Pasif' END as status,
                               COALESCE(last_login, 'Hiçbir zaman') as last_login
                        FROM users
                        WHERE username != '__super__'
                        ORDER BY username
                    """
                else:
                    query = """
                        SELECT id, username, 
                               COALESCE(email, '') as email,
                               COALESCE(role_name, 'Kullanıcı') as role_name,
                               'Aktif' as status,
                               COALESCE(last_login, 'Hiçbir zaman') as last_login
                        FROM users
                        WHERE username != '__super__'
                        ORDER BY username
                    """

                cursor.execute(query)
                users = cursor.fetchall()

                # Kullanıcıları tabloya ekle
                for user in users:
                    # Status ve role çevirisi yapılabilir
                    user_list = list(user)
                    user_list[3] = self.lm.tr(user_list[3].lower(), user_list[3]) if user_list[3] else ""
                    user_list[4] = self.lm.tr(user_list[4].lower(), user_list[4]) if user_list[4] else ""
                    user_tree.insert('', 'end', values=user_list)

                conn.close()

                # Eğer hiç kullanıcı yoksa örnek veri göster
                if not users:
                    sample_users = [
                        (1, 'admin', 'admin@company.com', 'Super Admin', 'Aktif', '28.10.2024 15:30'),
                        (2, 'user1', 'user1@company.com', 'Admin', 'Aktif', '28.10.2024 14:20')
                    ]
                    for user in sample_users:
                        user_list = list(user)
                        user_list[3] = self.lm.tr('super_admin', 'Super Admin') if user_list[3] == 'Super Admin' else self.lm.tr('admin', 'Admin')
                        user_list[4] = self.lm.tr('active', 'Aktif')
                        user_tree.insert('', 'end', values=user_list)

            except Exception as db_error:
                # Veritabanı hatası durumunda örnek veri göster
                logging.error(f"Veritabanı hatası: {db_error}")
                sample_users = [
                    (1, 'admin', 'admin@company.com', 'Super Admin', 'Aktif', '28.10.2024 15:30'),
                    (2, 'user1', 'user1@company.com', 'Admin', 'Aktif', '28.10.2024 14:20'),
                    (3, 'user2', 'user2@company.com', 'Kullanıcı', 'Aktif', '28.10.2024 13:15')
                ]
                for user in sample_users:
                    user_list = list(user)
                    user_list[3] = self.lm.tr('super_admin', 'Super Admin') if user_list[3] == 'Super Admin' else (self.lm.tr('admin', 'Admin') if user_list[3] == 'Admin' else self.lm.tr('user', 'Kullanıcı'))
                    user_list[4] = self.lm.tr('active', 'Aktif')
                    user_tree.insert('', 'end', values=user_list)

            user_tree.pack(fill='both', expand=True, padx=20, pady=10)

            # Alt butonlar
            btn_frame = tk.Frame(user_window, bg='#f5f5f5')
            btn_frame.pack(fill='x', padx=20, pady=10)

            tk.Button(
                btn_frame,
                text=f"{Icons.LOADING} {self.lm.tr('refresh', 'Yenile')}",
                bg='#3498db',
                fg='white',
                command=lambda: messagebox.showinfo(
                    self.lm.tr('refresh', "Yenile"),
                    self.lm.tr('user_list_refreshed', "Kullanıcı listesi yenilendi!"),
                ),
            ).pack(side='left', padx=5)

            tk.Button(
                btn_frame,
                text=f"{Icons.REPORT} {self.lm.tr('details', 'Detay')}",
                bg='#27ae60',
                fg='white',
                command=lambda: messagebox.showinfo(
                    self.lm.tr('details', "Detay"),
                    self.lm.tr('user_details_placeholder', "Seçili kullanıcının detayları gösterilecek"),
                ),
            ).pack(side='left', padx=5)

            tk.Button(btn_frame, text=f"{Icons.FAIL} {self.lm.tr('btn_close', 'Kapat')}", bg='#e74c3c', fg='white',
                     command=user_window.destroy).pack(side='right', padx=5)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('user_list_error', 'Kullanıcı listesi hatası')}: {e}")

    def block_unblock_user(self):
        """Kullanıcı blokla/çöz"""
        try:
            from tkinter import simpledialog

            username = simpledialog.askstring(self.lm.tr('select_user', "Kullanıcı Seç"), 
                                            self.lm.tr('enter_username_block', "Bloklanacak/çözülecek kullanıcı adını girin:"))

            if username:
                # Rastgele durum belirle (demo için)
                import random
                current_status = random.choice(['Aktif', 'Bloklu'])
                new_status = 'Bloklu' if current_status == 'Aktif' else 'Aktif'
                
                current_status_tr = self.lm.tr('active', 'Aktif') if current_status == 'Aktif' else self.lm.tr('blocked', 'Bloklu')
                new_status_tr = self.lm.tr('blocked', 'Bloklu') if new_status == 'Bloklu' else self.lm.tr('active', 'Aktif')

                result = messagebox.askyesno(self.lm.tr('user_status_change', "Kullanıcı Durum Değişikliği"),
                                           f"{self.lm.tr('user', 'Kullanıcı')}: {username}\n"
                                           f"{self.lm.tr('current_status', 'Mevcut Durum')}: {current_status_tr}\n"
                                           f"{self.lm.tr('new_status', 'Yeni Durum')}: {new_status_tr}\n\n"
                                           f"{self.lm.tr('confirm_continue', 'Devam etmek istediğinizden emin misiniz?')}")

                if result:
                    messagebox.showinfo(
                        self.lm.tr('success', "Başarılı"),
                        f"{Icons.SUCCESS} {self.lm.tr('user_status_updated', f'Kullanıcı {username} durumu {new_status_tr} olarak güncellendi!')}",
                    )

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('block_user_error', 'Kullanıcı blokla/çöz hatası')}: {e}")

    def reset_password(self):
        """Şifre sıfırla"""
        try:
            import random
            import string
            from tkinter import simpledialog

            username = simpledialog.askstring(self.lm.tr('select_user', "Kullanıcı Seç"), 
                                            self.lm.tr('enter_username_reset', "Şifresi sıfırlanacak kullanıcı adını girin:"))

            if username:
                result = messagebox.askyesno(self.lm.tr('password_reset', "Şifre Sıfırlama"),
                                           f"{self.lm.tr('reset_confirm_msg', f'Kullanıcı {username} için şifre sıfırlanacak.')}\n\n"
                                           f"{self.lm.tr('generate_auto_pass', 'Otomatik şifre oluşturulsun mu?')}")

                if result:
                    # Rastgele şifre oluştur
                    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                    messagebox.showinfo(self.lm.tr('password_reset_done', "Şifre Sıfırlandı"),
                                      f"{Icons.SUCCESS} {self.lm.tr('user', 'Kullanıcı')}: {username}\n"
                                      f"{Icons.KEY} {self.lm.tr('new_password', 'Yeni Şifre')}: {new_password}\n\n"
                                      f"{self.lm.tr('share_securely', 'Bu şifreyi kullanıcıya güvenli bir şekilde iletin!')}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('password_reset_error', 'Şifre sıfırlama hatası')}: {e}")

    def user_activity_report(self):
        """Kullanıcı aktivite raporu"""
        try:
            # Aktivite raporu penceresi
            activity_window = tk.Toplevel()
            activity_window.title(self.lm.tr('user_activity_report', "Kullanıcı Aktivite Raporu"))
            activity_window.geometry("900x700")
            activity_window.configure(bg='#f5f5f5')

            # Başlık
            title_label = tk.Label(activity_window, text=f"{Icons.REPORT} {self.lm.tr('user_activity_report', 'Kullanıcı Aktivite Raporu')}",
                                  font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f5f5f5')
            title_label.pack(pady=15)

            # İçerik alanı
            from tkinter import scrolledtext
            report_text = scrolledtext.ScrolledText(activity_window, height=25, font=('Consolas', 10))
            report_text.pack(fill='both', expand=True, padx=20, pady=10)

            # Örnek aktivite raporu
            report_content = f"""{Icons.CHART_UP} {self.lm.tr('user_activity_report_title', 'KULLANICI AKTİVİTE RAPORU')}
===============================================

{Icons.CALENDAR} {self.lm.tr('report_date', 'Rapor Tarihi')}: 28.10.2024 15:30
{Icons.TIME} {self.lm.tr('report_range', 'Rapor Aralığı')}: {self.lm.tr('last_7_days', 'Son 7 gün')}

{Icons.USERS} {self.lm.tr('general_stats', 'GENEL İSTATİSTİKLER')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('total_users', 'Toplam Kullanıcı')}: 25
• {self.lm.tr('active_users_7d', 'Aktif Kullanıcı (Son 7 gün)')}: 18
• {self.lm.tr('new_registrations_7d', 'Yeni Kayıt (Son 7 gün)')}: 2
• {self.lm.tr('blocked_users', 'Bloklu Kullanıcı')}: 1

{Icons.KEY} {self.lm.tr('login_stats', 'GİRİŞ İSTATİSTİKLERİ')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('total_logins', 'Toplam Giriş')}: 147
• {self.lm.tr('successful_logins', 'Başarılı Giriş')}: 142 (96.6%)
• {self.lm.tr('failed_logins', 'Başarısız Giriş')}: 5 (3.4%)
• {self.lm.tr('avg_session_time', 'Ortalama Oturum Süresi')}: 2.3 {self.lm.tr('hours', 'saat')}

{Icons.REPORT} {self.lm.tr('module_usage_report', 'MODÜL KULLANIM RAPORU')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('most_used', 'En Çok Kullanılan')}: {Icons.USER} {self.lm.tr('user_management', 'Kullanıcı Yönetimi')} (45%)
• {self.lm.tr('second', 'İkinci')}: {Icons.REPORT} {self.lm.tr('reporting', 'Raporlama')} (23%)
• {self.lm.tr('third', 'Üçüncü')}: 🛡️ {self.lm.tr('security', 'Güvenlik')} (18%)
• {self.lm.tr('fourth', 'Dördüncü')}: {Icons.SETTINGS} {self.lm.tr('system_settings', 'Sistem Ayarları')} (14%)

{Icons.TIME} {self.lm.tr('daily_activity', 'GÜNLÜK AKTİVİTE')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('peak_hour', 'En Yoğun Saat')}: 09:00-11:00 (32 {self.lm.tr('users', 'kullanıcı')})
• {self.lm.tr('lowest_hour', 'En Düşük Saat')}: 18:00-20:00 (8 {self.lm.tr('users', 'kullanıcı')})
• {self.lm.tr('weekend_activity', 'Hafta Sonu Aktivitesi')}: %23 {self.lm.tr('decrease', 'azalma')}

🚨 {self.lm.tr('security_events', 'GÜVENLİK OLAYLARI')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('suspicious_login', 'Şüpheli Giriş')}: 0
• {self.lm.tr('password_reset', 'Şifre Sıfırlama')}: 2
• {self.lm.tr('account_lockout', 'Hesap Kilitleme')}: 1
• {self.lm.tr('unauthorized_access', 'Yetkisiz Erişim Denemesi')}: 0

{Icons.CHART_UP} {self.lm.tr('trend_analysis', 'TREND ANALİZİ')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('user_growth', 'Kullanıcı Artışı')}: ↗️ %8 ({self.lm.tr('vs_last_month', 'Geçen aya göre')})
• {self.lm.tr('activity_growth', 'Aktivite Artışı')}: ↗️ %12 ({self.lm.tr('vs_last_month', 'Geçen aya göre')})
• {self.lm.tr('system_performance', 'Sistem Performansı')}: {Icons.SUCCESS} {self.lm.tr('stable', 'Stabil')}

{Icons.LIGHTBULB} {self.lm.tr('recommendations', 'ÖNERİLER')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('rec_weekend', 'Hafta sonu kullanımını teşvik edin')}
• {self.lm.tr('rec_security_training', 'Güvenlik eğitimi düzenleyin')}
• {self.lm.tr('rec_load_balance', 'Sistem yükünü dağıtın (09-11 arası)')}
"""

            report_text.insert('1.0', report_content)
            report_text.config(state='disabled')

            # Kapat butonu
            tk.Button(activity_window, text=f"{Icons.FAIL} {self.lm.tr('btn_close', 'Kapat')}", bg='#e74c3c', fg='white',
                     command=activity_window.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('activity_report_error', 'Aktivite raporu hatası')}: {e}")

    # ========================================================================
    # VERİTABANI YÖNETİM FONKSİYONLARI
    # ========================================================================

    def manual_backup(self):
        """Manuel yedekleme"""
        try:
            result = messagebox.askyesno(self.lm.tr('manual_backup', "Manuel Yedekleme"),
                                       f"{self.lm.tr('backup_start_confirm', 'Veritabanı manuel yedeklemesi başlatılsın mı?')}\n\n"
                                       f"• {self.lm.tr('backup_location_info', 'Yedek dosyası \'yedek\' klasöründe saklanacak')}\n"
                                       f"• {self.lm.tr('process_duration_warning', 'İşlem birkaç dakika sürebilir')}")

            if result:
                # Backup simulation with non-blocking delay
                messagebox.showinfo(
                    self.lm.tr('backup_started', "Yedekleme Başladı"),
                    f"{Icons.LOADING} {self.lm.tr('backup_in_progress', 'Veritabanı yedeklemesi başlatıldı...\\n\\nLütfen bekleyin...')}",
                )

                def finish_backup():
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = f"sdg_backup_{timestamp}.sqlite"

                    messagebox.showinfo(self.lm.tr('backup_completed', "Yedekleme Tamamlandı"),
                                      f"{Icons.SUCCESS} {self.lm.tr('backup_success', 'Veritabanı başarıyla yedeklendi!')}\\n\\n"
                                      f"📁 {self.lm.tr('file', 'Dosya')}: {backup_file}\\n"
                                      f"{Icons.CALENDAR} {self.lm.tr('date', 'Tarih')}: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\\n"
                                      f"{Icons.SAVE} {self.lm.tr('location', 'Konum')}: yedek/\\n\\n"
                                      f"{self.lm.tr('backup_secure_msg', 'Yedek dosyası güven altında saklandı.')}")

                # 2 saniye sonra tamamla (UI bloklamadan)
                self.parent.after(2000, finish_backup)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('backup_error', 'Manuel yedekleme hatası')}: {e}")

    def sync_database(self):
        """Veritabanı senkronizasyonu"""
        try:
            result = messagebox.askyesno(self.lm.tr('db_sync', "Veritabanı Senkronizasyonu"),
                                       f"{self.lm.tr('sync_start_confirm', 'Veritabanı senkronizasyonu başlatılsın mı?')}\n\n"
                                       f"• {self.lm.tr('tables_sync', 'Tüm tablolar eşitlenecek')}\n"
                                       f"• {self.lm.tr('data_consistency', 'Veri tutarlılığı kontrol edilecek')}\n"
                                       f"• {self.lm.tr('reindex', 'İndeksler yeniden oluşturulacak')}")

            if result:
                tables = ["users", "companies", "modules", "logs", "permissions", "settings"]

                messagebox.showinfo(self.lm.tr('sync_started', "Senkronizasyon Başladı"), 
                                  f"{Icons.LOADING} {self.lm.tr('sync_in_progress', 'Veritabanı senkronizasyonu başlatıldı...')}")

                def finish_sync():
                    messagebox.showinfo(self.lm.tr('sync_completed', "Senkronizasyon Tamamlandı"),
                                      f"{Icons.SUCCESS} {self.lm.tr('sync_success', 'Veritabanı senkronizasyonu tamamlandı!')}\\n\\n"
                                      f"{Icons.REPORT} {self.lm.tr('synced_tables', 'Eşitlenen Tablo')}: {len(tables)}\\n"
                                      f"{Icons.LOADING} {self.lm.tr('updated_records', 'Güncellenen Kayıt')}: 1,247\\n"
                                      f"{Icons.WRENCH} {self.lm.tr('recreated_indexes', 'Yeniden Oluşturulan İndeks')}: 15\\n\\n"
                                      f"{self.lm.tr('system_optimum', 'Sistem optimum performansta çalışıyor.')}")

                # Her tablo için 0.5sn (toplam len(tables) * 500 ms)
                total_delay = len(tables) * 500
                self.parent.after(total_delay, finish_sync)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('sync_error', 'Veritabanı senkronizasyon hatası')}: {e}")

    def cleanup_database(self):
        """Veritabanı temizleme"""
        try:
            result = messagebox.askyesno(self.lm.tr('db_cleanup', "Veritabanı Temizleme"),
                                       f"{Icons.WARNING} {self.lm.tr('cleanup_start_confirm', 'Veritabanı temizleme işlemi başlatılsın mı?')}\n\n"
                                       f"• {self.lm.tr('delete_unnecessary', 'Gereksiz kayıtlar silinecek')}\n"
                                       f"• {self.lm.tr('clean_orphan', 'Orphan datalar temizlenecek')}\n"
                                       f"• {self.lm.tr('archive_old_logs', 'Eski log kayıtları arşivlenecek')}\n\n"
                                       f"{self.lm.tr('irreversible_action', 'Bu işlem geri alınamaz!')}")

            if result:
                messagebox.showinfo(self.lm.tr('cleanup_started', "Temizleme Başladı"), 
                                  f"🧹 {self.lm.tr('cleanup_in_progress', 'Veritabanı temizleme işlemi başlatıldı...')}")

                def finish_cleanup():
                    cleanup_stats = {
                        'deleted_records': 1453,
                        'orphan_data': 89,
                        'archived_logs': 2341,
                        'freed_space': '125 MB'
                    }

                    messagebox.showinfo(self.lm.tr('cleanup_completed', "Temizleme Tamamlandı"),
                                      f"{Icons.SUCCESS} {self.lm.tr('cleanup_success', 'Veritabanı temizleme tamamlandı!')}\\n\\n"
                                      f"{Icons.DELETE} {self.lm.tr('deleted_records', 'Silinen Kayıt')}: {cleanup_stats['deleted_records']}\\n"
                                      f"🧹 {self.lm.tr('cleaned_orphan', 'Temizlenen Orphan')}: {cleanup_stats['orphan_data']}\\n"
                                      f"📦 {self.lm.tr('archived_logs', 'Arşivlenen Log')}: {cleanup_stats['archived_logs']}\\n"
                                      f"{Icons.SAVE} {self.lm.tr('freed_space', 'Serbest Alan')}: {cleanup_stats['freed_space']}\\n\\n"
                                      f"{self.lm.tr('db_optimized', 'Veritabanı optimize edildi!')}")

                # 3 saniye sonra tamamla
                self.parent.after(3000, finish_cleanup)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('cleanup_error', 'Veritabanı temizleme hatası')}: {e}")

    def maintenance_database(self):
        """Veritabanı bakımı"""
        try:
            result = messagebox.askyesno(self.lm.tr('db_maintenance', "Veritabanı Bakımı"),
                                       f"{self.lm.tr('maintenance_start_confirm', 'Kapsamlı veritabanı bakımı başlatılsın mı?')}\n\n"
                                       f"• {self.lm.tr('index_optimization', 'İndeks optimizasyonu')}\n"
                                       f"• {self.lm.tr('vacuum_process', 'VACUUM işlemi')}\n"
                                       f"• {self.lm.tr('stats_update', 'İstatistik güncelleme')}\n"
                                       f"• {self.lm.tr('perf_analysis', 'Performans analizi')}")

            if result:
                steps = [
                    self.lm.tr('step_index_analysis', "İndeks analizi yapılıyor..."),
                    self.lm.tr('step_vacuum', "VACUUM işlemi çalıştırılıyor..."),
                    self.lm.tr('step_stats_update', "İstatistikler güncelleniyor..."),
                    self.lm.tr('step_perf_metrics', "Performans metrikleri hesaplanıyor..."),
                    self.lm.tr('step_optimization_complete', "Optimizasyon tamamlanıyor...")
                ]

                messagebox.showinfo(self.lm.tr('maintenance_started', "Bakım Başladı"), 
                                  f"{Icons.WRENCH} {self.lm.tr('maintenance_in_progress', 'Kapsamlı veritabanı bakımı başlatıldı...')}")

                def process_step(step_index=0):
                    if step_index < len(steps):
                        # Her adım için 1000ms bekle
                        self.parent.after(1000, lambda: process_step(step_index + 1))
                    else:
                        messagebox.showinfo(self.lm.tr('maintenance_completed', "Bakım Tamamlandı"),
                                          f"{Icons.SUCCESS} {self.lm.tr('maintenance_success', 'Veritabanı bakımı tamamlandı!')}\\n\\n"
                                          f"{Icons.WRENCH} {self.lm.tr('optimization_steps', 'Optimizasyon Adımı')}: {len(steps)}\n"
                                          f"⚡ {self.lm.tr('perf_improvement', 'Performans İyileşmesi')}: %18\n"
                                          f"{Icons.REPORT} {self.lm.tr('index_efficiency', 'İndeks Verimliliği')}: %95\n"
                                          f"{Icons.SAVE} {self.lm.tr('disk_usage', 'Disk Kullanımı')}: {self.lm.tr('optimized', 'Optimize edildi')}\n\n"
                                          f"{self.lm.tr('system_max_perf', 'Sistem maksimum performansta çalışıyor!')}")

                # İşlemi başlat
                process_step()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('maintenance_error', 'Veritabanı bakım hatası')}: {e}")

    def performance_analysis(self):
        """Performans analizi"""
        try:
            # Performans analizi penceresi
            perf_window = tk.Toplevel()
            perf_window.title(self.lm.tr('db_perf_analysis', "Veritabanı Performans Analizi"))
            perf_window.geometry("900x700")
            perf_window.configure(bg='#f5f5f5')

            # Başlık
            title_label = tk.Label(perf_window, text=f"{Icons.REPORT} {self.lm.tr('db_perf_analysis', 'Veritabanı Performans Analizi')}",
                                  font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f5f5f5')
            title_label.pack(pady=15)

            # İçerik alanı
            from tkinter import scrolledtext
            perf_text = scrolledtext.ScrolledText(perf_window, height=30, font=('Consolas', 10))
            perf_text.pack(fill='both', expand=True, padx=20, pady=10)

            # Örnek performans analizi
            import random

            perf_content = f"""{Icons.SEARCH} {self.lm.tr('db_perf_analysis_title', 'VERİTABANI PERFORMANS ANALİZİ')}
===============================================

{Icons.CALENDAR} {self.lm.tr('analysis_date', 'Analiz Tarihi')}: 28.10.2024 15:30
🗃️ {self.lm.tr('database', 'Veritabanı')}: sdg_desktop.sqlite
📏 {self.lm.tr('total_size', 'Toplam Boyut')}: 15.2 MB

{Icons.REPORT} {self.lm.tr('table_analysis', 'TABLO ANALİZİ')}
━━━━━━━━━━━━━━━━━━━━━━━━━
{self.lm.tr('table_name', 'Tablo Adı').ljust(20)} {self.lm.tr('records', 'Kayıt').ljust(10)} {self.lm.tr('size', 'Boyut').ljust(10)} {self.lm.tr('index', 'İndeks').ljust(10)} {self.lm.tr('performance', 'Performans')}
─────────────────────────────────────────────────────────
users               {random.randint(50, 200):,}       245 KB   {Icons.SUCCESS} {self.lm.tr('good', 'İyi')}    🟢 {self.lm.tr('high', 'Yüksek')}
companies           {random.randint(10, 50):,}        89 KB    {Icons.SUCCESS} {self.lm.tr('good', 'İyi')}    🟢 {self.lm.tr('high', 'Yüksek')}  
modules             {random.randint(100, 500):,}      567 KB   {Icons.WARNING} {self.lm.tr('medium', 'Orta')}   🟡 {self.lm.tr('medium', 'Orta')}
logs                {random.randint(1000, 5000):,}    2.3 MB   {Icons.FAIL} {self.lm.tr('bad', 'Kötü')}   🔴 {self.lm.tr('low', 'Düşük')}
permissions         {random.randint(20, 100):,}       156 KB   {Icons.SUCCESS} {self.lm.tr('good', 'İyi')}    🟢 {self.lm.tr('high', 'Yüksek')}
settings            {random.randint(10, 30):,}        23 KB    {Icons.SUCCESS} {self.lm.tr('good', 'İyi')}    🟢 {self.lm.tr('high', 'Yüksek')}

⚡ {self.lm.tr('query_performance', 'SORGU PERFORMANSI')}
━━━━━━━━━━━━━━━━━━━━━━━━━
{self.lm.tr('query_type', 'Sorgu Türü').ljust(20)} {self.lm.tr('avg_time', 'Ort.Süre').ljust(10)} {self.lm.tr('frequency', 'Sıklık').ljust(10)} {self.lm.tr('optimization', 'Optimizasyon')}
─────────────────────────────────────────────────────
SELECT users        {random.randint(1, 5)}ms       {self.lm.tr('high', 'Yüksek')}   {Icons.SUCCESS} {self.lm.tr('optimum', 'Optimum')}
INSERT logs         {random.randint(2, 8)}ms       {self.lm.tr('high', 'Yüksek')}   {Icons.WARNING} {self.lm.tr('improvable', 'İyileştirilebilir')}
UPDATE companies    {random.randint(3, 10)}ms      {self.lm.tr('medium', 'Orta')}     {Icons.SUCCESS} {self.lm.tr('good', 'İyi')}
DELETE old_logs     {random.randint(50, 200)}ms     {self.lm.tr('low', 'Düşük')}    {Icons.FAIL} {self.lm.tr('slow', 'Yavaş')}

{Icons.WRENCH} {self.lm.tr('index_status', 'İNDEKS DURUMU')}  
━━━━━━━━━━━━━━━━━━━━━━━━━
{self.lm.tr('index_name', 'İndeks Adı').ljust(25)} {self.lm.tr('usage', 'Kullanım').ljust(10)} {self.lm.tr('efficiency', 'Etkinlik').ljust(10)} {self.lm.tr('recommendation', 'Öneri')}
─────────────────────────────────────────────────────
idx_users_email          %95       {Icons.SUCCESS} {self.lm.tr('high', 'Yüksek')}   {self.lm.tr('keep', 'Koru')}
idx_logs_timestamp       %78       🟡 {self.lm.tr('medium', 'Orta')}     {self.lm.tr('optimize', 'Optimize et')}
idx_companies_id         %98       {Icons.SUCCESS} {self.lm.tr('high', 'Yüksek')}   {self.lm.tr('keep', 'Koru')}
idx_modules_name         %45       {Icons.FAIL} {self.lm.tr('low', 'Düşük')}    {self.lm.tr('recreate', 'Yeniden oluştur')}

{Icons.SAVE} {self.lm.tr('storage_analysis', 'DEPOLAMA ANALİZİ')}
━━━━━━━━━━━━━━━━━━━━━━━━━
• {self.lm.tr('used_space', 'Kullanılan Alan')}: 15.2 MB
• {self.lm.tr('free_space', 'Boş Alan')}: 2.8 MB  
• {self.lm.tr('fragmentation', 'Fragmentasyon')}: %12
• {self.lm.tr('vacuum_rec', 'VACUUM Önerisi')}: {Icons.WARNING} {self.lm.tr('run_soon', 'Yakında çalıştır')}

🚨 {self.lm.tr('issue_detection', 'SORUN TESPİTLERİ')}
━━━━━━━━━━━━━━━━━━━━━━━━━
{Icons.WARNING} {self.lm.tr('logs_growing', 'logs tablosu büyüyor (günlük temizlik önerilir)')}
{Icons.WARNING} {self.lm.tr('idx_slow', 'idx_logs_timestamp yavaş (yeniden oluştur)')}
{Icons.FAIL} {self.lm.tr('old_logs_perf', 'Eski log kayıtları performansı düşürüyor')}

{Icons.LIGHTBULB} {self.lm.tr('improvement_recs', 'İYİLEŞTİRME ÖNERİLERİ')}
━━━━━━━━━━━━━━━━━━━━━━━━━
1. {Icons.DELETE} {self.lm.tr('archive_logs_rec', '30 günden eski logları arşivle')}
2. {Icons.WRENCH} {self.lm.tr('recreate_idx_rec', 'idx_modules_name indeksini yeniden oluştur')}
3. 🧹 {self.lm.tr('run_vacuum_rec', 'VACUUM işlemi çalıştır')}
4. {Icons.REPORT} {self.lm.tr('update_stats_rec', 'İstatistikleri güncelle')}
5. {Icons.SETTINGS} {self.lm.tr('schedule_maint_rec', 'Otomatik bakım zamanla')}

{Icons.CHART_UP} {self.lm.tr('perf_score', 'PERFORMANS SKORU')}: {random.randint(75, 95)}/100
{'🟢 ' + self.lm.tr('excellent', 'Mükemmel') if random.randint(75, 95) > 90 else '🟡 ' + self.lm.tr('good', 'İyi') if random.randint(75, 95) > 80 else '🟠 ' + self.lm.tr('medium', 'Orta')}
"""

            perf_text.insert('1.0', perf_content)
            perf_text.config(state='disabled')

            # Alt butonlar
            btn_frame = tk.Frame(perf_window, bg='#f5f5f5')
            btn_frame.pack(fill='x', padx=20, pady=10)

            tk.Button(
                btn_frame,
                text=f"{Icons.WRENCH} {self.lm.tr('optimize', 'Optimize Et')}",
                bg='#27ae60',
                fg='white',
                command=lambda: messagebox.showinfo(
                    self.lm.tr('optimization', "Optimizasyon"),
                    self.lm.tr('perf_optimization_started', "Performans optimizasyonu başlatıldı!"),
                ),
            ).pack(side='left', padx=5)

            tk.Button(
                btn_frame,
                text=f"{Icons.REPORT} {self.lm.tr('save_report', 'Rapor Kaydet')}",
                bg='#3498db',
                fg='white',
                command=lambda: messagebox.showinfo(
                    self.lm.tr('btn_save', "Kaydet"),
                    self.lm.tr('perf_report_saved', "Performans raporu kaydedildi!"),
                ),
            ).pack(side='left', padx=5)

            tk.Button(btn_frame, text=f"{Icons.FAIL} {self.lm.tr('btn_close', 'Kapat')}", bg='#e74c3c', fg='white',
                     command=perf_window.destroy).pack(side='right', padx=5)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('perf_analysis_error', 'Performans analizi hatası')}: {e}")

    # ========================================================================
    # LOG YÖNETİM FONKSİYONLARI
    # ========================================================================

    def view_all_logs(self):
        """Tüm logları görüntüle"""
        try:
            # Log görüntüleme penceresi
            log_window = tk.Toplevel()
            log_window.title("Sistem Logları")
            log_window.geometry("1000x700")
            log_window.configure(bg='#f5f5f5')

            # Başlık
            title_label = tk.Label(log_window, text=f"{Icons.CLIPBOARD} {self.lm.tr('system_logs_title', 'Sistem Logları')}",
                                  font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f5f5f5')
            title_label.pack(pady=15)

            # Log tablosu

            columns = ('Zaman', 'Seviye', 'Kullanıcı', 'Modül', 'Mesaj')
            log_tree = ttk.Treeview(log_window, columns=columns, show='headings', height=20)

            # Sütun ayarları
            log_tree.heading('Zaman', text=self.lm.tr('time', 'Zaman'))
            log_tree.heading('Seviye', text=self.lm.tr('level', 'Seviye'))
            log_tree.heading('Kullanıcı', text=self.lm.tr('user', 'Kullanıcı'))
            log_tree.heading('Modül', text=self.lm.tr('module', 'Modül'))
            log_tree.heading('Mesaj', text=self.lm.tr('message', 'Mesaj'))

            log_tree.column('Zaman', width=150)
            log_tree.column('Seviye', width=80)
            log_tree.column('Kullanıcı', width=100)
            log_tree.column('Modül', width=120)
            log_tree.column('Mesaj', width=300)

            # Örnek log verileri
            import random
            from datetime import datetime, timedelta

            log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
            users = ['admin', 'user1', 'user2', 'system']
            modules = ['Login', 'Database', 'Reports', 'Security', 'Backup']
            messages = [
                self.lm.tr('log_user_login', 'Kullanıcı başarıyla giriş yaptı'),
                self.lm.tr('log_db_connected', 'Veritabanı bağlantısı kuruldu'),
                self.lm.tr('log_report_generated', 'Rapor oluşturuldu'),
                self.lm.tr('log_security_scan', 'Güvenlik taraması tamamlandı'),
                self.lm.tr('log_backup_success', 'Yedekleme işlemi başarılı'),
                self.lm.tr('log_perf_check', 'Sistem performansı kontrol edildi'),
                self.lm.tr('log_user_logout', 'Kullanıcı çıkış yaptı'),
                self.lm.tr('log_cache_cleared', 'Cache temizlendi')
            ]

            # Rastgele loglar oluştur
            for i in range(50):
                log_time = (datetime.now() - timedelta(hours=random.randint(0, 72))).strftime('%d.%m.%Y %H:%M:%S')
                level = random.choice(log_levels)
                user = random.choice(users)
                module = random.choice(modules)
                message = random.choice(messages)

                # Seviye rengine göre tag
                tags = []
                if level == 'ERROR':
                    tags = ['error']
                elif level == 'WARNING':
                    tags = ['warning']
                elif level == 'INFO':
                    tags = ['info']

                log_tree.insert('', 'end', values=(log_time, level, user, module, message), tags=tags)

            # Renk etiketleri
            log_tree.tag_configure('error', foreground='#e74c3c')
            log_tree.tag_configure('warning', foreground='#f39c12')
            log_tree.tag_configure('info', foreground='#27ae60')

            # Scrollbar
            log_scroll = ttk.Scrollbar(log_window, orient='vertical', command=log_tree.yview)
            log_tree.configure(yscrollcommand=log_scroll.set)

            log_tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=10)
            log_scroll.pack(side='right', fill='y', padx=(0, 20), pady=10)

            # Alt butonlar
            btn_frame = tk.Frame(log_window, bg='#f5f5f5')
            btn_frame.pack(fill='x', padx=20, pady=10)

            tk.Button(btn_frame, text=f"{Icons.LOADING} {self.lm.tr('refresh', 'Yenile')}", bg='#3498db', fg='white',
                     command=lambda: messagebox.showinfo(self.lm.tr('refresh', "Yenile"), self.lm.tr('log_list_refreshed', "Log listesi yenilendi!"))).pack(side='left', padx=5)

            tk.Button(
                btn_frame,
                text=f"{Icons.REPORT} {self.lm.tr('filter', 'Filtrele')}",
                bg='#9b59b6',
                fg='white',
                command=lambda: messagebox.showinfo(
                    self.lm.tr('filter', "Filtre"),
                    self.lm.tr('log_filter_options', "Log filtreleme seçenekleri açılacak"),
                ),
            ).pack(side='left', padx=5)

            tk.Button(btn_frame, text=f"{Icons.FAIL} {self.lm.tr('btn_close', 'Kapat')}", bg='#e74c3c', fg='white',
                     command=log_window.destroy).pack(side='right', padx=5)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('log_view_error', 'Log görüntüleme hatası')}: {e}")

    def filter_error_logs(self):
        """Error logları filtrele"""
        try:
            # Error log penceresi
            error_window = tk.Toplevel()
            error_window.title(self.lm.tr('error_logs_title', "Error Logları"))
            error_window.geometry("900x600")
            error_window.configure(bg='#f5f5f5')

            # Başlık
            title_label = tk.Label(error_window, text=f"{Icons.FAIL} {self.lm.tr('error_logs_title', 'Error Logları')}",
                                  font=('Segoe UI', 16, 'bold'), fg='#e74c3c', bg='#f5f5f5')
            title_label.pack(pady=15)

            # Error log içeriği
            from tkinter import scrolledtext
            error_text = scrolledtext.ScrolledText(error_window, height=25, font=('Consolas', 10))
            error_text.pack(fill='both', expand=True, padx=20, pady=10)

            # Örnek error logları
            error_content = f"""{Icons.FAIL} SİSTEM ERROR LOGLARI
===============================================

🕐 28.10.2024 15:25:33 | ERROR | Database | Connection timeout
   ├─ Detay: Veritabanı bağlantısı 30 saniye sonra zaman aşımına uğradı
   ├─ Kullanıcı: system
   └─ Çözüm: Veritabanı sunucusu kontrol edilmeli

🕐 28.10.2024 14:42:15 | ERROR | Login | Authentication failed
   ├─ Detay: Kullanıcı 'guest' için geçersiz kimlik bilgileri
   ├─ IP: 192.168.1.105
   └─ Aksyon: Hesap 3 başarısız denemeden sonra geçici kilitlendi

🕐 28.10.2024 13:18:07 | ERROR | Reports | File generation failed
   ├─ Detay: Excel raporu oluşturulurken disk alanı yetersiz
   ├─ Modül: ReportGenerator
   └─ Çözüm: Disk temizliği gerekli (kalan alan: 245 MB)

🕐 28.10.2024 12:55:42 | ERROR | Backup | Backup process interrupted
   ├─ Detay: Yedekleme işlemi %67'de kesildi
   ├─ Hata Kodu: BACKUP_ERR_003
   └─ Aksyon: Manuel yedekleme başlatılmalı

🕐 28.10.2024 11:33:29 | ERROR | Security | Suspicious activity detected
   ├─ Detay: Bilinmeyen IP'den çoklu başarısız giriş denemesi
   ├─ IP: 203.142.87.45
   └─ Aksyon: IP adresi otomatik olarak engellendi

🕐 28.10.2024 10:15:18 | ERROR | Module | Import error in UserManager
   ├─ Detay: Python modülü yüklenirken hata
   ├─ Dosya: /modules/user/user_manager.py:line 45
   └─ Çözüm: Modül bağımlılıkları kontrol edilmeli

{Icons.REPORT} ERROR İSTATİSTİKLERİ (Son 24 Saat)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Toplam Error: 15
• Database Errors: 4
• Authentication Errors: 3
• System Errors: 8

🚨 KRİTİK DURUMLAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{Icons.WARNING} Veritabanı bağlantı sorunları artıyor
{Icons.WARNING} Disk alanı kritik seviyede (%8 kaldı)
{Icons.WARNING} Güvenlik tehditleri tespit edildi

{Icons.LIGHTBULB} ÖNERİLER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Veritabanı sunucusu performansını kontrol edin
2. Disk temizliği yapın
3. Güvenlik güncellemelerini uygulayın
4. Sistem yedeklemesini tamamlayın"""

            error_text.insert('1.0', error_content)
            error_text.config(state='disabled')

            # Kapat butonu
            tk.Button(error_window, text=f"{Icons.FAIL} {self.lm.tr('btn_close', 'Kapat')}", bg='#e74c3c', fg='white',
                     command=error_window.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_filter_error', 'Error log filtresi hatası')}: {e}")

    def analyze_logs(self):
        """Log analizi"""
        try:
            import random

            messagebox.showinfo(
                self.lm.tr('log_analysis_started', "Log Analizi Başladı"),
                self.lm.tr('log_analysis_wait', f"{Icons.SEARCH} Gelişmiş log analizi başlatılıyor...\n\nLütfen bekleyin..."),
            )

            def finish_analysis():
                # Rastgele analiz sonuçları
                analysis_results = {
                    'total_logs': random.randint(1000, 5000),
                    'error_rate': random.randint(2, 8),
                    'peak_hours': ['09:00-11:00', '14:00-16:00'],
                    'top_modules': ['Login', 'Database', 'Reports'],
                    'threats_detected': random.randint(0, 3)
                }

                analysis_msg = f"""{Icons.SEARCH} {self.lm.tr('log_analysis_results', 'LOG ANALİZİ SONUÇLARI')}

{Icons.REPORT} {self.lm.tr('general_stats', 'GENEL İSTATİSTİKLER')}:
• {self.lm.tr('analyzed_logs', 'Analiz Edilen Log')}: {analysis_results['total_logs']:,}
• {self.lm.tr('error_rate', 'Hata Oranı')}: %{analysis_results['error_rate']}
• {self.lm.tr('analysis_time', 'Analiz Süresi')}: 3.2 {self.lm.tr('seconds', 'saniye')}

{Icons.TIME} {self.lm.tr('peak_hours', 'YOĞUN SAATLER')}:
• {analysis_results['peak_hours'][0]} (%35 {self.lm.tr('activity', 'aktivite')})
• {analysis_results['peak_hours'][1]} (%28 {self.lm.tr('activity', 'aktivite')})

Icons.CHART_UP {self.lm.tr('top_used_modules', 'EN ÇOK KULLANILAN MODÜLLER')}:
• {analysis_results['top_modules'][0]} (%42)
• {analysis_results['top_modules'][1]} (%31)
• {analysis_results['top_modules'][2]} (%18)

Icons.SEARCH {self.lm.tr('pattern_analysis', 'PATTERN ANALİZİ')}:
• {self.lm.tr('repeated_errors_detected', 'Tekrarlanan hatalar tespit edildi')}
• {self.lm.tr('security_patterns_analyzed', 'Güvenlik paternleri analiz edildi')}
• {self.lm.tr('perf_bottlenecks_identified', 'Performans darboğazları belirlendi')}

{
    '🛡️ ' + self.lm.tr('security_threats_detected', 'Güvenlik tehditleri tespit edildi!')
    if analysis_results['threats_detected'] > 0
    else f"{Icons.SUCCESS} " + self.lm.tr('security_ok', 'Güvenlik açısından sorun tespit edilmedi')
}"""

                messagebox.showinfo(self.lm.tr('log_analysis_completed', "Log Analizi Tamamlandı"), analysis_msg)

            # 3 saniye sonra tamamla
            self.parent.after(3000, finish_analysis)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('log_analysis_error', 'Log analizi hatası')}: {e}")

    def cleanup_old_logs(self):
        """Eski logları temizle"""
        try:
            result = messagebox.askyesno(self.lm.tr('log_cleanup_title', "Log Temizleme"),
                                       f"{Icons.WARNING} {self.lm.tr('log_cleanup_confirm', '30 günden eski loglar silinsin mi?')}\n\n"
                                       f"• {self.lm.tr('log_cleanup_warn1', 'Eski log kayıtları kalıcı olarak silinecek')}\n"
                                       f"• {self.lm.tr('log_cleanup_warn2', 'Sistem performansı iyileşecek')}\n"
                                       f"• {self.lm.tr('log_cleanup_warn3', 'Disk alanı serbest kalacak')}\n\n"
                                       f"{self.lm.tr('action_irreversible', 'Bu işlem geri alınamaz!')}")

            if result:
                messagebox.showinfo(self.lm.tr('log_cleanup_started', "Log Temizleme Başladı"), f"{Icons.DELETE} {self.lm.tr('log_cleanup_progress', 'Eski loglar temizleniyor...')}")

                def finish_cleanup_logs():
                    cleanup_stats = {
                        'deleted_logs': 2847,
                        'freed_space': '89 MB',
                        'oldest_deleted': '28.09.2024',
                        'performance_gain': '15%'
                    }

                    messagebox.showinfo(self.lm.tr('log_cleanup_completed', "Log Temizleme Tamamlandı"),
                                      f"{Icons.SUCCESS} {self.lm.tr('log_cleanup_completed_msg', 'Eski log temizleme tamamlandı!')}\\n\\n"
                                      f"{Icons.DELETE} {self.lm.tr('deleted_logs', 'Silinen Log')}: {cleanup_stats['deleted_logs']:,}\\n"
                                      f"{Icons.SAVE} {self.lm.tr('freed_space', 'Serbest Alan')}: {cleanup_stats['freed_space']}\\n"
                                      f"{Icons.CALENDAR} {self.lm.tr('oldest_date', 'En Eski Tarih')}: {cleanup_stats['oldest_deleted']}\\n"
                                      f"⚡ {self.lm.tr('perf_gain', 'Performans Artışı')}: {cleanup_stats['performance_gain']}\\n\\n"
                                      f"{self.lm.tr('system_faster', 'Sistem daha hızlı çalışacak!')}")

                # 2 saniye sonra tamamla
                self.parent.after(2000, finish_cleanup_logs)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('log_cleanup_error', 'Log temizleme hatası')}: {e}")

    def export_logs(self):
        """Log dışa aktarma"""
        try:
            from tkinter import filedialog

            # Dosya formatı seçimi
            format_choice = messagebox.askyesnocancel(self.lm.tr('log_export_format', "Export Formatı"),
                                                    f"{self.lm.tr('log_export_msg', 'Log dışa aktarma formatını seçin:')}\n\n"
                                                    "EVET: CSV\n"
                                                    "HAYIR: Excel\n"
                                                    f"{self.lm.tr('cancel_to_abort', 'İPTAL: İşlemi iptal et')}")

            if format_choice is not None:  # İptal edilmedi
                file_format = "CSV" if format_choice else "Excel"
                extension = ".csv" if format_choice else ".xlsx"

                # Dosya kaydetme dialogu
                import datetime
                default_name = f"sistem_loglari_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"

                file_path = filedialog.asksaveasfilename(
                    title=self.lm.tr('export_logs_title', 'Logları Dışa Aktar'),
                    defaultextension=extension,
                    initialname=default_name,
                    filetypes=[
                        (f"{file_format} {self.lm.tr('files_suffix', 'Dosyaları')}", f"*{extension}"),
                        (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")
                    ]
                )

                if file_path:
                    messagebox.showinfo(self.lm.tr('log_export_started', "Export Başladı"), f"{Icons.REPORT} {self.lm.tr('log_export_progress', 'Loglar {file_format} formatında dışa aktarılıyor...').format(file_format=file_format)}")

                def finish_export():
                    export_stats = {
                        'total_logs': 1524,
                        'file_size': '2.3 MB',
                        'export_time': '2.1 saniye'
                    }

                    messagebox.showinfo(self.lm.tr('log_export_completed', "Export Tamamlandı"),
                                      f"{Icons.SUCCESS} {self.lm.tr('log_export_completed_msg', 'Log dışa aktarma tamamlandı!')}\\n\\n"
                                      f"📁 {self.lm.tr('file', 'Dosya')}: {file_path}\\n"
                                      f"{Icons.REPORT} {self.lm.tr('log_count', 'Log Sayısı')}: {export_stats['total_logs']:,}\\n"
                                      f"{Icons.SAVE} {self.lm.tr('file_size', 'Dosya Boyutu')}: {export_stats['file_size']}\\n"
                                      f"⏱️ {self.lm.tr('duration', 'Süre')}: {export_stats['export_time']}\\n\\n"
                                      f"{self.lm.tr('log_export_success', 'Dosya başarıyla kaydedildi!')}")

                # 2 saniye sonra tamamla
                self.parent.after(2000, finish_export)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('log_export_error', 'Log dışa aktarma hatası')}: {e}")

    # ========================================================================
    # MODÜL YETKİLERİ YÖNETİMİ
    # ========================================================================

    def show_module_permissions(self) -> None:
        """Modül yetkileri yönetim sayfasını göster"""
        self.clear_container()

        self.current_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.current_frame.pack(fill='both', expand=True)

        # Geri butonu
        self.create_back_button(self.current_frame)

        # Başlık
        title_label = tk.Label(self.current_frame, text=f"{Icons.WRENCH} {self.lm.tr('module_permissions_title', 'MODÜL YETKİLERİ YÖNETİMİ')}",
                              font=('Segoe UI', 18, 'bold'), fg='#16a085', bg='#2c3e50')
        title_label.pack(pady=20)

        # Açıklama
        desc_label = tk.Label(self.current_frame,
                             text=self.lm.tr('module_permissions_desc', "Sistem modüllerini açıp kapatabilir, lisans kontrolü yapabilirsiniz."),
                             font=('Segoe UI', 11), fg='#bdc3c7', bg='#2c3e50')
        desc_label.pack(pady=(0, 20))

        # Ana içerik alanı
        main_content = tk.Frame(self.current_frame, bg='#ecf0f1', relief='raised', bd=3)
        main_content.pack(fill='both', expand=True, padx=20, pady=10)

        # Scrollable area için canvas
        canvas = tk.Canvas(main_content, bg='#ecf0f1', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Modül listesi başlığı
        header_frame = tk.Frame(scrollable_frame, bg='#34495e', height=40)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=f"{Icons.CLIPBOARD} {self.lm.tr('system_modules_title', 'SİSTEM MODÜLLERİ')}", font=('Segoe UI', 14, 'bold'),
                fg='white', bg='#34495e').pack(expand=True)

        # Modül listesi
        self.module_checkboxes = {}
        self.create_module_list(scrollable_frame)

        # Canvas ve scrollbar yerleştirme
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Alt butonlar
        button_frame = tk.Frame(self.current_frame, bg='#2c3e50')
        button_frame.pack(fill='x', padx=20, pady=10)

        tk.Button(button_frame, text=f"{Icons.SAVE} {self.lm.tr('save_changes', 'Değişiklikleri Kaydet')}", font=('Segoe UI', 11, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', padx=20, pady=8,
                 command=self.save_module_permissions, cursor='hand2').pack(side='left', padx=5)

        tk.Button(button_frame, text=f"{Icons.LOADING} {self.lm.tr('refresh', 'Yenile')}", font=('Segoe UI', 11, 'bold'),
                 bg='#3498db', fg='white', relief='flat', padx=20, pady=8,
                 command=self.show_module_permissions, cursor='hand2').pack(side='left', padx=5)

        tk.Button(button_frame, text=f"{Icons.SUCCESS} {self.lm.tr('enable_all', 'Tümünü Aç')}", font=('Segoe UI', 11, 'bold'),
                 bg='#f39c12', fg='white', relief='flat', padx=20, pady=8,
                 command=self.enable_all_modules, cursor='hand2').pack(side='left', padx=5)

        tk.Button(button_frame, text=f"{Icons.FAIL} {self.lm.tr('disable_all', 'Tümünü Kapat')}", font=('Segoe UI', 11, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', padx=20, pady=8,
                 command=self.disable_all_modules, cursor='hand2').pack(side='right', padx=5)

    def create_module_list(self, parent) -> None:
        """Modül listesi oluştur"""
        # Sistemdeki tüm modüller
        all_modules = [
            # Ana SDG modülleri
            (self.lm.tr('module_sdg_title', "SDG Hedefleri"), "sdg", self.lm.tr('module_sdg_desc', "Sürdürülebilir Kalkınma Hedefleri"), True),
            (self.lm.tr('module_gri_title', "GRI Standartları"), "gri", self.lm.tr('module_gri_desc', "Global Reporting Initiative"), True),
            (self.lm.tr('module_tsrs_title', "TSRS Raporlama"), "tsrs", self.lm.tr('module_tsrs_desc', "Türkiye Sürdürülebilirlik Raporlaması"), True),
            (self.lm.tr('module_esrs_title', "ESRS (Avrupa)"), "esrs", self.lm.tr('module_esrs_desc', "Avrupa Sürdürülebilirlik Standartları"), True),
            (self.lm.tr('module_tcfd_title', "TCFD Framework"), "tcfd", self.lm.tr('module_tcfd_desc', "Task Force on Climate-related Disclosures"), False),
            (self.lm.tr('module_sasb_title', "SASB Standartları"), "sasb", self.lm.tr('module_sasb_desc', "Sustainability Accounting Standards Board"), False),
            (self.lm.tr('module_eu_taxonomy_title', "EU Taxonomy"), "eu_taxonomy", self.lm.tr('module_eu_taxonomy_desc', "Avrupa Birliği Taksonomisi"), False),

            # Yönetim modülleri
            (self.lm.tr('module_user_mgmt_title', "Kullanıcı Yönetimi"), "user_management", self.lm.tr('module_user_mgmt_desc', "Kullanıcı ve yetki yönetimi"), True),
            (self.lm.tr('module_company_mgmt_title', "Şirket Yönetimi"), "company_management", self.lm.tr('module_company_mgmt_desc', "Çoklu şirket sistemi"), True),
            (self.lm.tr('module_security_mgmt_title', "Güvenlik Yönetimi"), "security_management", self.lm.tr('module_security_mgmt_desc', "2FA, şifreleme ve güvenlik"), True),
            (self.lm.tr('module_license_mgmt_title', "Lisans Yönetimi"), "license_management", self.lm.tr('module_license_mgmt_desc', "Lisanslama ve donanım bağlama"), True),

            # Raporlama modülleri
            (self.lm.tr('module_reporting_title', "Raporlama Merkezi"), "reporting", self.lm.tr('module_reporting_desc', "Birleşik rapor sistemi"), True),
            (self.lm.tr('module_auto_reporting_title', "Otomatik Raporlama"), "auto_reporting", self.lm.tr('module_auto_reporting_desc', "Zamanlı otomatik raporlar"), False),
            (self.lm.tr('module_advanced_dashboard_title', "Gelişmiş Dashboard"), "advanced_dashboard", self.lm.tr('module_advanced_dashboard_desc', "İstatistikler ve grafikler"), True),

            # Entegrasyon modülleri
            (self.lm.tr('module_erp_integration_title', "ERP Entegrasyon"), "erp_integration", self.lm.tr('module_erp_integration_desc', "ERP sistemleri ile entegrasyon"), False),
            (self.lm.tr('module_doc_processing_title', "Belge İşleme & AI"), "document_processing", self.lm.tr('module_doc_processing_desc', "AI destekli belge analizi"), False),
            (self.lm.tr('module_ai_module_title', "AI Analiz Modülü"), "ai_module", self.lm.tr('module_ai_module_desc', "Yapay zeka destekli analiz"), False),

            # Destek modülleri
            (self.lm.tr('module_task_mgmt_title', "Görev Yönetimi"), "task_management", self.lm.tr('module_task_mgmt_desc', "Proje ve görev takibi"), True),
            (self.lm.tr('module_advanced_security_title', "Gelişmiş Güvenlik"), "advanced_security", self.lm.tr('module_advanced_security_desc', "İleri güvenlik özellikleri"), False),
            (self.lm.tr('module_super_admin_title', "Super Admin"), "super_admin", self.lm.tr('module_super_admin_desc', "Sistem yönetimi (her zaman açık)"), True)
        ]

        # Mevcut modül durumlarını yükle
        module_states = self.load_module_states()

        for i, (name, key, description, default_enabled) in enumerate(all_modules):
            # Modül durumunu al (varsayılan veya kayıtlı)
            is_enabled = module_states.get(key, default_enabled)

            # Modül frame'i
            module_frame = tk.Frame(parent, bg='#ffffff' if i % 2 == 0 else '#f8f9fa',
                                   relief='solid', bd=1)
            module_frame.pack(fill='x', padx=10, pady=2)

            # Sol taraf - Checkbox ve modül bilgisi
            left_frame = tk.Frame(module_frame, bg=module_frame['bg'])
            left_frame.pack(side='left', fill='both', expand=True, padx=15, pady=10)

            # Checkbox
            var = tk.BooleanVar(value=is_enabled)
            self.module_checkboxes[key] = var

            checkbox = tk.Checkbutton(left_frame, variable=var,
                                     font=('Segoe UI', 10, 'bold'), bg=module_frame['bg'],
                                     activebackground=module_frame['bg'])

            # Super Admin modülü her zaman açık kalmalı
            if key == "super_admin":
                checkbox.config(state='disabled')
                var.set(True)

            checkbox.pack(side='left', padx=(0, 10))

            # Modül bilgileri
            info_frame = tk.Frame(left_frame, bg=module_frame['bg'])
            info_frame.pack(side='left', fill='both', expand=True)

            # Modül adı
            name_label = tk.Label(info_frame, text=name, font=('Segoe UI', 11, 'bold'),
                                 fg='#2c3e50', bg=module_frame['bg'])
            name_label.pack(anchor='w')

            # Modül açıklaması
            desc_label = tk.Label(info_frame, text=description, font=('Segoe UI', 9),
                                 fg='#7f8c8d', bg=module_frame['bg'])
            desc_label.pack(anchor='w')

            # Sağ taraf - Durum göstergesi
            right_frame = tk.Frame(module_frame, bg=module_frame['bg'])
            right_frame.pack(side='right', padx=15, pady=10)

            # Durum etiketi
            status_color = '#27ae60' if is_enabled else '#e74c3c'
            status_text = '🟢 AKTİF' if is_enabled else '🔴 PASİF'

            status_label = tk.Label(right_frame, text=status_text, font=('Segoe UI', 10, 'bold'),
                                   fg=status_color, bg=module_frame['bg'])
            status_label.pack()

            # Modül key'ini tooltip olarak sakla
            module_frame.module_key = key

    def load_module_states(self) -> dict:
        """Modül durumlarını veritabanından yükle"""
        try:
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Module_states tablosunu oluştur (yoksa)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS module_states (
                    module_key TEXT PRIMARY KEY,
                    enabled BOOLEAN NOT NULL DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            ''')

            # Mevcut durumları al
            cursor.execute('SELECT module_key, enabled FROM module_states')
            results = cursor.fetchall()

            conn.close()

            return {key: bool(enabled) for key, enabled in results}

        except Exception as e:
            logging.error(f"Modül durumları yüklenirken hata: {e}")
            return {}

    def save_module_permissions(self) -> None:
        """Modül izinlerini kaydet"""
        try:
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Tüm modül durumlarını kaydet
            for module_key, var in self.module_checkboxes.items():
                enabled = var.get()

                cursor.execute('''
                    INSERT OR REPLACE INTO module_states 
                    (module_key, enabled, updated_at, updated_by)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ''', (module_key, enabled, f'super_admin_{self.current_user_id}'))

            conn.commit()
            conn.close()

            # Başarı mesajı
            changed_modules = []
            for module_key, var in self.module_checkboxes.items():
                if var.get():
                    changed_modules.append(f"{Icons.SUCCESS} {module_key}")
                else:
                    changed_modules.append(f"{Icons.FAIL} {module_key}")

            module_summary = "\\n".join(changed_modules[:10])  # İlk 10'unu göster
            if len(changed_modules) > 10:
                module_summary += f"\\n... ve {len(changed_modules) - 10} modül daha"

            messagebox.showinfo("Başarılı",
                              f"{Icons.SUCCESS} Modül izinleri başarıyla kaydedildi!\\n\\n"
                              f"{Icons.REPORT} Güncellenen Modül Sayısı: {len(self.module_checkboxes)}\\n\\n"
                              f"{Icons.CLIPBOARD} MODÜL DURUMLARI:\\n{module_summary}\\n\\n"
                              f"{Icons.WARNING} Değişikliklerin etkili olması için\\n"
                              f"uygulamayı yeniden başlatın.")

        except Exception as e:
            messagebox.showerror("Hata", f"Modül izinleri kaydedilemedi: {e}")

    def enable_all_modules(self) -> None:
        """Tüm modülleri etkinleştir"""
        result = messagebox.askyesno("Tüm Modülleri Etkinleştir",
                                   "Tüm modüller etkinleştirilsin mi?\\n\\n"
                                   "Bu işlem tüm özellikleri açar ve\\n"
                                   "lisans kontrolünü devre dışı bırakır.")

        if result:
            for var in self.module_checkboxes.values():
                var.set(True)
            messagebox.showinfo("Başarılı", f"{Icons.SUCCESS} Tüm modüller etkinleştirildi!")

    def disable_all_modules(self) -> None:
        """Tüm modülleri devre dışı bırak (Super Admin hariç)"""
        result = messagebox.askyesno("Tüm Modülleri Devre Dışı Bırak",
                                   f"{Icons.WARNING} Tüm modüller kapatılsın mı?\\n\\n"
                                   "Bu işlem sistemi minimal moda geçirir.\\n"
                                   "Sadece Super Admin açık kalacak.\\n\\n"
                                   "Bu işlemi onaylıyor musunuz?")

        if result:
            for key, var in self.module_checkboxes.items():
                if key != "super_admin":  # Super Admin her zaman açık
                    var.set(False)
            messagebox.showinfo("Başarılı",
                              f"{Icons.FAIL} Tüm modüller kapatıldı!\\n\\n"
                              f"{Icons.SUCCESS} Super Admin açık kaldı.\\n"
                              f"{Icons.SAVE} Değişiklikleri kaydetmeyi unutmayın!")
