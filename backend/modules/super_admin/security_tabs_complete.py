import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super Admin Security Tabs - COMPLETE VERSION
IP Control, Rate Limiting, Monitoring Dashboard
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from config.icons import Icons

# Import edilecek (super_admin_gui.py içinde)
# from .components.ip_manager import IPManager
# from .components.rate_limiter import RateLimiter
# from .components.monitoring_dashboard import MonitoringDashboard


class SecurityTabsComplete:
    """Kalan güvenlik sekmelerini ekleyen mixin - IP, Rate Limiting, Monitoring"""

    def __init__(self):
        """Mixin başlatıcı"""
        pass

    def show_ip_control(self):
        """🛡️ IP Kontrolü Sekmesi"""
        self.clear_right_panel()

        # Import
        from .components.ip_manager import IPManager
        self.ip_manager = IPManager(self.db_path)

        # Başlık
        header = tk.Frame(self.right_frame, bg='#e67e22', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🛡️ IP KONTROLÜ",
            font=('Segoe UI', 16, 'bold'),
            bg='#e67e22',
            fg='white'
        ).pack(pady=15)

        # Notebook
        notebook = ttk.Notebook(self.right_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Whitelist
        white_frame = tk.Frame(notebook, bg='white')
        notebook.add(white_frame, text=" Whitelist")
        self._create_whitelist_tab(white_frame)

        # Tab 2: Blacklist
        black_frame = tk.Frame(notebook, bg='white')
        notebook.add(black_frame, text=" Blacklist")
        self._create_blacklist_tab(black_frame)

        # Tab 3: İstatistikler
        stats_frame = tk.Frame(notebook, bg='white')
        notebook.add(stats_frame, text=" İstatistikler")
        self._create_ip_stats_tab(stats_frame)

    def _create_whitelist_tab(self, parent):
        """IP Whitelist UI"""
        # Add IP Form
        form_frame = tk.LabelFrame(parent, text="Whitelist'e Ekle",
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        form_frame.pack(fill='x', padx=20, pady=15)

        form_inner = tk.Frame(form_frame, bg='white')
        form_inner.pack(padx=15, pady=15)

        tk.Label(form_inner, text="IP Adresi:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ip_entry = tk.Entry(form_inner, font=('Segoe UI', 10), width=20)
        ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_inner, text="Açıklama:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        desc_entry = tk.Entry(form_inner, font=('Segoe UI', 10), width=30)
        desc_entry.grid(row=0, column=3, padx=5, pady=5)

        def add_to_whitelist():
            ip = ip_entry.get().strip()
            desc = desc_entry.get().strip()

            if not ip:
                messagebox.showerror("Hata", "IP adresi gerekli!")
                return

            result = self.ip_manager.add_to_whitelist(ip, desc, "admin")
            if result['success']:
                messagebox.showinfo("Başarılı", result['message'])
                ip_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                load_whitelist()
            else:
                messagebox.showerror("Hata", result['message'])

        tk.Button(form_inner, text=f"{Icons.ADD} Whitelist'e Ekle", font=('Segoe UI', 10, 'bold'),
                 bg='#27ae60', fg='white', padx=15, pady=8, command=add_to_whitelist).grid(row=0, column=4, padx=10)

        # Whitelist Table
        list_frame = tk.LabelFrame(parent, text="Whitelist'teki IP'ler",
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Toolbar
        toolbar = tk.Frame(list_frame, bg='white')
        toolbar.pack(fill='x', padx=10, pady=10)

        tk.Button(toolbar, text=f"{Icons.LOADING} Yenile", font=('Segoe UI', 9, 'bold'),
                 bg='#3498db', fg='white', padx=12, pady=6,
                 command=lambda: load_whitelist()).pack(side='left', padx=5)

        tk.Button(toolbar, text=f"{Icons.FAIL} Seçileni Sil", font=('Segoe UI', 9, 'bold'),
                 bg='#e74c3c', fg='white', padx=12, pady=6,
                 command=lambda: remove_from_whitelist()).pack(side='left', padx=5)

        # Tree
        columns = ('ID', 'IP Adresi', 'Açıklama', 'Ekleyen', 'Tarih', 'Aktif')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        def load_whitelist():
            for item in tree.get_children():
                tree.delete(item)

            whitelist = self.ip_manager.get_whitelist()
            for item in whitelist:
                tree.insert('', 'end', values=(
                    item['id'],
                    item['ip'],
                    item['description'],
                    item['added_by'],
                    item['created_at'][:16],
                    Icons.PASS if item['active'] else Icons.REJECT
                ))

        def remove_from_whitelist():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Uyarı", "Lütfen bir IP seçin!")
                return

            item = tree.item(selection[0])
            ip = item['values'][1]

            confirm = messagebox.askyesno("Onay", f"{ip} adresini whitelist'ten çıkarmak istiyor musunuz?")
            if confirm:
                if self.ip_manager.remove_from_whitelist(ip):
                    messagebox.showinfo("Başarılı", "IP whitelist'ten çıkarıldı!")
                    load_whitelist()
                else:
                    messagebox.showerror("Hata", "IP çıkarılamadı!")

        load_whitelist()

    def _create_blacklist_tab(self, parent):
        """IP Blacklist UI"""
        # Add IP Form
        form_frame = tk.LabelFrame(parent, text="Blacklist'e Ekle",
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        form_frame.pack(fill='x', padx=20, pady=15)

        form_inner = tk.Frame(form_frame, bg='white')
        form_inner.pack(padx=15, pady=15)

        tk.Label(form_inner, text="IP Adresi:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ip_entry = tk.Entry(form_inner, font=('Segoe UI', 10), width=20)
        ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_inner, text="Sebep:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        reason_var = tk.StringVar(value='manual')
        reasons = [('Manuel', 'manual'), ('Brute Force', 'brute_force'), ('Şüpheli', 'suspicious')]
        reason_menu = ttk.Combobox(form_inner, textvariable=reason_var, values=[r[0] for r in reasons], width=15)
        reason_menu.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_inner, text="Süre:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        duration_var = tk.StringVar(value='permanent')
        durations_frame = tk.Frame(form_inner, bg='white')
        durations_frame.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)

        tk.Radiobutton(durations_frame, text='15 dk', variable=duration_var, value='15', bg='white').pack(side='left', padx=5)
        tk.Radiobutton(durations_frame, text='1 saat', variable=duration_var, value='60', bg='white').pack(side='left', padx=5)
        tk.Radiobutton(durations_frame, text='1 gün', variable=duration_var, value='1440', bg='white').pack(side='left', padx=5)
        tk.Radiobutton(durations_frame, text='Kalıcı', variable=duration_var, value='permanent', bg='white').pack(side='left', padx=5)

        def add_to_blacklist():
            ip = ip_entry.get().strip()
            reason = reason_var.get()
            duration = duration_var.get()

            if not ip:
                messagebox.showerror("Hata", "IP adresi gerekli!")
                return

            duration_minutes = None if duration == 'permanent' else int(duration)

            result = self.ip_manager.add_to_blacklist(ip, reason, "admin", 'manual', duration_minutes)
            if result['success']:
                messagebox.showinfo("Başarılı", result['message'])
                ip_entry.delete(0, tk.END)
                load_blacklist()
            else:
                messagebox.showerror("Hata", result['message'])

        tk.Button(form_inner, text="🚫 Blacklist'e Ekle", font=('Segoe UI', 10, 'bold'),
                 bg='#e74c3c', fg='white', padx=15, pady=8, command=add_to_blacklist).grid(row=2, column=0, columnspan=4, pady=10)

        # Blacklist Table
        list_frame = tk.LabelFrame(parent, text="Blacklist'teki IP'ler",
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Toolbar
        toolbar = tk.Frame(list_frame, bg='white')
        toolbar.pack(fill='x', padx=10, pady=10)

        tk.Button(toolbar, text=f"{Icons.LOADING} Yenile", font=('Segoe UI', 9, 'bold'),
                 bg='#3498db', fg='white', padx=12, pady=6,
                 command=lambda: load_blacklist()).pack(side='left', padx=5)

        tk.Button(toolbar, text=f"{Icons.PASS} Seçileni Kaldır", font=('Segoe UI', 9, 'bold'),
                 bg='#27ae60', fg='white', padx=12, pady=6,
                 command=lambda: remove_from_blacklist()).pack(side='left', padx=5)

        # Tree
        columns = ('ID', 'IP Adresi', 'Sebep', 'Blokleyen', 'Tarih', 'Bitiş', 'Durum')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        def load_blacklist():
            for item in tree.get_children():
                tree.delete(item)

            blacklist = self.ip_manager.get_blacklist()
            for item in blacklist:
                tree.insert('', 'end', values=(
                    item['id'],
                    item['ip'],
                    item['reason'],
                    item['blocked_by'],
                    item['created_at'][:16],
                    item['expires_at'][:16] if item['expires_at'] != 'Permanent' else 'Kalıcı',
                    item['status']
                ))

        def remove_from_blacklist():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Uyarı", "Lütfen bir IP seçin!")
                return

            item = tree.item(selection[0])
            ip = item['values'][1]

            confirm = messagebox.askyesno("Onay", f"{ip} adresini blacklist'ten çıkarmak istiyor musunuz?")
            if confirm:
                if self.ip_manager.remove_from_blacklist(ip):
                    messagebox.showinfo("Başarılı", "IP blacklist'ten çıkarıldı!")
                    load_blacklist()
                else:
                    messagebox.showerror("Hata", "IP çıkarılamadı!")

        load_blacklist()

    def _create_ip_stats_tab(self, parent):
        """IP İstatistikleri"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)

        try:
            stats = self.ip_manager.get_ip_statistics()

            # Kartlar
            cards_frame = tk.Frame(stats_frame, bg='white')
            cards_frame.pack(fill='x', pady=20)

            cards = [
                ('Whitelist', stats['whitelist_count'], '#27ae60'),
                ('Blacklist', stats['blacklist_count'], '#e74c3c'),
                ('Otomatik Blok', stats['auto_blocked'], '#f39c12')
            ]

            for i, (title, value, color) in enumerate(cards):
                card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
                card.grid(row=0, column=i, padx=15, sticky='ew')
                cards_frame.grid_columnconfigure(i, weight=1)

                tk.Label(card, text=title, font=('Segoe UI', 11, 'bold'),
                        bg=color, fg='white').pack(pady=8)
                tk.Label(card, text=str(value), font=('Segoe UI', 24, 'bold'),
                        bg=color, fg='white').pack(pady=15)
        except Exception as e:
            tk.Label(stats_frame, text=f"İstatistik hatası: {str(e)}",
                    font=('Segoe UI', 10), bg='white', fg='red').pack(pady=20)

    def show_rate_limiting(self):
        """⚡ Rate Limiting Sekmesi"""
        self.clear_right_panel()

        from .components.rate_limiter import RateLimiter
        self.rate_limiter = RateLimiter(self.db_path)

        # Başlık
        header = tk.Frame(self.right_frame, bg='#9b59b6', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚡ RATE LIMITING",
            font=('Segoe UI', 16, 'bold'),
            bg='#9b59b6',
            fg='white'
        ).pack(pady=15)

        # İçerik
        content = tk.Frame(self.right_frame, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Global Limits Info
        info_frame = tk.LabelFrame(content, text="Global Rate Limits",
                                   font=('Segoe UI', 12, 'bold'), bg='white')
        info_frame.pack(fill='x', pady=10)

        limits_text = f"""
{Icons.LOCKED_KEY} Login Denemeleri:      5 / dakika
{Icons.REPORT} API İstekleri:         100 / dakika  
{Icons.FILE} Rapor Oluşturma:      10 / saat
{Icons.SAVE} Veri Export:          5 / saat
        """

        tk.Label(info_frame, text=limits_text, font=('Courier', 10),
                bg='white', justify='left').pack(pady=15, padx=20)

        # Current Stats
        stats_frame = tk.LabelFrame(content, text="Aktif Rate Limits (Son 1 Saat)",
                                    font=('Segoe UI', 12, 'bold'), bg='white')
        stats_frame.pack(fill='both', expand=True, pady=10)

        # Toolbar
        toolbar = tk.Frame(stats_frame, bg='white')
        toolbar.pack(fill='x', padx=10, pady=10)

        tk.Button(toolbar, text=f"{Icons.LOADING} Yenile", font=('Segoe UI', 9, 'bold'),
                 bg='#3498db', fg='white', padx=12, pady=6,
                 command=lambda: load_rate_limits()).pack(side='left', padx=5)

        tk.Button(toolbar, text="🧹 Eski Kayıtları Temizle", font=('Segoe UI', 9, 'bold'),
                 bg='#e74c3c', fg='white', padx=12, pady=6,
                 command=lambda: cleanup_old()).pack(side='left', padx=5)

        # Tree
        columns = ('Resource', 'Identifier', 'İstek Sayısı', 'Başlangıç', 'Durum')
        tree = ttk.Treeview(stats_frame, columns=columns, show='headings', height=12)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(stats_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        def load_rate_limits():
            for item in tree.get_children():
                tree.delete(item)

            stats = self.rate_limiter.get_rate_limit_stats()
            for stat in stats:
                status = '🚫 Blok' if stat['blocked'] else f'{Icons.PASS} Normal'
                tree.insert('', 'end', values=(
                    stat['resource'],
                    stat['identifier'],
                    stat['count'],
                    stat['window_start'][:16],
                    status
                ))

        def cleanup_old():
            deleted = self.rate_limiter.cleanup_old_records(24)
            messagebox.showinfo("Tamamlandı", f"{deleted} eski kayıt temizlendi!")
            load_rate_limits()

        load_rate_limits()

        editor = tk.LabelFrame(content, text="Kural Editörü", font=('Segoe UI', 12, 'bold'), bg='white')
        editor.pack(fill='x', pady=10)
        grid = tk.Frame(editor, bg='white')
        grid.pack(padx=10, pady=10)
        tk.Label(grid, text="Kaynak", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, padx=6, pady=6)
        tk.Label(grid, text="Limit", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=1, padx=6, pady=6)
        tk.Label(grid, text="Pencere (sn)", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=2, padx=6, pady=6)
        rows = [
            ('login', 'rl_login_limit', 'rl_login_window'),
            ('api', 'rl_api_limit', 'rl_api_window'),
            ('report', 'rl_report_limit', 'rl_report_window'),
            ('export', 'rl_export_limit', 'rl_export_window'),
        ]
        entries = {}
        for i, (name, k_limit, k_win) in enumerate(rows, start=1):
            tk.Label(grid, text=name, bg='white').grid(row=i, column=0, sticky='w', padx=6, pady=6)
            e1 = tk.Entry(grid, width=10)
            e2 = tk.Entry(grid, width=10)
            e1.grid(row=i, column=1, padx=6, pady=6)
            e2.grid(row=i, column=2, padx=6, pady=6)
            entries[k_limit] = e1
            entries[k_win] = e2

        def load_rule_values():
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                for k in entries.keys():
                    cur.execute("SELECT value FROM system_settings WHERE key=?", (k,))
                    row = cur.fetchone()
                    if row and row[0] is not None:
                        entries[k].delete(0, tk.END)
                        entries[k].insert(0, str(row[0]))
                conn.close()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        def save_rules():
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                for k, entry in entries.items():
                    val = entry.get().strip()
                    if k.endswith('_limit') or k.endswith('_window'):
                        if val and not str(val).isdigit():
                            messagebox.showerror("Hata", f"Geçersiz sayı: {k} = {val}")
                            return
                    cur.execute("""
                        INSERT INTO system_settings (key, value, category, description)
                        VALUES (?, ?, 'rate_limit', 'Rate limit ayarı')
                        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                    """, (k, val))
                conn.commit()
                conn.close()
                messagebox.showinfo("Kaydedildi", "Rate limit kuralları güncellendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydetme hatası: {e}")

        tk.Button(editor, text="Kaydet", font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', padx=20, pady=8, command=save_rules).pack(pady=10)
        load_rule_values()

    def show_monitoring_dashboard(self):
        """Monitoring Dashboard Sekmesi"""
        self.clear_right_panel()

        from .components.monitoring_dashboard import MonitoringDashboard
        self.monitoring = MonitoringDashboard(self.db_path)

        # Başlık
        header = tk.Frame(self.right_frame, bg='#16a085', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"{Icons.REPORT} MONİTORİNG DASHBOARD",
            font=('Segoe UI', 16, 'bold'),
            bg='#16a085',
            fg='white'
        ).pack(pady=15)

        # Notebook
        notebook = ttk.Notebook(self.right_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Real-time Stats
        stats_frame = tk.Frame(notebook, bg='white')
        notebook.add(stats_frame, text=" Real-time Stats")
        self._create_realtime_stats_tab(stats_frame)

        # Tab 2: Alerts
        alerts_frame = tk.Frame(notebook, bg='white')
        notebook.add(alerts_frame, text=" Alerts & Uyarılar")
        self._create_alerts_tab(alerts_frame)

        # Tab 3: Email Settings
        email_frame = tk.Frame(notebook, bg='white')
        notebook.add(email_frame, text=" Email Ayarları")
        self._create_email_settings_tab(email_frame)

    def _create_realtime_stats_tab(self, parent):
        """Real-time istatistikler"""
        # Stats Cards
        cards_container = tk.Frame(parent, bg='white')
        cards_container.pack(fill='x', padx=20, pady=20)

        # Auto-refresh label
        refresh_label = tk.Label(cards_container, text=f"{Icons.LOADING} Auto-refresh: 5 saniye",
                                font=('Segoe UI', 9), bg='white', fg='gray')
        refresh_label.pack(anchor='e', padx=10)

        cards_frame = tk.Frame(cards_container, bg='white')
        cards_frame.pack(fill='x', pady=10)

        # Stat card'ları oluştur
        stat_labels = {}

        stats_config = [
            ('active_users', 'Aktif Kullanıcılar', '#3498db'),
            ('sessions_today', 'Bugünkü Oturumlar', '#27ae60'),
            ('failed_logins', 'Başarısız Girişler', '#e74c3c'),
            ('security_events', 'Güvenlik Olayları', '#f39c12'),
            ('cpu_usage', 'CPU Kullanımı (%)', '#9b59b6'),
            ('memory_usage', 'RAM Kullanımı (%)', '#e67e22'),
        ]

        for i, (key, title, color) in enumerate(stats_config):
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='ew')
            cards_frame.grid_columnconfigure(i%3, weight=1)

            tk.Label(card, text=title, font=('Segoe UI', 9, 'bold'),
                    bg=color, fg='white').pack(pady=5)
            value_label = tk.Label(card, text='...', font=('Segoe UI', 20, 'bold'),
                                  bg=color, fg='white')
            value_label.pack(pady=10)

            stat_labels[key] = value_label

        # Recent Events
        events_frame = tk.LabelFrame(parent, text="Son Olaylar",
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        events_frame.pack(fill='both', expand=True, padx=20, pady=10)

        events_text = scrolledtext.ScrolledText(events_frame, height=10, font=('Courier', 9))
        events_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Auto-refresh function
        def update_stats():
            try:
                stats = self.monitoring.get_live_stats()

                for key, label in stat_labels.items():
                    value = stats.get(key, 0)
                    if 'usage' in key:
                        label.config(text=f"{value}%")
                    else:
                        label.config(text=str(value))

                # Update events
                events = self.monitoring.get_recent_events(20)
                events_text.delete('1.0', tk.END)
                for event in events[:10]:
                    events_text.insert(tk.END, f"[{event['timestamp'][:16]}] ")
                    events_text.insert(tk.END, f"{event['severity'].upper()}: {event['description']}\n")

                # Schedule next update
                parent.after(5000, update_stats)  # 5 saniye

            except Exception as e:
                logging.error(f"Stats update error: {e}")

        # İlk yükleme
        update_stats()

    def _create_alerts_tab(self, parent):
        """Alerts ve uyarılar"""
        # Toolbar
        toolbar = tk.Frame(parent, bg='white')
        toolbar.pack(fill='x', padx=20, pady=15)

        # Alerts list
        columns = ('Severity', 'Mesaj', 'Zaman')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)

        tree.heading('Severity', text='Önem')
        tree.heading('Mesaj', text='Mesaj')
        tree.heading('Zaman', text='Zaman')

        tree.column('Severity', width=100)
        tree.column('Mesaj', width=400)
        tree.column('Zaman', width=150)

        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        def load_alerts():
            for item in tree.get_children():
                tree.delete(item)
            try:
                alerts = self.monitoring.get_alerts()
            except Exception:
                alerts = []
            for alert in alerts:
                severity_icon = {
                    'critical': '🔴',
                    'warning': '🟠',
                    'info': '🔵'
                }.get(alert.get('severity'), '⚪')
                tree.insert('', 'end', values=(
                    f"{severity_icon} {str(alert.get('severity','')).upper()}",
                    str(alert.get('message','')),
                    str(alert.get('timestamp',''))[:16]
                ))

        tk.Button(toolbar, text=f"{Icons.LOADING} Yenile", font=('Segoe UI', 9, 'bold'),
                 bg='#3498db', fg='white', padx=15, pady=8,
                 command=load_alerts).pack(side='left', padx=5)

        load_alerts()

    def show_twofa_management(self):
        self.clear_right_panel()

        header = tk.Frame(self.right_frame, bg="#2980b9", height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"{Icons.LOCKED_KEY} 2FA YÖNETİMİ",
            font=('Segoe UI', 16, 'bold'),
            bg="#2980b9",
            fg='white'
        ).pack(pady=15)

        content = tk.Frame(self.right_frame, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        toolbar = tk.Frame(content, bg='white')
        toolbar.pack(fill='x', pady=5)

        user_var = tk.StringVar()
        status_var = tk.StringVar(value="Durum: -")

        tk.Label(toolbar, text="Kullanıcı:", font=('Segoe UI', 10), bg='white').pack(side='left')
        user_combo = ttk.Combobox(toolbar, width=24, textvariable=user_var, state='readonly')
        user_combo.pack(side='left', padx=10)

        tk.Label(toolbar, textvariable=status_var, font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left', padx=10)

        actions = tk.Frame(content, bg='white')
        actions.pack(fill='x', pady=10)

        qr_frame = tk.Frame(content, bg='white')
        qr_frame.pack(fill='x', pady=10)

        backup_frame = tk.LabelFrame(content, text="Yedek Kodlar", font=('Segoe UI', 12, 'bold'), bg='white')
        backup_frame.pack(fill='both', expand=True, pady=10)

        backup_text = scrolledtext.ScrolledText(backup_frame, font=('Consolas', 10), height=8)
        backup_text.pack(fill='both', expand=True, padx=10, pady=10)

        force_frame = tk.LabelFrame(content, text="Zorunlu 2FA", font=('Segoe UI', 12, 'bold'), bg='white')
        force_frame.pack(fill='x', pady=10)

        force_var = tk.BooleanVar(value=False)
        tk.Checkbutton(force_frame, text="Tüm kullanıcılar için 2FA zorunlu olsun", variable=force_var, bg='white').pack(side='left', padx=10, pady=10)

        def ensure_columns():
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("PRAGMA table_info(users)")
                cols = [c[1] for c in cur.fetchall()]
                if 'totp_secret' not in cols:
                    cur.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT")
                if 'totp_enabled' not in cols:
                    cur.execute("ALTER TABLE users ADD COLUMN totp_enabled INTEGER DEFAULT 0")
                if 'backup_codes' not in cols:
                    cur.execute("ALTER TABLE users ADD COLUMN backup_codes TEXT")
                conn.commit()
                conn.close()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        def load_users():
            ensure_columns()
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT username, COALESCE(totp_enabled,0) FROM users WHERE deleted_at IS NULL")
                rows = cur.fetchall()
                conn.close()
                values = [r[0] for r in rows]
                user_combo['values'] = values
                if values:
                    user_combo.current(0)
                update_status()
            except Exception:
                user_combo['values'] = []

        def update_status():
            uname = user_var.get()
            if not uname:
                status_var.set("Durum: -")
                return
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT COALESCE(totp_enabled,0) FROM users WHERE username=?", (uname,))
                row = cur.fetchone()
                conn.close()
                on = bool(int((row[0] if row else 0)))
                status_var.set("Durum: Aktif" if on else "Durum: Pasif")
            except Exception:
                status_var.set("Durum: Bilinmiyor")

        def show_qr_image(data_uri: str):
            for w in qr_frame.winfo_children():
                w.destroy()
            try:
                import qrcode
                try:
                    from PIL import ImageTk as PIL_ImageTk
                    has_pil = True
                except Exception:
                    has_pil = False
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(data_uri)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                if has_pil:
                    img = img.resize((200, 200))
                    photo = PIL_ImageTk.PhotoImage(img)
                    lbl = tk.Label(qr_frame, image=photo, bg='white')
                    from typing import Any, cast
                    cast(Any, lbl).image = photo
                    lbl.pack(pady=10)
                else:
                    tk.Label(qr_frame, text=data_uri, font=('Consolas', 9), bg='white').pack(pady=10)
            except Exception:
                tk.Label(qr_frame, text=data_uri, font=('Consolas', 9), bg='white').pack(pady=10)

        def enable_clicked():
            uname = user_var.get()
            if not uname:
                messagebox.showerror("Hata", "Kullanıcı seçin")
                return
            try:
                import sqlite3

                from yonetim.security.core.auth import (enable_2fa,
                                                        generate_totp_secret,
                                                        get_otpauth_uri)
                ensure_columns()
                secret = generate_totp_secret()
                conn = sqlite3.connect(self.db_path)
                res = enable_2fa(conn, uname, secret)
                conn.close()
                backup_text.delete('1.0', tk.END)
                for c in res.get('backup_plain', []):
                    backup_text.insert(tk.END, f"{c}\n")
                uri = get_otpauth_uri(uname, secret, issuer="Sustainage SDG")
                show_qr_image(uri)
                update_status()
                messagebox.showinfo("Başarılı", "2FA etkinleştirildi")
            except Exception as e:
                messagebox.showerror("Hata", f"2FA etkinleştirme hatası: {e}")

        def disable_clicked():
            uname = user_var.get()
            if not uname:
                messagebox.showerror("Hata", "Kullanıcı seçin")
                return
            try:
                import sqlite3

                from yonetim.security.core.auth import disable_2fa
                conn = sqlite3.connect(self.db_path)
                res = disable_2fa(conn, uname)
                conn.close()
                backup_text.delete('1.0', tk.END)
                for w in qr_frame.winfo_children():
                    w.destroy()
                update_status()
                if res.get('ok'):
                    messagebox.showinfo("Başarılı", "2FA devre dışı bırakıldı")
                else:
                    messagebox.showwarning("Bilgi", "İşlem tamamlanamadı")
            except Exception as e:
                messagebox.showerror("Hata", f"2FA kapatma hatası: {e}")

        def show_backup_clicked():
            uname = user_var.get()
            if not uname:
                messagebox.showerror("Hata", "Kullanıcı seçin")
                return
            try:
                import json
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT backup_codes FROM users WHERE username=?", (uname,))
                row = cur.fetchone()
                conn.close()
                backup_text.delete('1.0', tk.END)
                if row and row[0]:
                    codes = json.loads(row[0])
                    backup_text.insert(tk.END, "Hashlenmiş kodlar:\n")
                    for h in codes:
                        backup_text.insert(tk.END, f"{h}\n")
                else:
                    backup_text.insert(tk.END, "Kod yok\n")
            except Exception as e:
                messagebox.showerror("Hata", f"Kodlar alınamadı: {e}")

        def regen_backup_clicked():
            uname = user_var.get()
            if not uname:
                messagebox.showerror("Hata", "Kullanıcı seçin")
                return
            try:
                import sqlite3

                from yonetim.security.core.auth import regen_backup_codes
                conn = sqlite3.connect(self.db_path)
                res = regen_backup_codes(conn, uname)
                conn.close()
                backup_text.delete('1.0', tk.END)
                for c in res.get('backup_plain', []):
                    backup_text.insert(tk.END, f"{c}\n")
                messagebox.showinfo("Başarılı", "Yedek kodlar yenilendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Yenileme hatası: {e}")

        def toggle_force_clicked():
            try:
                import sqlite3

                from yonetim.security.core.auth import (is_force_2fa,
                                                        set_force_2fa)
                conn = sqlite3.connect(self.db_path)
                set_force_2fa(conn, bool(force_var.get()))
                on = is_force_2fa(conn)
                conn.close()
                force_var.set(on)
                messagebox.showinfo("Kaydedildi", "Zorunlu 2FA ayarı güncellendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Ayar kaydedilemedi: {e}")

        tk.Button(actions, text="2FA’yı Etkinleştir", font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white', padx=20, pady=8, command=enable_clicked).pack(side='left', padx=5)
        tk.Button(actions, text="2FA’yı Kapat", font=('Segoe UI', 11, 'bold'), bg='#e74c3c', fg='white', padx=20, pady=8, command=disable_clicked).pack(side='left', padx=5)
        tk.Button(actions, text="Yedek Kodları Göster", font=('Segoe UI', 10), bg='#3498db', fg='white', padx=15, pady=6, command=show_backup_clicked).pack(side='left', padx=5)
        tk.Button(actions, text="Yedek Kodları Yenile", font=('Segoe UI', 10), bg='#f39c12', fg='white', padx=15, pady=6, command=regen_backup_clicked).pack(side='left', padx=5)
        tk.Button(force_frame, text="Kaydet", font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', padx=20, pady=6, command=toggle_force_clicked).pack(side='left', padx=10)

        user_combo.bind('<<ComboboxSelected>>', lambda e: update_status())
        try:
            import sqlite3

            from yonetim.security.core.auth import is_force_2fa
            conn = sqlite3.connect(self.db_path)
            on = is_force_2fa(conn)
            conn.close()
            force_var.set(on)
        except Exception:
            force_var.set(False)
        load_users()

    def _create_email_settings_tab(self, parent):
        """Email notification ayarları"""
        settings_frame = tk.LabelFrame(parent, text="SMTP Ayarları",
                                       font=('Segoe UI', 11, 'bold'), bg='white')
        settings_frame.pack(fill='x', padx=20, pady=20)

        form = tk.Frame(settings_frame, bg='white')
        form.pack(padx=20, pady=20)

        # DB Key, Label, Default, Show
        fields_config = [
            ('smtp_server', 'SMTP Server:', 'smtp.gmail.com', None),
            ('smtp_port', 'Port:', '587', None),
            ('sender_email', 'Email (Gönderen):', 'noreply@sustainage.com', None),
            ('sender_password', 'Password:', '', '*'),
            ('sender_name', 'Gönderen Adı:', 'Sustainage SDG Platform', None),
            ('admin_email', 'Admin Email (Alıcı):', 'admin@company.com', None)
        ]

        entries = {}
        for i, (key, label, default, show_char) in enumerate(fields_config):
            tk.Label(form, text=label, font=('Segoe UI', 10, 'bold'), bg='white').grid(row=i, column=0, sticky='w', padx=5, pady=8)
            entry = tk.Entry(form, font=('Segoe UI', 10), width=40)
            if show_char:
                entry.config(show=show_char)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[key] = entry

        btn_frame = tk.Frame(settings_frame, bg='white')
        btn_frame.pack(pady=15)

        def load_settings():
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                # Ensure table exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                for key, _, default, _ in fields_config:
                    cur.execute("SELECT value FROM system_settings WHERE key=?", (key,))
                    row = cur.fetchone()
                    entries[key].delete(0, tk.END)
                    if row and row[0]:
                        entries[key].insert(0, row[0])
                    else:
                        entries[key].insert(0, default)
                conn.close()
            except Exception as e:
                logging.error(f"Settings load error: {e}")

        def save_settings():
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                
                for key, _, _, _ in fields_config:
                    val = entries[key].get().strip()
                    cur.execute("""
                        INSERT INTO system_settings (key, value, category, description)
                        VALUES (?, ?, 'email', 'SMTP Ayarı')
                        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                    """, (key, val))
                
                conn.commit()
                conn.close()
                messagebox.showinfo("Başarılı", "Email ayarları kaydedildi!")
                return True
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydetme hatası: {e}")
                return False

        def test_email():
            if not save_settings():
                return
                
            try:
                # Local import to avoid circular dependency
                from backend.services.email_service import EmailService
                
                # Re-initialize service to pick up new DB settings
                service = EmailService(self.db_path)
                
                to_email = entries['admin_email'].get()
                subject = "Sustainage SMTP Test"
                body = """
                <h1>SMTP Test Başarılı</h1>
                <p>Bu email Sustainage SDG Platform Süper Yönetici panelinden gönderilmiştir.</p>
                <p>Ayarlarınız doğru çalışıyor.</p>
                """
                
                if service.send_email(to_email, subject, body):
                    messagebox.showinfo("Başarılı", f"Test emaili gönderildi:\n{to_email}")
                else:
                    messagebox.showerror("Hata", "Email gönderilemedi! Logları kontrol edin.")
                    
            except Exception as e:
                messagebox.showerror("Hata", f"Test hatası: {e}")

        tk.Button(btn_frame, text=f"{Icons.EMAIL} Test Email Gönder", font=('Segoe UI', 10, 'bold'),
                 bg='#3498db', fg='white', padx=20, pady=10, command=test_email).pack(side='left', padx=10)

        tk.Button(btn_frame, text=f"{Icons.SAVE} Kaydet", font=('Segoe UI', 10, 'bold'),
                 bg='#27ae60', fg='white', padx=20, pady=10,
                 command=save_settings).pack(side='left', padx=10)

        # Notification Rules
        rules_frame = tk.LabelFrame(parent, text="Bildirim Kuralları",
                                    font=('Segoe UI', 11, 'bold'), bg='white')
        rules_frame.pack(fill='both', expand=True, padx=20, pady=10)

        rules_text = f"""
{Icons.SUCCESS} Başarısız giriş (5+)          → Email gönder
{Icons.SUCCESS} Lisans süresi doluyor (30 gün) → Email gönder  
{Icons.SUCCESS} Güvenlik ihlali                → Email gönder
{Icons.SUCCESS} Sistem hatası                  → Email gönder
{Icons.SUCCESS} Database yedekleme              → Email gönder
        """

        tk.Label(rules_frame, text=rules_text, font=('Courier', 10),
                bg='white', justify='left').pack(pady=15, padx=20)
        
        # Load initial values
        load_settings()

